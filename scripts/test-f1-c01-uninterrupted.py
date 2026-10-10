#!/usr/bin/env python3
"""One separately frozen uninterrupted opening, then conditional cold; no retries."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,resource,shutil,stat,struct,subprocess,time,traceback
ROOT=Path(__file__).resolve().parents[1]
BASE='b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae'
GAME='4a92a9de70848b9d7275f9f255bb0d2f53232ab8'
TREE='0fedd142f43f136ceee189c54101b095fc88f495'
BUILD=Path('/workspace/scratch/c01a-journal-art-r2-20261010/candidate-build')
ENGINE=BUILD/'source/engine'
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
ROM_SHA='79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246'
ELF_SHA='7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d'
DEFAULT=Path('/workspace/scratch/c01-uninterrupted-unprepared-r1-20261010')
SOURCE_ADMISSION=Path('/workspace/scratch/c01-uninterrupted-source-admission-20261010')
GiB=1024**3;MiB=1024**2
ENV=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(MiB),b''):h.update(block)
 return h.hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def storage():
 # Raw RGB worst case, BOTH complete traces even though field/battle are
 # disjoint, retained PNG+PPM, full logs, encoder cap and source/Save overhead.
 budgets={}
 for mode,frames,cap in [('opening',100000,12*GiB),('cold',6000,GiB)]:
  rows={'native_RGB_all_frames':frames*115200,'complete_field_trace':frames*3340,'complete_battle_trace':frames*1040,
    'index':frames*16,'two_logs':64*MiB,'256_PPM_and_PNG_captures':256*2*115500,'bounded_review_exports':(512 if mode=='opening' else 128)*MiB,
    'source_manifest_save_receipts_overhead':32*MiB}
  assert sum(rows.values())<cap
  budgets[mode]={'components':rows,'worst_case_bytes':sum(rows.values()),'limit_bytes':cap,'per_file_limit_bytes':2*GiB,'per_log_limit_bytes':32*MiB}
 return budgets
def binding_table(code,out):
 parser=module('co_elf',ROOT/'scripts/floor1/v01-battle-symbols.py');boundary=module('co_compiled',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
 rows=parser.elf_symbols(ENGINE/'pokeemerald.elf');functions=parser.functions(rows)
 aliases={'DccTestInputAction':('HandleInputChooseAction','battle_controller_player.o'),
  'DccTestInputMove':('HandleInputChooseMove','battle_controller_player.o'),'DccTestInputTarget':('HandleInputChooseTarget','battle_controller_player.o'),
  'Task_DisplayHPRestoredMessage':('Task_DisplayHPRestoredMessage','party_menu.o'),
  'coYesNo':('Task_HandleYesNoInput','script_menu.o'),'coStartTask':('Task_ShowStartMenu',None),
  'coStartInput':('HandleStartMenuInput','start_menu.o'),'coStartCursor':('sStartMenuCursorPos','start_menu.o'),
  'coSaveFn':('sSaveDialogCallback','start_menu.o'),'coConfirmSave':('SaveConfirmInputCallback','start_menu.o'),
  'coSaveSuccess':('SaveSuccessCallback','start_menu.o'),'coSaveReturn':('SaveReturnSuccessCallback','start_menu.o'),'coMenu':('sMenu','menu.o')}
 unused={'gDccCollectionProbe','gDccEquipmentProbe','gDccMembershipProbe','gDccRewardProbe'}
 names=set(re.findall(r'strcmp\(symbol,\s*"([^"]+)"',code))
 plans=module('co_binding_routes',ROOT/'scripts/floor1/continuous-opening-route.py').routes()
 for text in plans.values():
  for line in text.splitlines():
   if line.startswith('pages '):names.update(line.split()[2].split(','))
 proof={};table=[]
 for alias in sorted(names):
  name,scope=aliases.get(alias,(alias,None));hits=[r for r in rows if r['name']==name and r['index'] and (scope is None or r['scope']==scope)]
  if name in unused:assert not hits;proof[alias]={'present':False,'unreachable_historical_probe':True};continue
  assert len(hits)==1,('missing/ambiguous actual ELF binding',alias,hits)
  row=hits[0];value=row['value'];record=dict(row)
  if row['type']==2:
   identity=('L:'+row['scope']+':' if row['bind']==0 else 'G:')+name
   matches=[r for r in functions if identity in r['aliases']];assert len(matches)==1 and matches[0]['size']
   fn=matches[0];record['function_identity']=identity;record['compiled_SHA256']=hashlib.sha256(boundary.rom_bytes(ENGINE/'pokeemerald.elf',fn['address'],fn['size'])).hexdigest()
   # The original battle driver compares its already-masked callback to these
   # three aliases directly. Other callback checks mask both operands.
   if alias in ('DccTestInputAction','DccTestInputMove','DccTestInputTarget'):value&=~1
   record['effective_alias_address']=value
  elif name.startswith('DCC_'):
   data=boundary.rom_bytes(ENGINE/'pokeemerald.elf',value,1024);end=data.index(255)+1;record['native_text_SHA256']=hashlib.sha256(data[:end]).hexdigest()
  else:assert row['type'] in (0,1) and (row['type']==1 or name=='gMapGroups')
  proof[alias]=record;table.append(f'{value:08x} V {alias}')
 (out/'game.sym').write_text('\n'.join(table)+'\n');write(out/'actual-ELF-bindings-private.json',proof)
 return proof

def abi(out):
 source=ROOT/'scripts/floor1/continuous-opening-abi.c'
 pp=subprocess.check_output(['gcc','-E','-iquote','include','-iquote','src','-DMODERN=0','-I','tools/agbcc/include','-I','tools/agbcc','-nostdinc','-undef','-std=gnu89',str(source)],cwd=ENGINE)
 assembly=subprocess.check_output([str(TOOL/'tools/agbcc/bin/agbcc'),'-mthumb-interwork','-Wimplicit','-Wparentheses','-Werror','-O2','-fhex-asm','-o','-','-'],input=pp,cwd=ENGINE)
 (out/'native-ABI.s').write_bytes(assembly+b'\n.text\n\t.align\t2, 0\n');obj=out/'native-ABI.o'
 subprocess.run([str(TOOL/'usr/bin/arm-none-eabi-as'),'-mcpu=arm7tdmi','--defsym','MODERN=0','-o',str(obj),str(out/'native-ABI.s')],check=True)
 parser=module('co_abi',ROOT/'scripts/floor1/v01-battle-symbols.py');rows=parser.elf_symbols(obj);hits=[r for r in rows if r['name']=='continuousLayout'];assert len(hits)==1
 data=obj.read_bytes();head=struct.unpack_from('<16sHHIIIIIHHHHHH',data);sections=[struct.unpack_from('<10I',data,head[6]+i*head[11]) for i in range(head[12])];r=hits[0];sec=sections[r['index']];values=list(struct.unpack('<'+str(r['size']//4)+'I',data[sec[4]+r['value']:sec[4]+r['value']+r['size']]))
 assert values==[12,0,4,8,28,4,5,8,18,20,9,88,42,40,19,40,8],values
 return {'values':values,'assembly_SHA256':sha(out/'native-ABI.s'),'object_SHA256':sha(obj),'compile_only':True}

def verify_game():
 assert git('rev-parse','HEAD:engine')==TREE==git('rev-parse',GAME+':engine')
 subprocess.run(['git','diff','--quiet',GAME,'HEAD','--','engine'],cwd=ROOT,check=True)
 assert (BUILD/'tested-commit.txt').read_text().strip()==GAME
 assert sha(ENGINE/'pokeemerald.gba')==ROM_SHA and sha(ENGINE/'pokeemerald.elf')==ELF_SHA
 source_manifest=json.loads((BUILD/'source-inventory.json').read_text());post=json.loads((BUILD/'post-build-source-inventory.json').read_text())
 # Verify the retained accepted engine manifest, without rerunning its completed
 # source import/generation/Journal tests. Tracked source incl export EOL pins.
 checked=0
 for rel,expected in source_manifest.items():
  if rel.startswith('engine/'):
   assert post[rel]==expected and sha(BUILD/'source'/rel)==expected,('accepted compiled source',rel);checked+=1
 return {'engine_manifest_entries_rehashed':checked,'new_game_builds':0,'retained_manifest_SHA256':sha(BUILD/'source-inventory.json')}

def dependencies():
 paths=set(p for p in (ROOT/'scripts').rglob('*') if p.is_file() and p.suffix in ('.py','.c','.h','.route','.json'))
 paths.add(ROOT/'docs/floor1/c01-uninterrupted-unprepared-contract.md');paths.add(ROOT/'docs/evidence/floor1/g01e/verified-partial-live/fresh-trial/input.route')
 # All current reachable modules and inherited committed generators are covered.
 return {str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}

def prepare(out):
 assert not git('status','--porcelain'),'commit reviewed source/contract before preparing'
 assert not out.exists(),'new separately named preparation only'
 out.mkdir(parents=True)
 try:
  game=verify_game();old=json.loads(Path('/workspace/scratch/c01a-journal-admission-r3-20261010/freeze.json').read_text());tools=dict(old['tool_files']);tools[str(Path(shutil.which('ffmpeg')).resolve())]=sha(shutil.which('ffmpeg'));tools[str(Path(shutil.which('python3')).resolve())]=sha(shutil.which('python3'))
  for p,h in tools.items():assert sha(p)==h,('verified tooling changed',p)
  mgba=json.loads(Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/libmgba-identity.json').read_text());assert sha(mgba['path'])==mgba['SHA256']=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
  receipt=json.loads((SOURCE_ADMISSION/'admission-receipt.json').read_text())
  assert receipt['PASS'] and receipt['gameplay_processes']==0
  for rel,h in receipt['dependencies'].items():assert sha(ROOT/rel)==h,('final source admission dependency changed',rel)
  for rel,h in receipt['artifacts'].items():assert sha(SOURCE_ADMISSION/rel)==h,('final source admission evidence changed',rel)
  shutil.copyfile(SOURCE_ADMISSION/'final-offline.log',out/'offline.log')
  host=module('co_prepare_host',ROOT/'scripts/floor1/continuous-opening-host.py');code,base=host.generate(git);(out/'observer.c').write_text(code)
  with (out/'compile.log').open('w') as log:subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(out/'observer.c'),'-L'+str(TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(out/'observer')],stdout=log,stderr=subprocess.STDOUT,check=True)
  os.chmod(out/'observer',0o700);s=(out/'observer').lstat();executable={'SHA256':sha(out/'observer'),'owner_uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino}
  admission=module('co_exec_admission',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(out/'observer',executable)
  assert sha(out/'observer.c')==receipt['generated_host_SHA256']
  proof=binding_table(code,out);assert sha(out/'game.sym')==receipt['artifacts']['game.sym'],'final native binding table changed'
  native=receipt['native_ABI']
  for name in ('native-ABI.s','native-ABI.o'):shutil.copyfile(SOURCE_ADMISSION/name,out/name)
  plans=module('co_prepare_route',ROOT/'scripts/floor1/continuous-opening-route.py').routes()
  for mode,text in plans.items():
   assert text==(ROOT/('scripts/contracts/f1-c01-uninterrupted-'+mode+'.route')).read_text();(out/(mode+'.route')).write_text(text)
  budgets=storage();assert shutil.disk_usage(out).free>=13*GiB,'entire conservative opening+cold reservation unavailable'
  st=set(out.iterdir());files={str(p):sha(p) for p in st if p.is_file()}
  freeze={'helper_commit':git('rev-parse','HEAD'),'base':BASE,'compiled_game':GAME,'engine_tree':TREE,'ROM_SHA256':ROM_SHA,'ELF_SHA256':ELF_SHA,
   'output_directory':str(out),
   'inherited_generated_base_SHA256':base,'source_verification':game,'native_ABI':native,'binding_count':len(proof),'files':files,'dependencies':dependencies(),'tool_files':tools,
   'executable':executable,'executable_admission':admission,'storage':budgets,'reservation_bytes':13*GiB,'available_bytes_at_freeze':shutil.disk_usage(out).free,
   'opening_claims_allowed':1,'conditional_cold_claims_allowed':1,'first_failure_stop':True,'all_frames_captured':True,'chunk_frames':2000,'native_fps':'16777216/280896',
   'opening_frame_limit':100000,'cold_frame_limit':6000,'earlier_whole_battle_limits':36000,'Warden_whole_battle_limit':30000,'wall_limit_seconds':600,
   'cold_actual_Save_binding':'only after full opening/Save PASS','C01a_actual_counts_unchanged':[5,3,1,9],'C01a_consumed_claim_counts_unchanged':[6,3,1,10]}
  write(out/'freeze.json',freeze);print('PASS frozen actual source/build/ELF callbacks/ABI/tooling/observer/routes/offline guards/conservative storage; no emulator')
 except BaseException as error:
  (out/'preparation-errors.log').write_text(traceback.format_exc())
  write(out/'PREPARATION-STOP.json',{'exception':type(error).__name__,'reason':str(error),'emulators':0,'claims':0});raise

def admission(out,mode):
 f=json.loads((out/'freeze.json').read_text());assert not(out/'STOP.json').exists() and not(out/'PREPARATION-STOP.json').exists()
 assert str(out)==f['output_directory']==str(DEFAULT.resolve()),'one named output only'
 assert git('rev-parse','HEAD')==f['helper_commit'] and not git('status','--porcelain')
 verify_game()
 for rel,h in f['dependencies'].items():assert sha(ROOT/rel)==h,('source dependency changed',rel)
 for p,h in f['files'].items():assert sha(p)==h,('frozen observer/route file changed',p)
 for p,h in f['tool_files'].items():assert sha(p)==h,('frozen tool changed',p)
 module('co_run_exec',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(out/'observer',f['executable'])
 reserve=13*GiB if mode=='opening' else GiB;assert shutil.disk_usage(out).free>=reserve
 return f

def limits():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(2*GiB,2*GiB));os.umask(0o077)

def execute(out,mode):
 f=admission(out,mode);d=out/mode;d.mkdir()
 if mode=='opening':assert not(out/'cold').exists();(d/'game.sav').write_bytes(b'\xff'*131072);binding={'native_blank_flash':True,'input_SHA256':sha(d/'game.sav')}
 else:
  prior=json.loads((out/'opening-verdict-private.json').read_text());assert prior['PASS'];opening=out/'opening'
  model=module('co_run_disk',ROOT/'scripts/floor1/continuous-opening-state.py');final=model.snapshot(opening/'phase-17-state.bin');model.disk_equivalence(opening/'game.sav',final)
  shutil.copyfile(opening/'game.sav',d/'game.sav');shutil.copyfile(opening/'phase-17-state.bin',d/'expected-final-state.bin')
  binding={'actual_opening_Save_SHA256':sha(d/'game.sav'),'expected_actual_final_state_SHA256':sha(d/'expected-final-state.bin'),'source_guard_admitted_before_opening':True}
 write(d/'input-binding-private.json',binding)
 claim={'helper':f['helper_commit'],'mode':mode,'limit':1,'freeze_SHA256':sha(out/'freeze.json'),'binding_SHA256':sha(d/'input-binding-private.json'),'route_SHA256':sha(out/(mode+'.route')),'first_failure_stop':True}
 with (out/(mode+'-exclusive-claim.json')).open('x') as c:json.dump(claim,c,indent=2)
 before=sha(d/'game.sav');start=time.monotonic();process=None;failure=None
 try:
  with (out/(mode+'.route')).open() as inp,(d/'runtime.log').open('wb') as log,(d/'errors.log').open('wb') as err:
   process=subprocess.Popen([str(out/'observer'),str(ENGINE/'pokeemerald.gba'),str(d/'game.sav'),str(out/'game.sym'),mode],cwd=d,stdin=inp,stdout=log,stderr=err,env=ENV,preexec_fn=limits)
   write(d/'process-started.json',dict(pid=process.pid,mode=mode,helper=f['helper_commit'],exclusive_claim_SHA256=sha(out/(mode+'-exclusive-claim.json'))))
   while process.poll() is None:
    if time.monotonic()-start>600:failure='wall bound600 seconds';process.terminate();break
    if (d/'runtime.log').stat().st_size>32*MiB or (d/'errors.log').stat().st_size>32*MiB:failure='log32MiB bound';process.terminate();break
    total=sum(p.stat().st_size for p in d.iterdir() if p.is_file())
    if total>f['storage'][mode]['limit_bytes']:failure='storage bound';process.terminate();break
    time.sleep(.2)
   try:code=process.wait(timeout=5)
   except subprocess.TimeoutExpired:process.kill();code=process.wait();failure='process failed to terminate'
  log=(d/'runtime.log').read_text();footer=re.search(r'CONTINUOUS frames=(\d+) valid=(\d+) deferred=(\d+) attempts=(\d+) per-encounter=(\d+),(\d+),(\d+),(\d+)',log)
  assert not failure and code==0 and not(d/'errors.log').stat().st_size and footer and re.search(r'assertions=\d+\n$',log),'native host failure: '+str((failure,code,(d/'errors.log').read_text()[-1500:]))
  frames=int(footer[1]);assert (d/'frame-index.bin').stat().st_size==frames*16
  motion=sorted(d.glob('motion-*.rgb'));assert sum(p.stat().st_size for p in motion)==frames*115200 and all(p.stat().st_size<=230400000 for p in motion)
  model=module('co_actual_disk',ROOT/'scripts/floor1/continuous-opening-state.py')
  if mode=='opening':
   final=model.snapshot(d/'phase-17-state.bin');check=model.disk_equivalence(d/'game.sav',final);assert int(footer[4])==4 and 'PASS CONTINUOUS phase=save' in log
  else:
   final=model.snapshot(d/'current-state.bin');check=model.disk_equivalence(d/'game.sav',final);assert int(footer[4])==0 and sha(d/'game.sav')==before
  receipt={'PASS':True,'helper':f['helper_commit'],'mode':mode,'frames':frames,'phase_valid_field_snapshots':int(footer[2]),'deferred_frames':int(footer[3]),'battle_attempts':int(footer[4]),'battle_frames':list(map(int,footer.groups()[4:])),
   'actual_Save_SHA256':sha(d/'game.sav'),'source_guard_checks':check,'runtime_log_SHA256':sha(d/'runtime.log'),'raw_RGB_all_frames':True,'independent_backup_verified':False,'wall_seconds':time.monotonic()-start}
  write(out/(mode+'-verdict-private.json'),receipt);print('PASS '+mode+' '+str(frames)+' actual native frames')
 except BaseException as error:
  if process and process.poll() is None:process.terminate();process.wait(timeout=5)
  record={'mode':mode,'helper':f['helper_commit'],'error':type(error).__name__,'reason':str(error),'pid':process.pid if process else None,'actual_processes_started':1 if process else 0,'cold_admitted':False,'terminal_no_retry':True}
  write(out/'STOP.json',record);print(json.dumps(record));raise

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stage',choices=['prepare','opening','cold'],required=True);parser.add_argument('--output',type=Path,default=DEFAULT);a=parser.parse_args()
 assert a.output.resolve()==DEFAULT.resolve(),'separately approved named output only; no alternate output/retry'
 if a.stage=='prepare':prepare(a.output.resolve())
 else:execute(a.output.resolve(),a.stage)
if __name__=='__main__':main()
