"""Explicit Git/GitHub milestone synchronization; CI remains a separate fact."""
import json
import re
import subprocess
from urllib.parse import quote
from pmp import git
from pmp.core.storage import PMPError, write_json, now
from pmp.security import relative_path, scan, sensitive_name
from pmp.events import Journal

def gh(*args):
    try:
        r=subprocess.run(['gh',*args],capture_output=True,timeout=30)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise PMPError('GitHub CLI unavailable or timed out; local state remains usable',4) from exc
    if r.returncode:
        raise PMPError('GitHub verification unavailable; check gh auth status and network. Synchronization remains unverified.',4)
    try:
        return json.loads(r.stdout)
    except ValueError as exc:
        raise PMPError('GitHub returned invalid JSON; synchronization unverified',4) from exc

def repository(project):
    repo=project.config['github']
    if not repo or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):
        raise PMPError('Set github to an owner/repository reference in .pmp.yml')
    expected={f'https://github.com/{repo}',f'https://github.com/{repo}.git',f'git@github.com:{repo}.git',f'ssh://git@github.com/{repo}.git'}
    urls=git.text(project.root,'remote','get-url','--push','--all','origin',check=False)
    fetch=git.text(project.root,'remote','get-url','--all','origin',check=False)
    if not urls or any(u not in expected for u in urls.splitlines()) or not fetch or any(u not in expected for u in fetch.splitlines()):
        raise PMPError('origin fetch/push URLs must match configured GitHub repository exactly')
    return repo

def inspect(project,refresh=False):
    from pmp.checkpoints import history
    result={'remote':git.remote_status(project.root),'head':project.source()['head'],'checkpoints':[],
            'github_verified':False,'ci':None}
    records,_=history(project)
    for c in records:
        path=(project.shared/'checkpoints'/(c['checkpoint_id']+'.json')).relative_to(project.root).as_posix()
        r=git.run(project.root,'show','HEAD:'+path,check=False)
        committed = r.returncode==0 and r.stdout == (project.local/'checkpoints'/(c['checkpoint_id']+'.json')).read_bytes()
        result['checkpoints'].append({'checkpoint_id':c['checkpoint_id'],'state':'COMMITTED' if committed else 'LOCAL'})
    if refresh:
        repo=repository(project)
        source=project.source()
        branch=source['branch']
        if not branch or not source['head']: raise PMPError('Synchronization requires a named branch with a commit')
        remote=gh('api',f'repos/{repo}/commits/{quote(branch,safe="")}')
        matches=remote.get('sha')==source['head']
        result['github_verified']=matches
        result['remote_commit']=remote.get('sha')
        result['remote']['fresh']=True
        if matches:
            for c in result['checkpoints']:
                if c['state']=='COMMITTED': c['state']='SYNCED'
            result['ci']=gh('run','list','--repo',repo,'--commit',source['head'],'--json','headSha,status,conclusion,url')
    return result

def export(project):
    from pmp.checkpoints import history
    from pmp.verification import evidence_list
    from pmp.recovery import generate
    records,damaged=history(project)
    if damaged: raise PMPError('Repair checkpoint damage before export')
    blobs=[]
    for c in records:
        blobs.append((project.shared/'checkpoints'/(c['checkpoint_id']+'.json'), (project.local/'checkpoints'/(c['checkpoint_id']+'.json')).read_bytes()))
        blobs.append((project.shared/c['handoff'],(project.local/c['handoff']).read_bytes()))
    for e in evidence_list(project):
        blobs.append((project.shared/'evidence'/(e['evidence_id']+'.json'),(project.local/'evidence'/(e['evidence_id']+'.json')).read_bytes()))
    from pmp.core.storage import atomic_write
    for path,blob in blobs:
        relative_path(project.root,path.relative_to(project.root).as_posix())
        if scan(blob) or len(blob)>project.config['security']['max_shared_bytes']:
            raise PMPError('Export refused: potential secret or size limit. Inspect private memory locally.')
        if path.exists() and path.read_bytes()!=blob:
            raise PMPError('Immutable shared record conflict: '+str(path))
    generate(project,shared=True)
    for path,blob in blobs:
        if not path.exists(): atomic_write(path,blob,exclusive=True)
    return {'exported_records':len(blobs),'committed':False,'pushed':False}

def publish(project,*,commit=False,push=False,message='PMP milestone memory'):
    repo=repository(project) if push else None
    # Never include unrelated pre-staged changes, even if the paths look shareable.
    if git.text(project.root,'diff','--cached','--name-only'):
        raise PMPError('Index has staged changes. Review and commit them separately before PMP synchronization.')
    paths=[]
    for name in git.filenames(project.root):
        if not any(name == p or name.startswith(p.rstrip('/')+'/') for p in project.config['security']['share_allowlist']):
            continue
        target=relative_path(project.root,name)
        if not target.is_file():
            raise PMPError('Shareable file missing; review deletion manually: '+name)
        if sensitive_name(name) or target.stat().st_size>project.config['security']['max_shared_bytes'] or scan(target.read_bytes()):
            raise PMPError('Publication refused: potential sensitive data or oversized memory file: '+name)
        paths.append(name)
    if commit:
        if not paths: raise PMPError('No allowlisted memory to commit; run sync --export first')
        git.run(project.root,'add','--',*paths)
        if git.text(project.root,'diff','--cached','--name-only'):
            git.run(project.root,'commit','-m',message)
    if push:
        branch=project.source()['branch']
        if not branch: raise PMPError('Cannot push detached HEAD')
        # Exact branch refspec, no force, no tags, no bypass of protection.
        git.run(project.root,'push','origin',f'HEAD:refs/heads/{branch}')
        result=inspect(project,refresh=True)
        if not result['github_verified']:
            raise PMPError('Push returned but GitHub branch identity differs; synchronization unverified',4)
        Journal(project).append('git.remote_verified',{'commit':result['head'],'repository':repo})
        write_json(project.local/'sync-observation.json',{'commit':result['head'],'timestamp':now(),'repository':repo})
        return result
    return inspect(project)
