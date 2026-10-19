"""Durable writes and cooperative exclusion. Never silently break a stale lock."""
from __future__ import annotations
import contextlib
import hashlib
import json
import os
from pathlib import Path
import socket
import tempfile
from datetime import datetime, timezone

class PMPError(Exception):
    """An actionable protocol or operating error."""
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code

def now():
    return datetime.now(timezone.utc).isoformat()

def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def digest(data):
    return hashlib.sha256(canonical(data)).hexdigest()

def seal(data):
    return dict(data, integrity=digest({k:v for k,v in data.items() if k != 'integrity'}))

def intact(data):
    return data.get('integrity') == seal(data)['integrity']

def fsync_dir(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

def atomic_write(path: Path, content: bytes, *, exclusive=False):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise PMPError(f'Refusing symlink target: {path}')
    fd, tmp = tempfile.mkstemp(prefix='.pmp-write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            # Hard-link publication guarantees no existing target can be overwritten.
            os.link(tmp, path)
            os.unlink(tmp)
        else:
            os.replace(tmp, path)
        fsync_dir(path.parent)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

def write_json(path, data, **kwargs):
    atomic_write(path, json.dumps(data, indent=2, ensure_ascii=True).encode()+b'\n', **kwargs)

def read_json(path):
    try:
        return json.loads(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise PMPError(f'Cannot read {path}: {exc}. Run pmp doctor.') from exc

@contextlib.contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise PMPError(f'Writer lock exists: {path}. Inspect with pmp doctor; no automatic takeover.', 3) from exc
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(canonical({'pid':os.getpid(),'host':socket.gethostname(),'created':now()}))
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        path.unlink()
        fsync_dir(path.parent)
