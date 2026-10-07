#!/usr/bin/env python3
"""Ordinary pickup/repeat/traversal/re-entry/Save/cold presentation regression."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, importlib.util, json, os, re, shlex, shutil, struct, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

parser = argparse.ArgumentParser()
parser.add_argument('--build', type=Path, required=True)
parser.add_argument('--original', type=Path, required=True)
parser.add_argument('--baseline', action='store_true')
args = parser.parse_args()
assert not git('status', '--porcelain'), 'Commit before runtime checks'
head = git('rev-parse', 'HEAD')
build = args.build.resolve()
compiled = (build / 'tested-commit.txt').read_text().strip()
subprocess.run(['git', 'diff', '--quiet', compiled, head, '--', 'engine'], cwd=ROOT, check=True)
rom = build / 'source/engine/pokeemerald.gba'
original = args.original.resolve()
original_hash = digest(original)
parent = ROOT / 'artifacts/floor1/feedback'
parent.mkdir(parents=True, exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='baseline-' if args.baseline else 'candidate-', dir=parent))
print('Evidence:', out, flush=True)
sym = out / 'game.sym'
with sym.open('w') as log:
    subprocess.run(['arm-none-eabi-nm', '--defined-only', str(build / 'source/engine/pokeemerald.elf')], stdout=log, check=True)
with sym.open('a') as log:
    subprocess.run(['python3', str(ROOT / 'scripts/battle-input-symbols.py'), str(build / 'source/engine')], stdout=log, check=True)
observer = module('observer', ROOT / 'scripts/floor1/live-save-observer.py')
walking = module('walking', ROOT / 'scripts/floor1/walking-harness.py')
code = observer.instrument(walking.instrument(git('show', head + ':scripts/playtest.c') + '\n'))
code = code.replace('!number(values[0],15,&tx)', '!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)', '!number(values[1],255,&ty)')
assert 'busWrite' not in code
(out / 'observer.c').write_text(code)
with (out / 'host-build.log').open('w') as log:
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', *shlex.split(os.environ.get('DCC_TEST_CFLAGS', '')), str(out / 'observer.c'), *shlex.split(os.environ.get('DCC_TEST_LDFLAGS', '')), '-lmgba', '-o', str(out / 'playtest')], stdout=log, stderr=subprocess.STDOUT, check=True)
geometry = module('geometry', ROOT / 'scripts/floor1/relocation-graybox.py')
routes = module('routes', ROOT / 'scripts/floor1/live-route.py')
spec = json.loads((ROOT / 'scripts/contracts/f1-g01d-relocation.json').read_text())
off, on = (0x323B, 0x323B) if args.baseline else (0x3248, 0x3243)
attributes = (build / 'source/engine/data/tilesets/secondary/dcc/metatile_attributes.bin').read_bytes()
attribute = lambda word: struct.unpack_from('<H', attributes, ((word & 0x3FF) - 512) * 2)[0]
assert all(word & 0xFC00 == 0x3000 for word in (off, on))
assert attribute(off) == attribute(on) == attribute(0x323B)
boot = ['step 720 0 -', 'step 1 8 -', 'step 360 0 -', 'step 1 8 -', 'step 180 0 -', 'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 cold.ppm', 'ready']
summary = []
def run(name, save, lines):
    directory = out / name
    directory.mkdir()
    (directory / 'input.route').write_text('\n'.join(lines + ['quit']) + '\n')
    with (directory / 'input.route').open() as inputs, (directory / 'replay.log').open('w') as log, (directory / 'errors.log').open('w') as errors:
        subprocess.run([str(out / 'playtest'), str(rom), str(save), str(sym)], cwd=directory, stdin=inputs, stdout=log, stderr=errors, check=True)
    text = (directory / 'replay.log').read_text()
    checks = int(re.search(r'result=0 assertions=(\d+)\n$', text)[1])
    assert not (directory / 'errors.log').stat().st_size
    for image in directory.glob('*.ppm'):
        frame = Image.open(image)
        assert frame.size == (240, 160)
        frame.save(image.with_suffix('.png'))
    summary.append({'route': name, 'assertions': checks, 'emulator_errors': 0})
    print(name, 'PASS', checks, flush=True)

def panel_talk(r, label):
    # A direction press on walkable BG targets starts a step if already facing
    # that way. Turn only when needed; otherwise interact in place with A.
    if r.face != 64:
        r.step(1, 64); r.face = 64; r.step(40)
    r.step(1, 1); r.step(400, 0, label + '.ppm')
    r.lines += ['dialog 3600', 'ready']
    r.step(40); r.expect()

save = out / 'ordinary-copy.sav'
shutil.copyfile(original, save)
r = routes.Route(spec, geometry, 'field', (37, 31), 1, 7)
r.lines += ['flag 45 0', 'item 18 0', f'tile 55 42 {off}']
# The ordinary route crosses the panel before interacting, proving it is floor.
r.follow((55, 41)); r.follow((55, 42)); r.follow((55, 43))
r.step(40, 0, 'available.ppm')
panel_talk(r, 'pickup-dialog')
r.lines += ['flag 45 1', 'item 18 1', f'tile 55 42 {on}']
r.step(40, 0, 'resolved.ppm')
panel_talk(r, 'repeat-dialog')
r.lines += ['item 18 1', f'tile 55 42 {on}']
r.follow((55, 42)); r.follow((55, 41)); r.follow((55, 42)); r.follow((55, 43))
r.anchor('quiet_door'); r.anchor('donut_staging'); r.anchor('arrival')
r.follow((55, 41)); r.follow((55, 42)); r.follow((55, 43))
r.lines += ['flag 45 1', 'item 18 1', f'tile 55 42 {on}']
r.step(40, 0, 'reentered.ppm')
r.save()
r.lines = [line for line in r.lines if line != 'snapshot']
run('ordinary-pickup', save, boot + r.lines)
assert digest(original) == original_hash and digest(save) != original_hash
cold = out / 'cold-copy.sav'
shutil.copyfile(save, cold)
cold_hash = digest(cold)
r = routes.Route(spec, geometry, 'field', (55, 43), 1, 7)
r.lines += ['flag 45 1', 'item 18 1', f'tile 55 42 {on}']
r.step(40, 0, 'cold-resolved.ppm')
panel_talk(r, 'cold-repeat-dialog')
r.lines += ['item 18 1', f'tile 55 42 {on}']
r.follow((55, 42)); r.follow((55, 41)); r.follow((55, 42)); r.follow((55, 43))
run('cold-repeat-and-traversal', cold, boot + r.lines)
assert digest(cold) == cold_hash and digest(original) == original_hash
(out / 'summary.json').write_text(json.dumps({'compiled_source': compiled, 'runner_source': head, 'rom_sha256': digest(rom), 'baseline': args.baseline, 'sessions': summary, 'original_unchanged': True, 'cold_file_unchanged': True, 'collision_elevation_and_behavior_unchanged': True, 'method': 'Actual ordinary controller interactions, traversal, re-entry, manual Save and cold load. No injected flags, resources or ROM fixtures. Complete raw logs/saves remain local.'}, indent=2) + '\n')
assert not git('status', '--porcelain') and git('rev-parse', 'HEAD') == head
print('PASS', len(summary), 'sessions', sum(x['assertions'] for x in summary), 'assertions')
