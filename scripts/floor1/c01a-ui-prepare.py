"""Offline binding/preparation for the new C01a contract; never runs an emulator."""
from pathlib import Path
import hashlib,subprocess,shutil,json,os,re,struct,importlib.util
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-action-hints-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
BASE='bdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7'
GAME='807eeea457c973b097be9eab9e1556e20d0204aa'
SEED=Path('/workspace/scratch/ordinary-recovery-r6-20261010/runtime-prepare-03/patrol.sav')
SAVE='53f62dc2e283d89236d5572f47c3e7449c0bc1c06de738b1427fc9664ae67eb6'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def write(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def prepare(resume=False):
    assert not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    assert sha(SEED)==SAVE
    assert (OUT/'candidate-build/build.exit').read_text().strip()=='0'
    env=dict(os.environ);env['PATH']=str(TOOL/'usr/bin')+':'+env['PATH'];os.environ['PATH']=env['PATH']
    code=module('c01uihost',ROOT/'scripts/floor1/c01a-ui-host.py').generate(git)
    observer=OUT/'observer.c';observer.write_text(code)
    lib=TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5';assert sha(lib)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
    command=['cc','-DUSE_DEBUGGERS','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(observer),'-L'+str(lib.parent),'-lmgba','-o',str(OUT/'observer')]
    if not resume:
        proc=subprocess.run(command,env=env,capture_output=True);(OUT/'observer-compile.log').write_bytes(proc.stdout+proc.stderr);assert proc.returncode==0
    else:
        assert all(json.loads((OUT/c/'identity.json').read_text())['observer_source_SHA256']==sha(observer) for c in ['baseline','candidate'])
    assert 'busWrite' not in code and code.count('bv_native_frame(&native,')==1
    boundary=module('c01boundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py');symbols=boundary.symbols
    timeline=module('c01timeline',ROOT/'scripts/floor1/v01-native-timeline-symbols.py')
    state=module('c01state',Path('/workspace/scratch/ordinary-recovery-r4-20261010/build/source/scripts/floor1/guard-first-state.py'))
    names={'uiAction':'L:battle_controller_player.o:HandleInputChooseAction','uiMove':'L:battle_controller_player.o:HandleInputChooseMove','uiTarget':'L:battle_controller_player.o:HandleInputChooseTarget','uiBag':'L:item_menu.o:Task_BagMenu_HandleInput','uiParty':'G:Task_HandleChooseMonInput','uiContext':'L:party_menu.o:Task_HandleSelectionMenuInput','uiSummary':'L:pokemon_summary_screen.o:Task_HandleInput'}
    cases={}
    for case,game,engine in [('baseline',BASE,Path('/workspace/scratch/new-input-visual-pair-20261010/candidate-build/source/engine')),('candidate',GAME,OUT/'candidate-build/source/engine')]:
        out=OUT/case
        if resume:
            identity=json.loads((out/'identity.json').read_text())
            assert identity['source']==game and identity['ROM_SHA256']==sha(engine/'pokeemerald.gba') and identity['ELF_SHA256']==sha(engine/'pokeemerald.elf')
            for name,h in identity['files_SHA256'].items():assert sha(out/name)==h
            cases[case]=sha(out/'identity.json');continue
        out.mkdir()
        assert git('rev-parse',game+':engine')==git('rev-parse',('9c83611e8e9b61d55388c18496c361d3362e462e' if case=='baseline' else GAME)+':engine')
        elf=engine/'pokeemerald.elf';native=boundary.write(elf,out/'native-boundary.json')
        assert (native['entry'],native['caller_LR'],native['entry_opcode'])==(0x080008ac,0x080004bf,0xb500)
        text=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(elf)],env=env,text=True)
        text+=subprocess.check_output(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],env=env,text=True)
        text+=symbols.export(elf,out/'verified-functions.json')
        rows=json.loads((out/'verified-functions.json').read_text())
        for name,identity in names.items():
            hits=[r for r in rows if identity in r['aliases']];assert len(hits)==1
            text+=f"{hits[0]['address']:08x} A {name}\n"
        for name,key in [('Entry','entry'),('Caller','caller_LR'),('Opcode','entry_opcode')]:text+=f"{native[key]:08x} A bv_native{name}\n"
        text+=timeline.export(elf,out/'native-timeline-points.json')
        (out/'game.sym').write_text(text)
        raw=[line.split() for line in text.splitlines()];required=set(re.findall(r'strcmp\(symbol,\s*"([^"]+)"\)',code));optional={'gDccCollectionProbe','gDccEquipmentProbe','gDccMembershipProbe','gDccRewardProbe'}
        for name in required-optional:
            hits=[(a,k) for a,k,n in raw if n==name]
            assert hits and (len({a for a,k in hits})==1 or name=='Task_DisplayHPRestoredMessage'),name
        decoded=state.seed_snapshot(SEED,out/'expected');assert decoded['count']==2 and decoded['friendship_counter']==47
        (out/'expected-counter.bin').write_bytes(struct.pack('<H',47));(out/'visual-mode.bin').write_bytes(bytes([case=='candidate']))
        shutil.copyfile(ROOT/'scripts/contracts/f1-c01a-ui.route',out/'input.route');shutil.copyfile(SEED,out/'game.sav')
        identity=dict(case=case,source=game,engine_tree=git('rev-parse',game+':engine'),ROM=str(engine/'pokeemerald.gba'),ROM_SHA256=sha(engine/'pokeemerald.gba'),ELF_SHA256=sha(elf),Save_SHA256=SAVE,observer_source_SHA256=sha(observer),observer_binary_SHA256=sha(OUT/'observer'),files_SHA256={p.name:sha(p) for p in out.iterdir() if p.is_file()},native_bindings=names,full_2560_snapshot_preserved=True)
        write(out/'identity.json',identity);cases[case]=sha(out/'identity.json')
    if not resume or not (OUT/'ui-abi.json').exists():
        # All native ABI declarations used by the new menu observer are unchanged
        # between the exact baseline and candidate archives. Existing compiled task,
        # fade, full-state and native-boundary ABI evidence stays untouched.
        baseline=Path('/workspace/scratch/new-input-visual-pair-20261010/candidate-build/source/engine')
        candidate=OUT/'candidate-build/source/engine'
        headers=['global.h','battle_controllers.h','task.h','palette.h','party_menu.h']
        for name in headers:assert (baseline/'include'/name).read_bytes()==(candidate/'include'/name).read_bytes()
        abi=OUT/'ui-abi.c';abi.write_text('#include "global.h"\n#include "battle.h"\n#include "battle_controllers.h"\n#include "task.h"\n#include "party_menu.h"\n#define OFF(s,f) ((unsigned)&((struct s *)0)->f)\nconst unsigned uiLayout[]={sizeof(struct ChooseMoveStruct),OFF(ChooseMoveStruct,moves),OFF(ChooseMoveStruct,currentPP),OFF(ChooseMoveStruct,maxPP),sizeof(struct Task),OFF(Task,isActive),OFF(Task,data),OFF(PartyMenu,task)};\n')
        pp=subprocess.check_output(['gcc','-E','-iquote','include','-iquote','src','-Wno-trigraphs','-DMODERN=0','-I','tools/agbcc/include','-I','tools/agbcc','-nostdinc','-undef','-std=gnu89',str(abi)],cwd=candidate,env=env)
        assembly=subprocess.check_output(['tools/agbcc/bin/agbcc','-mthumb-interwork','-Wimplicit','-Wparentheses','-Werror','-O2','-fhex-asm','-o','-','-'],cwd=candidate,input=pp,env=env)
        (OUT/'ui-abi.s').write_bytes(assembly+b'\n.text\n\t.align\t2, 0\n')
        obj=OUT/'ui-abi.o';subprocess.run(['arm-none-eabi-as','-mcpu=arm7tdmi','--defsym','MODERN=0','-o',str(obj),str(OUT/'ui-abi.s')],check=True,env=env)
        audit=module('c01sections',ROOT/'scripts/floor1/v01-static-build-audit.py');data=audit.sections(obj)['.rodata']['bytes'];row=[r for r in symbols.elf_symbols(obj) if r['name']=='uiLayout'];assert len(row)==1
        values=struct.unpack('<8I',data[row[0]['value']:row[0]['value']+row[0]['size']]);assert values==(20,0,8,12,40,4,8,4)
        write(OUT/'ui-abi.json',dict(PASS=True,values=values,headers={n:sha(candidate/'include'/n) for n in headers},object_SHA256=sha(obj)))
        # The new strings are verified from compiled ELF bytes, not assumed build outputs.
        elf=OUT/'candidate-build/source/engine/pokeemerald.elf';rows=symbols.elf_symbols(elf)
        cm={c:int(h,16) for c,h in re.findall(r"^'([^']*)'\s*=\s*([0-9A-Fa-f]+)",(ROOT/'engine/charmap.txt').read_text(),re.M)}
        compiled={}
        for name,s in [('gText_MoveInterfaceUses','USES'),('gText_DccStrikeHint','ONE FOE'),('gText_DccBraceHint','SELF DEF+'),('gText_DccSparkHint','BOTH FOES'),('gText_DccWeakenHint','ALL FOES ATK-')]:
            hits=[r for r in rows if r['name']==name];assert len(hits)==1
            expected=bytes(cm[c] for c in s)+b'\xff';assert boundary.rom_bytes(elf,hits[0]['value'],len(expected))==expected
            compiled[name]=dict(text=s,compiled_bytes=expected.hex())
        write(OUT/'compiled-strings.json',compiled)
    else:
        abi=json.loads((OUT/'ui-abi.json').read_text());assert abi['PASS'] and abi['object_SHA256']==sha(OUT/'ui-abi.o')
        assert (OUT/'compiled-strings.json').is_file()
    tooling=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009');ag=json.loads((tooling/'agbcc-identity.json').read_text());libid=json.loads((tooling/'libmgba-identity.json').read_text())
    toolfiles={r['path']:r['SHA256'] for r in ag['compilers']};toolfiles[ag['GCC_path']]=ag['GCC_SHA256'];toolfiles.update({r['resolved_path']:r['SHA256'] for r in libid['resolved_dependency_hashes']});toolfiles[libid['path']]=libid['SHA256']
    for p,h in toolfiles.items():assert sha(p)==h
    assert ag['source_commit']=='da598c1d918402c42c0c0d7128ba14567f3175e9' and not ag['original_tool_identity_claimed']
    # Bound native startup/window, summaries, full reference copies, RGB captures,
    # logs, supplemental frames and private lossless/viewing captures for BOTH cases.
    route=(ROOT/'scripts/contracts/f1-c01a-ui.route').read_text().splitlines();assert len(route)==156 and not any(l.startswith('pilot ') for l in route)
    storage=dict(visual_frames=18000,battle_frames=30000,native_boundaries_per_frame=4096,native_timeline_startup_frames=2046,native_timeline_active_window=250,native_detail_file_max=1542000000,each_file_hard_max=2*1024**3,RGB_capture_max_per_case=18000*(240*160*3+32)+100*(240*160*3+32),native_reference_max_per_case=2*1024**3,supplemental_reference_max_per_case=18000*2700,logs_max_per_case=32*1024**2,clips_max_per_case=2*1024**3,pair_total_reserved_bytes=20*1024**3,claim_limit_per_case=1,first_failure_stop=True,no_Save=True)
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=storage['pair_total_reserved_bytes']
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    write(OUT/'freeze.json',dict(source_checkpoint=git('rev-parse','HEAD'),base=BASE,tested=GAME,cases=cases,route_SHA256=sha(ROOT/'scripts/contracts/f1-c01a-ui.route'),Save_path=str(SEED),Save_SHA256=SAVE,storage=storage,dependencies=dependencies,tool_files=toolfiles,scope='One ordinary menu baseline plus conditional candidate; partial UI route only, no V01 pair replay/Save/victory/full-floor or legacy claim'))
    print('OFFLINE PREPARED: exact source/build/observer/route/Save/tooling bindings and capacity frozen; no gameplay')
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--resume-offline-abi',action='store_true');prepare(p.parse_args().resume_offline_abi)
