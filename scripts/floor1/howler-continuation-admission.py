"""Offline dependency hash gates. Runtime authority is closed in this increment."""
from pathlib import Path
import hashlib,stat
def digest(path):
    path=Path(path);info=path.lstat();assert stat.S_ISREG(info.st_mode) and not path.is_symlink()
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()
def verify(pins,expected_paths):
    assert set(pins)==set(map(str,expected_paths)), 'complete dependency inventory'
    for path,pin in pins.items():assert digest(path)==pin,('dependency identity',path)
    return True
def runtime_action(*args,**kwargs):
    raise RuntimeError('CLOSED: offline-only review; no runtime admission, freeze, claim, Save or cold process')
