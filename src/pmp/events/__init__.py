"""Append-only per-worktree journal. Sequence, not wall time, defines order."""
import json
import os
import uuid
from pmp.core.config import validate
from pmp.core.storage import PMPError, canonical, lock, now, atomic_write

class Journal:
    def __init__(self, project):
        self.p = project
        self.path = project.local/'events.jsonl'

    def read(self):
        if not self.path.exists():
            return [], None
        data = self.path.read_bytes()
        rows = data.splitlines(keepends=True)
        events=[]
        seen={}
        for i,line in enumerate(rows):
            if not line.endswith(b'\n'):
                return events, {'offset':sum(len(x) for x in rows[:i]),'bytes':len(line),'reason':'truncated final record'}
            try:
                e = validate('event',json.loads(line))
            except (PMPError,ValueError) as exc:
                raise PMPError(f'Journal corruption at record {i+1}; preserve file and inspect: {exc}') from exc
            if e['project_id'] != self.p.project_id or e['worktree_id'] != self.p.worktree_id:
                raise PMPError('Journal identity mismatch')
            if e['event_id'] in seen:
                if seen[e['event_id']] != e:
                    raise PMPError('Conflicting duplicate event ID')
                continue
            if e['sequence'] != len(events)+1:
                raise PMPError('Journal sequence gap or reordering')
            seen[e['event_id']] = e
            events.append(e)
        return events, None

    def append(self, event_type, payload, *, event_id=None, credibility='verified', session=None):
        with lock(self.p.local/'journal.lock'):
            events,tail = self.read()
            if tail:
                raise PMPError('Truncated journal tail; run pmp doctor --repair-journal to preserve and repair it.')
            event_id = event_id or str(uuid.uuid4())
            for e in events:
                if e['event_id']==event_id:
                    if e['event_type'] != event_type or e['payload'] != payload:
                        raise PMPError('Idempotency key reused with different content')
                    return e
            state = self.p.state()
            e = {'schema_version':'1.0','event_id':event_id,'event_type':event_type,'sequence':len(events)+1,
                 'timestamp':now(),'project_id':self.p.project_id,'worktree_id':self.p.worktree_id,
                 'session_id':session or os.environ.get('PMP_SESSION_ID','manual'),'task_id':state['task_id'],
                 'producer':'pmp-core','credibility':credibility,'privacy':'private','payload':payload}
            validate('event',e)
            self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            fd=os.open(self.path,os.O_APPEND|os.O_CREAT|os.O_WRONLY,0o600)
            try:
                blob=canonical(e)+b'\n'
                with os.fdopen(fd,'ab') as stream:
                    stream.write(blob)
                    stream.flush()
                    os.fsync(stream.fileno())
            except OSError as exc:
                raise PMPError(f'Event persistence failed; inspect disk space: {exc}') from exc
            return e

    def repair_tail(self):
        with lock(self.p.local/'journal.lock'):
            events,tail=self.read()
            if not tail:
                return {'repaired':False}
            original=self.path.read_bytes()
            backup=self.path.with_name('events-damaged-'+str(uuid.uuid4())+'.jsonl')
            atomic_write(backup,original,exclusive=True)
            atomic_write(self.path,original[:tail['offset']])
            return {'repaired':True,'preserved_original':str(backup),'events':len(events)}
