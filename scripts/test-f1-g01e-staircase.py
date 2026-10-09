#!/usr/bin/env python3
"""Ordinary resolved-staircase/interior-buffer checks; never starts a battle."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, importlib.util, json, os, re, shlex, shutil, struct, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
ROM_SHA = 'b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

p = argparse.ArgumentParser()
p.add_argument('--build', type=Path, required=True)
p.add_argument('--originals', type=Path, required=True)
p.add_argument('--case', choices=['stairs', 'quiet', 'workshop', 'sealed'])
args = p.parse_args()
assert not git('status', '--porcelain'), 'Commit runner before runtime'
head = git('rev-parse', 'HEAD')
build = args.build.resolve()
compiled = (build / 'tested-commit.txt').read_text().strip()
subprocess.run(['git', 'diff', '--quiet', compiled, head, '--', 'engine'], cwd=ROOT, check=True)
rom = build / 'source/engine/pokeemerald.gba'
assert sha(rom) == ROM_SHA
parent = ROOT / ('artifacts/floor1/sealed' if args.case == 'sealed' else 'artifacts/floor1/staircase')
parent.mkdir(parents=True, exist_ok=True)
out = Path(tempfile.mkdtemp(prefix='runtime-', dir=parent))
print('Evidence:', out, flush=True)
sym = out / 'game.sym'
with sym.open('w') as f:
    subprocess.run(['arm-none-eabi-nm', '--defined-only', str(build / 'source/engine/pokeemerald.elf')], stdout=f, check=True)
with sym.open('a') as f:
    subprocess.run(['python3', str(ROOT / 'scripts/battle-input-symbols.py'), str(build / 'source/engine')], stdout=f, check=True)
observer = module('observer', ROOT / 'scripts/floor1/live-save-observer.py')
native = module('native', ROOT / 'scripts/floor1/native-text-observer.py')
walking = module('walking', ROOT / 'scripts/floor1/walking-harness.py')
code = native.instrument(observer.instrument(walking.instrument(git('show', head + ':scripts/playtest.c') + '\n')))
code = code.replace('!number(values[0],15,&tx)', '!number(values[0],255,&tx)').replace('!number(values[1],11,&ty)', '!number(values[1],255,&ty)')
# Bounded equality verdicts only: no state/key dump and no writes to the game.
point = '        if (!strcmp(line,"quit\\n")) break;'
assert code.count(point) == 1
code = code.replace(point, point + r'''
        if (!strncmp(line,"unchanged ",10)) {
            static unsigned char savedFlags[300], savedDuo[200];
            static unsigned short savedBag[512];
            static unsigned savedSlots=0, initialized=0;
            unsigned sb=core->busRead32(core,saveptr), slots=0;
            unsigned short bag[512];
            if (!pockets || !save2ptr) {result=42;break;}
            unsigned key=core->busRead16(core,core->busRead32(core,save2ptr)+0xAC);
            for (unsigned pocket=0;pocket<5;pocket++) {
                unsigned data=core->busRead32(core,pockets+8*pocket);
                unsigned capacity=core->busRead8(core,pockets+8*pocket+4);
                if (!data || slots+capacity>256) {result=42;break;}
                for (unsigned i=0;i<capacity;i++,slots++) {
                    bag[2*slots]=core->busRead16(core,data+4*i);
                    bag[2*slots+1]=core->busRead16(core,data+4*i+2)^key;
                }
            }
            if (result) break;
            if (!strcmp(line,"unchanged start\n")) {
                for (unsigned i=0;i<300;i++) savedFlags[i]=core->busRead8(core,sb+0x1270+i);
                for (unsigned i=0;i<200;i++) savedDuo[i]=core->busRead8(core,party+i);
                memcpy(savedBag,bag,2*slots*sizeof(*bag));savedSlots=slots;initialized=1;
                continue;
            }
            if (strcmp(line,"unchanged check\n") || !initialized || slots!=savedSlots
                || memcmp(savedBag,bag,2*slots*sizeof(*bag))) {result=42;fprintf(stderr,"Inventory equality failed\n");break;}
            for (unsigned i=0;i<300;i++) if (savedFlags[i]!=core->busRead8(core,sb+0x1270+i)) {result=42;break;}
            for (unsigned i=0;i<200;i++) if (savedDuo[i]!=core->busRead8(core,party+i)) {result=42;break;}
            if (result) {fprintf(stderr,"Persistent flags or duo equality failed\n");break;}
            checks+=3;printf("PASS unchanged flags inventory duo\n");continue;
        }
''')
if args.case == 'sealed':
    # Latch a battle on every emulated frame, including text/menu/save frames.
    declaration = '    unsigned frames,keys,total=0,checks=0,lastPilotIncap=0;\n    int result=0;\n'
    assert code.count(declaration) == 1
    code = code.replace(declaration, declaration + '    unsigned sawBattle=0, guardedFrames=0;\n')
    assert code.count('core->runFrame(core);') >= 3
    code = code.replace('core->runFrame(core);', 'core->runFrame(core); guardedFrames++; if (core->busRead8(core,mainstate+0x439)&2) sawBattle=1;')
    code = code.replace(point, point + r'''
        if (!strcmp(line,"no-battle\n")) {
            if (sawBattle || (core->busRead8(core,mainstate+0x439)&2)) {result=43;fprintf(stderr,"Unexpected battle frame\n");break;}
            checks++;printf("PASS no-battle observed_frames=%u\n",guardedFrames);continue;
        }
''')
assert 'busWrite' not in code
(out / 'observer.c').write_text(code)
with (out / 'host-build.log').open('w') as f:
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', *shlex.split(os.environ.get('DCC_TEST_CFLAGS', '')), str(out / 'observer.c'), *shlex.split(os.environ.get('DCC_TEST_LDFLAGS', '')), '-lmgba', '-o', str(out / 'playtest')], stdout=f, stderr=subprocess.STDOUT, check=True)
spec = json.loads((ROOT / 'scripts/contracts/f1-g01d-relocation.json').read_text())
g = module('geometry', ROOT / 'scripts/floor1/relocation-graybox.py')
routes = module('routes', ROOT / 'scripts/floor1/live-route.py')
summary, originals = [], {}
boot = ['step 720 0 -', 'step 1 8 -', 'step 360 0 -', 'step 1 8 -', 'step 180 0 -', 'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 cold.ppm', 'ready']

def R(key, pos, facing=1):
    r = routes.Route(spec, g, key, pos, facing, 7)
    r.cursor = 0
    return r

def copy(name, original):
    f = args.originals.resolve() / (original + '.sav')
    originals[f] = sha(f)
    dest = out / (name + '.sav')
    shutil.copyfile(f, dest)
    return dest

def cold(name, save):
    dest = out / (name + '.sav')
    shutil.copyfile(save, dest)
    return dest, sha(dest)

def run(name, save, r):
    assert not any(line.startswith(('pilot ', 'engage ', 'snapshot', 'policy ')) for line in r.lines)
    d = out / name
    d.mkdir()
    (d / 'input.route').write_text('\n'.join(boot + ['unchanged start'] + r.lines + ['unchanged check', 'quit']) + '\n')
    with (d / 'input.route').open() as inp, (d / 'replay.log').open('w') as log, (d / 'errors.log').open('w') as err:
        result = subprocess.run([str(out / 'playtest'), str(rom), str(save), str(sym)], cwd=d, stdin=inp, stdout=log, stderr=err)
    for image in d.glob('*.ppm'):
        frame = Image.open(image)
        assert frame.size == (240, 160)
        frame.save(image.with_suffix('.png'))
    assert result.returncode == 0, (name, 'Retained failed evidence', d, result.returncode)
    log = (d / 'replay.log').read_text()
    assert not (d / 'errors.log').stat().st_size
    checks = int(re.search(r'result=0 assertions=(\d+)\n$', log)[1])
    summary.append(dict(route=name, assertions=checks, map_words=sum(line.startswith('tile ') for line in r.lines), emulator_errors=0, native_messages=sum(map(int, re.findall(r'native-pages messages=(\d+)', log))), native_pages=sum(map(int, re.findall(r'native-pages messages=\d+ pages=(\d+)', log))), method='Original ordinary save/controller-authored Save only; controller inputs and RAM reads'))
    print('PASS', name, checks, flush=True)

def page(r, prefix, *labels):
    r.lines.append('pages ' + prefix + ' ' + ','.join(labels))

def close(r):
    r.lines += ['dialog 3600', 'ready']
    r.step(40)
    r.expect()

def face(r, button):
    if r.face != button:
        r.step(1, button)
        r.face = button
        r.step(40)

def talk(r, button, prefix, *labels, finish=True):
    face(r, button)
    r.step(1, 1)
    r.step(400)
    page(r, prefix, *labels)
    if finish:
        close(r)

def save(r):
    if r.cursor:
        r.step(1, 8)
        r.step(120)
        for i in range(r.cursor):
            r.step(1, 64)
            r.step(20)
        r.step(1, 2)
        r.step(120)
        r.cursor = 0
    r.save()
    r.lines = [line for line in r.lines if line != 'snapshot']
    r.cursor = 2
    r.lines.append('unchanged check')

def saved_facing(r):
    return {128: 1, 64: 2, 32: 3, 16: 4}[r.face]

def words(r, cleared=False):
    name = spec['production_identity_proposal']['maps'][r.key]['name']
    raw = (build / 'source/engine/data/layouts' / name / 'map.bin').read_bytes()
    data = list(struct.unpack('<' + 'H' * (len(raw) // 2), raw))
    w = spec['maps'][r.key]['width']
    if r.key == 'boss':
        data[11 * w + 12] = 0x362A if cleared else 0x3618
    r.lines += [f'tile {i % w} {i // w} {value}' for i, value in enumerate(data)]

def completed(r):
    r.lines += ['flag 47 1', 'flag 48 1', 'flag 46 1', 'flag 2138 0', 'flag 2139 1', 'flag 43 0', 'flag 49 0', 'item 13 1', 'item 22 1', 'item 378 0', 'item 379 0', 'item 380 0', 'growth 11 940 0 10 1250 0', 'unchanged check']

def pending(r):
    r.lines += ['flag 2135 1', 'flag 2136 0', 'flag 2137 0', 'flag 47 0', 'flag 48 0', 'flag 43 0', 'flag 49 0', 'item 378 2', 'item 380 0', 'item 22 0', 'unchanged check']

def journal(r, prefix):
    r.step(1, 8)
    r.step(120)
    for i in range((4 - r.cursor) % 6):
        r.step(1, 128)
        r.step(20)
    r.cursor = 4
    r.step(1, 1)
    r.step(400)
    page(r, prefix, 'DCC_Live_Journal_Text_Done', 'DCC_Live_Journal_Text_Rules', 'DCC_Live_Journal_Text_Optional')
    close(r)

def stairs(r, prefix, no=False):
    r.anchor('stairs')
    talk(r, 128, prefix, 'DCC_F1D1Warden_StairsText', finish=False)
    r.step(40, 0, prefix + '-choice.ppm')
    if no:
        r.step(1, 128)
        r.step(20)
    r.step(1, 1)
    r.step(400)
    if no:
        page(r, prefix + '-cancelled', 'DCC_Boss_Text_StairsCancel')
        close(r)
    else:
        r.lines += ['ready']
        r.key, r.pos = 'checkpoint', (4, 4)
        r.expect()
        r.step(40, 0, prefix + '-arrived.ppm')
    completed(r)

if not args.case or args.case == 'stairs':
    s = copy('resolved', 'continuous')
    r = R('checkpoint', (4, 4))
    r.expect(); completed(r); words(r)
    journal(r, 'opening-only')
    r.anchor('review'); talk(r, 128, 'review', 'DCC_F1D1Checkpoint_ReviewText')
    r.anchor('donut_staging'); talk(r, 128, 'donut', 'DCC_F1D1Checkpoint_DonutText')
    r.anchor('arrival'); words(r, True)
    r.anchor('warden'); talk(r, 128, 'warden-resolved', 'DCC_Live_Boss_Text_Won')
    stairs(r, 'refusal', True); words(r, True); save(r)
    facing = saved_facing(r)
    run('ordinary-resolved-return-refusal-save', s, r)

    c, identity = cold('arena-cold', s)
    r = R('boss', (12, 10), facing)
    r.expect(); completed(r); words(r, True)
    stairs(r, 'cold-refusal', True); words(r, True)
    stairs(r, 'repeat-transition'); words(r)
    r.anchor('review'); talk(r, 128, 'reentered-review', 'DCC_F1D1Checkpoint_ReviewText')
    save(r)
    run('ordinary-resolved-arena-cold-repeat-transition-save', c, r)
    # This owned cold copy was deliberately changed by a real manual Save.

    d, identity = cold('checkpoint-cold', c)
    r = R('checkpoint', (8, 6), saved_facing(r))
    r.expect(); completed(r); words(r)
    talk(r, 128, 'cold-review', 'DCC_F1D1Checkpoint_ReviewText')
    journal(r, 'cold-opening-only')
    r.anchor('arrival'); words(r, True)
    r.anchor('warden'); talk(r, 128, 'cold-warden-resolved', 'DCC_Live_Boss_Text_Won')
    stairs(r, 'cold-return-transition'); words(r)
    r.anchor('donut_staging'); talk(r, 128, 'cold-donut', 'DCC_F1D1Checkpoint_DonutText')
    completed(r)
    run('ordinary-resolved-checkpoint-cold-return-reentry', d, r)
    assert sha(d) == identity

if not args.case or args.case == 'quiet':
    s = copy('quiet', 'both-pending')
    r = R('field', (37, 31))
    pending(r); r.anchor('quiet_door'); words(r)
    r.anchor('trial'); talk(r, 128, 'trial-resolved', 'DCC_Live_Vestibule_Text_Won')
    r.anchor('donut_staging'); talk(r, 128, 'quiet-donut', 'DCC_Donut_Text')
    r.anchor('arrival'); r.anchor('quiet_door'); words(r)
    r.anchor('guide'); save(r); pending(r)
    run('ordinary-quiet-buffer-reentry-save', s, r)
    c, identity = cold('quiet-cold', s)
    r = R('quiet', (4, 5), saved_facing(r))
    r.expect(); pending(r); words(r)
    r.anchor('trial'); talk(r, 128, 'cold-trial-resolved', 'DCC_Live_Vestibule_Text_Won')
    run('ordinary-quiet-cold-buffer', c, r)
    assert sha(c) == identity

if not args.case or args.case == 'workshop':
    s = copy('workshop', 'both-pending')
    r = R('field', (37, 31))
    pending(r); r.anchor('workshop_door'); words(r)
    r.anchor('lev'); talk(r, 128, 'lev', 'DCC_Live_Service_Text_Lev')
    r.anchor('cache'); talk(r, 128, 'cache-no-charge', 'DCC_Service_Text_NeedsCharge')
    r.anchor('arrival'); r.anchor('workshop_door'); words(r)
    r.anchor('cache'); talk(r, 128, 'cache-reentered', 'DCC_Service_Text_NeedsCharge')
    pending(r); save(r)
    run('ordinary-workshop-buffer-reentry-save', s, r)
    c, identity = cold('workshop-cold', s)
    r = R('workshop', (12, 9), saved_facing(r))
    r.expect(); pending(r); words(r)
    talk(r, 128, 'cold-cache-no-charge', 'DCC_Service_Text_NeedsCharge')
    run('ordinary-workshop-cold-buffer', c, r)
    assert sha(c) == identity

if args.case == 'sealed':
    def boss_pending(r):
        r.lines += ['no-battle', 'flag 2135 1', 'flag 2136 1', 'flag 2137 1',
                    'flag 2138 0', 'flag 2139 0', 'flag 47 0', 'flag 48 0',
                    'flag 40 0', 'flag 43 0', 'flag 45 0', 'flag 46 0', 'flag 49 0',
                    'item 378 2', 'item 380 0', 'item 22 0', 'unchanged check']

    def field_words(r):
        assert r.key == 'field'
        name = spec['production_identity_proposal']['maps']['field']['name']
        raw = (build / 'source/engine/data/layouts' / name / 'map.bin').read_bytes()
        data = list(struct.unpack('<' + 'H' * (len(raw) // 2), raw))
        text = (build / 'source/engine/src/data/dcc_opening.h').read_text()
        # All three persistent Field presentation flags are asserted unset.
        for x, y, off in re.findall(r'MAP_DCC_F1D1FIELD, (\d+), (\d+), FLAG_DCC_\w+, 0x([0-9A-F]+), 0x[0-9A-F]+', text):
            data[int(y) * 64 + int(x)] = int(off, 16)
        r.lines += [f'tile {i % 64} {i // 64} {value}' for i, value in enumerate(data)]

    def sealed(r, prefix):
        r.anchor('stairs')
        talk(r, 128, prefix, 'DCC_Boss_Text_StairsLocked')
        r.lines += ['tile 12 11 13848', 'no-battle']
        # Ordinary movement into the sealed stair must stay at12,10.
        r.step(20, 128)
        r.step(40, 0, prefix + '-blocked.ppm')
        r.expect()
        r.lines += ['ready', 'unchanged check']
        boss_pending(r)

    def boss_journal(r, prefix):
        r.step(1, 8); r.step(120)
        for i in range((4 - r.cursor) % 6):
            r.step(1, 128); r.step(20)
        r.cursor = 4
        r.step(1, 1); r.step(400)
        page(r, prefix, 'DCC_Live_Journal_Text_Boss', 'DCC_Live_Journal_Text_Rules', 'DCC_Live_Journal_Text_Optional')
        close(r)
        boss_pending(r)

    s = copy('sealed', 'boss-pending')
    r = R('field', (51, 27))
    r.expect(); boss_pending(r); field_words(r)
    r.anchor('warden_door'); words(r)
    sealed(r, 'first-refusal'); sealed(r, 'repeat-refusal'); words(r)
    r.anchor('arrival'); field_words(r); boss_pending(r)
    r.anchor('warden_door'); words(r)
    sealed(r, 'reentered-refusal'); boss_journal(r, 'boss-pending-journal')
    save(r); words(r); boss_pending(r)
    facing = saved_facing(r)
    run('ordinary-sealed-refusal-return-reentry-save', s, r)

    c, identity = cold('sealed-cold', s)
    r = R('boss', (12, 10), facing)
    r.expect(); boss_pending(r); words(r)
    sealed(r, 'cold-refusal'); sealed(r, 'cold-repeat-refusal'); words(r)
    r.anchor('arrival'); field_words(r); boss_pending(r)
    r.anchor('warden_door'); words(r)
    sealed(r, 'cold-reentered-refusal'); boss_journal(r, 'cold-boss-journal')
    words(r); boss_pending(r)
    run('ordinary-sealed-cold-return-reentry', c, r)
    assert sha(c) == identity
    # Publish frame-count verdicts only; no private state/key/saves.
    for verdict in summary:
        log = (out / verdict['route'] / 'replay.log').read_text()
        frames = list(map(int, re.findall(r'PASS no-battle observed_frames=(\d+)', log)))
        assert frames and frames == sorted(frames)
        verdict['no_battle_guarded_frames'] = frames[-1]
        verdict['no_battle_assertions'] = len(frames)

assert all(sha(f) == identity for f, identity in originals.items())
(out / 'summary.json').write_text(json.dumps(dict(compiled_source=compiled, runner_source=head, rom_sha256=sha(rom), sessions=summary, originals_unchanged=True, read_only_cold_inputs_unchanged=True, method='Already-completed/pending ordinary saves and actual manual Save copies. Normal controller input, read-only observer; no synthetic save input, snapshot dump, RAM/ROM write, new battle or first-clear claim. Full flags/live duo/decrypted inventory equality verdicts only; private values/logs/saves remain local.'), indent=2) + '\n')
assert not git('status', '--porcelain') and git('rev-parse', 'HEAD') == head
print('PASS', len(summary), 'ordinary sessions', sum(x['assertions'] for x in summary), 'assertions', flush=True)
