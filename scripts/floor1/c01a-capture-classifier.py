"""Exact native capture inventory, separate from declared retained derivatives."""
from pathlib import Path
import hashlib
FRAMES=7051
NAMED=[n+'.ppm' for n in ['boot','battle-start','carl-strike','carl-brace','strike-target','bag','party','summary','carl-return','donut-spark','donut-weaken','donut-return','spark-one','spark-empty','spark-rejected','spark-empty-return','weaken-after-empty']]+[f'cue-{i:03d}.ppm' for i in range(10)]
def classify_names(names,frames=FRAMES,declared_derivatives=()):
    assert frames==FRAMES,'Exact reviewed7051-frame sequence required'
    names=set(names);expected={f'battle-{i:05d}.ppm' for i in range(frames)}
    prefix={n for n in names if n.startswith('battle-')}
    allowed=expected|{'battle-start.ppm'}|(set(declared_derivatives)&names)
    assert prefix==allowed,('Unexpected/missing/malformed/out-of-range battle-prefixed name',sorted(prefix^allowed))
    assert set(NAMED)<=names,('Missing named capture',sorted(set(NAMED)-names))
    return [f'battle-{i:05d}.ppm' for i in range(frames)]
def classify(directory,frames=FRAMES,declared_derivatives=None):
    directory=Path(directory);declared_derivatives=declared_derivatives or {}
    names={p.name for p in directory.iterdir()};numbered=classify_names(names,frames,declared_derivatives)
    for n in numbered+NAMED:
        p=directory/n;assert p.is_file() and not p.is_symlink(),n
    for n,h in declared_derivatives.items():
        p=directory/n;assert p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==h,n
    return [directory/n for n in numbered]
