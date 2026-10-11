"""Prospective one-use Warden supervisor. Separate reviewed authority gates all writes.

Import, offline compilation and inert admission grant no runtime authority.
The accepted observer/state/route/policy are unchanged except the candidate's
single unconditional entry refusal, removed only in separately pinned tooling.
"""
from pathlib import Path
import fcntl,hashlib,importlib.util,json,os,re,resource,shutil,signal,struct,subprocess,sys,time
if not __debug__:raise RuntimeError('enabled full-state checks required')
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
b=module('warden_runtime_bindings',ROOT/'scripts/floor1/warden-runtime-bindings.py')
state=module('warden_native_state',ROOT/'scripts/floor1/warden-continuation-state.py')
storage_model=module('warden_storage',ROOT/'scripts/floor1/warden-continuation-admission.py')
execfile=module('warden_executable',ROOT/'scripts/floor1/c01a-prefix-execfile.py')
validator=module('warden_validator_closure',ROOT/'scripts/floor1/warden-runtime-validator-closure.py')
require,sha,read,git=b.require,b.sha,b.read,b.git
SCRATCH=b.SCRATCH
OUT=SCRATCH/'c01-warden-continuation-runtime-r1-20261011'
OFFLINE=SCRATCH/'c01-warden-supervisor-offline-r1-20261011'
AUTHORITY=SCRATCH/'c01-warden-runtime-r1-authority.json'
CONTRACT=ROOT/'scripts/contracts/f1-c01-warden-supervisor-r1.json'
BRANCH='task/floor1-c01-warden-continuation-offline'
MODES=('warden-continuation','warden-new-save-cold')
PHASES=['boss','boss-repeat','stairs-no','stairs-yes','checkpoint','save']
RESERVATION=17694519296
COPY_FILES=('observer.c','observer','game.sym','patrol-input-verified-copy.sav','expected-input-state.bin',
            'warden-continuation.route','warden-new-save-cold.route','source-contract.json','offline-admission-private.json')

def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(canonical(value).encode()).hexdigest()
def sync(directory):
    fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)
def write(path,value):
    with Path(path).open('x') as f:os.fchmod(f.fileno(),0o600);f.write(canonical(value)+'\n');f.flush();os.fsync(f.fileno())
    sync(Path(path).parent)
def capacity(free):require(type(free) is int and free>=RESERVATION,'STOP: full 17694519296-byte reservation before EACH process')
def storage():return storage_model.storage(134360,2044)

def contract():
    value=read(CONTRACT)
    expected=dict(schema='c01-Warden-exclusive-supervisor/v1',native_modes=list(MODES),phases=PHASES,
        trainer=858,continuation_frames=134360,encounter_frames=30000,cold_frames=2044,wall_seconds=600,
        reservation_bytes_before_each_process=RESERVATION,claims_per_mode=1,first_failure_terminal=True,retry=False,
        conditional_cold_requires_actual_complete_14_sector_manual_Save=True,native_Save_requires_overwrite_second_Yes=True,
        post_Continue_full_state_comparison=True,no_guide_healing_after_victory=True,no_New_Game_or_prior_encounter_replay=True,
        no_Floor_2_or_RNG_search=True,game_source=b.GAME_SOURCE,accepted_scaffold_source=b.TESTED,
        continuation_route_SHA256='5ace7218f7c095d757024d352296e668dc3872d6ea81eda37a626ba418f7b248',
        cold_route_SHA256='29400d7b31937b4f4c38231bbe8172e7c108b60ff9a908cdf4d5cd9253672fac')
    require(value==expected and storage()['reservation_bytes']==RESERVATION,'exact immutable Warden contract and full storage accounting')
    return value

def scope(head,receipt):
    return dict(schema='c01-Continue-Warden858/v1',source_commit=head,contract_SHA256=sha(CONTRACT),
        source_contract=contract(),accepted_scaffold_commit=b.TESTED,accepted_scaffold_receipt_SHA256=b.RECEIPT_SHA,
        accepted_scaffold_handoff_SHA256=b.HANDOFF_SHA,native_proof_SHA256=b.PROOF_SHA,
        runtime_output=str(OUT),claims_per_mode=1,source_manifest_SHA256=digest(receipt['source_files']),
        tool_manifest_SHA256=digest(receipt['tool_files']),observer_SHA256=receipt['candidate_artifacts']['observer'],
        observer_source_SHA256=receipt['candidate_artifacts']['observer.c'],route_SHA256=receipt['route_SHA256'],
        input_Save_SHA256=receipt['input_Save_SHA256'],input_state_SHA256=receipt['input_state_SHA256'],
        archive_representation=receipt['archive_representation'],storage=storage(),runtime_authority=False)

