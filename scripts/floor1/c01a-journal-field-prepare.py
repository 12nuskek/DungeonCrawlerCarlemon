"""Conditional field probe freeze; compiles only a read-only host observer."""
from pathlib import Path
import importlib.util,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-journal-field-r1-20261010')
BATTLE=Path('/workspace/scratch/c01a-journal-admission-r3-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
sha=module('fieldHash',ROOT/'scripts/floor1/c01a-complete-artifacts.py').sha
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def prepare():
    assert not git('status','--porcelain') and not (BATTLE/'STOP.json').exists()
    battle=json.loads((BATTLE/'battle-PASS.json').read_text());assert battle['PASS'] and battle['full_native_pixels_byte_equal'] and battle['pixel_masks']==0
    assert battle['actual_emulator_process']==8 and battle['consumed_claim']==9
    OUT.mkdir();case=OUT/'field-probe';case.mkdir()
    ident=json.loads((BATTLE/'candidate/identity.json').read_text());freeze=json.loads((BATTLE/'freeze.json').read_text());engine=Path(ident['ROM']).parent;elf=engine/'pokeemerald.elf'
    assert sha(ident['ROM'])==ident['ROM_SHA256'] and sha(elf)==ident['ELF_SHA256']
    assert git('rev-parse','HEAD:engine')==ident['engine_tree']
    for n,h in freeze['tool_files'].items():assert sha(n)==h,n
    source=module('fieldHost',ROOT/'scripts/floor1/c01a-journal-field-host.py').generate();(OUT/'observer.c').write_text(source)
    command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(OUT/'observer.c'),'-L'+str(TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(OUT/'observer')]
    env=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
    result=subprocess.run(command,env=env,capture_output=True);(OUT/'host-compile.log').write_bytes(result.stdout+result.stderr);assert result.returncode==0
    os.chmod(OUT/'observer',0o700)
    expected={'SHA256':sha(OUT/'observer'),'mode':0o700,'owner_uid':os.geteuid()}
    admission=module('fieldExecAdmission',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',expected);expected.update(device=admission['device'],inode=admission['inode'])
    boundary=module('fieldBindings',ROOT/'scripts/floor1/v01-native-boundary-symbols.py');rows=json.loads((BATTLE/'candidate/verified-functions.json').read_text());syms=boundary.symbols.elf_symbols(elf)
    text=(BATTLE/'candidate/game.sym').read_text();bindings={}
    for name,identity in [('jfYesNo','L:script_menu.o:Task_HandleYesNoInput'),('jfStartTask','G:Task_ShowStartMenu'),('jfStartInput','L:start_menu.o:HandleStartMenuInput')]:
        hit=[r for r in rows if identity in r['aliases']];assert len(hit)==1;row=hit[0];text+=f"{row['address']:08x} A {name}\n";bindings[name]={'identity':identity,'address':row['address'],'compiled_SHA256':__import__('hashlib').sha256(boundary.rom_bytes(elf,row['address'],row['size'])).hexdigest()}
    hit=[r for r in syms if r['name']=='sStartMenuCursorPos'];assert len(hit)==1;text+=f"{hit[0]['value']:08x} A jfStartCursor\n";bindings['jfStartCursor']={'native_symbol':'sStartMenuCursorPos','address':hit[0]['value']}
    (case/'game.sym').write_text(text)
    for name in ['global.h','task.h','text.h','palette.h']:
        assert (engine/'include'/name).read_bytes()==(Path('/workspace/scratch/new-input-visual-pair-20261010/candidate-build/source/engine/include')/name).read_bytes()
    seed=Path(freeze['Save_path']);assert sha(seed)==freeze['Save_SHA256'];shutil.copyfile(seed,case/'game.sav');shutil.copyfile(BATTLE/'candidate/expected-party.bin',case/'expected-party.bin')
    assert sha(case/'game.sav')==freeze['Save_SHA256']
    route=module('fieldRoute',ROOT/'scripts/floor1/c01a-journal-field-route.py').generate();(case/'input.route').write_text(route)
    storage={'max_frames':18000,'frame_dimensions':[240,160],'RGB_max_bytes':18000*115216+100*115216,'logs_max_bytes':32*1024**2,'file_hard_max':2*1024**3,'reserved_bytes':4*1024**3,'claim_limit':1,'first_failure_stop':True,'no_battle':True,'no_Save':True}
    st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=storage['reserved_bytes']
    field=dict(source=ident['source'],engine_tree=ident['engine_tree'],helper_commit=git('rev-parse','HEAD'),ROM=ident['ROM'],ROM_SHA256=ident['ROM_SHA256'],ELF_SHA256=ident['ELF_SHA256'],Save_path=str(seed),Save_SHA256=sha(seed),observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),observer_admission=expected,native_bindings=bindings,files_SHA256={p.name:sha(p) for p in case.iterdir() if p.is_file()},battle_PASS_SHA256=sha(BATTLE/'battle-PASS.json'),counts_before={'baseline':5,'candidate':3,'field_probes':0,'actual_total':8,'consumed_total':9},claim={'number':10,'type':'field-only-Journal','field_attempt':1,'process_if_launched':9},storage=storage,dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts},tool_files=freeze['tool_files'],packet_regions=['party600','count1','counter2','flags300','vars512','resources1440','key4','savedparty600','savedcount4','position/map6'],route_commands=len(route.splitlines()),first_failure_stop=True)
    write(OUT/'freeze.json',field);print('PASS conditional field-only host compile/scoped binding/Save/executable/storage/source freeze; no emulator')
if __name__=='__main__':prepare()
