#!/usr/bin/env python3
"""Recovery only: new ordinary inputs, unchanged published battle policy, stop on failure."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, importlib.util, json, re, shutil, subprocess

ROOT = Path(__file__).resolve().parents[1]
GAME = 'c643f01c11ec68119b0347b107ee20115131debc'
ROM = 'b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'
BASE = '72e08ed17afc69e28ef545bbbff383a434e90df5'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('--build', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--stage', choices=['prepare', 'fresh', 'seed', 'patrol', 'cold'], required=True)
parser.add_argument('--resume-from', type=Path, help='Prepare a diagnosed field-menu repair using the unchanged successful fresh Save')
args = parser.parse_args()
assert not git('status', '--porcelain'), 'Commit recovery source first'
head = git('rev-parse', 'HEAD')
build = args.build.resolve()
out = args.output.resolve()
assert (build / 'tested-commit.txt').read_text().strip() == GAME
subprocess.run(['git', 'diff', '--quiet', GAME, head, '--', 'engine'], cwd=ROOT, check=True)
engine = build / 'source/engine'
rom = engine / 'pokeemerald.gba'
assert sha(rom) == ROM
out.mkdir(parents=True, exist_ok=True)
if args.stage == 'prepare':
    assert not (out / 'identity.json').exists(), 'Preserve prepared host and every execution'
    host = module('recovery_host', ROOT / 'scripts/floor1/recovery-host.py')
    code, base_observer = host.generate(git)
    (out / 'observer.c').write_text(code)
    with (out / 'host-build.log').open('w') as log:
        subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', str(out / 'observer.c'), '-lmgba', '-o', str(out / 'playtest')], stdout=log, stderr=subprocess.STDOUT, check=True)
    with (out / 'game.sym').open('w') as symbols:
        subprocess.run(['arm-none-eabi-nm', '--defined-only', str(engine / 'pokeemerald.elf')], stdout=symbols, check=True)
    with (out / 'game.sym').open('a') as symbols:
        subprocess.run(['python3', str(ROOT / 'scripts/battle-input-symbols.py'), str(engine)], stdout=symbols, check=True)
    identity = dict(runner=head, game=GAME, rom=ROM, reconstructed_base_observer=base_observer,
                    host_sha256=sha(out / 'observer.c'), method='Fresh ordinary gameplay recovery; no original input or acceptance transfer')
    (out / 'identity.json').write_text(json.dumps(identity, indent=2) + '\n')
    if args.resume_from:
        prior = args.resume_from.resolve()
        failure = json.loads((prior / 'STOP.json').read_text())
        rows = json.loads((prior / 'summary.json').read_text())
        assert failure['stage'] == 'seed' and failure['exit'] == 46
        assert 'wait-task field-context 3600' in (prior / 'seed/errors.log').read_text()
        assert [x['stage'] for x in rows] == ['fresh', 'seed'] and rows[0]['exit'] == 0 and rows[0]['errors_bytes'] == 0
        assert sha(prior / 'fresh.sav') == sha(prior / 'seed.sav') == rows[0]['output_save_sha256']
        assert json.loads((prior / 'identity.json').read_text())['rom'] == ROM
        shutil.copyfile(prior / 'fresh.sav', out / 'fresh.sav')
        (out / 'summary.json').write_text(json.dumps(rows[:1], indent=2) + '\n')
        (out / 'diagnosed-resume.json').write_text(json.dumps(dict(source=head, prior=str(prior),
            failed_claim_sha256=sha(prior / 'seed/execution-claim.json'),
            preserved_failure_sha256=sha(prior / 'STOP.json'),
            reason='SetupBagMenu creates input task at state14 before fade at state20 and callback switch; require CB2_BagMenuRun. No battle replay.'), indent=2) + '\n')
    print('PASS prepared recovery host; no emulator or save execution')
    raise SystemExit(0)

identity = json.loads((out / 'identity.json').read_text())
assert identity['host_sha256'] == sha(out / 'observer.c')
subprocess.run(['git', 'diff', '--quiet', identity['runner'], head, '--', 'engine',
    'scripts/playtest.c', 'scripts/floor1/recovery-host.py', 'scripts/floor1/live-save-observer.py',
    'scripts/floor1/walking-harness.py', 'scripts/floor1/potion-menu-readiness.h'], cwd=ROOT, check=True)
assert not (out / 'STOP.json').exists(), 'A prior failure requires diagnosis and parent review before another execution'
summary_path = out / 'summary.json'
summary = json.loads(summary_path.read_text()) if summary_path.exists() else []
completed = [x['stage'] for x in summary]
assert completed == ['fresh', 'seed', 'patrol', 'cold'][:['fresh', 'seed', 'patrol', 'cold'].index(args.stage)]
d = out / args.stage
d.mkdir()  # Existing output never permits a repeated execution.
boot = ['step 720 0 -', 'step 1 8 -', 'step 360 0 -', 'step 1 8 -', 'step 180 0 -',
        'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 cold.ppm', 'ready']
pending = ['flag 46 0', 'flag 47 0', 'flag 48 0', 'flag 49 0', 'flag 2138 0', 'flag 2139 0']
target = ['expect 35 0 37 31 7', 'levels 11 10', 'growth 11 748 0 10 1058 0',
          'duo healthy', 'uses 8 40 2 40', 'item 13 0', 'item 378 2', 'flag 2135 1',
          'flag 2136 1', 'flag 2137 1'] + pending
save = out / (args.stage + '.sav')
if args.stage == 'fresh':
    lines = git('show', BASE + ':docs/evidence/floor1/g01e/verified-partial-live/fresh-trial/input.route').splitlines()
    lines = [x for x in lines if x not in ['snapshot', 'quit']]
    lines += ['levels 9 9', 'growth 9 495 0 9 805 0', 'item 13 2', 'flag 2136 0', 'flag 2137 0'] + pending
elif args.stage == 'seed':
    shutil.copyfile(out / 'fresh.sav', save)
    geometry = module('recovery_geometry', ROOT / 'scripts/floor1/relocation-graybox.py')
    routes = module('recovery_routes', ROOT / 'scripts/floor1/live-route.py')
    spec = json.loads((ROOT / 'scripts/contracts/f1-g01d-relocation.json').read_text())
    r = routes.Route(spec, geometry, 'quiet', (10, 7), 1, 7)
    r.anchor('rack'); r.talk(128, 'scrap-box')
    r.lines += ['item 378 2', 'item 13 2', 'flag 39 1']
    # Published setup consumes one of two owned Potions on injured Donut.
    r.lines += ['step 1 8 -', 'step 120 0 -', 'step 1 128 -', 'step 20 0 -',
                'step 1 1 -', 'wait-task bag 3600', 'step 1 1 -', 'step 12 0 -',
                'wait-task field-context 3600', 'step 1 1 -', 'step 12 0 -',
                'wait-task party 3600', 'step 1 128 -', 'step 40 0 -',
                'step 1 1 -', 'wait-task healed 3600', 'step 40 0 field-potion.ppm',
                'item 13 1', 'uses 3 40 0 37', 'return-field', 'ready']
    r.anchor('guide'); r.talk(128, 'guide-rest')
    r.lines += ['duo healthy', 'uses 8 40 2 40', 'growth 9 495 0 9 805 0']
    r.anchor('arrival'); r.anchor('guard')
    # Inventory left the Start cursor at 1; restore the published Save route's 0.
    r.lines += ['step 1 8 -', 'step 120 0 -', 'step 1 64 -', 'step 20 0 -', 'step 1 2 -', 'step 120 0 -']
    r.save()
    lines = boot + [x for x in r.lines if x != 'snapshot']
    lines += ['expect 35 0 37 31 7', 'duo healthy', 'uses 8 40 2 40', 'levels 9 9',
              'item 13 1', 'item 378 2', 'flag 2135 1', 'flag 2136 0', 'flag 2137 0'] + pending
elif args.stage == 'patrol':
    shutil.copyfile(out / 'seed.sav', save)
    lines = git('show', BASE + ':docs/evidence/floor1/g01e/attempts/patrol-single-weaken/input.route').splitlines()
    lines = [x for x in lines if x not in ['snapshot', 'quit']]
    assert lines.count('pilot offensive 36000') == 1
    lines[lines.index('pilot offensive 36000')] = 'pilot potion-once 36000'
    lines[9:9] = ['item 13 1', 'item 378 2', 'growth 9 495 0 9 805 0'] + pending
    i = lines.index('flag 2136 1')
    lines[i+1:i+1] = ['item 13 0', 'xp remember']
    i = lines.index('step 1 8 -', i)
    lines[i:i] = ['xp same', 'no-battle start', 'step 1 1 -', 'step 400 0 guard-resolved.ppm',
                  'dialog 3600', 'ready', 'step 40 0 -'] + target + ['xp same', 'no-battle end']
    lines += target + ['xp same']
else:
    shutil.copyfile(out / 'patrol.sav', save)
    lines = boot + target + ['xp remember', 'no-battle start', 'step 1 1 -',
        'step 400 0 cold-guard-resolved.ppm', 'dialog 3600', 'ready', 'step 40 0 -'] + target + ['xp same', 'no-battle end']

route = d / 'input.route'
route.write_text('\n'.join(lines + ['quit']) + '\n')
before = sha(save) if save.exists() else None
with (d / 'execution-claim.json').open('x') as claim:
    json.dump(dict(runner=head, stage=args.stage, route_sha256=sha(route), input_save_sha256=before), claim, indent=2)
with route.open() as inp, (d / 'replay.log').open('w') as log, (d / 'errors.log').open('w') as err:
    result = subprocess.run([str(out / 'playtest'), str(rom), str(save), str(out / 'game.sym')], cwd=d, stdin=inp, stdout=log, stderr=err)
for image in d.glob('*.ppm'):
    frame = Image.open(image)
    assert frame.size == (240, 160)
    frame.save(image.with_suffix('.png'))
log = (d / 'replay.log').read_text()
verdict = dict(stage=args.stage, runner=head, host_runner=identity['runner'], exit=result.returncode, errors_bytes=(d / 'errors.log').stat().st_size,
               assertions=int(re.search(r'assertions=(\d+)\n$', log)[1]), input_save_sha256=before,
               output_save_sha256=sha(save), route_sha256=sha(route), reconstructed_input=True)
summary.append(verdict)
summary_path.write_text(json.dumps(summary, indent=2) + '\n')
if result.returncode or verdict['errors_bytes']:
    (out / 'STOP.json').write_text(json.dumps(verdict, indent=2) + '\n')
    raise SystemExit('STOP: failure preserved; diagnosis required before another execution')
assert sha(rom) == ROM
if args.stage == 'cold':
    assert before == sha(save) == sha(out / 'patrol.sav'), 'Cold Continue must not write the save'
print('PASS recovery', args.stage, verdict['assertions'], 'assertions; new save', sha(save), flush=True)
