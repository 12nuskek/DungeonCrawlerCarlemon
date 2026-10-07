#!/usr/bin/env python3
"""Cold read-only state audit on copied ordinary production saves. No migration."""
from pathlib import Path
from PIL import Image
import hashlib, json, os, re, shlex, shutil, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[1]
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
assert not git('status', '--porcelain'), 'Commit first'
HEAD = git('rev-parse', 'HEAD')
BASE = 'ef5c012aba10b61cbcdbbc3313d7e25c5f448473'
subprocess.run(['git', 'diff', '--quiet', BASE, HEAD, '--', 'engine', 'scripts/playtest.c'], cwd=ROOT, check=True)
production = Path(os.environ['DCC_A01_BASE_RUN']).resolve()
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(production / 'production.gba') == '5c4f865a95c0b9e4c65f13d86c8ba44c9082599432b387f6fc350c0bd99b7230'
out = Path(tempfile.mkdtemp(prefix='state-', dir=ROOT / 'artifacts/floor1/g01c'))
print('Evidence:', out, flush=True)
code = git('show', HEAD + ':scripts/playtest.c') + '\n'
point = '        if (!strcmp(line,"quit\\n")) break;'
assert code.count(point) == 1
code = code.replace(point, point + r'''
        if (!strcmp(line,"audit\n")) {
            unsigned sb=core->busRead32(core,saveptr), group=core->busRead8(core,sb+4), num=core->busRead8(core,sb+5);
            unsigned version=core->busRead16(core,sb+0x139C+(0x404E - 0x4000)*2);
            unsigned loop=(core->busRead8(core,sb+0x1270+49/8)>>(49%8))&1;
            unsigned layout=core->busRead16(core,sb+0x32);
            checks+=4;
            if (version || loop || group!=34 || num>5 || layout!=442+num) {result=40;fprintf(stderr,"legacy state mismatch version=%u loop=%u map=%u/%u layout=%u\n",version,loop,group,num,layout);break;}
            printf("AUDIT {\"group\":%u,\"map\":%u,\"layout\":%u,\"version\":%u,\"loop\":%u,\"pos\":[%d,%d],\"warps\":[",group,num,layout,version,loop,(short)core->busRead16(core,sb),(short)core->busRead16(core,sb+2));
            for (unsigned w=0;w<5;w++) {
                unsigned a=sb+4+8*w;
                printf("%s[%d,%d,%d,%d,%d]",w?",":"",(signed char)core->busRead8(core,a),(signed char)core->busRead8(core,a+1),(signed char)core->busRead8(core,a+2),(short)core->busRead16(core,a+4),(short)core->busRead16(core,a+6));
            }
            printf("],\"avatar_object\":%u,\"live_objects\":[",core->busRead8(core,avatar+5));
            unsigned first=1;
            for (unsigned i=0;i<16;i++) {
                unsigned a=objects+36*i;
                if (!(core->busRead8(core,a)&1)) continue;
                printf("%s{\"slot\":%u,\"player\":%u,\"local_id\":%u,\"group\":%u,\"map\":%u,\"gfx\":%u,\"coords\":[%d,%d],\"facing\":%u}",first?"":",",i,core->busRead8(core,a+2)&1,core->busRead8(core,a+8),core->busRead8(core,a+10),core->busRead8(core,a+9),core->busRead8(core,a+5),(short)core->busRead16(core,a+16)-7,(short)core->busRead16(core,a+18)-7,core->busRead8(core,a+24)&15);first=0;
            }
            printf("],\"regions\":{");
            const unsigned offsets[]={0x34,0x234,0xA30,0xC70,0x1270,0x139C};
            const unsigned sizes[]={0x200,0x7FC,0x240,0x600,300,512};
            const char *labels[]={"map_view","party_inventory","saved_objects","templates","flags","vars"};
            for (unsigned r=0;r<6;r++) {
                printf("%s\"%s\":\"",r?",":"",labels[r]);
                for (unsigned i=0;i<sizes[r];i++) printf("%02x",core->busRead8(core,sb+offsets[r]+i));
                printf("\"");
            }
            printf("}}\n");continue;
        }
''')
assert 'busWrite' not in code
(out / 'read-state.c').write_text(code)
with (out / 'host-build.log').open('w') as host_log:
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                    *shlex.split(os.environ.get('DCC_TEST_CFLAGS', '')), str(out / 'read-state.c'),
                    *shlex.split(os.environ.get('DCC_TEST_LDFLAGS', '')), '-lmgba', '-o', str(out / 'playtest')],
                    stdout=host_log, stderr=subprocess.STDOUT, check=True)
fixtures = [('i01-' + name, ROOT / 'artifacts/i01/run-Yw6WfM' / (name + '.sav'))
            for name in ('motion', 'craft', 'quest', 'playtest', 'boss-loss')]
fixtures += [('legacy-corner', ROOT / 'artifacts/n02/legacy-corner-setup/normal-save.sav')]
fixtures += [('a01-' + name, production / (name + '.sav')) for name in
             ('guide-before-trial', 'guide-after-trial', 'both-pending', 'howler-pending',
              'boss-pending', 'prepared', 'legacy-workshop', 'legacy-ending')]
