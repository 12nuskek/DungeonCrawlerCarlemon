#!/usr/bin/env python3
"""Focused cold2 native-state/operand/admission rejection tests; no gameplay."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('cold2_test_gate',ROOT/'scripts/test-f1-c01-cold2-continue-r1.py')
state=gate.state;old=gate.OLD;out=gate.OFFLINE
counts={}
def reject(label,call):
 try:call()
 except (AssertionError,ValueError,KeyError,IndexError,struct.error,RuntimeError):counts[label]=counts.get(label,0)+1
 else:raise AssertionError('accepted negative: '+label)
def main():
 assert not out.exists() and not gate.OUT.exists(),'one new offline directory; runtime untouched'
 assert not gate.git('status','--porcelain'),'test exact clean committed source'
 before_status=gate.git('rev-parse','HEAD');out.mkdir(mode=0o700)
 # Cache the immutable source substructure table solely inside this offline mock.
 orders=state.base.fields.orders();state.base.fields.orders=lambda:orders
 saved=old/'opening/phase-09-state.bin';save=old/'opening/game.sav';retained=old/'cold/current-state.bin'
 before,disk=state.original(save,saved);after=state.base.snapshot(retained)
 assert state.validate(save,saved,retained)['PASS'] and disk['all14_sector_checksums']
 original=copy.deepcopy(before);observed=copy.deepcopy(after);expected=state.expected(before)
 assert before==original and after==observed and expected['flags'][274]==2
 assert expected['flags']!=before['flags'] and expected['flags'] is not before['flags']
 assert state.compare(before,after)['all_decoded_fields_exact']
 for bit in range(2400):
  bad=dict(after);flags=bytearray(after['flags']);flags[bit//8]^=1<<(bit%8);bad['flags']=bytes(flags)
  reject('all_flag_bits',lambda:state.compare(before,bad))
 for flag in (2193,2194):
  bad=dict(before);flags=bytearray(before['flags']);flags[flag//8]|=1<<(flag%8);bad['flags']=bytes(flags)
  reject('initial_TV_precondition',lambda:state.expected(bad))
 for key in ('party','saved','vars','logical'):
  for i in range(len(after[key])):
   bad=dict(after);value=bytearray(after[key]);value[i]^=1;bad[key]=bytes(value)
   reject('all_decoded_byte_fields',lambda:state.compare(before,bad))
 for key in ('counter','count','saved_count','group','mapnum','section','x','y','facing'):
  bad=dict(after);bad[key]+=1;reject('all_scalar_fields',lambda:state.compare(before,bad))
 for key in ('map','position'):
  for i in range(2):
   bad=dict(after);value=list(after[key]);value[i]+=1;bad[key]=value;reject('endpoint_vectors',lambda:state.compare(before,bad))
 for key in after:
  bad=dict(after);del bad[key];reject('decoded_inventory',lambda:state.compare(before,bad))
 bad=dict(after,extra=0);reject('decoded_inventory',lambda:state.compare(before,bad))
 raw=retained.read_bytes()
 with tempfile.TemporaryDirectory(dir=out) as temporary:
  temp=Path(temporary);sp=temp/'game.sav';bp=temp/'saved.bin';ap=temp/'observed.bin'
  def restore():sp.write_bytes(save.read_bytes());bp.write_bytes(saved.read_bytes());ap.write_bytes(raw)
  restore()
  for i in range(600):
   data=bytearray(raw);data[i]^=1;ap.write_bytes(data)
   reject('physical_party_checksum_bytes',lambda:state.validate(sp,bp,ap))
  for data in (raw[:-1],raw+b'\0',b''):
   ap.write_bytes(data);reject('malformed_snapshot_size',lambda:state.validate(sp,bp,ap))
  for i in range(3324):
   data=bytearray(saved.read_bytes());data[i]^=1;bp.write_bytes(data)
   reject('immutable_saved_snapshot_bytes',lambda:state.original(sp,bp))
  restore()
  for sid in range(14):
   data=bytearray(save.read_bytes());data[sid*4096+10]^=1;sp.write_bytes(data)
   reject('wrong_Save_each_sector',lambda:state.original(sp,bp))
  for data in (save.read_bytes()[:-1],b'\xff'*131072,b''):
   sp.write_bytes(data);reject('wrong_Save_shape_identity',lambda:state.original(sp,bp))
  # Existing canonical transform is involutive. Only mock encrypted keys vary.
  for key in (0,1,0x12345678,0xffffffff):
   data=bytearray(raw);struct.pack_into('<I',data,3284,key)
   data[900:2172]=state.base.prior.resources.canonical(after['logical'],struct.pack('<I',key))
   ap.write_bytes(data);parsed=state.base.snapshot(ap);assert state.compare(before,parsed)['native_canonical_resources_exact']
  for operand in (sp,bp,ap):
   restore();original_snapshot=state.base.snapshot
   def mutate_after_read(path):
    value=original_snapshot(path)
    if Path(path)==ap:
     data=bytearray(operand.read_bytes());data[0]^=1;operand.write_bytes(data)
    return value
   state.base.snapshot=mutate_after_read
   try:reject('operand_mutated_during_validation',lambda:state.validate(sp,bp,ap))
   finally:state.base.snapshot=original_snapshot
  restore();assert state.validate(sp,bp,ap)['PASS']
 gate.capacity(gate.RESERVATION);reject('storage_boundary',lambda:gate.capacity(gate.RESERVATION-1))
 record=gate.scope();gate.verify_scope(record)
 for key in record:
  bad=copy.deepcopy(record);del bad[key];reject('scope_inventory_and_identity',lambda:gate.verify_scope(bad))
  bad=copy.deepcopy(record);bad[key]='changed';reject('scope_inventory_and_identity',lambda:gate.verify_scope(bad))
 for path,value in [('RAM_derivation',{'flag':2193,'byte':274,'bit':2,'TV_START_initially_clear':False}),('first_failure_stop',1),('retry',0)]:
  bad=copy.deepcopy(record);bad[path]=value;reject('scope_inventory_and_identity',lambda:gate.verify_scope(bad))
 for mode in ('opening','cold2','prepare','',None):reject('execution_mode',lambda:gate.verify_mode(gate.OUT,mode))
 reject('output_identity',lambda:gate.verify_mode(gate.OUT.parent/'other','cold'))
 host=module('cold2_offline_host',ROOT/'scripts/floor1/cold2-continue-host.py');code,base=host.generate(gate.git)
 oldcode=(old/'observer.c').read_text()
 reconstructed=code.replace('if(argc!=5||strcmp(argv[4],"cold"))return 2;','if(argc!=5||(strcmp(argv[4],"opening")&&strcmp(argv[4],"cold")))return 2;').replace('python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/cold2-continue-state.py cold','python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/guard-choice-r2-state.py cold')
 assert reconstructed==oldcode,'exactly two authorized C changes; native observer/inputs/guards unchanged'
 (out/'observer.c').write_text(code)
 with (out/'compile.log').open('wb') as log:
  subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(gate.runner.TOOL/'usr/include'),str(out/'observer.c'),'-L'+str(gate.runner.TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(out/'observer')],stdout=log,stderr=subprocess.STDOUT,check=True)
 os.chmod(out/'observer',0o700)
 for mode in ('opening','cold2','prepare',''):
  run=subprocess.run([str(out/'observer'),'/missing-ROM','/missing-Save','/missing-symbols',mode],env=gate.runner.ENV,capture_output=True)
  assert run.returncode==2 and not run.stdout and not run.stderr;counts['compiled_pre_init_mode_rejection']=counts.get('compiled_pre_init_mode_rejection',0)+1
 run=subprocess.run([str(out/'observer'),'/missing-ROM','/missing-Save','/missing-symbols','cold'],env=gate.runner.ENV,capture_output=True)
 assert run.returncode==3 and not run.stdout and not run.stderr,'cold mode reaches missing-symbol check before emulator init'
 for script,args in [('scripts/test-f1-c01-cold2-continue-r1.py',['--stage','prepare']),('scripts/floor1/cold2-continue-state.py',['cold'])]:
  run=subprocess.run(['python3','-O',str(ROOT/script),*args],capture_output=True);assert run.returncode and b'cold2 requires enabled checks' in run.stderr;counts['optimized_check_rejection']=counts.get('optimized_check_rejection',0)+1
 for mode in ('opening','cold2','save'):
  run=subprocess.run(['python3',str(ROOT/'scripts/test-f1-c01-cold2-continue-r1.py'),'--stage',mode],capture_output=True);assert run.returncode==2;counts['CLI_mode_rejection']=counts.get('CLI_mode_rejection',0)+1
 source=gate.source_identity();tools=gate.tools_verified();history=gate.preserved();gate.capacity(__import__('shutil').disk_usage(out).free)
 # Exercise the same frozen-file and claim checks, against inert copied files.
 with tempfile.TemporaryDirectory(dir=out) as temporary:
  d=Path(temporary)
  receipt={'tested_commit':before_status,'artifacts':{'observer.c':gate.sha(out/'observer.c'),'observer':gate.sha(out/'observer')}}
  for name in ('observer.c','observer'):__import__('shutil').copyfile(out/name,d/name)
  for name in ('game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o'):__import__('shutil').copyfile(old/name,d/name)
  __import__('shutil').copyfile(ROOT/'scripts/contracts/f1-c01-guard-choice-cold.route',d/'cold.route')
  __import__('shutil').copyfile(gate.CONTRACT,d/'execution-contract.md')
  __import__('shutil').copyfile(save,d/'original-game.sav');__import__('shutil').copyfile(saved,d/'original-saved-state.bin')
  (d/'offline-admission-receipt.json').write_text('inert test receipt')
  (d/'source-checkpoint.tar').write_text('inert source archive')
  os.chmod(d/'observer',0o700);st=(d/'observer').lstat()
  f={'helper_commit':before_status,'base':gate.runner.BASE,'compiled_game':gate.runner.GAME,'engine_tree':gate.runner.TREE,'ROM_SHA256':gate.runner.ROM_SHA,'ELF_SHA256':gate.runner.ELF_SHA,'scope':record,
   'files':{q.name:gate.sha(q) for q in d.iterdir()},'dependencies':gate.dependencies(),'tool_files':tools,
   'executable':{'SHA256':gate.sha(d/'observer'),'owner_uid':st.st_uid,'mode':0o700,'device':st.st_dev,'inode':st.st_ino},'storage':gate.budget(),'reservation_bytes':gate.RESERVATION,'available_bytes_at_freeze':gate.RESERVATION,
   'source_identity':source,'preservation':history,'offline_tested_commit':before_status,'source_archive_SHA256':gate.sha(d/'source-checkpoint.tar'),'independent_backup_verified':False}
  frozen_receipt_hash=gate.sha
  # Test file uses a distinct receipt path; pin resolver has no runtime effect.
  def inert_sha(path):
   return frozen_receipt_hash(d/'offline-admission-receipt.json') if Path(path)==out/'admission-receipt.json' else frozen_receipt_hash(path)
  gate.sha=inert_sha
  try:
   gate.verify_frozen(f,receipt,d)
   for key in f:
    bad=copy.deepcopy(f);del bad[key];reject('frozen_inventory',lambda:gate.verify_frozen(bad,receipt,d))
   for key in ('base','compiled_game','engine_tree','ROM_SHA256','ELF_SHA256','reservation_bytes','storage','dependencies','offline_tested_commit','files','independent_backup_verified','source_archive_SHA256'):
    bad=copy.deepcopy(f);bad[key]='changed';reject('frozen_identity_bounds',lambda:gate.verify_frozen(bad,receipt,d))
   for key in f['executable']:
    bad=copy.deepcopy(f);bad['executable'][key]='changed' if key=='SHA256' else bad['executable'][key]+1;reject('executable_identity',lambda:gate.verify_frozen(bad,receipt,d))
   for name in f['files']:
    original_bytes=(d/name).read_bytes();(d/name).write_bytes(original_bytes+b'X')
    reject('all_frozen_file_hashes',lambda:gate.verify_frozen(f,receipt,d));(d/name).write_bytes(original_bytes)
   os.chmod(d/'observer',0o600);reject('executable_mode',lambda:gate.verify_frozen(f,receipt,d));os.chmod(d/'observer',0o700)
   gate.verify_admission_state(f,before_status,'',False,False,False)
   for args in [('changed','',False,False,False),(before_status,'dirty',False,False,False),(before_status,'',True,False,False),(before_status,'',False,True,False),(before_status,'',False,False,True)]:
    reject('consumed_claim_STOP_head',lambda:gate.verify_admission_state(f,*args))
  finally:gate.sha=frozen_receipt_hash
 assert not gate.OUT.exists() and gate.git('status','--porcelain')=='' and gate.git('rev-parse','HEAD')==before_status
 artifacts={p.name:gate.sha(p) for p in out.iterdir() if p.is_file()}
 receipt={'PASS':True,'tested_commit':before_status,'clean_status':'','gameplay_processes':0,'scope':record,'dependencies':gate.dependencies(),'artifacts':artifacts,'negative_checks':counts,'negative_checks_total':sum(counts.values()),'retained_transition_offline_PASS':True,'cold1_runtime_retroactive_PASS':False,'canonical_rekey_positives':4,'original14_sector_disk_PASS':disk,'source_identity':source,'tool_files':tools,'preservation':history,'generated_C_diff':'only pre-init cold-only mode guard and cold-validator command','inherited_generated_base_SHA256':base,'production_compile_PASS':True}
 gate.write(out/'admission-receipt.json',receipt)
 print(json.dumps({'PASS':True,'tested_commit':before_status,'negative_checks':counts,'negative_checks_total':sum(counts.values()),'gameplay_processes':0},indent=2))
if __name__=='__main__':main()
