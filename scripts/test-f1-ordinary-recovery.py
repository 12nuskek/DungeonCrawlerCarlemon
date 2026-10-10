#!/usr/bin/env python3
"""One new ordinary New Game reconstruction, then exact independent cold. No retry."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
GAME = 'c6d647a815ffce44a2419a2cf83b6c2c094359f0'
ENGINE = '76001ee128785714b7c15aef6d9c95630587d0a9'
BASE = '5b1c108557ecdb2704dea94c61aff1fb28845acd'
STAGES = ['fresh', 'seed', 'patrol', 'cold']
CONTRACT = 'docs/floor1/ordinary-gameplay-recovery-20261009-contract.md'
NEW = ['scripts/test-f1-ordinary-recovery.py', 'scripts/floor1/ordinary-recovery-host.py',
       'scripts/floor1/ordinary-recovery-abi.c', CONTRACT]


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(command, **kwargs):
    return subprocess.run(command, check=True, capture_output=True, **kwargs).stdout


def captures(directory):
    result = {}
    for path in sorted(directory.glob('*.ppm')):
        frame = Image.open(path); assert frame.size == (240,160)
        png = path.with_suffix('.png'); assert not png.exists(); frame.save(png)
        result[png.name] = sha(png)
    raw = directory/'motion.rgb'
    if raw.exists():
        assert 0 < raw.stat().st_size <= 2880000000 and raw.stat().st_size % 115200 == 0
        video=directory/'motion.mkv';assert not video.exists()
        run(['ffmpeg','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','240x160',
             '-framerate','16777216/1123584','-i',str(raw),'-c:v','ffv1','-level','3','-pix_fmt','bgr0',str(video)])
        result['motion'] = dict(samples=raw.stat().st_size//115200, raw_SHA256=sha(raw),
                                FFV1_SHA256=sha(video), native_speed=True)
    return result


def routes(source):
    fresh = (source / 'docs/evidence/floor1/g01e/verified-partial-live/fresh-trial/input.route').read_text().splitlines()
    fresh = [x for x in fresh if x not in ('snapshot', 'quit')]
    pending = ['flag 46 0', 'flag 47 0', 'flag 48 0', 'flag 49 0', 'flag 2138 0', 'flag 2139 0']
    fresh += ['levels 9 9', 'growth 9 495 0 9 805 0', 'uses 3 40 0 37',
              'item 13 2', 'flag 2136 0', 'flag 2137 0'] + pending + ['ordinary-checkpoint fresh-saved', 'quit']
    geometry = module('ordinary_geometry', source / 'scripts/floor1/relocation-graybox.py')
    live = module('ordinary_routes', source / 'scripts/floor1/live-route.py')
    spec = json.loads((source / 'scripts/contracts/f1-g01d-relocation.json').read_text())
    route = live.Route(spec, geometry, 'quiet', (10, 7), 1, 7)
    route.anchor('rack'); route.talk(128, 'scrap-box')
    route.lines += ['item 378 2', 'item 13 2', 'flag 39 1']
    route.lines += ['step 1 8 -', 'step 120 0 -', 'step 1 128 -', 'step 20 0 -',
                    'step 1 1 -', 'wait-task bag 3600', 'step 1 1 -', 'step 12 0 -',
                    'wait-task field-context 3600', 'step 1 1 -', 'step 12 0 -',
                    'wait-task party 3600', 'step 1 128 -', 'step 40 0 -',
                    'step 1 1 -', 'wait-task healed 3600', 'step 40 0 field-potion.ppm',
                    'item 13 1', 'uses 3 40 0 37', 'return-field', 'ready']
    route.anchor('guide'); route.talk(128, 'guide-rest')
    route.lines += ['duo healthy', 'uses 8 40 2 40', 'growth 9 495 0 9 805 0']
    route.anchor('arrival'); route.anchor('guard')
    route.lines += ['step 1 8 -', 'step 120 0 -', 'step 1 64 -', 'step 20 0 -', 'step 1 2 -', 'step 120 0 -']
    route.save()
    boot = ['step 720 0 -', 'step 1 8 -', 'step 360 0 -', 'step 1 8 -', 'step 180 0 -',
            'step 1 1 -', 'step 180 0 -', 'step 1 1 -', 'step 600 0 cold.ppm', 'ready']
    seed = boot + [x for x in route.lines if x != 'snapshot']
    seed += ['expect 35 0 37 31 7', 'duo healthy', 'uses 8 40 2 40', 'levels 9 9',
             'item 13 1', 'item 378 2', 'flag 2135 1', 'flag 2136 0', 'flag 2137 0'] + pending
    seed += ['ordinary-checkpoint seed-saved', 'quit']
    result = dict(fresh='\n'.join(fresh)+'\n', seed='\n'.join(seed)+'\n')
    for stage, suffix, pin in [('patrol', '', '8de593f9f8c95fb52a1a63e4b104ee75d627670c2568a1dd6c41213c1ad175b5'),
                               ('cold', '-cold', 'b042379c0f70dbba87e3f25f5fe66ce6384752ac9cafdea07d73d9de2823aa67')]:
        path = source / ('scripts/contracts/f1-g01e-guard-first-current'+suffix+'.route')
        assert sha(path) == pin
        result[stage] = path.read_text()
    assert all(not any(x.startswith('policy ') for x in text.splitlines()) for text in result.values())
    return result


def bindings(engine, code, out):
    text = run(['arm-none-eabi-nm', '--defined-only', str(engine / 'pokeemerald.elf')], text=True)
    text += run(['python3', str(ROOT / 'scripts/battle-input-symbols.py'), str(engine)], text=True)
    (out / 'game.sym').write_text(text)
    symbols = module('ordinary_symbols', ROOT / 'scripts/floor1/v01-battle-symbols.py')
    functions = symbols.functions(symbols.elf_symbols(engine / 'pokeemerald.elf'))
    rows = [line.split() for line in text.splitlines()]
    result = {}
    absent = {'gDccCollectionProbe', 'gDccEquipmentProbe', 'gDccMembershipProbe', 'gDccRewardProbe'}
    for name in sorted(set(re.findall(r'strcmp\(symbol,\s*"([^"]+)"\)', code))):
        ordered = [int(a, 16) for a, k, n in rows if n == name]
        if name in absent:
            assert not ordered
            result[name] = {'present': False, 'unused_fail_closed_policy': True}
            continue
        if name == 'Task_DisplayHPRestoredMessage':
            candidates = [r for r in functions if 'L:party_menu.o:'+name in r['aliases']]
            assert len(set(ordered)) == 2 and len(candidates) == 1 and ordered[-1] == candidates[0]['address']
            result[name] = {'ordered_addresses': ordered, 'effective_identity': candidates[0]['identity']}
        else:
            assert len(set(ordered)) == 1, ('missing/ambiguous ordinary binding', name)
            result[name] = {'address': ordered[-1]}
    return result


def abi(engine, out):
    source = ROOT / 'scripts/floor1/ordinary-recovery-abi.c'
    pp = run(['gcc', '-E', '-iquote', 'include', '-iquote', 'src', '-DMODERN=0', '-I', 'tools/agbcc/include',
              '-I', 'tools/agbcc', '-nostdinc', '-undef', '-std=gnu89', str(source)], cwd=engine)
    assembly = run(['tools/agbcc/bin/agbcc', '-mthumb-interwork', '-Wimplicit', '-Wparentheses', '-Werror',
                    '-O2', '-fhex-asm', '-o', '-', '-'], cwd=engine, input=pp)
    (out / 'native-abi.s').write_bytes(assembly+b'\n.text\n\t.align\t2, 0\n')
    obj = out / 'native-abi.o'
    run(['arm-none-eabi-as', '-mcpu=arm7tdmi', '--defsym', 'MODERN=0', '-o', str(obj), str(out / 'native-abi.s')])
    data = obj.read_bytes(); header = struct.unpack_from('<16sHHIIIIIHHHHHH', data)
    sections = [struct.unpack_from('<10I', data, header[6]+i*header[11]) for i in range(header[12])]
    symbols = module('ordinary_abi_symbols', ROOT / 'scripts/floor1/v01-battle-symbols.py').elf_symbols(obj)
    def constant(name):
        hits = [r for r in symbols if r['name'] == name]; assert len(hits) == 1
        row = hits[0]; section = sections[row['index']]
        return data[section[4]+row['value']:section[4]+row['value']+row['size']]
    values = list(struct.unpack('<22I', constant('ordinaryLayout')))
    expected = [100,80,88,40,0x3d88,0xf2c,0x1270,300,0x490,0x988,0x234,0x238,0x13f0,0xac,
                0x24,0x10,5,0,4,12,40,4]
    assert values == expected, ('native ordinary ABI', values)
    bits = [('ordinaryFacing',0x18,1), ('ordinaryBattle',0x439,2), ('ordinaryFade',7,128)]
    for name, offset, value in bits:
        raw = constant(name); assert raw[offset] == sum(raw) == value, (name, raw.hex())
    return dict(layout=values, bitfields=bits, source_SHA256=sha(source), object_SHA256=sha(obj))


def prepare(build, out):
    assert not out.exists(), 'New output only'
    out.mkdir(parents=True)
    source = build / 'source'; engine = source / 'engine'
    assert (build / 'tested-commit.txt').read_text().strip() == GAME
    assert git('rev-parse', GAME+':engine') == ENGINE
    # Every archived tracked engine file, except the three pinned hydrated blobs.
    hydration = json.loads((build.parent / 'hydration.json').read_text())
    for path in git('ls-tree', '-r', '--name-only', GAME, '--', 'engine').splitlines():
        local = source / path
        if path[7:] in hydration:
            assert sha(local) == hydration[path[7:]]['SHA256']
        else:
            expected = subprocess.check_output(['git','show',GAME+':'+path],cwd=ROOT)
            assert local.read_bytes() == expected, ('main source bytes', path)
    host = module('ordinary_host', ROOT / 'scripts/floor1/ordinary-recovery-host.py')
    code, base = host.generate(git, source); (out / 'observer.c').write_text(code)
    with (out / 'host-build.log').open('w') as log:
        subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror',str(out/'observer.c'),'-lmgba','-o',str(out/'playtest')],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    observer = bindings(engine, code, out); native = abi(engine, out)
    for stage, text in routes(source).items(): (out / (stage+'.route')).write_text(text)
    identity = dict(host_source=git('rev-parse','HEAD'), game_source=GAME, engine_tree=ENGINE, publication_base=BASE,
                    ROM_SHA256=sha(engine/'pokeemerald.gba'), ELF_SHA256=sha(engine/'pokeemerald.elf'),
                    host_SHA256=sha(out/'observer.c'), binary_SHA256=sha(out/'playtest'), symbols_SHA256=sha(out/'game.sym'),
                    routes={s:sha(out/(s+'.route')) for s in STAGES}, bindings=observer, native_ABI=native,
                    reconstructed_base_observer=base, hydrated_blobs=hydration,
                    frame_limit_each=100000, battle_frame_limit_each=36000, execution_limit_each=1,
                    motion=dict(sample_every_frames=4, native_fps='16777216/280896', rgb_bytes_limit_each=2880000000,
                                no_replay=True, encoded_speed='native ordinary speed'),
                    total_output_storage_limit=13000000000, wall_seconds_limit_each=600,
                    ffmpeg_SHA256=sha(Path(shutil.which('ffmpeg'))),
                    tooling=json.loads((build.parent.parent/'ordinary-recovery-tooling-r3-20261009/agbcc-identity.json').read_text()),
                    mgba=json.loads((build.parent.parent/'ordinary-recovery-tooling-r3-20261009/libmgba-identity.json').read_text()))
    (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    print('PASS prepare: actual main ROM/ELF, source, generated host, symbols, native ABI and routes verified; no emulator')


def execute(build, out, stage):
    identity = json.loads((out/'identity.json').read_text()); head = git('rev-parse','HEAD')
    assert not (out/'STOP.json').exists(), 'First failure remains terminal'
    subprocess.run(['git','diff','--quiet',identity['host_source'],head,'--',*NEW,'scripts/floor1','scripts/contracts'],cwd=ROOT,check=True)
    source = build/'source'; engine = source/'engine'
    for path, key in [(engine/'pokeemerald.gba','ROM_SHA256'), (engine/'pokeemerald.elf','ELF_SHA256'),
                      (out/'observer.c','host_SHA256'), (out/'playtest','binary_SHA256'), (out/'game.sym','symbols_SHA256')]:
        assert sha(path) == identity[key]
    assert sha(out/(stage+'.route')) == identity['routes'][stage]
    assert sha(Path(shutil.which('ffmpeg'))) == identity['ffmpeg_SHA256']
    summaryfile=out/'summary.json'; summary=json.loads(summaryfile.read_text()) if summaryfile.exists() else []
    assert [r['stage'] for r in summary] == STAGES[:STAGES.index(stage)]
    assert shutil.disk_usage(out).free >= 7000000000, 'Fresh storage check before emulator'
    assert sum(p.stat().st_size for p in out.rglob('*') if p.is_file()) < 13000000000
    d=out/stage;d.mkdir();save=out/(stage+'.sav');assert not save.exists()
    if stage!='fresh': shutil.copyfile(out/(STAGES[STAGES.index(stage)-1]+'.sav'),save)
    before=sha(save) if save.exists() else None
    state=module('ordinary_state',source/'scripts/floor1/guard-first-state.py')
    if stage in ('patrol','cold'): state.seed_snapshot(save,d/'expected')
    shutil.copyfile(out/(stage+'.route'),d/'input.route')
    claim=dict(execution_source=head, host_source=identity['host_source'], stage=stage, execution_limit=1,
               identity_SHA256=sha(out/'identity.json'), input_Save_SHA256=before, route_SHA256=sha(d/'input.route'),
               battles=1 if stage=='fresh' else 2 if stage=='patrol' else 0)
    with (d/'execution-claim.json').open('x') as f:json.dump(claim,f,indent=2)
    verdict=dict(claim)
    try:
        with (d/'input.route').open() as inp,(d/'replay.log').open('w') as log,(d/'errors.log').open('w') as err:
            result=subprocess.run([str(out/'playtest'),str(engine/'pokeemerald.gba'),str(save),str(out/'game.sym'),stage],
                                  cwd=d,stdin=inp,stdout=log,stderr=err,timeout=600)
        verdict.update(exit=result.returncode,errors_bytes=(d/'errors.log').stat().st_size,output_Save_SHA256=sha(save))
        verdict['captures']=captures(d)
        text=(d/'replay.log').read_text();footer=re.search(r'assertions=(\d+)\n$',text)
        verdict['assertions']=int(footer[1]) if footer else None
        assert result.returncode==0 and not verdict['errors_bytes'] and footer, 'first native failure'
        clock=re.search(r'PATROL_CLOCK absolute_frames=(\d+) valid_samples=(\d+) deferred_samples=(\d+) reentries=(\d+) unarmed_frames=(\d+) mutation_frames=(\d+) checkpoints=(\d+) battle_frames=(\d+) battle_attempts=(\d+) stage=(\d+)',text)
        assert clock
        c=dict(zip(['frames','valid','deferred','reentries','unarmed','mutation','checkpoints','battle_frames','battle_attempts','stage'],map(int,clock.groups())))
        verdict['clock']=c
        assert c['frames']==c['valid']+c['deferred']+c['unarmed']+c['mutation']<=100000
        if stage!='cold':
            state.seed_snapshot(save,d/'disk');disk=state.snapshot(d/'disk')
            live=state.snapshot(d/({'fresh':'fresh-saved','seed':'seed-saved','patrol':'saved'}[stage]))
            for k in ('party','flags','logical','count','saved_count','counter','map','position'):
                assert disk[k]==live[k], ('complete manual Save persistence',k)
            assert disk['count']==2 and 0<=disk['counter']<128
            for i in range(2):
                decoded=state.fields.decode(disk['party'][i*100:(i+1)*100])
                assert decoded['checksum_valid'] and decoded['reencoding_exact'] and not decoded['bad_egg'] and not decoded['egg']
            verdict['native_manual_Save_exact']=True
        if stage=='patrol':
            assert c['battle_attempts']==2 and c['stage']==4
            reviewed=module('ordinary_travel',source/'scripts/test-f1-g01e-guard-first-current.py')
            verdict['travel']=reviewed.travel(text)
            assert disk['map']==[35,3] and disk['position']==[8,7]
        if stage=='cold':
            assert c['battle_attempts']==c['battle_frames']==0 and sha(save)==before==sha(out/'patrol.sav')
            for k in ('party','flags','logical','count','saved_count','counter','map','position'):
                assert state.snapshot(d/'cold')[k]==state.snapshot(d/'expected')[k],('independent full cold',k)
            verdict['native_cold_exact']=True
        verdict['facing']=re.findall(r'FIELD_FACING checkpoint=(\S+) facing=(\d+)',text)
    except BaseException as e:
        verdict['validation_failure']=str(e)
        if save.exists():verdict['output_Save_SHA256']=sha(save)
        (out/'STOP.json').write_text(json.dumps(verdict,indent=2)+'\n')
        summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n')
        raise SystemExit('STOP: first failure retained; no dependent emulator execution')
    summary.append(verdict);summaryfile.write_text(json.dumps(summary,indent=2)+'\n')
    print('PASS',stage,verdict['assertions'],'assertions; actual Save',sha(save))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--build',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--stage',choices=['prepare']+STAGES,required=True)
    args=parser.parse_args();assert not git('status','--porcelain'),'Freeze committed source first'
    if args.stage=='prepare': prepare(args.build.resolve(),args.output.resolve())
    else: execute(args.build.resolve(),args.output.resolve(),args.stage)


if __name__=='__main__':main()