def authority_template(receipt):
    return dict(status='APPROVED_ONE_WARDEN_AND_CONDITIONAL_INDEPENDENT_COLD',source_commit=receipt['tested_source_commit'],
        offline_admission_SHA256=sha(OFFLINE/'offline-admission-private.json'),scope_SHA256=digest(receipt['scope']),
        output_root=str(OUT),execution_limit_per_mode=1,conditional_cold=True,runtime_authority=True,parent_review_verified=True)

def runtime_authority():
    require(AUTHORITY.is_file(),'CLOSED: separate exact runtime authority is absent; no freeze/claim/process')
    receipt=read(OFFLINE/'offline-admission-private.json');require(receipt['PASS'] and receipt['runtime_actions_executed']==0,'accepted offline wiring receipt required')
    require(read(AUTHORITY)==authority_template(receipt),'exact separately reviewed runtime authority')
    head=git('rev-parse','HEAD')
    require(not git('status','--porcelain') and head==receipt['tested_source_commit'],'exact clean admitted implementation source')
    require(git('branch','--show-current')==BRANCH and git('ls-remote','--heads','origin',BRANCH)==head+'\trefs/heads/'+BRANCH,'exact published implementation branch')
    return head,receipt

def verify_lifecycle(mode,present):
    require(mode in MODES,'Warden modes only')
    require(not {'STOP.json','PREPARATION-STOP.json'}&set(present),'first failure terminal; no retry')
    require(mode not in present and mode+'-exclusive-claim.json' not in present,'one-use mode already consumed')
    if mode==MODES[0]:require(not any(x in present for x in (MODES[1],MODES[1]+'-exclusive-claim.json')),'cold cannot precede continuation')
    else:require(all(x in present for x in (MODES[0],MODES[0]+'-exclusive-claim.json',MODES[0]+'-verdict-private.json')),'actual successful continuation required before cold')

def verify_frozen(f,receipt):
    require(set(f)=={'source_commit','scope','files','source_files','tool_files','executable','authority_SHA256'},'exact frozen record keys')
    require(f['source_commit']==receipt['tested_source_commit'] and f['scope']==scope(f['source_commit'],receipt)==receipt['scope'],'exact immutable source/scope binding')
    require(set(f['files'])==set(COPY_FILES)|{'source-checkpoint.tar'},'exact frozen file keys')
    require(f['source_files']==receipt['source_files'] and f['tool_files']==receipt['tool_files'],'exact source/provider sets; no subset waiver')
    require(f['authority_SHA256']==sha(AUTHORITY),'unchanged runtime authority')
    for name,pin in f['files'].items():require(sha(OUT/name)==pin,'frozen file changed: '+name)
    expected=dict(receipt['candidate_artifacts']);expected.update({'patrol-input-verified-copy.sav':receipt['input_Save_SHA256'],
        'expected-input-state.bin':receipt['input_state_SHA256'],'source-contract.json':sha(CONTRACT),
        'offline-admission-private.json':sha(OFFLINE/'offline-admission-private.json')})
    for mode,pin in receipt['route_SHA256'].items():expected[mode+'.route']=pin
    for name,pin in expected.items():require(f['files'][name]==pin,'exact frozen accepted artifact: '+name)
    require(f['executable']['SHA256']==receipt['candidate_artifacts']['observer'],'exact candidate executable pin')
    execfile.verify_executable(OUT/'observer',f['executable'])