boot = ['step 720 0 -', 'step 1 8 -', 'step 360 0 -', 'step 1 8 -',
        'step 180 0 -', 'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 cold.ppm']
manual_save = ['step 1 8 -', 'step 120 0 -', 'step 1 128 -', 'step 20 0 -',
               'step 1 128 -', 'step 20 0 -', 'step 1 1 -', 'step 160 0 -',
               'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 -',
               'step 1 1 -', 'step 600 0 saved.ppm']
seed_summary = []
seed_navigation = {
    'entrance': ['expect 34 1 4 7 7', 'step 132 16 -', 'step 40 0 -',
                 'step 52 64 -', 'step 220 0 -', 'expect 34 0 12 4 7',
                 'step 20 128 -', 'step 40 0 -', 'expect 34 0 12 5 7'],
    'service': ['expect 34 1 4 7 7', 'step 20 32 -', 'step 40 0 -',
                'step 52 64 -', 'step 40 0 -', 'step 20 32 -', 'step 220 0 -',
                'expect 34 2 2 4 7', 'step 36 16 -', 'step 40 0 -',
                'step 36 128 -', 'step 40 0 -', 'expect 34 2 4 6 7']}
for name, navigation in seed_navigation.items():
    seed = production / 'guide-before-trial.sav'; original = digest(seed)
    d = out / ('ordinary-' + name + '-seed'); d.mkdir(); save = d / 'copy.sav'; shutil.copyfile(seed, save)
    lines = boot + navigation + manual_save + ['audit', 'quit']
    (d / 'input.route').write_text('\n'.join(lines) + '\n')
    with (d / 'input.route').open() as inputs, (d / 'replay.log').open('w') as log, (d / 'errors.log').open('w') as errors:
        subprocess.run([str(out / 'playtest'), str(production / 'production.gba'), str(save), str(production / 'game.sym')],
                       cwd=d, stdin=inputs, stdout=log, stderr=errors, check=True)
    assert not (d / 'errors.log').stat().st_size
    assert (d / 'replay.log').read_text().endswith('result=0 assertions=7\n')
    assert digest(seed) == original and digest(save) != original
    for p in d.glob('*.ppm'): Image.open(p).save(p.with_suffix('.png'))
    seed_summary.append({'route': d.name, 'source_save': str(seed.relative_to(ROOT)), 'source_sha256': original,
                         'generated_save_sha256': digest(save), 'original_unchanged': True, 'assertions': 7,
                         'method': 'Ordinary navigation and manual Save/overwrite confirmation; no RAM/save-file patch.'})
    fixtures.append(('ordinary-' + name + '-cold', save))
    print(d.name, 'PASS', flush=True)
summary = []
for name, seed in fixtures:
    original = digest(seed); d = out / name; d.mkdir(); save = d / 'copy.sav'; shutil.copyfile(seed, save)
    lines = boot + ['audit', 'quit']; (d / 'input.route').write_text('\n'.join(lines) + '\n')
    with (d / 'input.route').open() as inputs, (d / 'replay.log').open('w') as log, (d / 'errors.log').open('w') as errors:
        subprocess.run([str(out / 'playtest'), str(production / 'production.gba'), str(save), str(production / 'game.sym')],
                       cwd=d, stdin=inputs, stdout=log, stderr=errors, check=True)
    assert not (d / 'errors.log').stat().st_size
    log = (d / 'replay.log').read_text(); assert log.endswith('result=0 assertions=4\n')
    rows = re.findall(r'^AUDIT (.+)$', log, re.M); assert len(rows) == 1
    state = json.loads(rows[0])
    state['region_sha256'] = {n: hashlib.sha256(bytes.fromhex(v)).hexdigest() for n, v in state['regions'].items()}
    state['nonzero_cache_words'] = sum(bytes.fromhex(state['regions']['map_view'])[i:i+2] != b'\0\0' for i in range(0,512,2))
    del state['regions']
    assert digest(seed) == original and digest(save) == original, 'Read-only cold route changed a save'
    Image.open(d / 'cold.ppm').save(d / 'cold.png')
    summary.append({'route': name, 'source_save': str(seed.relative_to(ROOT)), 'source_sha256': original,
                    'original_and_copy_unchanged': True, 'assertions': 4, 'state': state})
    print(name, 'PASS', state['group'], state['map'], state['pos'], flush=True)
(out / 'identity.json').write_text(json.dumps({'runner_source': HEAD, 'engine_base': BASE,
    'production_compiled_source': (production / 'tested-commit.txt').read_text().strip(),
    'production_rom_sha256': digest(production / 'production.gba'),
    'method': '16 copied ordinary saves plus2 controller-produced seed sessions; cold Continue, read-only bus sampling. No ROM rebuild, save-file edits, RAM writes or migration. Every cold original/copy hash unchanged;2 new seed files are saved by normal gameplay.'}, indent=2) + '\n')
(out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
(out / 'seeds.json').write_text(json.dumps(seed_summary, indent=2) + '\n')
assert {row['state']['map'] for row in summary} == set(range(6)), 'All six legacy maps required'
assert not git('status', '--porcelain') and git('rev-parse', 'HEAD') == HEAD
print('PASS', len(summary) + len(seed_summary), 'ordinary production sessions /',
      sum(x['assertions'] for x in summary + seed_summary), 'assertions', flush=True)
