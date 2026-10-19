"""Git inspection without destructive worktree operations."""
import hashlib
import os
from pathlib import Path
import subprocess
from pmp.core.storage import PMPError

def run(root, *args, check=True, timeout=30):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_TERMINAL_PROMPT='0')
    try:
        result = subprocess.run(['git','-C',str(root),*args], capture_output=True, env=env, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PMPError(f'Git unavailable or timed out: {exc}') from exc
    if check and result.returncode:
        raise PMPError(f'Git {args[0]} failed (exit {result.returncode}); inspect repository and permissions.')
    return result

def text(root, *args, check=True):
    r = run(root,*args,check=check)
    return r.stdout.decode('utf-8', 'surrogateescape').strip() if r.returncode == 0 else None

def root_at(path):
    value = text(path,'rev-parse','--show-toplevel',check=False)
    if not value:
        raise PMPError('Not a Git worktree. Run pmp init here, or select a project with --project.')
    return Path(value).resolve()

def filenames(root):
    result = run(root,'ls-files','-z','--cached','--others','--exclude-standard')
    return sorted(set(os.fsdecode(p) for p in result.stdout.split(b'\0') if p))

def inspect(root, excluded=()):
    before = text(root,'status','--porcelain=v1','--untracked-files=all')
    h = hashlib.sha256()
    complete = True
    for name in filenames(root):
        if any(name == p or name.startswith(p.rstrip('/')+'/') for p in excluded):
            continue
        p = root / name
        h.update(os.fsencode(name)+b'\0')
        try:
            if p.is_symlink():
                h.update(b'link\0'+os.fsencode(os.readlink(p)))
            elif p.is_file():
                # Incremental, bounded-memory hashing; never persist contents here.
                meta = p.stat()
                h.update(str(meta.st_mode & 0o111).encode()+b'\0')
                with p.open('rb') as stream:
                    while block := stream.read(1024*1024):
                        h.update(block)
                after = p.stat()
                if (meta.st_size,meta.st_mtime_ns) != (after.st_size,after.st_mtime_ns):
                    complete = False
            elif p.is_dir():
                # Submodules need a separate protocol context; never certify implicitly.
                complete = False
                h.update(b'unsupported-directory')
            else:
                h.update(b'missing')
        except OSError:
            complete = False
            h.update(b'unreadable')
    status = text(root,'status','--porcelain=v1','--untracked-files=all')
    return {'head':text(root,'rev-parse','--verify','HEAD',check=False),
            'branch':text(root,'symbolic-ref','--short','-q','HEAD',check=False),
            'status':status or '', 'clean':not status,'fingerprint':h.hexdigest(),
            'complete':complete and before == status}

def remote_status(root):
    upstream = text(root,'rev-parse','--abbrev-ref','@{upstream}',check=False)
    if not upstream:
        return {'upstream':None,'ahead':None,'behind':None,'fresh':False}
    counts = text(root,'rev-list','--left-right','--count','HEAD...@{upstream}').split()
    return {'upstream':upstream,'ahead':int(counts[0]),'behind':int(counts[1]),'fresh':False}