def refresh(receipt):
    config,accepted=b.reviewed();b.verify_manifest(b.sources(config,accepted),receipt['source_files'])
    closure=validator.derive(b.environment(Path(config['tool_root'])))
    b.verify_manifest(closure['files'],receipt['validator_tool_files'])
    b.verify_manifest(b.tools(config,OFFLINE/'observer',closure),receipt['tool_files'])
    require(b.retention.verify_protected()==receipt['archive_representation'],'approved archive representation unchanged; no loose-frame restoration')
    expected=state.snapshot(config['patrol_state']);state.continue_equivalence(expected,expected,config['patrol_save'])
    return config

def prepare():
    head,receipt=runtime_authority() # Refuse before any write without separate authority.
    require(not os.path.lexists(OUT),'one exclusive fresh runtime preparation')
    config=refresh(receipt);capacity(shutil.disk_usage(SCRATCH).free)
    OUT.mkdir(mode=0o700);sync(OUT.parent)
    try:
        with (OUT/'exclusive.lock').open('x') as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            sources={name:OFFLINE/name for name in ('observer.c','observer','game.sym')}
            sources.update({'patrol-input-verified-copy.sav':Path(config['patrol_save']),'expected-input-state.bin':Path(config['patrol_state']),
                'source-contract.json':CONTRACT,'offline-admission-private.json':OFFLINE/'offline-admission-private.json'})
            sources.update({mode+'.route':OFFLINE/(mode+'.route') for mode in MODES})
            for name,path in sources.items():
                shutil.copyfile(path,OUT/name);os.chmod(OUT/name,0o700 if name=='observer' else 0o600)
                with (OUT/name).open('rb') as f:os.fsync(f.fileno())
            with (OUT/'source-checkpoint.tar').open('xb') as f:
                subprocess.run(['git','archive',head,'scripts','docs/floor1/c01-warden-supervisor-r1-contract.md'],cwd=ROOT,stdout=f,check=True,timeout=30);f.flush();os.fsync(f.fileno())
            require((OUT/'source-checkpoint.tar').stat().st_size<32*1024**2,'source checkpoint bound')
            info=(OUT/'observer').lstat();executable=dict(SHA256=receipt['candidate_artifacts']['observer'],owner_uid=info.st_uid,mode=0o700,device=info.st_dev,inode=info.st_ino)
            execfile.verify_executable(OUT/'observer',executable)
            frozen=dict(source_commit=head,scope=scope(head,receipt),files={name:sha(OUT/name) for name in (*COPY_FILES,'source-checkpoint.tar')},
                source_files=receipt['source_files'],tool_files=receipt['tool_files'],executable=executable,authority_SHA256=sha(AUTHORITY))
            write(OUT/'freeze.json',frozen);capacity(shutil.disk_usage(OUT).free);check_root_usage()
    except BaseException as error:
        if not (OUT/'PREPARATION-STOP.json').exists():write(OUT/'PREPARATION-STOP.json',dict(reason=str(error),terminal_no_retry=True,actual_processes=0,claims=0))
        raise

def verify_continuation_handoff(f):
    mode=MODES[0];directory=OUT/mode;v=read(OUT/(mode+'-verdict-private.json'))
    require(v['PASS'] and v['source_commit']==f['source_commit'] and v['mode']==mode and v['battle_attempts']==1 and v['full_14_sector_live_disk_verified'] is True,'actual complete native continuation/Save success required')
    require(set(v['handoff_files'])=={'game.sav','runtime.log','errors.log','phase-05-state.bin'},'complete actual manual-Save handoff')
    for name,pin in v['handoff_files'].items():require(sha(directory/name)==pin,'actual Save/state/log changed')
    claim_path=OUT/(mode+'-exclusive-claim.json');claim=read(claim_path);started=read(directory/'process-started.json')
    require(claim==dict(source_commit=f['source_commit'],mode=mode,freeze_SHA256=sha(OUT/'freeze.json'),binding_SHA256=sha(directory/'input-binding-private.json'),route_SHA256=f['scope']['route_SHA256'][mode],limit=1,terminal_on_failure=True),'actual exact one-use claim')
    require(started['pid']==v['PID'] and started['exclusive_claim_SHA256']==sha(claim_path) and started['source_commit']==f['source_commit'] and started['mode']==mode,'actual native process/claim/source binding')
    require(read(directory/'input-binding-private.json')==dict(input_Save_SHA256=f['scope']['input_Save_SHA256'],source_Save_SHA256=f['scope']['input_Save_SHA256'],actual_new_Save=False,
            source_state_SHA256=f['scope']['input_state_SHA256'],expected_state_SHA256=f['scope']['input_state_SHA256']),'original patrol Save/state input only')
    require(sha(directory/'game.sav')!=f['scope']['input_Save_SHA256'] and 'PASS CONTINUOUS phase=save' in (directory/'runtime.log').read_text() and not (directory/'errors.log').stat().st_size,'actual changed manual Save and successful callback')
    final=state.snapshot(directory/'phase-05-state.bin');state.disk_equivalence(directory/'game.sav',final,([35,4],[8,6]))
    require_wounded(final)
    return v

