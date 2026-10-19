"""Conservative path and publication checks; not a complete secret scanner."""
import re
from pathlib import Path
from pmp.core.storage import PMPError

PATTERNS = [rb'-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----', rb'gh[pousr]_[A-Za-z0-9]{20,}',
            rb'github_pat_[A-Za-z0-9_]{20,}',rb'AKIA[0-9A-Z]{16}',rb'sk-[A-Za-z0-9_-]{20,}',
            rb'(?i)(?:password|api[_-]?key|token|secret)\s*[:=]\s*["\']?[^\s"\']{8,}']

def scan(content):
    return any(re.search(p, content) for p in PATTERNS)

def sensitive_name(name):
    parts = Path(name).parts
    return any(p in {'.env','.aws','.ssh','.gnupg'} or p.endswith(('.pem','.key')) or p.startswith('.env.') for p in parts)

def relative_path(root, name):
    if not isinstance(name,str) or not name or '\\' in name or ':' in name:
        raise PMPError(f'Unsafe portable relative path: {name!r}')
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or p == Path('.'):
        raise PMPError(f'Path must stay inside project: {name!r}')
    target = root / p
    if '.git' in p.parts or any(x.is_symlink() for x in [target, *target.parents] if x != root.parent):
        raise PMPError(f'Symlink or Git metadata path refused: {name}')
    if not target.resolve().is_relative_to(root.resolve()):
        raise PMPError(f'Path escapes project: {name}')
    return target
