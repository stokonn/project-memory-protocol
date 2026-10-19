"""PMP command line. JSON goes to stdout; errors to stderr."""
import argparse
import json
import os
from pathlib import Path
import sys
from pmp import __version__, git
from pmp.core.config import Project, initialize
from pmp.core.storage import PMPError, now, read_json, write_json
from pmp.core.session import writer, start, end, release_stale
from pmp.security import relative_path
from pmp.events import Journal

def parser():
    p=argparse.ArgumentParser(prog='pmp',description='Project Memory Protocol: safe, local-first Git development memory')
    p.add_argument('--version',action='version',version=__version__)
    p.add_argument('--project',default='.',help='Project directory (default: current directory)')
    p.add_argument('--json',action='store_true',help='Print structured JSON')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('init',help='Initialize safely; preserve existing files')
    sub.add_parser('status',help='Inspect state and actual worktree')
    sub.add_parser('check',help='Validate contracts, references and consistency')
    s=sub.add_parser('snapshot',help='Create immutable LOCAL checkpoint; no commit/push')
    s.add_argument('--reason',default='manual')
    s=sub.add_parser('handoff',help='Generate context, never authorization')
    s.add_argument('--shared',action='store_true',help='Explicitly export handoff into repository')
    s=sub.add_parser('resume',help='Read-only recovery inspection; never discard changes')
    s.add_argument('--record',action='store_true',help='Explicitly persist private recovery report and events')
    s=sub.add_parser('verify',help='Inspect applicability or execute an explicit check')
    s.add_argument('--run',metavar='CHECK',help='Check name; command follows --')
    s.add_argument('--timeout',type=float,default=3600)
    s.add_argument('argv',nargs=argparse.REMAINDER)
    s=sub.add_parser('sync',help='Inspect by default; export/commit/push require explicit flags')
    s.add_argument('--refresh',action='store_true',help='Query GitHub branch and CI identity')
    s.add_argument('--export',action='store_true',help='Copy scanned memory into repository for review')
    s.add_argument('--commit',action='store_true',help='Authorize commit of allowlisted shared memory only')
    s.add_argument('--push',action='store_true',help='Authorize ordinary branch push to configured GitHub origin')
    s.add_argument('--message',default='PMP milestone memory')
    s=sub.add_parser('doctor',help='Diagnose without modifying state by default')
    s.add_argument('--repair-journal',action='store_true',help='Preserve damaged original then remove truncated tail')
    sub.add_parser('release-check',help='Evaluate release prerequisites; never publish')
    s=sub.add_parser('history',help='Inspect immutable checkpoint history')
    s.add_argument('--rebuild-index',action='store_true',help='Rebuild disposable local index from validated records')
    s=sub.add_parser('task',help='Activate owner-approved scope, or change task state explicitly')
    t=s.add_subparsers(dest='action',required=True)
    a=t.add_parser('activate'); a.add_argument('task_id'); a.add_argument('--approved-scope',required=True)
    t.add_parser('archive')
    a=t.add_parser('set'); a.add_argument('--phase',choices=['planning','approved','implementing','verifying','ready_for_release','released'])
    a.add_argument('--status',choices=['active','paused','interrupted','blocked'])
    a.add_argument('--authorization',help='Existing owner approval reference; explicit caller assertion, not inferred from text')
    for flag in ['completed','in-progress','blocker','next-action']: a.add_argument('--'+flag,action='append')
    s=sub.add_parser('session',help='Manual single-writer ownership')
    t=s.add_subparsers(dest='action',required=True)
    a=t.add_parser('start'); a.add_argument('--owner',default='human')
    t.add_parser('end')
    a=t.add_parser('release-stale'); a.add_argument('--session-id',required=True)
    s=sub.add_parser('watcher',help='Session-scoped observer lifecycle')
    s.add_argument('action',choices=['start','stop','status','run'])
    s=sub.add_parser('launch',help='Launch an agent or human command with lease and independent watcher')
    s.add_argument('adapter',choices=['generic','codex','claude','opencode'])
    s.add_argument('argv',nargs=argparse.REMAINDER)
    s=sub.add_parser('adapter',help='Inspect/install/remove optional integrations')
    s.add_argument('action',choices=['inspect','install','uninstall'])
    s.add_argument('name',choices=['generic','codex','claude','opencode'])
    s.add_argument('--native',action='store_true',help='Opt in to experimental documented native artifacts')
    s=sub.add_parser('hook',help='Bounded native hook receiver; no transcript collection')
    s.add_argument('--event',required=True)
    return p

