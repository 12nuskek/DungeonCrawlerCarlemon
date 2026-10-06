"""Negative tests for baseline validation and source-cache integrity.

Usage: python3 scripts/test-foundation.py HARNESS ROM
Runs a real core, not a mock. Each route gets an empty temporary output directory.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parent.parent
harness, rom = map(lambda p: str(Path(p).resolve()), sys.argv[1:])
route = (repo / 'docs/evidence/f01/route.txt').read_text()
cases = {
    'valid': (route, 0),
    'empty': ('', 12),
    'malformed': ('garbage\n', 10),
    'trailing-token': ('120 0 boot.ppm extra\n', 10),
    'truncated': ('120 0 boot.ppm\n600 0', 10),
    'missing-checkpoint': (route.replace('menu.ppm', '-'), 12),
    'wrong-input': (route.replace('1 1 -', '1 0 -'), 11),
    'zero-frames': ('0 0 boot.ppm\n', 6),
}
for name, (input_text, expected) in cases.items():
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run([harness, rom], input=input_text, text=True, cwd=tmp,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        assert result.returncode == expected, (name, result.returncode, expected)
        if expected == 0:
            assert result.stdout.count(' PASS rgb-fnv1a64=') == 3
    print(f'{name}: PASS (exit {expected})')

for dirty_kind in ('tracked', 'untracked'):
    with tempfile.TemporaryDirectory() as tmp:
        cache = Path(tmp)
        compiler = cache / 'agbcc'
        compiler.mkdir()
        subprocess.run(['git', 'init', '-q', str(compiler)], check=True)
        source = compiler / 'compiler.c'
        source.write_text('original\n')
        subprocess.run(['git', '-C', str(compiler), 'add', 'compiler.c'], check=True)
        subprocess.run(['git', '-C', str(compiler), '-c', 'user.name=Test', '-c',
                        'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
        changed = source if dirty_kind == 'tracked' else compiler / 'new-source.c'
        changed.write_text('preserve this work\n')
        env = dict(os.environ, DCC_CACHE=str(cache))
        result = subprocess.run(['bash', str(repo / 'scripts/setup-foundation.sh')], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert result.returncode != 0 and 'Refusing dirty source cache' in result.stderr
        assert changed.read_text() == 'preserve this work\n'
        assert not (cache / 'pokeemerald').exists(), 'must reject before network/import work'
    print(f'dirty-cache-{dirty_kind}: PASS (preserved and rejected before fetch)')
