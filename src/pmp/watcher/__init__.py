"""Session-scoped independent observer; bounded work, no model calls."""
import os
import subprocess
import sys
import time
from pmp.core.config import Project
from pmp.core.storage import PMPError, write_json, read_json, now
from pmp.core.session import lease, writer, heartbeat, process_alive
from pmp.events import Journal
from pmp.checkpoints import create

def start(project):
    current=lease(project)
    if not current or current['session_id']!=os.environ.get('PMP_SESSION_ID'):
        raise PMPError('Start/own a session before starting its watcher')
    marker=project.local/'watcher.json'
    if marker.exists() and read_json(marker).get('state') in ['running','starting']:
        raise PMPError('Watcher may already be active; inspect metadata before restarting')
    stop=project.local/'watcher.stop'
    if stop.exists(): stop.unlink()
    write_json(marker,{'state':'starting','session_id':current['session_id'],'timestamp':now()})
    process=subprocess.Popen([sys.executable,'-m','pmp','--project',str(project.root),'watcher','run'],
                             stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                             start_new_session=(os.name!='nt'))
    # Worker owns metadata after launch; do not overwrite it here.
    return {'pid':process.pid,'session_id':current['session_id']}

def stop(project):
    from pmp.core.storage import atomic_write
    atomic_write(project.local/'watcher.stop',b'stop\n')
    return {'stop_requested':True,'note':'Cooperative stop within next poll; no unrelated PID is signalled.'}

def run(project):
    current=lease(project)
    if not current or current['session_id']!=os.environ.get('PMP_SESSION_ID'):
        raise PMPError('Watcher session identity mismatch')
    cfg=project.config['automation']
    from pmp.core.storage import lock
    with lock(project.local/'watcher.lock'):
        metadata={'state':'running','pid':os.getpid(),'session_id':current['session_id'],'timestamp':now(),'last_error':None}
        write_json(project.local/'watcher.json',metadata)
        last=project.source()['fingerprint']; saved=last
        changed_at=None; checkpoint_at=time.monotonic()
        try:
            while not (project.local/'watcher.stop').exists():
                try:
                    if not lease(project) or lease(project)['session_id'] != current['session_id']:
                        break
                    heartbeat(project)
                    source=project.source(); tick=time.monotonic()
                    if source['fingerprint']!=last:
                        last=source['fingerprint']; changed_at=tick
                        with writer(project):
                            Journal(project).append('workspace.changed',{'fingerprint':last})
                    if changed_at is not None and last!=saved and tick-changed_at>=cfg['debounce_seconds'] and tick-checkpoint_at>=cfg['checkpoint_seconds']:
                        with writer(project): create(project,'watcher: debounced changes')
                        saved=last; checkpoint_at=tick
                    # Positive local owner death warrants observation, not lease takeover.
                    if current['host']==__import__('socket').gethostname():
                        if process_alive(current['pid']) is False:
                            with writer(project):
                                Journal(project).append('session.interruption_suspected',{'reason':'Watcher observed owner process exit'})
                                create(project,'watcher: owner process exited')
                            break
                except (PMPError,OSError) as exc:
                    metadata['last_error']=str(exc)
                metadata['timestamp']=now()
                write_json(project.local/'watcher.json',metadata)
                deadline=time.monotonic()+cfg['heartbeat_seconds']
                while time.monotonic()<deadline and not (project.local/'watcher.stop').exists():
                    time.sleep(min(.1,max(0,deadline-time.monotonic())))
        finally:
            metadata.update(state='stopped',timestamp=now())
            write_json(project.local/'watcher.json',metadata)

def launch(project,command,owner):
    from pmp.core.session import start as session_start, end
    value=session_start(project,owner)
    old=os.environ.get('PMP_SESSION_ID')
    os.environ['PMP_SESSION_ID']=value['session_id']
    watcher=None
    result=1
    try:
        watcher=start(project)
        with writer(project): create(project,'session launch')
        result=subprocess.call(command,cwd=project.root)
    except KeyboardInterrupt:
        result=130
    finally:
        if watcher:
            stop(project)
            # Wait briefly for in-flight checkpoint work to finish before final snapshot.
            deadline=time.monotonic()+5
            while time.monotonic()<deadline:
                meta=project.local/'watcher.json'
                if meta.exists() and read_json(meta).get('state')=='stopped': break
                time.sleep(.05)
        try:
            with writer(project): create(project,'session stopped')
            end(project,result)
        finally:
            if old is None: os.environ.pop('PMP_SESSION_ID',None)
            else: os.environ['PMP_SESSION_ID']=old
    return result