def require_wounded(final):
    members=[state.fields.decode(final['party'][i*100:(i+1)*100])['canonical'] for i in range(2)]
    hp=[struct.unpack_from('<HH',m,86) for m in members]
    require(all(current>0 for current,maximum in hp) and any(current<maximum for current,maximum in hp),'actual alive wounded party; no post-victory guide healing')

def admission(mode):
    head,receipt=runtime_authority();verify_lifecycle(mode,{p.name for p in OUT.iterdir()})
    frozen=read(OUT/'freeze.json');verify_frozen(frozen,receipt);refresh(receipt)
    require(frozen['source_commit']==head,'actual current frozen HEAD')
    if mode==MODES[1]:verify_continuation_handoff(frozen)
    check_root_usage();capacity(shutil.disk_usage(OUT).free)
    return frozen,receipt

def parse_footer(log,mode):
    require(mode in MODES and log.count('CONTINUOUS frames=')==1,'one scoped native footer')
    matches=re.findall(r'^CONTINUOUS frames=(\d+) valid=(\d+) deferred=(\d+) attempts=(\d+) per-encounter=(\d+),(\d+),(\d+),(\d+)\nresult=0 assertions=(\d+)\n\Z',log,re.M)
    require(len(matches)==1,'complete native footer/result/EOF')
    frames,valid,deferred,attempts,*rest=map(int,matches[0]);battle=rest[:4]
    require(0<frames<=(134360 if mode==MODES[0] else 2044) and valid+deferred==frames and rest[4]>0,'unchanged complete frame/assertion bounds')
    require(attempts==(1 if mode==MODES[0] else 0) and battle[:3]==[0,0,0] and 0<=battle[3]<=30000 and bool(battle[3])==(mode==MODES[0]),'only one trainer858 whole battle; no replay/other encounter')
    return dict(frames=frames,valid=valid,deferred=deferred,battle_attempts=attempts,battle_frames=battle,assertions=rest[4])

