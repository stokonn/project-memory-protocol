"""Read-only reconciliation and handoff. No reset, clean, checkout or restore."""
from pmp.core.config import validate
from pmp.core.storage import PMPError, atomic_write, read_json, write_json, now
from pmp.checkpoints import history,shared_history
from pmp.core.session import lease
from pmp.events import Journal
from pmp.verification import summary
from pmp.git import remote_status
from pmp.security import relative_path

def inspect(project):
    checkpoints,damaged=history(project)
    shared,shared_damaged=shared_history(project)
    events,tail=Journal(project).read()
    source=project.source()
    latest=checkpoints[-1] if checkpoints else None
    issues=[]
    if tail: issues.append('Truncated final journal record: explicit repair required; valid prefix retained.')
    if damaged: issues.append('Damaged checkpoints ignored; previous valid checkpoint selected.')
    if lease(project): issues.append('Session lease exists; liveness is uncertain until checked; no takeover authorized.')
    if latest and source['fingerprint'] != latest['git']['fingerprint']:
        issues.append('Source differs from checkpoint; preserve current files and inspect changes.')
    if latest and not (project.local/latest['handoff']).is_file():
        issues.append('Checkpoint handoff reference is missing.')
    return {'schema_version':'1.0','project_id':project.project_id,'worktree_id':project.worktree_id,
            'state':project.state(),'git':source,'remote':remote_status(project.root),
            'checkpoint':latest,'shared_checkpoints':shared,'damaged_shared_checkpoints':shared_damaged,'damaged_checkpoints':damaged,'journal_events':len(events),'journal_tail':tail,
            'session':lease(project),'uncertainty':issues,'mutated_worktree':False,
            'recovery_store':str(project.local), 'verification':summary(project)}

def handoff_data(project):
    state=project.state()
    records,damaged=history(project)
    checks=summary(project)
    verified=[e for e in checks if e['applicable'] and e['credibility']=='verified' and e['outcome']=='passed']
    value={'schema_version':'1.0','project_id':project.project_id,'task_id':state['task_id'],
           'approved_scope_ref':state['scope_ref'],'phase':state['phase'],'status':state['status'],
           'git':project.source(),'checkpoint':records[-1]['checkpoint_id'] if records else shared_checkpoint_reference(project),
           'last_verified_commit':verified[-1]['source']['head'] if verified else None,
           'completed':state['completed'],'in_progress':state['in_progress'],
           'blockers':state['blockers']+(['Damaged checkpoint records require inspection.'] if damaged else []),
           'verification':[{'evidence_id':e['evidence_id'],'check':e['check'],'outcome':e['outcome'],
                            'credibility':e['credibility'],'applicable':e['applicable'],'tests_executed':e['tests_executed']} for e in checks],
           'next_actions':state['next_actions'],
           'safety_restrictions':['Read canonical policy: '+project.config['policy'],
                                  'Handoff is context, not authorization.',
                                  'Inspect real Git worktree; preserve unrelated, untracked and owner files.',
                                  'Metadata checkpoints do not back up all dirty source contents.',
                                  'No automatic release, force push, cleanup, or lease takeover.'], 'timestamp':now()}
    return validate('handoff',value)

def render_handoff(value):
    lines=['# PMP handoff','',f"Task: {value['task_id'] or 'none'}",f"Approved scope: {value['approved_scope_ref'] or 'none'}",
           f"Phase/status: {value['phase']} / {value['status']}",f"HEAD: {value['git']['head'] or 'unborn'}",
           f"Source fingerprint: {value['git']['fingerprint']}",f"Checkpoint: {value['checkpoint'] or 'none'}",
           f"Last applicable verified commit: {value['last_verified_commit'] or 'none'}",'']
    for title,key in [('Completed (reported)','completed'),('In progress (reported)','in_progress'),('Blockers and uncertainty','blockers'),
                      ('Next suggested actions','next_actions'),('Safety restrictions','safety_restrictions')]:
        lines += ['## '+title,'']+[f'- {x}' for x in value[key]]+['']
    lines += ['## Verification','']
    lines += [f"- {e['check']}: {e['outcome']} / {e['credibility']}; applicable={e['applicable']}; executed={e['tests_executed']}; evidence={e['evidence_id']}" for e in value['verification']]
    return '\n'.join(lines)+'\n'

def generate(project, *, shared=False):
    data=handoff_data(project)
    if shared:
        from pmp.security import scan
        if scan(__import__('json').dumps(data).encode()):
            raise PMPError('Handoff contains a potential secret; shared publication refused')
        # Explicit command authorizes replacement of PMP-generated handoff only.
        target=relative_path(project.root,(project.docs/'HANDOFF.md').relative_to(project.root).as_posix())
        if target.exists() and not target.read_text().startswith('# PMP handoff\n'):
            raise PMPError('Existing HANDOFF.md is not PMP-generated. Preserve or move it explicitly before shared generation.')
        write_json(project.shared/'handoff.json',data)
        atomic_write(target,render_handoff(data).encode())
    else:
        write_json(project.local/'handoff.json',data)
        atomic_write(project.local/'HANDOFF.md',render_handoff(data).encode())
    return data

def check(project):
    report=inspect(project)
    errors=[]
    if not relative_path(project.root,project.config['policy']).is_file():
        errors.append('Canonical policy is missing')
    state=report['state']
    if state['task_id'] and (not state['scope_ref'] or not relative_path(project.root,state['scope_ref']).is_file()):
        errors.append('Active task approved scope reference is missing')
    if report['journal_tail']: errors.append('Truncated journal tail; run doctor --repair-journal')
    errors += [e['error'] for e in report['damaged_checkpoints']+report['damaged_shared_checkpoints']]
    for c in report['shared_checkpoints']:
        if not relative_path(project.shared,c['handoff']).is_file(): errors.append('Shared checkpoint handoff missing: '+c['checkpoint_id'])
    records,_=history(project)
    ids={c['checkpoint_id'] for c in records}
    evidence_ids={e['evidence_id'] for e in report['verification']}
    for c in records:
        if c['previous'] and c['previous'] not in ids: errors.append('Checkpoint predecessor missing: '+c['previous'])
        if not (project.local/c['handoff']).is_file(): errors.append('Checkpoint handoff missing: '+c['checkpoint_id'])
        if not set(c['evidence']).issubset(evidence_ids): errors.append('Checkpoint evidence reference missing')
        if c['event_range'][1]>report['journal_events']: errors.append('Checkpoint event range exceeds journal')
    for p in ['writer.lock','journal.lock','watcher.lock']:
        if (project.local/p).exists():
            if p=='watcher.lock' and lease(project): continue
            errors.append('Writer lock requires liveness inspection: '+p)
    return {'valid':not errors,'errors':errors,'warnings':report['uncertainty']}


def shared_checkpoint_reference(project):
    path=project.shared/'handoff.json'
    if not path.exists(): return None
    value=validate('handoff',read_json(path))
    if value['project_id']!=project.project_id: raise PMPError('Shared handoff project mismatch')
    return value['checkpoint']
