#!/usr/bin/env python3
"""One separately frozen Continue-only cold2; immutable cold1 failure retained."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,shutil,stat,struct,subprocess,time,traceback
if not __debug__:raise RuntimeError('cold2 requires enabled checks; no output or process')
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01-cold2-continue-r1-20261010')
OLD=Path('/workspace/scratch/c01-conserve-medicine-opening5-r1-20261010')
OFFLINE=Path('/workspace/scratch/c01-cold2-continue-offline-r1-20261010')
CONTRACT=ROOT/'docs/floor1/c01-cold2-continue-r1-contract.md'
REGISTRY=ROOT/'docs/evidence/floor1/c01/cold2-continue-r1-20261010/reviewed-artifacts.json'
PUBLICATION='fb259f2addc71598e1fafffcf2d95d39b5d848ce'
BRANCH='task/floor1-c01-uninterrupted-unprepared'
OLD_MANIFEST='723046a77f8f5987b3935cbec9a59549a3449e762122027c58b3851c84682c15'
OLD_FREEZE='5c6cb0c82a70cb14c87257354349d753ee702c0f8070d7995151819e2372ad55'
ROUTE_SHA='d75f3b8943f7a4b1fddb7c363750fffcb32e94fd1a1823391f558d98f1f00b72'
SOURCE_PINS={'src/overworld.c':'f4517f3a29a42888529467bc623d63d2c264610bc75175f89d363700fe385864',
 'src/fieldmap.c':'4ea8660fe30317c60d399b0ed03ada44f36b55cf05d2ba48b97992bb9d9753c5',
 'src/tv.c':'a03c9b32feaa3bdb71da35e9aa69fe0acb9df27923d6cb24ab98bd028eb01efd',
 'include/constants/flags.h':'76df30b41e0072f9b6cae8b7fd7cc6251c51cf4d2aa03006f3282f185cc18654'}
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
runner=module('cold2_retained_runner',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
state=module('cold2_explicit_state',ROOT/'scripts/floor1/cold2-continue-state.py')
sha=runner.sha;git=runner.git;write=runner.write
ALLOCATION=894152512;RESERVATION=1162587968
def require(condition,reason):
 if not condition:raise AssertionError(reason)
def capacity(available):require(available>=RESERVATION,'full cold allocation plus256MiB unavailable')
def budget():
 b=runner.storage()['cold'];require(b['limit_bytes']==ALLOCATION,'unchanged cold allocation');return b
def scope():
 return {'schema':'c01-cold2-native-Continue/v1','reviewed_publication':PUBLICATION,
  'output_directory':str(OUT),'allowed_modes':['cold'],'cold_ordinal':2,'claims_allowed':1,
  'opening_claims_processes':[5,5],'prior_cold_claims_processes':[1,1],
  'Save_SHA256':state.SAVE_SHA,'original_snapshot_SHA256':state.ORIGINAL_SHA,
  'contract_SHA256':sha(CONTRACT),'route_SHA256':ROUTE_SHA,'source_pins':SOURCE_PINS,
  'ROM_SHA256':runner.ROM_SHA,'ELF_SHA256':runner.ELF_SHA,
  'library_SHA256':'a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63',
  'frame_limit':6000,'wall_seconds':600,'allocation_bytes':ALLOCATION,'reservation_bytes':RESERVATION,
  'chunk_frames':2000,'native_fps':'262144/4389','first_failure_stop':True,'retry':False,
  'disk_operand':'original saved snapshot','RAM_derivation':{'flag':2193,'byte':274,'bit':2,'TV_START_initially_clear':True}}
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def verify_scope(record):require(canonical(record)==canonical(scope()),'exact named cold2 scope changed')
def verify_mode(output,mode):require(Path(output).resolve()==OUT and mode=='cold','one named Continue-only output/mode')
def dependencies():
 d=runner.dependencies();d[str(CONTRACT.relative_to(ROOT))]=sha(CONTRACT);return d
def preserved():
 require(sha(OLD/'private-retention-manifest.json')==OLD_MANIFEST,'opening5/cold1 manifest changed')
 require(sha(OLD/'freeze.json')==OLD_FREEZE,'opening5/cold1 freeze changed')
 j=json.loads((OLD/'private-retention-manifest.json').read_text())
 for name,pin in j['entries'].items():
  p=OLD/name;require(p.stat().st_size==pin['bytes'] and sha(p)==pin['SHA256'],'preserved opening5/cold1 evidence changed: '+name)
 stop=json.loads((OLD/'STOP.json').read_text());require(stop['mode']=='cold' and stop['pid']==177954 and stop['terminal_no_retry'],'cold1 STOP96 remains terminal')
 require('96' in stop['reason'] and not(OLD/'cold-verdict-private.json').exists(),'cold1 original failure retained')
 for mode in ('opening','cold'):
  c=json.loads((OLD/(mode+'-exclusive-claim.json')).read_text());s=json.loads((OLD/mode/'process-started.json').read_text())
  require(c['freeze_SHA256']==OLD_FREEZE and s['exclusive_claim_SHA256']==sha(OLD/(mode+'-exclusive-claim.json')),'prior claim/process binding')
 state.original(OLD/'opening/game.sav',OLD/'opening/phase-09-state.bin')
 require(git('merge-base','--is-ancestor',PUBLICATION,'HEAD')=='','reviewed publication ancestry')
 return {'entries':len(j['entries']),'bytes':j['bytes'],'manifest_SHA256':OLD_MANIFEST,'cold1_STOP96_unchanged':True}
def source_identity():
 game=runner.verify_game()
 for name,pin in SOURCE_PINS.items():
  require(sha(ROOT/'engine'/name)==sha(runner.ENGINE/name)==pin,'native source changed: '+name)
 tv=(runner.ENGINE/'src/tv.c').read_text();field=(runner.ENGINE/'src/fieldmap.c').read_text();over=(runner.ENGINE/'src/overworld.c').read_text()
 require('FlagSet(FLAG_SYS_TV_WATCH);' in tv and 'else if (FlagGet(FLAG_SYS_TV_START)' in tv and 'FlagClear(FLAG_SYS_TV_WATCH);' in tv,'TV source lifecycle')
 require('InitMapFromSavedGame();' in over and 'UpdateTVScreensOnMap(gBackupMapLayout.width, gBackupMapLayout.height);' in field,'source Continue chain')
 boundary=module('cold2_compiled_boundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
 rows=boundary.symbols.functions(boundary.symbols.elf_symbols(runner.ENGINE/'pokeemerald.elf'));functions={}
 for name in ('CB2_ContinueSavedGame','InitMapFromSavedGame','UpdateTVScreensOnMap','FlagSet','FlagGet'):
  matches=[r for r in rows if 'G:'+name in r['aliases']];require(len(matches)==1 and matches[0]['size'],'compiled lifecycle function '+name)
  row=matches[0];raw=boundary.rom_bytes(runner.ENGINE/'pokeemerald.elf',row['address'],row['size'])
  functions[name]={'address':row['address'],'size':row['size'],'SHA256':hashlib.sha256(raw).hexdigest()}
 def calls(caller,callee):
  r=functions[caller];raw=boundary.rom_bytes(runner.ENGINE/'pokeemerald.elf',r['address'],r['size'])
  return [r['address']+i for i in range(0,len(raw)-3,2) if boundary.thumb_bl(r['address']+i,raw[i:i+4])==functions[callee]['address']]
 require(len(calls('CB2_ContinueSavedGame','InitMapFromSavedGame'))==1,'compiled Continue -> map')
 require(len(calls('InitMapFromSavedGame','UpdateTVScreensOnMap'))==1,'compiled map -> TV')
 tvaddr=functions['UpdateTVScreensOnMap']['address'];raw=boundary.rom_bytes(runner.ENGINE/'pokeemerald.elf',tvaddr,136)
 require(raw[6:8]==b'\x0b\x48' and struct.unpack_from('<I',raw,52)[0]==2193 and calls('UpdateTVScreensOnMap','FlagSet')==[tvaddr+8],'compiled entry FlagSet2193 literal/call')
 require(raw[60:62]==b'\x10\x48' and struct.unpack_from('<I',raw,128)[0]==2194 and calls('UpdateTVScreensOnMap','FlagGet')==[tvaddr+62] and raw[70:72]==b'\x18\xd0','compiled TV_START2194 gate')
 return dict(game,source_SHA256=SOURCE_PINS,compiled_functions=functions,compiled_chain_and_flag_literals_verified=True)
def tools_verified():
 f=json.loads((OLD/'freeze.json').read_text());tools=f['tool_files']
 for p,h in tools.items():require(sha(p)==h,'retained tool changed: '+p)
 require(sha(runner.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5')==scope()['library_SHA256'],'unchanged library')
 return tools
def receipt_verified():
 j=json.loads((OFFLINE/'admission-receipt.json').read_text())
 registry=json.loads(REGISTRY.read_text())
 require(registry=={'tested_commit':j['tested_commit'],'receipt_SHA256':sha(OFFLINE/'admission-receipt.json'),'artifacts':j['artifacts'],'scope':j['scope']},'published offline identity registry')
 require(hashlib.sha256(subprocess.check_output(['git','show','HEAD:'+str(REGISTRY.relative_to(ROOT))],cwd=ROOT)).hexdigest()==sha(REGISTRY),'registry must be published at clean HEAD')
 require(j['PASS'] and j['gameplay_processes']==0 and j['clean_status']=='','clean exact offline checks required')
 require(j['scope']==scope() and j['dependencies']==dependencies(),'tested contract/helper/dependencies changed')
 for rel,h in j['dependencies'].items():
  require(hashlib.sha256(subprocess.check_output(['git','show',j['tested_commit']+':'+rel],cwd=ROOT)).hexdigest()==h,'tested source commit mismatch: '+rel)
 for rel,h in j['artifacts'].items():require(sha(OFFLINE/rel)==h,'tested artifact changed: '+rel)
 host=module('cold2_frozen_host',ROOT/'scripts/floor1/cold2-continue-host.py');code,_=host.generate(git)
 require(hashlib.sha256(code.encode()).hexdigest()==j['artifacts']['observer.c'],'generated observer changed')
 return j
def freeze_files_expected(receipt):
 names={'observer.c':receipt['artifacts']['observer.c'],'observer':receipt['artifacts']['observer']}
 for name in ('game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o'):names[name]=sha(OLD/name)
 names.update({'cold.route':ROUTE_SHA,'execution-contract.md':sha(CONTRACT),'offline-admission-receipt.json':sha(OFFLINE/'admission-receipt.json'),'original-game.sav':state.SAVE_SHA,'original-saved-state.bin':state.ORIGINAL_SHA})
 return names
def verify_frozen(f,receipt,directory=OUT):
 require(set(f)=={'helper_commit','base','compiled_game','engine_tree','ROM_SHA256','ELF_SHA256','scope','files','dependencies','tool_files','executable','storage','reservation_bytes','available_bytes_at_freeze','source_identity','preservation','offline_tested_commit','source_archive_SHA256','independent_backup_verified'},'frozen identity inventory')
 verify_scope(f['scope'])
 require((f['base'],f['compiled_game'],f['engine_tree'],f['ROM_SHA256'],f['ELF_SHA256'])==(runner.BASE,runner.GAME,runner.TREE,runner.ROM_SHA,runner.ELF_SHA),'frozen compiled game identity')
 require(f['storage']==budget() and f['reservation_bytes']==RESERVATION and f['independent_backup_verified'] is False,'frozen cold bounds')
 require(f['dependencies']==dependencies() and f['offline_tested_commit']==receipt['tested_commit'],'frozen tested dependencies')
 names=freeze_files_expected(receipt);names['source-checkpoint.tar']=f['source_archive_SHA256']
 require(f['files']==names,'frozen file identity inventory/values')
 for name,h in names.items():require(sha(directory/name)==h,'frozen file changed: '+name)
 for rel,h in f['dependencies'].items():require(sha(ROOT/rel)==h,'frozen dependency changed: '+rel)
 for p,h in f['tool_files'].items():require(sha(p)==h,'frozen tool changed: '+p)
 require(f['executable']['SHA256']==names['observer'],'frozen executable hash')
 module('cold2_execfile',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(directory/'observer',f['executable'])
def verify_admission_state(f,head,dirty,claim_exists,directory_exists,stop_exists):
 require(not stop_exists,'terminal STOP, no retry')
 require(not claim_exists and not directory_exists,'cold2 claim/process consumed')
 require(not dirty and f['helper_commit']==head,'exact clean frozen published helper')
def published_clean():
 require(not git('status','--porcelain') and git('branch','--show-current')==BRANCH,'publish clean named branch')
 head=git('rev-parse','HEAD');remote=git('ls-remote','--heads','origin','refs/heads/'+BRANCH).split()
 require(len(remote)==2 and remote[0]==head,'publish exact helper before freeze/claim');return head
def prepare():
 require(not OUT.exists(),'existing cold2 output is terminal')
 head=published_clean();capacity(shutil.disk_usage(OUT.parent).free)
 history=preserved();source=source_identity();tools=tools_verified();receipt=receipt_verified()
 capacity(shutil.disk_usage(OUT.parent).free);OUT.mkdir(mode=0o700)
 for name in ('observer.c','observer'):shutil.copyfile(OFFLINE/name,OUT/name)
 for name in ('game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o'):shutil.copyfile(OLD/name,OUT/name)
 shutil.copyfile(ROOT/'scripts/contracts/f1-c01-guard-choice-cold.route',OUT/'cold.route')
 shutil.copyfile(CONTRACT,OUT/'execution-contract.md');shutil.copyfile(OFFLINE/'admission-receipt.json',OUT/'offline-admission-receipt.json')
 shutil.copyfile(OLD/'opening/game.sav',OUT/'original-game.sav');shutil.copyfile(OLD/'opening/phase-09-state.bin',OUT/'original-saved-state.bin')
 state.original(OUT/'original-game.sav',OUT/'original-saved-state.bin')
 with (OUT/'source-checkpoint.tar').open('wb') as archive:subprocess.run(['git','archive','HEAD','scripts',str(CONTRACT.relative_to(ROOT))],cwd=ROOT,stdout=archive,check=True)
 require((OUT/'source-checkpoint.tar').stat().st_size<32*runner.MiB,'source budget')
 os.chmod(OUT/'observer',0o700);s=(OUT/'observer').lstat()
 f={'helper_commit':head,'base':runner.BASE,'compiled_game':runner.GAME,'engine_tree':runner.TREE,'ROM_SHA256':runner.ROM_SHA,'ELF_SHA256':runner.ELF_SHA,'scope':scope(),
  'files':{p.name:sha(p) for p in OUT.iterdir()},'dependencies':dependencies(),'tool_files':tools,
  'executable':{'SHA256':sha(OUT/'observer'),'owner_uid':s.st_uid,'mode':stat.S_IMODE(s.st_mode),'device':s.st_dev,'inode':s.st_ino},
  'storage':budget(),'reservation_bytes':RESERVATION,'available_bytes_at_freeze':shutil.disk_usage(OUT).free,'source_identity':source,'preservation':history,
  'offline_tested_commit':receipt['tested_commit'],'source_archive_SHA256':sha(OUT/'source-checkpoint.tar'),'independent_backup_verified':False}
 verify_frozen(f,receipt);capacity(shutil.disk_usage(OUT).free);write(OUT/'freeze.json',f)
 print('PASS cold2 freeze; no claim or emulator')
def admission(output,mode):
 verify_mode(output,mode)
 f=json.loads((OUT/'freeze.json').read_text())
 verify_admission_state(f,published_clean(),git('status','--porcelain'),(OUT/'cold-exclusive-claim.json').exists(),(OUT/'cold').exists(),(OUT/'STOP.json').exists() or (OUT/'PREPARATION-STOP.json').exists())
 receipt=receipt_verified();verify_frozen(f,receipt)
 require(f['source_identity']==source_identity() and f['preservation']==preserved() and f['tool_files']==tools_verified(),'source/tools/history changed')
 state.original(OUT/'original-game.sav',OUT/'original-saved-state.bin');capacity(shutil.disk_usage(OUT).free);return f
def execute():
 f=admission(OUT,'cold');d=OUT/'cold';d.mkdir(mode=0o700)
 shutil.copyfile(OUT/'original-game.sav',d/'game.sav');shutil.copyfile(OUT/'original-saved-state.bin',d/'expected-final-state.bin')
 state.original(d/'game.sav',d/'expected-final-state.bin')
 binding={'Save_SHA256':sha(d/'game.sav'),'original_snapshot_SHA256':sha(d/'expected-final-state.bin'),'expected_RAM_derivation':scope()['RAM_derivation'],'disk_operand':'original saved snapshot'}
 write(d/'input-binding-private.json',binding)
 claim={'helper':f['helper_commit'],'mode':'cold','ordinal':2,'limit':1,'freeze_SHA256':sha(OUT/'freeze.json'),'binding_SHA256':sha(d/'input-binding-private.json'),'route_SHA256':ROUTE_SHA,'first_failure_stop':True}
 with (OUT/'cold-exclusive-claim.json').open('x') as c:json.dump(claim,c,indent=2)
 started=time.monotonic();process=None;failure=None
 try:
  with (OUT/'cold.route').open() as inp,(d/'runtime.log').open('wb') as log,(d/'errors.log').open('wb') as err:
   process=subprocess.Popen([str(OUT/'observer'),str(runner.ENGINE/'pokeemerald.gba'),str(d/'game.sav'),str(OUT/'game.sym'),'cold'],cwd=d,stdin=inp,stdout=log,stderr=err,env=runner.ENV,preexec_fn=runner.limits)
   write(d/'process-started.json',{'pid':process.pid,'mode':'cold','ordinal':2,'helper':f['helper_commit'],'exclusive_claim_SHA256':sha(OUT/'cold-exclusive-claim.json')})
   while process.poll() is None:
    if time.monotonic()-started>600:failure='wall600 seconds'
    elif any((d/n).stat().st_size>32*runner.MiB for n in ('runtime.log','errors.log')):failure='log32MiB bound'
    elif sum(p.stat().st_size for p in d.iterdir() if p.is_file())>ALLOCATION:failure='cold storage bound'
    if failure:process.terminate();break
    time.sleep(.2)
   try:code=process.wait(timeout=5)
   except subprocess.TimeoutExpired:process.kill();code=process.wait();failure='failed to terminate'
  log=(d/'runtime.log').read_text();footer=re.search(r'CONTINUOUS frames=(\d+) valid=(\d+) deferred=(\d+) attempts=(\d+) per-encounter=(\d+),(\d+),(\d+),(\d+)',log)
  require(not failure and code==0 and not(d/'errors.log').stat().st_size and footer and re.search(r'assertions=\d+\n$',log),'native cold2 failure: '+str((failure,code,(d/'errors.log').read_text()[-1800:])))
  frames=int(footer[1]);require(0<frames<=6000 and int(footer[4])==0 and not any(map(int,footer.groups()[4:])),'cold frames/no encounters')
  require((d/'frame-index.bin').stat().st_size==frames*16 and sum(p.stat().st_size for p in d.glob('motion-*.rgb'))==frames*115200,'complete indexed raw frames')
  result=state.validate(d/'game.sav',d/'expected-final-state.bin',d/'current-state.bin')
  require(sha(OUT/'original-game.sav')==state.SAVE_SHA and sha(OLD/'opening/game.sav')==state.SAVE_SHA,'original Save unchanged')
  receipt={'PASS':True,'helper':f['helper_commit'],'mode':'cold','ordinal':2,'PID':process.pid,'frames':frames,'field_frames':int(footer[2]),'deferred_frames':int(footer[3]),'battle_attempts':0,'battle_frames':[0,0,0,0],'state_verification':result,'Save_SHA256':sha(d/'game.sav'),'runtime_log_SHA256':sha(d/'runtime.log'),'all_raw_native_frames':True,'wall_seconds':time.monotonic()-started,'independent_backup_verified':False}
  write(OUT/'cold-verdict-private.json',receipt);print('PASS cold2 '+str(frames)+' actual native frames')
 except BaseException as error:
  if process and process.poll() is None:process.terminate();process.wait(timeout=5)
  write(OUT/'STOP.json',{'mode':'cold','ordinal':2,'helper':f['helper_commit'],'error':type(error).__name__,'reason':str(error),'PID':process.pid if process else None,'actual_processes_started':1 if process else 0,'terminal_no_retry':True});raise
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','cold'],required=True);a=p.parse_args()
 try:prepare() if a.stage=='prepare' else execute()
 except BaseException as error:
  if OUT.exists() and not(OUT/'STOP.json').exists() and not(OUT/'PREPARATION-STOP.json').exists():
   write(OUT/('PREPARATION-STOP.json' if a.stage=='prepare' else 'STOP.json'),{'stage':a.stage,'reason':str(error),'terminal_no_retry':True,'claims_added_by_error_handler':0})
   (OUT/'launcher-errors.log').write_text(traceback.format_exc())
  raise
if __name__=='__main__':main()