def strip_separator(argv):
    return argv[1:] if argv and argv[0]=='--' else argv

def dispatch(a):
    if a.command=='init':
        p,m=initialize(a.project)
        return {'initialized':True,'project_id':p.project_id,'root':str(p.root),'preserved':m},0
    p=Project(a.project)
    if a.command in ['status','resume']:
        from pmp.recovery import inspect
        if a.command=='resume' and a.record:
            import uuid
            with writer(p):
                Journal(p).append('recovery.started',{'reason':'Explicit recovery report'})
                result=inspect(p)
                ref='recovery/'+str(uuid.uuid4())+'.json'
                write_json(p.local/ref,result,exclusive=True)
                Journal(p).append('recovery.completed',{'report':ref})
                result['recorded_report']=ref
        else:
            result=inspect(p)
        if a.command=='status':
            from pmp.github import inspect as sync_status
            result['synchronization']=sync_status(p)
        return result,0
    if a.command in ['check','doctor']:
        from pmp.recovery import check
        repair=None
        if a.command=='doctor' and a.repair_journal:
            with writer(p): repair=Journal(p).repair_tail()
        result=check(p)
        if a.command=='doctor':
            import shutil
            result['dependencies']={x:bool(shutil.which(x)) for x in ['git','gh','codex','claude','opencode']}
            result['recovery_store']=str(p.local)
            result['disk_free_bytes']=shutil.disk_usage(p.root).free
            if repair: result['repair']=repair
        return result,0 if result['valid'] else 2
    if a.command=='snapshot':
        from pmp.checkpoints import create
        with writer(p): result=create(p,a.reason)
        return result,0
    if a.command=='handoff':
        from pmp.recovery import generate
        with writer(p): result=generate(p,shared=a.shared)
        return result,0
    if a.command=='verify':
        from pmp.verification import summary,execute
        if a.run:
            if a.timeout<=0: raise PMPError('Timeout must be positive')
            with writer(p): result=execute(p,a.run,strip_separator(a.argv),a.timeout)
            return result,0 if result['outcome']=='passed' else 1
        if a.argv: raise PMPError('Use verify --run CHECK -- COMMAND to execute a check')
        return {'verification':summary(p)},0
    if a.command=='release-check':
        from pmp.verification import release_check
        result=release_check(p)
        return result,0 if result['ready'] else 1
    if a.command=='sync':
        from pmp.github import inspect,export,publish
        if a.export or a.commit or a.push:
            with writer(p):
                exported=export(p) if a.export else None
                result=publish(p,commit=a.commit,push=a.push,message=a.message) if a.commit or a.push else exported
        else: result=inspect(p,refresh=a.refresh)
        return result,0
    if a.command=='history':
        from pmp.checkpoints import history,shared_history
        records,damaged=history(p)
        shared,shared_damaged=shared_history(p)
        if a.rebuild_index:
            with writer(p): write_json(p.local/'checkpoint-index.json',[c['checkpoint_id'] for c in records])
        return {'checkpoints':records,'shared_checkpoints':shared,'damaged':damaged+shared_damaged},0 if not damaged+shared_damaged else 2
    if a.command=='task':
        with writer(p):
            state=p.state()
            if a.action=='activate':
                if not relative_path(p.root,a.approved_scope).is_file(): raise PMPError('Approved scope reference must exist inside repository')
                if state['task_id'] and state['task_id']!=a.task_id:
                    Journal(p).append('task.scope_conflict',{'expected':state['task_id'],'actual':a.task_id})
                    raise PMPError('Active task scope conflict. Finish or explicitly archive existing task before switching.',3)
                state.update(task_id=a.task_id,scope_ref=a.approved_scope,phase='approved',status='active')
                p.save_state(state)
                Journal(p).append('task.activated',{'scope_ref':a.approved_scope},credibility='reported')
            elif a.action=='archive':
                state.update(task_id=None,scope_ref=None,phase='planning',status='paused',release_authorization=None)
                p.save_state(state)
            else:
                if a.phase in ['ready_for_release','released']:
                    from pmp.verification import summary
                    if not a.authorization or not relative_path(p.root,a.authorization).is_file():
                        raise PMPError('Explicit owner authorization reference required for release phases')
                    checks=summary(p)
                    for name in p.config['verification']['required_checks']:
                        good=[e for e in checks if e['check']==name and e['applicable'] and e['outcome']=='passed' and e['credibility']=='verified']
                        if p.config['verification']['require_test_count']: good=[e for e in good if (e['tests_executed'] or 0)>0]
                        if not good: raise PMPError('Missing applicable verified evidence: '+name)
                    state['release_authorization']=a.authorization
                if a.phase: state['phase']=a.phase
                if a.status: state['status']=a.status
                for arg,key in [('completed','completed'),('in_progress','in_progress'),('blocker','blockers'),('next_action','next_actions')]:
                    if getattr(a,arg): state[key]=getattr(a,arg)
                p.save_state(state)
        return state,0
    if a.command=='session':
        if a.action=='start': return start(p,a.owner),0
        if a.action=='end': end(p); return {'ended':True},0
        return release_stale(p,a.session_id),0
    if a.command=='watcher':
        from pmp import watcher
        if a.action=='status':
            path=p.local/'watcher.json'
            return read_json(path) if path.exists() else {'state':'absent'},0
        if a.action=='run': watcher.run(p); return {'stopped':True},0
        with writer(p): return getattr(watcher,a.action)(p),0
    if a.command=='launch':
        from pmp.watcher import launch
        from pmp.adapters import inspect
        if p.config['adapters'][a.adapter]=='disabled': raise PMPError('Adapter disabled')
        cmd=strip_separator(a.argv)
        if a.adapter!='generic':
            if not inspect(a.adapter)['binary_available']: raise PMPError('Agent executable unavailable; use generic wrapper with an explicit command')
            cmd=[a.adapter,*cmd]
        if not cmd: raise PMPError('Generic launch requires a command after --')
        code=launch(p,cmd,a.adapter)
        return {'exit_code':code},code
    if a.command=='adapter':
        from pmp import adapters
        if a.action=='inspect': return adapters.inspect(a.name),0
        with writer(p):
            result=adapters.install(p,a.name,native=a.native) if a.action=='install' else adapters.uninstall(p,a.name)
        return result,0
    if a.command=='hook':
        from pmp.adapters import hook
        blob=sys.stdin.buffer.read(65537)
        if len(blob)>65536: raise PMPError('Hook payload exceeds 64 KiB; ignored')
        try: value=json.loads(blob)
        except ValueError as exc: raise PMPError('Invalid hook JSON') from exc
        return hook(p,a.event,value),0
    raise PMPError('Unknown command')

def main(argv=None):
    a=parser().parse_args(argv)
    try:
        result,code=dispatch(a)
        # Stable structured output for every command; --json retained for explicit scripts.
        print(json.dumps(result,indent=2,ensure_ascii=True))
        return code
    except PMPError as exc:
        print(json.dumps({'error':str(exc),'exit_code':exc.code}),file=sys.stderr)
        return exc.code
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc),'hint':'Inspect disk space, permissions and pmp doctor; worktree files are preserved.'}),file=sys.stderr)
        return 2
