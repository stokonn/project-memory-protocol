"""Immutable, integrity-protected local checkpoints and opt-in private backups."""
import hashlib
import uuid
from pmp.core.config import validate
from pmp.core.storage import PMPError, intact, seal, write_json, read_json, now, atomic_write
from pmp.events import Journal
from pmp.security import relative_path, scan, sensitive_name

def history(project):
    valid=[]
    damaged=[]
    for path in sorted((project.local/'checkpoints').glob('*.json')):
        try:
            c=validate('checkpoint',read_json(path))
            relative_path(project.local,c['handoff'])
            if not intact(c) or c['project_id']!=project.project_id or c['worktree_id']!=project.worktree_id or path.stem != c['checkpoint_id']:
                raise PMPError('Checkpoint integrity or identity mismatch')
            validate_handoff(project.local,c)
            validate_backup(project,c)
            valid.append(c)
        except PMPError as exc:
            damaged.append({'path':str(path),'error':str(exc)})
    # An independent local checkpoint sequence also orders orphan records after failed event appends.
    valid.sort(key=lambda c:c['sequence'])
    if len({c['sequence'] for c in valid})!=len(valid):
        raise PMPError('Duplicate local checkpoint sequence; inspect competing writers')
    return valid,damaged

def create(project,reason='manual'):
    from pmp.recovery import handoff_data
    from pmp.verification import evidence_list
    records,damaged=history(project)
    previous=records[-1]['checkpoint_id'] if records else None
    state=project.state()
    source=project.source()
    cp_id=str(uuid.uuid4())
    folder=project.local/'checkpoints'
    handoff_path=project.local/'handoffs'/(cp_id+'.json')
    handoff=handoff_data(project)
    handoff['checkpoint']=cp_id
    write_json(handoff_path,handoff,exclusive=True)
    handoff_hash=hashlib.sha256(handoff_path.read_bytes()).hexdigest()
    backups=[]
    limit=project.config['checkpoint']['max_backup_bytes']
    total=0
    for name in project.config['checkpoint']['backup_allowlist']:
        path=relative_path(project.root,name)
        if not path.is_file():
            continue
        if sensitive_name(name) or path.stat().st_size > limit-total:
            raise PMPError('Private backup refused: sensitive filename or size limit')
        with path.open('rb') as stream: blob=stream.read(limit-total+1)
        if len(blob)>limit-total: raise PMPError('Backup grew beyond configured size limit')
        if scan(blob):
            raise PMPError('Private backup refused: potential secret; no content persisted')
        dest=project.local/'backups'/cp_id/name
        atomic_write(dest,blob,exclusive=True)
        total+=len(blob)
        backups.append({'path':name,'sha256':hashlib.sha256(blob).hexdigest()})
    manifest_hash=None
    if backups:
        write_json(project.local/'backups'/cp_id/'manifest.json',backups,exclusive=True)
        manifest_hash=hashlib.sha256((project.local/'backups'/cp_id/'manifest.json').read_bytes()).hexdigest()
    # Source changed during capture => no coherent source claim.
    if project.source()['fingerprint']!=source['fingerprint']:
        source['complete']=False
    if source['head'] and (not records or records[-1]['git']['head']!=source['head']):
        Journal(project).append('git.commit_observed',{'commit':source['head']})
    events,tail=Journal(project).read()
    if tail:
        raise PMPError('Repair truncated journal before checkpointing')
    data={'schema_version':'1.0','sequence':max((c['sequence'] for c in records),default=0)+1,'checkpoint_id':cp_id,'project_id':project.project_id,
          'worktree_id':project.worktree_id,'task_id':state['task_id'],
          'session_id':__import__('os').environ.get('PMP_SESSION_ID','manual'),'timestamp':now(),'reason':reason,
          'previous':previous,'phase':state['phase'],'status':state['status'],'git':source,
          'evidence':[e['evidence_id'] for e in evidence_list(project)],
          'event_range':[1 if events else 0,len(events)],'handoff':handoff_path.relative_to(project.local).as_posix(),
          'handoff_hash':handoff_hash,'storage_state':'LOCAL','recovery':{'backup_manifest_hash':manifest_hash,'content_backup':bool(backups),'files':[b['path'] for b in backups],
          'limitations':['Metadata checkpoint is not a full worktree backup. Only explicitly allowlisted files have private content copies.',
                        'Ignored files, secrets, and unsaved editor buffers are not backed up.']}}
    data=seal(data)
    validate('checkpoint',data)
    write_json(folder/(cp_id+'.json'),data,exclusive=True)
    Journal(project).append('checkpoint.created',{'checkpoint_id':cp_id})
    return data


def shared_history(project):
    """Read exported context without importing another worktree's private ownership."""
    records=[]; damaged=[]
    for path in sorted((project.shared/'checkpoints').glob('*.json')):
        try:
            c=validate('checkpoint',read_json(path))
            relative_path(project.shared,c['handoff'])
            if not intact(c) or c['project_id']!=project.project_id or path.stem!=c['checkpoint_id']:
                raise PMPError('Shared checkpoint integrity or project identity mismatch')
            validate_handoff(project.shared,c)
            records.append(c)
        except PMPError as exc:
            damaged.append({'path':str(path),'error':str(exc)})
    return records,damaged


def validate_handoff(base,c):
    path=relative_path(base,c['handoff'])
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=c['handoff_hash']:
        raise PMPError('Checkpoint handoff missing or corrupted')
    validate('handoff',read_json(path))


def validate_backup(project,c):
    if not c['recovery']['content_backup']: return
    base=project.local/'backups'/c['checkpoint_id']
    manifest=base/'manifest.json'
    if not manifest.is_file() or hashlib.sha256(manifest.read_bytes()).hexdigest()!=c['recovery']['backup_manifest_hash']:
        raise PMPError('Checkpoint private backup manifest missing or corrupted')
    entries=read_json(manifest)
    if not isinstance(entries,list) or not all(isinstance(e,dict) and set(e)=={'path','sha256'} for e in entries):
        raise PMPError('Invalid backup manifest')
    if [e['path'] for e in entries]!=c['recovery']['files']: raise PMPError('Backup manifest coverage mismatch')
    for entry in entries:
        path=relative_path(base,entry['path'])
        if not path.is_file(): raise PMPError('Private backup file missing')
        h=hashlib.sha256()
        with path.open('rb') as stream:
            while block:=stream.read(1024*1024): h.update(block)
        if h.hexdigest()!=entry['sha256']: raise PMPError('Private backup file corrupted')
