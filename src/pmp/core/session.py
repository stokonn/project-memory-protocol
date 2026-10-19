"""Cooperative ownership. Expired heartbeat alone never authorizes takeover."""
import os
import socket
import uuid
from contextlib import contextmanager
from pmp.core.storage import PMPError, lock, read_json, write_json, now
from pmp.events import Journal

def lease(project):
    path=project.local/'session.json'
    return read_json(path) if path.exists() else None

def check_owner(project):
    current=lease(project)
    if current and current['session_id'] != os.environ.get('PMP_SESSION_ID'):
        raise PMPError('Workspace has a session lease. Use its session environment or inspect pmp resume; never take over automatically.',3)

@contextmanager
def writer(project):
    with lock(project.local/'writer.lock'):
        check_owner(project)
        yield

def start(project, owner='human'):
    with writer(project):
        if lease(project):
            raise PMPError('A session already owns this worktree',3)
        value={'session_id':str(uuid.uuid4()),'pid':os.getpid(),'host':socket.gethostname(),
               'owner':owner,'started':now(),'heartbeat':now(),'worktree_id':project.worktree_id}
        write_json(project.local/'session.json',value,exclusive=True)
        Journal(project).append('session.started',{'owner':owner},session=value['session_id'])
        return value

def heartbeat(project):
    with writer(project):
        value=lease(project)
        if not value:
            raise PMPError('No session lease')
        value['heartbeat']=now()
        write_json(project.local/'session.json',value)
        Journal(project).append('session.heartbeat',{'pid':os.getpid()})

def end(project, exit_code=0):
    with writer(project):
        if not lease(project):
            raise PMPError('No session lease')
        Journal(project).append('session.ended',{'exit_code':exit_code})
        (project.local/'session.json').unlink()

def release_stale(project, session_id):
    # Explicit operator acknowledgement plus positive local process death required.
    with lock(project.local/'writer.lock'):
        value=lease(project)
        if not value or value['session_id'] != session_id:
            raise PMPError('Session ID mismatch')
        if value['host'] != socket.gethostname():
            raise PMPError('Remote host lease cannot be safely classified; coordinate with its owner')
        alive=process_alive(value['pid'])
        if alive is None:
            raise PMPError('Process liveness uncertain; refusing takeover')
        if alive:
            raise PMPError('Lease process may still be alive; refusing takeover',3)
        Journal(project).append('session.interruption_suspected',{'reason':'Operator confirmed dead local process'},session=session_id)
        destination=project.local/('session-ended-'+session_id+'.json')
        write_json(destination,value,exclusive=True)
        (project.local/'session.json').unlink()
        return {'released':session_id,'preserved':str(destination)}


def process_alive(pid):
    """Tri-state probe. Windows kill(pid, 0) is NOT a safe liveness primitive."""
    if not isinstance(pid,int) or pid<=0: return None
    if os.name=='nt':
        import ctypes
        from ctypes import wintypes
        api=ctypes.WinDLL('kernel32',use_last_error=True)
        api.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
        api.OpenProcess.restype=wintypes.HANDLE
        api.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
        api.GetExitCodeProcess.restype=wintypes.BOOL
        api.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=api.OpenProcess(0x1000,False,pid) # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle: return False if ctypes.get_last_error()==87 else None
        try:
            code=wintypes.DWORD()
            if not api.GetExitCodeProcess(handle,ctypes.byref(code)): return None
            return code.value==259 # STILL_ACTIVE
        finally:
            api.CloseHandle(handle)
    try:
        os.kill(pid,0)
        return True
    except ProcessLookupError: return False
    except OSError: return None
