#!/usr/bin/env python3
"""One bounded inert Warden supervisor admission. Candidate observer is never run."""
from pathlib import Path
import ast,copy,fcntl,hashlib,importlib.util,json,os,resource,signal,struct,subprocess,time
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('warden_offline_wiring',ROOT/'scripts/floor1/warden-runtime-supervisor.py')
w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
OUT=w.OFFLINE
REVIEW=w.SCRATCH/'c01-warden-supervisor-source-review-r1-20261011.json'
CAP=64*1024**2

def deadline(*_):raise TimeoutError('one bounded offline admission240 seconds')

def main():
    start=time.monotonic();head=w.git('rev-parse','HEAD')
    w.require(not w.git('status','--porcelain') and w.git('branch','--show-current')==w.BRANCH,'clean committed implementation branch')
    w.require(not any(os.path.lexists(p) for p in (OUT,w.OUT,w.AUTHORITY)),'fresh offline output; runtime output/authority absent')
    review=w.read(REVIEW)
    w.require(review['PASS'] and review['source_commit']==head and review['source_files']=={p:w.sha(ROOT/p) for p in w.b.WIRING},'exact full-diff static review precedes bounded suite')
    OUT.mkdir(mode=0o700);w.sync(OUT.parent)
    signal.signal(signal.SIGALRM,deadline);signal.alarm(240)
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
    cases=[];negatives=[]
    def reject(label,fn,prefix):
        try:fn()
        except (AssertionError,RuntimeError) as error:
            w.require(str(error).startswith(prefix),'specific inert rejection: '+label+': '+str(error));negatives.append(dict(case=label,reason=str(error)))
        else:raise AssertionError('accepted invalid inert fixture: '+label)
    config,accepted=w.b.reviewed();cases.append('sealed actual ffc scaffold/input/compiled observer/native proof/source chain')
    representation=w.b.retention.verify_protected();cases.append('accepted actual archive representation and37000 protected identities; no raw restoration')
    original_pins={path:w.sha(path) for path in (config['patrol_save'],config['patrol_state'])}
    original=w.state.snapshot(config['patrol_state']);w.state.continue_equivalence(original,original,config['patrol_save']);cases.append('read-only original patrol Save complete native14-sector/full snapshot binding')
    contract=w.contract();w.require(contract['continuation_frames']==134360 and contract['encounter_frames']==30000 and contract['cold_frames']==2044 and w.storage()==accepted['storage'],'exact unchanged full storage/route/battle/cold/capture accounting')
    cases.append('full old reservation and bounds; no small dialogue/trace proposal')
    code=w.b.candidate_source();(OUT/'observer.c').write_text(code)
    closed=(w.b.ACCEPTED/'observer.c').read_text();gate='    return 101; /* CLOSED: offline-only; no core, ROM, Save, reset or frames. */\n'
    at=closed.index(gate);w.require(code[:at]+gate+code[at:]==closed,'precisely one declared entry-line change; all runtime assertions retained')
    w.require('hc_save_ready(core,stage,saveFn,confirmSave,saveSuccess,saveReturn,fade,printers,menuState)' in code and 'co overwrite-ready' in code and 'wc_continue_anchor(&current)' in code and 'wc_cold_anchor(&current)' in code,'native second Yes/readiness and post-Continue/cold full-state anchors retained')
    env=w.b.environment(Path(config['tool_root']));tool=Path(config['tool_root'])
    command=['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I'+str(tool/'usr/include'),str(OUT/'observer.c'),'-L'+str(tool/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(OUT/'observer')]
    with (OUT/'compile.log').open('xb') as log:subprocess.run(command,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=60)
    os.chmod(OUT/'observer',0o700)
    (OUT/'game.sym').write_bytes((w.b.ACCEPTED/'game.sym').read_bytes())
    for mode,name,key in zip(w.MODES,('continuation.route','cold.route'),('continuation_route_SHA256','cold_route_SHA256')):
        data=(w.b.ACCEPTED/name).read_bytes();w.require(hashlib.sha256(data).hexdigest()==contract[key],'exact accepted route bytes');(OUT/(mode+'.route')).write_bytes(data)
    closure=w.validator.derive(env);w.require(closure['entry_points_executed']==closure['emulators']==0 and not closure['Tk_imported'],'source-reviewed import-only actual validator closure')
    sources=w.b.sources(config,accepted);tools=w.b.tools(config,OUT/'observer',closure)
    for path,pin in closure['project_sources'].items():w.require(sources[path]==pin,'actual imported project provider matches exact declared source closure')
    cases.append('compile-only exact runtime candidate; genuine source/native/interpreter/link dependencies')
    for label,manifest in (('source',sources),('tool',tools),('validator',closure['files'])):
        w.b.verify_manifest(manifest,dict(manifest));cases.append('exact '+label+' dependency manifest')
        key=next(iter(manifest))
        missing=dict(manifest);del missing[key];reject(label+'-missing',lambda missing=missing,manifest=manifest:w.b.verify_manifest(missing,manifest),'exact dependency keys/hashes')
        extra=dict(manifest);extra['unreviewed-extra']='0'*64;reject(label+'-extra',lambda extra=extra,manifest=manifest:w.b.verify_manifest(extra,manifest),'exact dependency keys/hashes')
        changed=dict(manifest);changed[key]='0'*64;reject(label+'-changed',lambda changed=changed,manifest=manifest:w.b.verify_manifest(changed,manifest),'exact dependency keys/hashes')
    reject('conflicting inherited source overlap',lambda:w.b.merge_exact({'a':'1'},{'a':'2'}),'conflicting exact dependency overlap')
    w.b.merge_exact({'a':'1'},{'a':'1','b':'2'});cases.append('exact source union permits only agreeing historical overlap')
    # Exact frozen-record admission, entirely virtual. No runtime root, authority,
    # source checkpoint, claim or freeze is written by these fixtures.
    receipt=dict(tested_source_commit=head,source_files=sources,tool_files=tools,
        candidate_artifacts={n:w.sha(OUT/n) for n in ('observer.c','observer','game.sym')},
        route_SHA256={mode:w.sha(OUT/(mode+'.route')) for mode in w.MODES},
        input_Save_SHA256='patrol-save',input_state_SHA256='patrol-state',archive_representation=representation)
    receipt['scope']=w.scope(head,receipt)
    receipt['PASS']=True;receipt['runtime_actions_executed']=0
    real_sha=w.sha
    with patch.object(Path,'is_file',return_value=True),patch.object(w,'sha',return_value='SYNTHETIC-offline-receipt'):
        authority=w.authority_template(receipt)
        def authority_read(path):return receipt if path==w.OFFLINE/'offline-admission-private.json' else authority
        def authority_git(*args):
            return {('rev-parse','HEAD'):head,('status','--porcelain'):'',('branch','--show-current'):w.BRANCH,
                ('ls-remote','--heads','origin',w.BRANCH):head+'\trefs/heads/'+w.BRANCH}[args]
        with patch.object(w,'read',side_effect=authority_read),patch.object(w,'git',side_effect=authority_git):
            w.require(w.runtime_authority()==(head,receipt),'virtual exact separate reviewed authority')
            cases.append('virtual exact authority/source/published branch gate')
            for key,bad in (('source_commit','old'),('scope_SHA256','changed'),('execution_limit_per_mode',2),('parent_review_verified',False)):
                old=authority[key];authority[key]=bad
                reject('authority-'+key,w.runtime_authority,'exact separately reviewed runtime authority');authority[key]=old
            authority['extra']='unreviewed';reject('authority-extra',w.runtime_authority,'exact separately reviewed runtime authority');del authority['extra']
    files=dict(receipt['candidate_artifacts'],**{'patrol-input-verified-copy.sav':'patrol-save','expected-input-state.bin':'patrol-state',
        'source-contract.json':w.sha(w.CONTRACT),'offline-admission-private.json':'offline-receipt','source-checkpoint.tar':'checkpoint'})
    files.update({mode+'.route':pin for mode,pin in receipt['route_SHA256'].items()})
    frozen=dict(source_commit=head,scope=receipt['scope'],files=files,source_files=sources,tool_files=tools,
        executable=dict(SHA256=receipt['candidate_artifacts']['observer']),authority_SHA256='authority')
    def frozen_sha(path):
        if path==w.AUTHORITY:return 'authority'
        if path==w.OFFLINE/'offline-admission-private.json':return 'offline-receipt'
        if path.parent==w.OUT:return files[path.name]
        return real_sha(path)
    with patch.object(w,'sha',side_effect=frozen_sha),patch.object(w.execfile,'verify_executable') as executable:
        w.verify_frozen(frozen,receipt);executable.assert_called_once_with(w.OUT/'observer',frozen['executable']);cases.append('exact virtual frozen artifact/source/tool/executable admission')
        for key,bad,reason in (('source_commit','old','exact immutable'),('files',dict(files,extra='unreviewed'),'exact frozen file keys'),
            ('source_files',{},'exact source/provider'),('tool_files',{},'exact source/provider'),('authority_SHA256','changed','unchanged runtime authority'),
            ('executable',dict(SHA256='changed'),'exact candidate executable')):
            altered=copy.deepcopy(frozen);altered[key]=bad
            reject('frozen-'+key,lambda altered=altered:w.verify_frozen(altered,receipt),reason)
        altered=dict(frozen,unreviewed=True);reject('frozen-extra-record',lambda:w.verify_frozen(altered,receipt),'exact frozen record keys')
        with patch.object(w.execfile,'verify_executable',side_effect=AssertionError('SYNTHETIC executable identity mismatch')):
            reject('frozen inode/owner/mode refusal',lambda:w.verify_frozen(frozen,receipt),'SYNTHETIC executable identity mismatch')
    # Exercise the actual admission ordering, using virtual providers throughout.
    for mode in w.MODES:
        events=[]
        with patch.object(w,'runtime_authority',side_effect=lambda:events.append('authority') or (head,receipt)),patch.object(Path,'iterdir',return_value=iter(())),patch.object(w,'verify_lifecycle',side_effect=lambda *_:events.append('lifecycle')),patch.object(w,'read',return_value=frozen),patch.object(w,'verify_frozen',side_effect=lambda *_:events.append('frozen')),patch.object(w,'refresh',side_effect=lambda *_:events.append('refresh')),patch.object(w,'verify_continuation_handoff',side_effect=lambda *_:events.append('actual-Save-handoff')),patch.object(w,'check_root_usage',side_effect=lambda:events.append('quota')),patch.object(w.shutil,'disk_usage',side_effect=lambda _:events.append('fresh-capacity') or SimpleNamespace(free=w.RESERVATION)):
            w.require(w.admission(mode)==(frozen,receipt),'virtual exact admission result')
        w.require(events==['authority','lifecycle','frozen','refresh']+(['actual-Save-handoff'] if mode==w.MODES[1] else [])+['quota','fresh-capacity'],'actual admission ordering and conditional Save gate')
        cases.append('ordered virtual full admission '+mode)
    # First-failure supervisor termination/reaping, without any real PID action.
    events=[]
    process=SimpleNamespace(pid=999999,wait=lambda **kw:events.append(('wait',kw['timeout'])))
    with patch.object(w.os,'killpg',side_effect=lambda pid,sig:events.append(('kill',pid,int(sig)))):w.stop_process(process)
    w.require(events==[('kill',999999,int(signal.SIGTERM)),('wait',5)],'first failure TERM and reap')
    events=[];waits=[subprocess.TimeoutExpired('SYNTHETIC',5),None]
    def wait(**kw):
        events.append(('wait',kw['timeout']));value=waits.pop(0)
        if isinstance(value,Exception):raise value
    process.wait=wait
    with patch.object(w.os,'killpg',side_effect=lambda pid,sig:events.append(('kill',pid,int(sig)))):w.stop_process(process)
    w.require(events==[('kill',999999,int(signal.SIGTERM)),('wait',5),('kill',999999,int(signal.SIGKILL)),('wait',5)],'bounded forced termination and reap')
    cases.append('virtual first failure TERM/KILL bounded reap; no retry')
    for mode in w.MODES:
        present=set() if mode==w.MODES[0] else {w.MODES[0],w.MODES[0]+'-exclusive-claim.json',w.MODES[0]+'-verdict-private.json'}
        w.verify_lifecycle(mode,present);cases.append('one-use ordered lifecycle '+mode)
        for marker in ('STOP.json','PREPARATION-STOP.json',mode,mode+'-exclusive-claim.json'):
            reason='first failure terminal' if 'STOP' in marker else 'one-use mode'
            reject('lifecycle-'+mode+'-'+marker,lambda marker=marker,mode=mode,present=present:w.verify_lifecycle(mode,present|{marker}),reason)
    reject('cold before actual continuation',lambda:w.verify_lifecycle(w.MODES[1],set()),'actual successful continuation')
    reject('continuation after cold claim',lambda:w.verify_lifecycle(w.MODES[0],{w.MODES[1]+'-exclusive-claim.json'}),'cold cannot precede')
    reject('wrong mode',lambda:w.verify_lifecycle('opening',set()),'Warden modes only')
    # Genuine kernel exclusivity, but only a labelled inert fixture inside OUT.
    with (OUT/'SYNTHETIC-exclusive-lock.fixture').open('xb') as first,(OUT/'SYNTHETIC-exclusive-lock.fixture').open('rb') as second:
        fcntl.flock(first,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:fcntl.flock(second,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:cases.append('actual inert exclusive-lock refusal')
        else:raise AssertionError('inert lock admitted two owners')
    events=[]
    def factory(argv,**kwargs):events.append(('created',list(argv)));return SimpleNamespace(pid=999999)
    for mode in w.MODES:
        path=OUT/('SYNTHETIC-capacity-'+mode+'.json');events.clear()
        with patch.object(w,'OUT',OUT),patch.object(w.shutil,'disk_usage',side_effect=lambda _:events.append(('fresh',w.RESERVATION)) or SimpleNamespace(free=w.RESERVATION)):
            p=w.capacity_before_creation(path,mode,head,factory,['SYNTHETIC-NOT-AN-EMULATOR'])
        w.require(p.pid==999999 and events==[('fresh',w.RESERVATION),('created',['SYNTHETIC-NOT-AN-EMULATOR'])] and w.read(path)['fresh_available_bytes']==w.RESERVATION,'fresh whole capacity log immediately precedes virtual creation')
        cases.append('actual bounded capacity record, full reservation immediately before virtual '+mode)
        with patch.object(w,'OUT',OUT),patch.object(w.shutil,'disk_usage',return_value=SimpleNamespace(free=w.RESERVATION-1)):
            before=len(events);reject('one byte short before creation '+mode,lambda:w.capacity_before_creation(OUT/('SYNTHETIC-short-'+mode+'.json'),mode,head,factory,['SYNTHETIC']),'STOP: full 17694519296-byte reservation')
            w.require(len(events)==before,'no virtual spawn after capacity failure')
    # Footer boundaries use exact whole-battle index3 and complete native EOF.
    def footer(frames,valid,deferred,attempts,battle,assertions=1):return f'CONTINUOUS frames={frames} valid={valid} deferred={deferred} attempts={attempts} per-encounter='+','.join(map(str,battle))+f'\nresult=0 assertions={assertions}\n'
    for mode,frames,battle,attempts in ((w.MODES[0],134360,[0,0,0,30000],1),(w.MODES[1],2044,[0,0,0,0],0)):
        good=footer(frames,1,frames-1,attempts,battle);w.parse_footer(good,mode);cases.append('unchanged exact upper footer '+mode)
        for label,bad in (('frame-over',footer(frames+1,1,frames,attempts,battle)),('count-gap',footer(frames,1,frames-2,attempts,battle)),('zero-assertions',footer(frames,1,frames-1,attempts,battle,0)),('extra-EOF',good+'extra\n'),('duplicate',good+good)):
            reject('footer-'+mode+'-'+label,lambda bad=bad,mode=mode:w.parse_footer(bad,mode),'complete native' if label in ('extra-EOF',) else 'one scoped' if label=='duplicate' else 'unchanged complete')
    for battle,attempts in (([1,0,0,1],1),([0,1,0,1],1),([0,0,1,1],1),([0,0,0,30001],1),([0,0,0,1],2),([0,0,0,0],1)):
        reject('wrong trainer/repeat/battle bound '+str(battle)+str(attempts),lambda battle=battle,attempts=attempts:w.parse_footer(footer(100,1,99,attempts,battle),w.MODES[0]),'only one trainer858')
    # Virtual native Save lineage. The exact disk validator must be called,
    # and each missing/invalid actual success record fails before cold admission.
    runtime=Path('/SYNTHETIC-NOT-RUNTIME');mode=w.MODES[0];directory=runtime/mode
    f=dict(source_commit=head,scope=dict(input_Save_SHA256='original-save',input_state_SHA256='original-state',route_SHA256={mode:'exact-route'}))
    v=dict(PASS=True,source_commit=head,mode=mode,battle_attempts=1,full_14_sector_live_disk_verified=True,PID=123,
           handoff_files={'game.sav':'new-native-save','runtime.log':'log','errors.log':'empty','phase-05-state.bin':'actual-state'})
    binding=dict(input_Save_SHA256='original-save',source_Save_SHA256='original-save',actual_new_Save=False,source_state_SHA256='original-state',expected_state_SHA256='original-state')
    claim=dict(source_commit=head,mode=mode,freeze_SHA256='freeze',binding_SHA256='binding',route_SHA256='exact-route',limit=1,terminal_on_failure=True)
    started=dict(pid=123,source_commit=head,mode=mode,exclusive_claim_SHA256='claim')
    data={str(runtime/(mode+'-verdict-private.json')):v,str(runtime/(mode+'-exclusive-claim.json')):claim,str(directory/'process-started.json'):started,str(directory/'input-binding-private.json'):binding}
    pins={str(directory/n):p for n,p in v['handoff_files'].items()};pins.update({str(runtime/'freeze.json'):'freeze',str(directory/'input-binding-private.json'):'binding',str(runtime/(mode+'-exclusive-claim.json')):'claim'})
    snapshot=object()
    with patch.object(w,'OUT',runtime),patch.object(w,'read',side_effect=lambda p:data[str(p)]),patch.object(w,'sha',side_effect=lambda p:pins[str(p)]),patch.object(Path,'read_text',return_value='PASS CONTINUOUS phase=save\n'),patch.object(Path,'stat',return_value=SimpleNamespace(st_size=0)),patch.object(w.state,'snapshot',return_value=snapshot) as decoder,patch.object(w.state,'disk_equivalence',return_value=True) as disk,patch.object(w,'require_wounded') as wounded:
        w.verify_continuation_handoff(f);decoder.assert_called_once_with(directory/'phase-05-state.bin');disk.assert_called_once_with(directory/'game.sav',snapshot,([35,4],[8,6]));wounded.assert_called_once_with(snapshot);cases.append('conditional cold requires actual full14-sector/manual-Save/native process/claim/state lineage')
        for record,key,bad,reason in ((v,'PASS',False,'actual complete'),(v,'full_14_sector_live_disk_verified',False,'actual complete'),(v,'source_commit','old','actual complete'),(v,'battle_attempts',0,'actual complete'),(v,'PID',124,'actual native'),(claim,'limit',2,'actual exact'),(claim,'terminal_on_failure',False,'actual exact'),(started,'exclusive_claim_SHA256','wrong','actual native'),(binding,'actual_new_Save',True,'original patrol'),(binding,'expected_state_SHA256','wrong','original patrol')):
            old=record[key];record[key]=bad;reject('actual manual Save handoff '+key,lambda:w.verify_continuation_handoff(f),reason);record[key]=old
        key=str(directory/'game.sav');old=pins[key];pins[key]='original-save';v['handoff_files']['game.sav']='original-save';reject('unchanged input Save cannot admit cold',lambda:w.verify_continuation_handoff(f),'actual changed manual Save');pins[key]=old;v['handoff_files']['game.sav']=old
        with patch.object(w.state,'disk_equivalence',side_effect=AssertionError('SYNTHETIC invalid14-sector disk')):reject('disk validator refusal blocks cold',lambda:w.verify_continuation_handoff(f),'SYNTHETIC invalid14-sector disk')
    # Wounded check on labelled canonical fixture records, not earned state.
    records=[bytearray(100),bytearray(100)]
    struct.pack_into('<HH',records[0],86,1,40);struct.pack_into('<HH',records[1],86,30,30)
    with patch.object(w.state.fields,'decode',side_effect=lambda data:dict(canonical=records[0] if data[0]==0 else records[1])):
        party=bytes(100)+bytes([1])+bytes(99);w.require_wounded(dict(party=party));cases.append('actual-wounded/alive predicate on synthetic canonical bytes')
        struct.pack_into('<H',records[0],86,0);reject('incapacitated party',lambda:w.require_wounded(dict(party=party)),'actual alive wounded')
        struct.pack_into('<H',records[0],86,40);reject('fully healed party',lambda:w.require_wounded(dict(party=party)),'actual alive wounded')
    # Small real inert native-index/RGB/P6 fixture; no gameplay state or core.
    capture=OUT/'SYNTHETIC-capture-fixture';capture.mkdir()
    rgb=bytes(115200);(capture/'motion-000.rgb').write_bytes(rgb)
    (capture/'frame-index.bin').write_bytes(struct.pack('<4I',1,0,0,0));(capture/'cold.ppm').write_bytes(b'P6\n240 160\n255\n'+rgb)
    (capture/'runtime.log').write_text('CAPTURE name=cold.ppm absolute=1 width=240 height=160\n')
    (capture/'complete-field-trace-private.bin').write_bytes(bytes(3340));(capture/'complete-battle-trace-private.bin').write_bytes(b'')
    fc=dict(frames=1,valid=1,battle_frames=[0,0,0,0]);w.verify_captures(capture,fc,w.MODES[1]);cases.append('synthetic actual indexed RGB/P6/full trace bytes')
    bad=dict(fc,valid=0);reject('changed trace accounting cannot pass',lambda:w.verify_captures(capture,bad,w.MODES[1]),'unchanged complete field/battle trace')
    reject('missing real runtime authority refuses before all writes',w.runtime_authority,'CLOSED: separate exact runtime authority')
    w.require(not os.path.lexists(w.OUT) and not os.path.lexists(w.AUTHORITY),'no actual runtime freeze/claim/authority or processes')
    for path,pin in original_pins.items():w.require(w.sha(path)==pin,'original patrol Save/state unchanged')
    w.require(w.b.retention.verify_representation()==representation,'all accepted preservation receipts/archive identity unchanged')
    w.require(not w.git('status','--porcelain') and w.git('rev-parse','HEAD')==head,'tested clean source unchanged')
    usage=sum(p.stat().st_blocks*512 for p in OUT.rglob('*') if p.is_file())
    w.require(usage+2*1024**2<CAP,'complete inert output with STOP reserve')
    artifact_names=('observer.c','observer','game.sym')
    result=dict(PASS=True,tested_source_commit=head,source_review_SHA256=w.sha(REVIEW),accepted_scaffold_commit=w.b.TESTED,
        accepted_scaffold_receipt_SHA256=w.b.RECEIPT_SHA,accepted_native_proof_SHA256=w.b.PROOF_SHA,
        cases=cases,case_count=len(cases),negative_cases=negatives,negative_case_count=len(negatives),
        candidate_artifacts={n:w.sha(OUT/n) for n in artifact_names},candidate_observer_never_invoked=True,
        candidate_only_removes_exact_unconditional_entry_refusal=True,source_files=sources,tool_files=tools,validator_tool_files=closure['files'],
        validator_source_import_closure=closure,archive_representation=representation,input_Save_SHA256=original_pins[config['patrol_save']],input_state_SHA256=original_pins[config['patrol_state']],
        route_SHA256={mode:w.sha(OUT/(mode+'.route')) for mode in w.MODES},storage=w.storage(),runtime_actions_executed=0,
        actual_runtime_authorities=0,actual_freezes=0,actual_claims=0,emulator_processes=0,actual_Save_UI_actions=0,actual_cold_processes=0,
        compiler=subprocess.check_output(['cc','-dumpfullversion'],text=True).strip(),compiler_identity='pinned recovered tools; no original historical binary identity claim',
        offline_bounds=dict(internal_seconds=240,outer_seconds=300,per_file_bytes=8*1024**2,total_bytes=CAP),actual_output_allocated_bytes_before_receipt=usage,
        fresh_available_bytes=shutil_free(),reservation_before_each_process=w.RESERVATION,elapsed_ms=int((time.monotonic()-start)*1000),runtime='CLOSED',independent_backup_verified=False)
    result['scope']=w.scope(head,result)
    w.write(OUT/'offline-admission-private.json',result)
    w.write(OUT/'proposed-contract-private.json',dict(status='OFFLINE_PROPOSED_REVIEW_ONLY',execution_permitted=False,scope=result['scope'],offline_receipt_SHA256=w.sha(OUT/'offline-admission-private.json')))
    w.write(OUT/'proposed-authority-private.json',dict(status='PROPOSED_ONLY_NOT_AUTHORITY',execution_permitted=False,would_require_separate_approved_authority=w.authority_template(result)))
    signal.alarm(0)
    print('PASS bounded Warden supervisor offline admission:',len(cases),'positive checks /',len(negatives),'negatives; runtime/freeze/claim/emulators=0')
    print('source',head,'receipt SHA256',w.sha(OUT/'offline-admission-private.json'),'compiled tooling observer SHA256',result['candidate_artifacts']['observer'])

def shutil_free():return os.statvfs(w.SCRATCH).f_bavail*os.statvfs(w.SCRATCH).f_frsize

if __name__=='__main__':
    try:main()
    except BaseException as error:
        signal.alarm(0)
        if OUT.is_dir() and not (OUT/'STOP-offline-private.json').exists():w.write(OUT/'STOP-offline-private.json',dict(PASS=False,error=type(error).__name__+': '+str(error),first_failure_terminal=True,retry_permitted=False,runtime='CLOSED',actual_runtime_authorities=0,actual_freezes=0,actual_claims=0,emulators=0))
        raise
