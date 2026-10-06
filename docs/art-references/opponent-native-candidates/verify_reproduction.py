#!/usr/bin/env python3
"""Reproduce candidate outputs in a clean temporary directory and compare bytes.

Run without -O so assertion checks remain enabled. This validates source assets,
not integration, compilation, animation quality, or actual emulator rendering.
"""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
INPUTS = (
    'convert_native.py',
    'validate_native.py',
    'source/opponents-reference-v2.png',
    'source/existing-shared.pal',
)
OUTPUTS = (
    sorted(str(path.relative_to(ROOT)) for path in (ROOT / 'assets').rglob('*') if path.is_file())
    + sorted(str(path.relative_to(ROOT)) for path in (ROOT / 'previews').glob('*.png'))
    + ['manifest.json', 'validation-report.json']
)
assert len(OUTPUTS) == 41, 'Expected exactly 41 generated candidate outputs'

with tempfile.TemporaryDirectory(prefix='opponent-art-') as temporary:
    destination = Path(temporary)
    for relative in INPUTS:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    for run in range(1, 3):
        for script in ('convert_native.py', 'validate_native.py'):
            subprocess.run([sys.executable, str(destination / script)], cwd=destination, check=True)
        for relative in OUTPUTS:
            expected = (ROOT / relative).read_bytes()
            actual = (destination / relative).read_bytes()
            assert actual == expected, f'Run {run} changed {relative}'
        print(f'Run {run}: all 41 generated outputs are byte-identical.')

palette = (ROOT / 'source/existing-shared.pal').read_bytes()
git_blob = hashlib.sha1(b'blob ' + str(len(palette)).encode() + b'\0' + palette).hexdigest()
assert git_blob == 'a53187e0f6ff720864149e69d6855dbce4db2c91'
print('Shared palette source matches the recorded repository Git blob.')
print('PASS: source reproducibility only; runtime remains NOT RUN.')
