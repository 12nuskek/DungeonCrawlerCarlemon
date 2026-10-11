"""Separately reviewed Howler2 wiring. Runtime requires new local admission.

Importing this module never freezes inputs, consumes claims or initializes a core.
Historical helpers and their closed offline admission remain unchanged.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,re,resource,shutil,signal,stat,struct,subprocess,sys,time
if not __debug__:raise RuntimeError('supervisor requires enabled checks')
ROOT=Path(__file__).resolve().parents[2]
SCRATCH=Path('/workspace/scratch')
OUT=SCRATCH/'c01-howler2-continuation-r1-20261011'
OFFLINE=SCRATCH/'c01-howler2-runtime-wiring-offline-r2-20261011'
AUTHORITY=SCRATCH/'c01-howler2-runtime-r1-authority.json'
ACCEPTED=SCRATCH/'c01-howler-continuation-correction-offline-r3-20261010'
REGISTRY=ROOT/'docs/evidence/floor1/c01/howler-continuation-offline-r2-20261010/offline-verification.json'
CONTRACT=ROOT/'scripts/contracts/f1-c01-howler2-contract.json'
HISTORICAL_CONTRACT=ROOT/'docs/floor1/c01-howler-continuation-offline-contract.md'
TESTED='86f6d88ed78700e4d21ac08690f87c0f3989b1d1'
PUBLICATION=TESTED
BASE='65bc4073d140b9d58bf1b83bd33235e28c972b23'
BRANCH='task/floor1-c01-howler-continuation-offline'
MODES=('howler-continuation','howler-new-save-cold')
WIRING=('scripts/floor1/howler2-runtime-supervisor.py','scripts/run-f1-c01-howler2-r1.py','scripts/test-howler2-runtime-wiring-offline.py','scripts/floor1/howler2-validator-closure.py')
COPY_FILES=('observer.c','observer','game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o')
PROOF=SCRATCH/'c01-medicine-transaction-offline-r3-20261010/reviewed-offsets-proof'
PROOFS={'transaction-proof-private.json':'7cbaee646dfc10b741a0b262b190f120d0284a2980c1ef872fa7784452aeb4f1','transaction-bindings.h':'623e3b3c6a1f478151e995a093dd3048a7b326d6e6d86be377e8ac927b7a0fa4'}


CORRECTION=SCRATCH/'c01-howler-step-predictor-offline-r2-20261010/offline-correction-receipt-private.json'
CORRECTION_SHA='70d4c2ca68c88cc377456fa2b8852c24425b4c0e305bf19fd3f432897f5d79dc'
HOWLER1=SCRATCH/'c01-howler-continuation-r1-20261010'
HOWLER1_AUTHORITY=SCRATCH/'c01-howler-runtime-r1-authority.json'
HOWLER1_READBACK=SCRATCH/'c01-howler-runtime-r1-post-STOP-private-readback-20261010.json'
HOWLER1_PINS={'authority':'61455b832ccf606914f1ae4b514154262c4d764d6c9e025647b40e757005f3f6',
    'freeze.json':'56b166b33a59d0cf544c94009f105c6dd3a8f122f36ed3294962cf813b6ca7a7',
    'STOP.json':'c150543d347bf59b9469041aef685bd6c228dfd55de068eb168fd5f8c75c3ab9',
    'howler-continuation-exclusive-claim.json':'d667d7ff540e737f901d6d000edde289eef9cf89a20cad8e18539811e50cf140',
    'readback':'c141b2edd5fb4bef25d70686791ad30b7047d8670e12653c9d3229a7b726fd89'}
NEW_SOURCE=set(WIRING)|{str(CONTRACT.relative_to(ROOT))}
RECEIPT_FILES={'correction-receipt.json':CORRECTION,'historical-helper-receipt.json':ACCEPTED/'offline-receipt.json'}

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
legacy=module('howler_supervisor_common',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
state=module('howler_supervisor_state',ROOT/'scripts/floor1/howler-continuation-state.py')
execfile=module('howler_supervisor_execfile',ROOT/'scripts/floor1/c01a-prefix-execfile.py')
validator=module('howler_supervisor_closure',ROOT/'scripts/floor1/howler2-validator-closure.py')
git=legacy.git
def require(value,reason):
    if not value:raise AssertionError(reason)
def sha(path):
    path=Path(path);info=path.lstat();require(stat.S_ISREG(info.st_mode) and not path.is_symlink(),'regular non-symlink operand')
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    after=path.lstat();stable=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns)
    require(stable(after)==stable(info),'operand changed during read');return h.hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    with Path(path).open('x') as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def validator_tools():
    interpreter=Path(sys.executable).resolve()
    selected=shutil.which('python3',path=execution_environment()['PATH']);require(selected,'native validator interpreter missing from PATH')
    require(Path(selected).resolve()==interpreter,'native validator interpreter selection')
    return validator.derive(execution_environment())['files']
def storage():
    old=legacy.storage();return {MODES[0]:old['opening'],MODES[1]:old['cold']}
def capacity(free):require(free>=10000408128,'full continuation/cold/headroom reservation unavailable')
def current_source(published=False):
    head=git('rev-parse','HEAD');require(not git('status','--porcelain'),'exact clean source required')
    require(git('merge-base',PUBLICATION,head)==PUBLICATION,'reviewed publication ancestry')
    if published:require(git('ls-remote','--heads','origin',BRANCH)==head+'\trefs/heads/'+BRANCH,'published exact branch head required')
    return head
def dependencies():
    pins=legacy.dependencies()
    for p in (CONTRACT,HISTORICAL_CONTRACT,REGISTRY,ROOT/'docs/floor1/accepted-plan.md'):
        pins[str(p.relative_to(ROOT))]=sha(p)
    return pins
def verify_dependency_inventory(actual,prior):
    require(set(actual)==set(prior)|NEW_SOURCE,'complete current dependency inventory')
    for rel,pin in prior.items():require(actual[rel]==pin,'accepted source dependency changed: '+rel)
def contract():
    value=read(CONTRACT)
    expected=dict(schema='c01-Howler2-source-contract/v1',native_modes=list(MODES),
        phases=['howler','howler-repeat','guide-howler','save'],trainer=857,
        continuation_frames=72000,encounter_frames=36000,cold_frames=6000,wall_seconds=600,
        route_budget_frames=70625,reservation_bytes=10000408128,claims_per_mode=1,
        physical_moves=34,counted_step_updates=32,ladder_transitions=2,
        friendship_counter_anchors=[78,94,110],final_poison_counter=0,
        original_Guard_Save_only=True,no_New_Game=True,conditional_cold_requires_actual_verified_manual_Save=True,
        first_failure_terminal=True,retry=False,maximum_earned_Potion_consumptions=1,
        policy_source='scripts/floor1/howler-continuation-integration.h',
        route_sources={m:'scripts/contracts/f1-c01-'+m+'.route' for m in MODES})
    require(value==expected,'exact Howler2 source contract')
    return value
def reviewed_tools():
    old=read(CORRECTION)['complete_current_tool_files']
    for p,h in old.items():require(sha(p)==h,'accepted correction tool changed')
    result=dict(old);result.update(validator_tools())
    return result

def scope(head):
    registry=read(REGISTRY);correction=read(CORRECTION)
    require(sha(CORRECTION)==CORRECTION_SHA,'accepted correction receipt identity')
    return dict(schema='c01-Continue-Howler2-857/v1',source_commit=head,base_commit=BASE,
        reviewed_helper_source=TESTED,reviewed_publication=PUBLICATION,output=str(OUT),modes=list(MODES),
        claims_per_mode=1,conditional_cold_requires_actual_Save=True,Save_SHA256=state.old.SAVE_SHA,
        original_snapshot_SHA256=state.old.ORIGINAL_SHA,accepted_receipt_SHA256=registry['private_receipt_SHA256'],
        correction_receipt_SHA256=CORRECTION_SHA,current_helper_pins=correction['current_helper_pins'],native_proof_pins=PROOFS,
        registry_SHA256=sha(REGISTRY),contract_SHA256=sha(CONTRACT),source_contract=contract(),
        observer_SHA256=correction['observer_SHA256'],generated_C_SHA256=correction['generated_C_SHA256'],
        build=registry['build_identity'],route_SHA256={mode:sha(ROOT/f'scripts/contracts/f1-c01-{mode}.route') for mode in MODES},
        continuation_frames=72000,encounter_frames=36000,cold_frames=6000,wall_seconds=600,
        storage=storage(),reservation_bytes=10000408128,first_failure_terminal=True,retry=False,
        no_New_Game=True,trainer=857,phases=['howler','howler-repeat','guide-howler','save'],
        ordinary_route=correction['step_source_proof'],actual_prior_history=claims(),
        complete_source_manifest_SHA256=hashlib.sha256(canonical(dependencies()).encode()).hexdigest(),
        complete_tool_manifest_SHA256=hashlib.sha256(canonical(reviewed_tools()).encode()).hexdigest(),
        validator_tool_manifest_SHA256=hashlib.sha256(canonical(validator_tools()).encode()).hexdigest())
def verify_scope(record,expected):require(canonical(record)==canonical(expected),'exact Howler scope mismatch')
def reviewed():
    registry=read(REGISTRY);r=read(ACCEPTED/'offline-receipt.json');c=read(CORRECTION)
    require(sha(CORRECTION)==CORRECTION_SHA and c['PASS'] and c['offline_only'] and not c['runtime_admission'],'accepted offline correction')
    require(c['tested_source_commit']==TESTED and c['source_status_at_start']=='','accepted clean correction source')
    require(c['counts']['physical_steps']==34 and c['counts']['ordinary_updates']==32 and c['counts']['ladder_transitions']==2,'corrected ordinary route')
    require(c['counts']['retained_phase_checks']==c['counts']['native_retained_phase_checks']==3 and c['counts']['exact_endpoint_counter_negatives']==127 and c['counts']['exact_endpoint_poison_negatives']==3 and c['counts']['retained_guide_byte_negatives']==3324,'accepted complete retained checks')
    require(len(c['current_helper_pins'])==13,'complete refreshed helper inventory')
    for rel,pin in c['current_helper_pins'].items():
        require(sha(ROOT/rel)==pin,'corrected helper changed')
        require(hashlib.sha256(subprocess.check_output(['git','show',TESTED+':'+rel],cwd=ROOT)).hexdigest()==pin,'accepted correction source mismatch')
    prior=c['complete_current_source_dependencies'];actual=dependencies()
    verify_dependency_inventory(actual,prior)
    require(set(git('diff','--name-only',TESTED,current_source()).splitlines())==NEW_SOURCE,'separate Howler2 wiring only')
    require(sha(ACCEPTED/'offline-receipt.json')==registry['private_receipt_SHA256'],'historical aggregate receipt identity')
    require(r['PASS'] and r['offline_only'] and r['tested_source_commit']=='7c2623ceddddd4fa5595293f4f61a8087bbe8587','inherited aggregate identity')
    for name,pin in r['artifacts'].items():require(sha(ACCEPTED/name)==pin,'accepted compiled artifact changed')
    require(r['storage']==legacy.storage() and r['reservation_bytes']==10000408128 and r['whole_route_budget']['total']==70625,'unchanged complete bounds')
    require(c['generated_C_SHA256']==r['generated_C_SHA256']==sha(ACCEPTED/'observer.c') and c['observer_SHA256']==r['observer_SHA256']==sha(ACCEPTED/'observer'),'unchanged compiled observer')
    for name,pin in PROOFS.items():require(sha(PROOF/name)==pin,'native transaction proof changed')
    require(read(PROOF/'transaction-proof-private.json')['ELF_SHA256']==legacy.ELF_SHA,'proof ELF identity')
    info=(ACCEPTED/'observer').lstat();execfile.verify_executable(ACCEPTED/'observer',dict(SHA256=c['observer_SHA256'],owner_uid=info.st_uid,mode=0o700))
    state.old.original(state.IMMUTABLE/'game.sav',state.IMMUTABLE/'phase-09-state.bin')
    tools=reviewed_tools();game=legacy.verify_game();require(game==c['build_verification']==r['build_verification'],'accepted game/source inventory changed')
    require(sha(legacy.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5')==registry['build_identity']['libmGBA_0_10_5_SHA256'],'library identity')
    contract();return r,tools,game
def claims():
    require(sha(HOWLER1_READBACK)==HOWLER1_PINS['readback'] and sha(HOWLER1_AUTHORITY)==HOWLER1_PINS['authority'],'immutable Howler1 history')
    for name in ('freeze.json','STOP.json','howler-continuation-exclusive-claim.json'):
        require(sha(HOWLER1/name)==HOWLER1_PINS[name],'Howler1 terminal record changed')
    frozen=read(HOWLER1/'freeze.json');records=dict(frozen['prior_claims']['files']);counts={'opening':0,'cold':0,'howler1':0}
    for path,pin in list(records.items()):
        require(sha(path)==pin,'prior opening/cold claim/start changed')
        if Path(path).name.endswith('-exclusive-claim.json'):
            claim=read(path);mode=claim['mode'];start_path=Path(path).parent/mode/'process-started.json';start=read(start_path)
            require(mode in ('opening','cold') and start['exclusive_claim_SHA256']==pin and start['helper']==claim['helper'],'prior actual claim/start binding')
            counts[mode]+=1
    claim_path=HOWLER1/'howler-continuation-exclusive-claim.json';start_path=HOWLER1/MODES[0]/'process-started.json'
    start=read(start_path);claim=read(claim_path);stop=read(HOWLER1/'STOP.json');readback=read(HOWLER1_READBACK)
    require(sha(start_path)==readback['complete_runtime_files']['howler-continuation/process-started.json']['SHA256'],'Howler1 actual process identity')
    require(start['exclusive_claim_SHA256']==sha(claim_path) and start['source_commit']==claim['source_commit']==frozen['source_commit'],'Howler1 claim/start/source binding')
    require(claim['freeze_SHA256']==sha(HOWLER1/'freeze.json') and frozen['authority_SHA256']==sha(HOWLER1_AUTHORITY),'Howler1 authority/freeze binding')
    require(claim['binding_SHA256']==sha(HOWLER1/MODES[0]/'input-binding-private.json'),'Howler1 original input binding')
    require(stop['PID']==start['pid'] and stop['actual_processes_started']==1 and stop['terminal_no_retry'] and stop['cleanup_error'] is None,'Howler1 actual terminal failure')
    errors=HOWLER1/MODES[0]/'errors.log'
    require(sha(errors)==readback['complete_runtime_files']['howler-continuation/errors.log']['SHA256'] and 'CONTINUOUS STOP reason=94 frame=12520 phase=4 encounters=1' in errors.read_text(),'Howler1 native STOP94 unchanged')
    counts['howler1']=1;require(counts=={'opening':5,'cold':2,'howler1':1},'actual historical counts changed')
    records.update({str(p):sha(p) for p in (HOWLER1_AUTHORITY,HOWLER1_READBACK,HOWLER1/'freeze.json',HOWLER1/'STOP.json',claim_path,start_path,HOWLER1/MODES[0]/'input-binding-private.json',errors)})
    # This namespace never counts, clears or amends a consumed Howler1 claim.
    return dict(counts=counts,process_counts=dict(counts),files=records,Howler1_terminal_no_retry=True,Howler1_native_STOP=dict(reason=94,frame=12520))
def no_active_process():
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:args=(p/'cmdline').read_bytes().split(b'\0')
        except OSError:continue
        if args and Path(args[0].decode(errors='replace')).name=='observer' and args[0].startswith(b'/workspace/scratch/'):
            raise AssertionError('existing native observer process')
def verify_authority(record,expected,receipt_hash):
    require(set(record)=={'schema','scope','wiring_receipt_SHA256','stages'},'complete separate runtime authority inventory')
    require(record['schema']=='separately-admitted-c01-howler2-runtime/v1' and record['stages']==['prepare',*MODES],'separate Howler2 stages unadmitted')
    verify_scope(record['scope'],expected);require(record['wiring_receipt_SHA256']==receipt_hash,'separate authority receipt mismatch')
def wiring_receipt():
    p=OFFLINE/'offline-admission-private.json';r=read(p);head=current_source()
    verify_wiring_record(r,head);return r
def verify_wiring_record(r,head):
    require(r['PASS'] and r['tested_source_commit']==head and r['runtime_actions_executed']==0,'exact offline wiring receipt required')
    require(set(r['wiring_files'])==set(WIRING),'complete wiring inventory')
    for name,pin in r['wiring_files'].items():require(sha(ROOT/name)==pin,'tested wiring source changed')
    validator.verify_manifest(validator_tools(),r['validator_tool_files'])
    verify_scope(r['scope'],scope(head))
def runtime_authority():
    require(AUTHORITY.is_file(),'CLOSED: separate runtime admission required before any mutation')
    head=current_source(published=True);r=wiring_receipt()
    verify_authority(read(AUTHORITY),scope(head),sha(OFFLINE/'offline-admission-private.json'))
    no_active_process();return head,r
def ensure_terminal_clear():require(not any((OUT/n).exists() for n in ('STOP.json','PREPARATION-STOP.json')),'terminal failure; no retry')
def prepare():
    head,_=runtime_authority();require(not OUT.exists(),'exclusive Howler output required')
    r,tools,game=reviewed();history=claims();capacity(shutil.disk_usage(SCRATCH).free)
    OUT.mkdir(mode=0o700)
    try:
        for name in COPY_FILES:shutil.copyfile(ACCEPTED/name,OUT/name);require(sha(OUT/name)==r['artifacts'][name],'reviewed copy mismatch')
        for mode in MODES:shutil.copyfile(ROOT/f'scripts/contracts/f1-c01-{mode}.route',OUT/(mode+'.route'))
        for name in PROOFS:shutil.copyfile(PROOF/name,OUT/name)
        for name,path in RECEIPT_FILES.items():shutil.copyfile(path,OUT/name)
        shutil.copyfile(CONTRACT,OUT/'execution-contract.json');shutil.copyfile(OFFLINE/'offline-admission-private.json',OUT/'wiring-receipt.json')
        shutil.copyfile(state.IMMUTABLE/'game.sav',OUT/'guard-input-verified-copy.sav')
        shutil.copyfile(state.IMMUTABLE/'phase-09-state.bin',OUT/'guard-original-saved-state.bin')
        state.old.original(OUT/'guard-input-verified-copy.sav',OUT/'guard-original-saved-state.bin')
        with (OUT/'source-checkpoint.tar').open('xb') as f:subprocess.run(['git','archive',head,'scripts',str(CONTRACT.relative_to(ROOT))],cwd=ROOT,stdout=f,check=True)
        require((OUT/'source-checkpoint.tar').stat().st_size<32*legacy.MiB,'source archive budget')
        os.chmod(OUT/'observer',0o700);info=(OUT/'observer').lstat()
        executable=dict(SHA256=r['observer_SHA256'],owner_uid=info.st_uid,mode=0o700,device=info.st_dev,inode=info.st_ino)
        execfile.verify_executable(OUT/'observer',executable);capacity(shutil.disk_usage(OUT).free)
        write(OUT/'freeze.json',dict(source_commit=head,scope=scope(head),files={p.name:sha(p) for p in OUT.iterdir()},dependencies=dependencies(),tool_files=tools,executable=executable,prior_claims=history,game=game,authority_SHA256=sha(AUTHORITY),available_bytes=shutil.disk_usage(OUT).free))
        check_root_usage()
    except BaseException as error:
        write(OUT/'PREPARATION-STOP.json',dict(reason=str(error),terminal_no_retry=True,claims=0));raise
def verify_frozen(f,expected):
    verify_scope(f['scope'],expected);require(f['source_commit']==expected['source_commit'],'frozen source mismatch')
    require(set(f['files'])==set(COPY_FILES)|set(PROOFS)|set(RECEIPT_FILES)|{mode+'.route' for mode in MODES}|{'execution-contract.json','wiring-receipt.json','guard-input-verified-copy.sav','guard-original-saved-state.bin','source-checkpoint.tar'},'complete frozen file inventory')
    require(f['dependencies']==dependencies(),'complete frozen source closure')
    accepted=read(ACCEPTED/'offline-receipt.json')
    known={name:accepted['artifacts'][name] for name in COPY_FILES}
    known.update(PROOFS);known.update({name:sha(path) for name,path in RECEIPT_FILES.items()});known.update({mode+'.route':expected['route_SHA256'][mode] for mode in MODES})
    known.update({'execution-contract.json':expected['contract_SHA256'],'wiring-receipt.json':sha(OFFLINE/'offline-admission-private.json'),
        'guard-input-verified-copy.sav':expected['Save_SHA256'],'guard-original-saved-state.bin':expected['original_snapshot_SHA256']})
    require(all(f['files'][name]==pin for name,pin in known.items()),'frozen reviewed identities waived')
    require(f['executable']['SHA256']==expected['observer_SHA256'],'frozen executable identity waived')
    for name,pin in f['files'].items():require(sha(OUT/name)==pin,'frozen input changed')
    for name,pin in f['dependencies'].items():require(sha(ROOT/name)==pin,'frozen source changed')
    for name,pin in f['tool_files'].items():require(sha(name)==pin,'frozen tool changed')
    require(f['authority_SHA256']==sha(AUTHORITY),'runtime authority changed')
    execfile.verify_executable(OUT/'observer',f['executable'])
def verify_lifecycle(mode,present):
    require(mode in MODES,'Howler modes only')
    require('STOP.json' not in present and 'PREPARATION-STOP.json' not in present,'terminal failure')
    require(mode not in present and mode+'-exclusive-claim.json' not in present,'claim/process already consumed')
    if mode==MODES[0]:require(not any(x in present for x in (MODES[1],MODES[1]+'-exclusive-claim.json')),'cold cannot precede continuation')
    else:require(all(x in present for x in (MODES[0],MODES[0]+'-exclusive-claim.json',MODES[0]+'-verdict-private.json')),'actual continuation required')
def admission(mode):
    head,_=runtime_authority();ensure_terminal_clear();verify_lifecycle(mode,{p.name for p in OUT.iterdir()})
    f=read(OUT/'freeze.json');verify_frozen(f,scope(head));r,tools,game=reviewed()
    require(tools==f['tool_files'] and game==f['game'],'reviewed tooling/build changed')
    for name,pin in f['prior_claims']['files'].items():require(sha(name)==pin,'prior actual claims changed')
    if mode==MODES[1]:verify_continuation_handoff(f)
    state.old.original(OUT/'guard-input-verified-copy.sav',OUT/'guard-original-saved-state.bin');check_root_usage();capacity(shutil.disk_usage(OUT).free);return f
def verify_continuation_handoff(f):
    d=OUT/MODES[0];v=read(OUT/(MODES[0]+'-verdict-private.json'))
    require(v['PASS'] and v['source_commit']==f['source_commit'] and v['mode']==MODES[0] and v['battle_attempts']==1,'successful actual Howler required')
    require(set(v['handoff_files'])=={'game.sav','runtime.log','errors.log','phase-03-state.bin'},'complete actual handoff inventory')
    for name,pin in v['handoff_files'].items():require(sha(d/name)==pin,'actual Save/state/log handoff changed')
    claim=OUT/(MODES[0]+'-exclusive-claim.json');start=read(d/'process-started.json')
    binding=sha(d/'input-binding-private.json')
    require(read(claim)['freeze_SHA256']==sha(OUT/'freeze.json') and read(claim)['binding_SHA256']==binding==v['input_binding_SHA256'] and start['exclusive_claim_SHA256']==sha(claim) and start['pid']==v['PID'],'actual freeze/claim/process binding')
    claim_record=read(claim)
    require(claim_record['source_commit']==start['source_commit']==f['source_commit'] and claim_record['mode']==start['mode']==MODES[0] and claim_record['limit']==1 and claim_record['terminal_on_failure'],'actual Howler2 source/mode/once-only claim')
    require(sha(d/'game.sav')!=state.old.SAVE_SHA,'actual newly saved continuation required')
    operand=read(d/'input-binding-private.json')
    require(operand==dict(input_Save_SHA256=state.old.SAVE_SHA,source_Save_SHA256=state.old.SAVE_SHA,actual_new_Save=False),'original Guard input only')
    state.disk_equivalence(d/'game.sav',state.snapshot(d/'phase-03-state.bin'))
    require('PASS CONTINUOUS phase=save' in (d/'runtime.log').read_text() and not(d/'errors.log').stat().st_size,'native manual Save success required')
    return v
def check_usage(directory,mode):
    rows=[]
    for p in directory.rglob('*'):
        info=p.lstat();require(not stat.S_ISLNK(info.st_mode),'output symlink')
        if p.is_file():rows.append((p,info.st_size,info.st_blocks*512))
    b=storage()[mode];require(max(sum(x[i] for x in rows) for i in (1,2))<=b['limit_bytes'],'complete process output bound')
    require(all(x[1]<=b['per_file_limit_bytes'] for x in rows),'per-file output bound')
    require(all(x[1]<=b['per_log_limit_bytes'] for x in rows if x[0].name.endswith('.log')),'per-log output bound')
    return dict(logical_bytes=sum(x[1] for x in rows),allocated_bytes=sum(x[2] for x in rows))
def check_root_usage():
    files=[]
    for p in OUT.iterdir():
        require(not p.is_symlink(),'root symlink')
        if p.is_dir():require(p.name in MODES,'unapproved runtime directory')
        else:require(p.is_file(),'regular root evidence');files.append(p)
    require(max(sum(p.stat().st_size for p in files),sum(p.stat().st_blocks*512 for p in files))<=256*legacy.MiB,'root source/evidence headroom bound')
    for mode in MODES:
        if (OUT/mode).exists():check_usage(OUT/mode,mode)
def parse_footer(log,mode):
    require(mode in MODES and log.count('CONTINUOUS frames=')==1,'one scoped native footer required')
    hits=re.findall(r'^CONTINUOUS frames=(\d+) valid=(\d+) deferred=(\d+) attempts=(\d+) per-encounter=(\d+),(\d+),(\d+),(\d+)\nresult=0 assertions=(\d+)\n\Z',log,re.M)
    require(len(hits)==1,'one complete native footer required');frames,valid,deferred,attempts,*rest=map(int,hits[0]);battle=rest[:4]
    require(0<frames<=(72000 if mode==MODES[0] else 6000) and valid+deferred==frames,'complete native frame bounds')
    require(attempts==(1 if mode==MODES[0] else 0) and battle[0]==battle[1]==battle[3]==0 and battle[2]<=36000,'only one Howler encounter')
    require((battle[2]>0)==(mode==MODES[0]),'actual encounter required only in continuation')
    require(rest[4]>0,'native assertions required')
    return dict(frames=frames,valid=valid,deferred=deferred,battle_attempts=attempts,battle_frames=battle,assertions=rest[4])
def verify_captures(d,footer,mode,uses):
    frames=footer['frames']
    raw=(d/'frame-index.bin').read_bytes();require(len(raw)==frames*16,'complete native index bytes')
    for i,values in enumerate(struct.iter_unpack('<4I',raw),1):require(values[0]==i and values[2] in (0,1) and values[3]<=(1 if mode==MODES[0] else 0),'native index order/encounters')
    chunks=sorted(d.glob('motion-*.rgb'));require([p.name for p in chunks]==[f'motion-{i:03}.rgb' for i in range((frames+1999)//2000)],'complete ordered motion chunks')
    for i,p in enumerate(chunks):require(p.stat().st_size==min(2000,frames-2000*i)*115200,'exact complete RGB chunk')
    log=(d/'runtime.log').read_text();captures=re.findall(r'^CAPTURE name=(\S+) absolute=(\d+) width=240 height=160$',log,re.M)
    names=[x[0] for x in captures];required=read(REGISTRY)['capture_ledger'][mode]+([f'medicine-01-{part}.ppm' for part in ('bag','recipient','healed')] if uses else [])
    require(set(names)==set(required) and len(names)==len(set(names)) and set(names)=={p.name for p in d.glob('*.ppm')},'exact named successful capture ledger')
    from PIL import Image,PpmImagePlugin
    require(Image.OPEN['PPM'][0] is PpmImagePlugin.PpmImageFile,'exact PPM decoder registration')
    for name,ordinal in captures:
        ordinal=int(ordinal);require(1<=ordinal<=frames,'capture frame range')
        with chunks[(ordinal-1)//2000].open('rb') as f:f.seek(((ordinal-1)%2000)*115200);rgb=f.read(115200)
        require((d/name).read_bytes()[:15]==b'P6\n240 160\n255\n','exact native P6 capture header')
        with Image.open(d/name,formats=['PPM']) as image:require(image.mode=='RGB' and image.size==(240,160) and image.convert('RGB').tobytes()==rgb,'named screenshot/native RGB equality')
    require((d/'complete-field-trace-private.bin').stat().st_size==footer['valid']*3340 and (d/'complete-battle-trace-private.bin').stat().st_size==sum(footer['battle_frames'])*1040,'complete trace record counts')
    return dict(native_frames=frames,RGB_bytes=frames*115200,index_SHA256=sha(d/'frame-index.bin'),motion_SHA256={p.name:sha(p) for p in chunks},named_captures={name:sha(d/name) for name in names})
def process_limits():
    os.umask(0o077);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(2*legacy.GiB,2*legacy.GiB))
def stop_process(process):
    if process is None:return
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:pass
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=5)
def execution_environment():
    env=dict(os.environ);env['LD_LIBRARY_PATH']=str(legacy.TOOL/'usr/lib/x86_64-linux-gnu');env['PATH']=str(Path(sys.executable).resolve().parent)+os.pathsep+os.defpath;env['PYTHONNOUSERSITE']='1';env['PYTHONDONTWRITEBYTECODE']='1'
    for name in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','LD_PRELOAD'):env.pop(name,None)
    return env
def execute(mode):
    head,_=runtime_authority();f=None;d=OUT/mode;process=None;started=time.monotonic()
    try:
        f=admission(mode);d.mkdir(mode=0o700)
        if mode==MODES[0]:source=OUT/'guard-input-verified-copy.sav'
        else:source=OUT/MODES[0]/'game.sav'
        shutil.copyfile(source,d/'game.sav');require(sha(d/'game.sav')==sha(source),'verified input copy')
        if mode==MODES[1]:shutil.copyfile(OUT/MODES[0]/'phase-03-state.bin',d/'expected-final-state.bin')
        binding=dict(input_Save_SHA256=sha(d/'game.sav'),source_Save_SHA256=sha(source),actual_new_Save=mode==MODES[1])
        if mode==MODES[1]:binding['expected_final_state_SHA256']=sha(d/'expected-final-state.bin')
        write(d/'input-binding-private.json',binding)
        claim=OUT/(mode+'-exclusive-claim.json');write(claim,dict(source_commit=f['source_commit'],mode=mode,freeze_SHA256=sha(OUT/'freeze.json'),binding_SHA256=sha(d/'input-binding-private.json'),route_SHA256=sha(OUT/(mode+'.route')),limit=1,terminal_on_failure=True))
        with (OUT/(mode+'.route')).open() as inp,(d/'runtime.log').open('xb') as log,(d/'errors.log').open('xb') as error:
            execfile.verify_executable(OUT/'observer',f['executable']);capacity(shutil.disk_usage(OUT).free)
            process=subprocess.Popen([str(OUT/'observer'),str(legacy.ENGINE/'pokeemerald.gba'),str(d/'game.sav'),str(OUT/'game.sym'),mode],cwd=d,stdin=inp,stdout=log,stderr=error,env=execution_environment(),preexec_fn=process_limits,start_new_session=True)
            write(d/'process-started.json',dict(pid=process.pid,mode=mode,source_commit=f['source_commit'],exclusive_claim_SHA256=sha(claim)))
            while process.poll() is None:
                require(time.monotonic()-started<=600,'wall600 seconds');check_root_usage();time.sleep(.05)
            require(process.wait()==0 and not(d/'errors.log').stat().st_size,'native process failure')
        check_root_usage();log=(d/'runtime.log').read_text();footer=parse_footer(log,mode);uses=0
        if mode==MODES[0]:
            phases=re.findall(r'^PASS CONTINUOUS phase=(\S+) ',log,re.M);require(phases==['howler','howler-repeat','guide-howler','save'],'complete ordered native phases')
            final=state.snapshot(d/'phase-03-state.bin');disk=state.disk_equivalence(d/'game.sav',final)
            require(sha(d/'game.sav')!=binding['input_Save_SHA256'],'genuine new manual Save required')
            require(sum(p.name.startswith('medicine-') and p.name.endswith('-order.bin') for p in d.iterdir())<=1,'one earned Potion bound')
            native=module('howler_runtime_medicine_audit',ROOT/'scripts/floor1/conserve-medicine-state.py');native.base.base.snapshot=state.snapshot;uses=len(native.audit(d));require(uses<=1,'one Potion bound')
        else:
            require(sha(d/'game.sav')==binding['input_Save_SHA256'],'cold cannot write Save')
            disk=state.cold_equivalence(state.snapshot(d/'expected-final-state.bin'),state.snapshot(d/'current-state.bin'),d/'game.sav')
        capture=verify_captures(d,footer,mode,uses)
        require(sha(state.IMMUTABLE/'game.sav')==state.old.SAVE_SHA and sha(OUT/'guard-input-verified-copy.sav')==state.old.SAVE_SHA,'immutable Guard Save changed')
        names=['game.sav','runtime.log','errors.log']+(['phase-03-state.bin'] if mode==MODES[0] else ['expected-final-state.bin','current-state.bin'])
        write(OUT/(mode+'-verdict-private.json'),dict(PASS=True,source_commit=f['source_commit'],mode=mode,PID=process.pid,**footer,medicine_consumptions=uses,full_disk_verification=disk,capture=capture,handoff_files={name:sha(d/name) for name in names},input_binding_SHA256=sha(d/'input-binding-private.json'),wall_seconds=time.monotonic()-started,independent_backup_verified=False))
    except BaseException as error:
        cleanup_error=None
        try:stop_process(process)
        except BaseException as cleanup:cleanup_error=str(cleanup)
        if OUT.exists() and not(OUT/'STOP.json').exists():write(OUT/'STOP.json',dict(mode=mode,source_commit=head,reason=str(error),cleanup_error=cleanup_error,PID=process.pid if process else None,actual_processes_started=int(process is not None),terminal_no_retry=True,cold_admitted=False))
        raise