def verify_captures(directory,footer,mode):
    frames=footer['frames'];raw=(directory/'frame-index.bin').read_bytes()
    require(len(raw)==frames*16,'complete native index')
    for i,record in enumerate(struct.iter_unpack('<4I',raw),1):require(record[0]==i and record[2] in (0,1) and record[3]<=(1 if mode==MODES[0] else 0),'exact ordered index/cadence')
    chunks=sorted(directory.glob('motion-*.rgb'));require([p.name for p in chunks]==[f'motion-{i:03}.rgb' for i in range((frames+1999)//2000)],'complete native motion sequence')
    for i,path in enumerate(chunks):require(path.stat().st_size==min(2000,frames-2000*i)*115200,'complete RGB chunk bytes')
    log=(directory/'runtime.log').read_text();captures=re.findall(r'^CAPTURE name=(\S+) absolute=(\d+) width=240 height=160$',log,re.M)
    expected={'cold.ppm'}
    if mode==MODES[0]:
        expected.update(('warden-start.ppm','warden-result.ppm','stairs-no-choice.ppm','stairs-yes-choice.ppm','saved-success.ppm','saved.ppm'))
        pages=re.findall(r'^PASS native-pages messages=1 pages=(\d+)$',log,re.M)
        require(len(pages)==5 and all(1<=int(n)<=32 for n in pages),'unchanged five full bounded native page calls')
        for prefix,count in zip(('warden-resolved','stairs-no','stairs-cancelled','stairs-yes','opening-checkpoint'),pages):expected.update(f'{prefix}-00-{i:02}.ppm' for i in range(int(count)))
    require(len(captures)==len(expected) and {n for n,_ in captures}==expected=={p.name for p in directory.glob('*.ppm')},'exact successful capture ledger; no missing/extra/duplicate captures')
    from PIL import Image,PpmImagePlugin
    require(Image.OPEN['PPM'][0] is PpmImagePlugin.PpmImageFile,'exact native P6 decoder')
    for name,ordinal in captures:
        ordinal=int(ordinal);require(1<=ordinal<=frames,'actual capture ordinal')
        with chunks[(ordinal-1)//2000].open('rb') as f:f.seek(((ordinal-1)%2000)*115200);rgb=f.read(115200)
        require((directory/name).read_bytes()==b'P6\n240 160\n255\n'+rgb,'actual screenshot/raw native pixels')
        with Image.open(directory/name,formats=['PPM']) as image:require(image.mode=='RGB' and image.size==(240,160) and image.tobytes()==rgb,'decoder/native pixels exact')
    require((directory/'complete-field-trace-private.bin').stat().st_size==footer['valid']*3340 and (directory/'complete-battle-trace-private.bin').stat().st_size==sum(footer['battle_frames'])*1040,'unchanged complete field/battle trace accounting')
    return dict(frames=frames,index_SHA256=sha(directory/'frame-index.bin'),motion_SHA256={p.name:sha(p) for p in chunks},captures_SHA256={name:sha(directory/name) for name,_ in captures})

def check_root_usage():
    root_bytes=0;budgets=storage()['processes']
    for path in OUT.iterdir():
        require(not path.is_symlink(),'no runtime output aliases')
        if path.is_dir():
            require(path.name in MODES,'only two runtime mode directories')
            budget=budgets['continuation' if path.name==MODES[0] else 'cold'];files=[p for p in path.rglob('*') if p.is_file()]
            require(all(not p.is_symlink() for p in path.rglob('*')),'no process output links')
            require(max(sum(p.stat().st_size for p in files),sum(p.stat().st_blocks*512 for p in files))<=budget['bytes'],'unchanged complete per-process storage bound')
            require(all(p.stat().st_size<=budget['per_file_limit_bytes'] for p in files),'unchanged per-file bound')
            require(all(p.stat().st_size<=budget['per_log_bytes'] for p in files if p.name.endswith('.log')),'unchanged 64MiB logs')
        else:require(path.is_file(),'regular root evidence');root_bytes+=max(path.stat().st_size,path.stat().st_blocks*512)
    require(root_bytes<=256*1024**2,'unchanged source/working/headroom allowance')

def process_limits():
    os.umask(0o077);resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_FSIZE,(512*1024**2,512*1024**2))

def stop_process(process):
    if process is None:return
    try:os.killpg(process.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    try:process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:os.killpg(process.pid,signal.SIGKILL)
        except ProcessLookupError:pass
        process.wait(timeout=5)

def capacity_before_creation(path,mode,source_commit,process_factory,argv,**kwargs):
    # Allocate the immutable log block before measuring, so writing its small
    # record cannot consume preparation credit between the measure and spawn.
    with Path(path).open('xb') as file:
        os.fchmod(file.fileno(),0o600);os.posix_fallocate(file.fileno(),0,4096)
        free=shutil.disk_usage(OUT).free;capacity(free)
        data=(canonical(dict(fresh_available_bytes=free,required_bytes=RESERVATION,source_commit=source_commit,mode=mode,measured_time_ns=time.time_ns(),measured_immediately_before_creation=True,prepared_credit=False))+'\n').encode()
        require(len(data)<=4096,'capacity log fixed allocation')
        file.write(data);file.truncate();file.flush();os.fsync(file.fileno())
    sync(Path(path).parent)
    return process_factory(argv,**kwargs)

def execute(mode):
    head,_=runtime_authority();process=None;owned=False;started=time.monotonic()
    with (OUT/'exclusive.lock').open('r+') as lock:
        fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB);owned=True
        try:
            frozen,receipt=admission(mode);directory=OUT/mode;directory.mkdir(mode=0o700)
            source=OUT/'patrol-input-verified-copy.sav' if mode==MODES[0] else OUT/MODES[0]/'game.sav'
            shutil.copyfile(source,directory/'game.sav');require(sha(directory/'game.sav')==sha(source),'ordinary verified Save input copy')
            state_source=OUT/'expected-input-state.bin' if mode==MODES[0] else OUT/MODES[0]/'phase-05-state.bin'
            state_target=directory/('expected-input-state.bin' if mode==MODES[0] else 'expected-final-state.bin')
            shutil.copyfile(state_source,state_target);require(sha(state_target)==sha(state_source),'actual exact post-Continue/cold expected state copy')
            binding=dict(input_Save_SHA256=sha(source),source_Save_SHA256=sha(source),actual_new_Save=mode==MODES[1],source_state_SHA256=sha(state_source),expected_state_SHA256=sha(state_target))
            write(directory/'input-binding-private.json',binding)
            claim=OUT/(mode+'-exclusive-claim.json');write(claim,dict(source_commit=head,mode=mode,freeze_SHA256=sha(OUT/'freeze.json'),binding_SHA256=sha(directory/'input-binding-private.json'),route_SHA256=frozen['scope']['route_SHA256'][mode],limit=1,terminal_on_failure=True))
            config=read(b.CONFIG);rom=next(Path(p) for p in config['files'] if p.endswith('pokeemerald.gba'))
            with (OUT/(mode+'.route')).open('rb') as route,(directory/'runtime.log').open('xb') as log,(directory/'errors.log').open('xb') as error:
                execfile.verify_executable(OUT/'observer',frozen['executable'])
                process=capacity_before_creation(directory/'capacity-before-process-private.json',mode,head,subprocess.Popen,
                    [str(OUT/'observer'),str(rom),str(directory/'game.sav'),str(OUT/'game.sym'),mode],cwd=directory,stdin=route,stdout=log,stderr=error,
                    env=b.environment(Path(config['tool_root'])),preexec_fn=process_limits,start_new_session=True)
                write(directory/'process-started.json',dict(pid=process.pid,mode=mode,source_commit=head,exclusive_claim_SHA256=sha(claim),capacity_record_SHA256=sha(directory/'capacity-before-process-private.json')))
                while process.poll() is None:
                    require(time.monotonic()-started<=600,'unchanged600-second first-failure wall');check_root_usage();time.sleep(.05)
                require(process.wait()==0 and not (directory/'errors.log').stat().st_size,'native first failure terminal')
            log=(directory/'runtime.log').read_text();footer=parse_footer(log,mode)
            if mode==MODES[0]:
                require(re.findall(r'^PASS CONTINUOUS phase=(\S+) ',log,re.M)==PHASES,'all six exact native phases')
                final=state.snapshot(directory/'phase-05-state.bin');state.disk_equivalence(directory/'game.sav',final,([35,4],[8,6]));require_wounded(final)
                require(sha(directory/'game.sav')!=binding['input_Save_SHA256'],'actual new native manual overwrite Save')
            else:
                require(sha(directory/'game.sav')==binding['input_Save_SHA256'],'cold cannot write Save')
                state.cold_equivalence(state.snapshot(directory/'expected-final-state.bin'),state.snapshot(directory/'current-state.bin'),directory/'game.sav')
            captures=verify_captures(directory,footer,mode);check_root_usage()
            require(sha(config['patrol_save'])==receipt['input_Save_SHA256'] and sha(config['patrol_state'])==receipt['input_state_SHA256'],'original patrol Save/state retained')
            names=['game.sav','runtime.log','errors.log']+(['phase-05-state.bin'] if mode==MODES[0] else ['expected-final-state.bin','current-state.bin'])
            write(OUT/(mode+'-verdict-private.json'),dict(PASS=True,source_commit=head,mode=mode,PID=process.pid,**footer,full_14_sector_live_disk_verified=True,captures=captures,handoff_files={name:sha(directory/name) for name in names},wall_seconds=time.monotonic()-started,independent_backup_verified=False))
        except BaseException as error:
            stop_process(process)
            if owned and not (OUT/'STOP.json').exists():write(OUT/'STOP.json',dict(mode=mode,source_commit=head,reason=str(error),PID=process.pid if process else None,actual_processes_started=int(process is not None),terminal_no_retry=True,cold_admitted=False))
            raise
