#!/usr/bin/env python3
"""One separately named offline correction check; consumed runtime stays CLOSED."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,resource,signal,struct,subprocess
if not __debug__:raise RuntimeError('offline checks require assertions')
ROOT=Path(__file__).resolve().parents[1]
BASE='24655f700a395f541ec853c7556522fbf5dfa317'
BOOTSTRAP_BASE='c727aa2d3279bdd49a043f085cfc71c8f7befd50'
OUT=Path('/workspace/scratch/c01-howler-step-predictor-offline-r2-20261010')
CHANGED=('scripts/floor1/howler-continuation-state.py',
         'scripts/floor1/howler-continuation-audit.py',
         'scripts/test-howler-continuation-offline.py',
         'scripts/test-howler-step-predictor-offline.py')
_owned_output=False
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=module('howler_step_review',ROOT/'scripts/floor1/howler-runtime-supervisor.py')
state=w.state
audit=module('howler_step_audit',ROOT/'scripts/floor1/howler-continuation-audit.py')
pack=module('howler_step_pack',ROOT/'scripts/floor1/guard-choice-offline.py').pack
def main():
    global _owned_output
    source=w.current_source();assert w.git('merge-base',BASE,source)==BASE
    assert set(w.git('diff','--name-only',BASE,source).splitlines())==set(CHANGED)
    assert w.git('merge-base',BOOTSTRAP_BASE,source)==BOOTSTRAP_BASE
    assert w.git('diff','--name-only',BOOTSTRAP_BASE,source)==CHANGED[3],'bootstrap harness correction only'
    assert not OUT.exists(),'exclusive offline output already consumed'
    w.no_active_process()
    OUT.mkdir(mode=0o700)
    _owned_output=True
    cases=[]
    def reject(label,fn):
        try:fn()
        except (AssertionError,RuntimeError):cases.append(label)
        else:raise AssertionError('unexpected offline acceptance: '+label)
    fixed={
      w.ACCEPTED/'offline-receipt.json':'a8bc08c9e52a73de404fbcd43754257192074a1a3be4a1c9946cd5377ff12825',
      w.OUT/'STOP.json':'c150543d347bf59b9469041aef685bd6c228dfd55de068eb168fd5f8c75c3ab9',
      w.SCRATCH/'c01-howler-runtime-r1-post-STOP-private-readback-20261010.json':'c141b2edd5fb4bef25d70686791ad30b7047d8670e12653c9d3229a7b726fd89',
      w.SCRATCH/'c01-howler-runtime-r1-final-STOP94-handoff-20261010.json':'4eae9d9f72d2a5f88327a6972f70a022005c19d9ef83042b961bb894501f1724',
      w.SCRATCH/'c01-howler-runtime-r1-handoff-export-STOP-20261010.json':'890097b9482d0e74ae365c009fe9738e3e73e8e2a35fbcd3cf1269101d7d8ce6',
      w.SCRATCH/'c01-howler-runtime-r1-admission-before-prepare-20261010.json':'e8aa0b9602af743bcc3107277e3b65e9723e4b6bc5897597d71c268ab0e12af5',
      w.SCRATCH/'c01-howler-step-offline-terminal-checkpoint-r1-20261010.json':'74618aa0fc7a5bb635de4503e4e5a9fcb94dbc4ce59a6dc220c602c479f9bf5c',
      w.SCRATCH/'c01-howler-step-predictor-offline-r1-20261010.log':'0ed7c1da4336e80059dc8a860cbf49f6dfa676ce6a1f6dfdbba35e5cc8c74f64'}
    prior_output=w.SCRATCH/'c01-howler-step-predictor-offline-r1-20261010'
    prior_files={'offline-STOP-private.json':'de787e2da6d8fc6adf018ddb830550036ae74d91b03abf33bb6454edd0b05f5f',
                 'step-source-proof-private.json':'ac61c379be504e8200ea5cff5f52c9e3c0fab1a8425ee8f94566f71ec15b6d73',
                 'synthetic-initial.bin':'96061074cedead4ebb088e6d8248afd9ff58e541ccaaecb59e024eb1b7e72e0f',
                 'synthetic-walk.bin':'645c3d3b77117697c6ac9e3cdf01149229dec61001defba0a03716818b2269bc',
                 'native-before.bin':'96061074cedead4ebb088e6d8248afd9ff58e541ccaaecb59e024eb1b7e72e0f',
                 'native-after.bin':'645c3d3b77117697c6ac9e3cdf01149229dec61001defba0a03716818b2269bc'}
    assert {p.name for p in prior_output.iterdir()}==set(prior_files)
    fixed.update({prior_output/name:pin for name,pin in prior_files.items()})
    for p,h in fixed.items():assert w.sha(p)==h
    accepted=w.read(w.ACCEPTED/'offline-receipt.json');registry=w.read(w.REGISTRY)
    assert accepted['PASS'] and accepted['tested_source_commit']==w.TESTED and accepted['source_status_at_start']==''
    assert len(accepted['dependency_pins'])==13
    assert {str(Path(p).relative_to(ROOT)):h for p,h in accepted['dependency_pins'].items()}==registry['dependency_Git_paths_SHA256']
    refreshed={};historical={}
    for path,pin in accepted['dependency_pins'].items():
        rel=str(Path(path).relative_to(ROOT))
        assert hashlib.sha256(subprocess.check_output(['git','show',w.TESTED+':'+rel],cwd=ROOT)).hexdigest()==pin
        actual=w.sha(path);historical[rel]=pin;refreshed[rel]=actual
        if rel not in CHANGED:assert actual==pin
    assert {p for p in historical if historical[p]!=refreshed[p]}==set(CHANGED[:3])
    for name,pin in accepted['artifacts'].items():assert w.sha(w.ACCEPTED/name)==pin
    for name,pin in w.PROOFS.items():assert w.sha(w.PROOF/name)==pin
    protected=w.read(w.SCRATCH/'c01-howler-runtime-r1-admission-before-prepare-20261010.json')['protected_evidence_SHA256']
    assert len(protected)==790
    for path,pin in protected.items():assert w.sha(path)==pin
    readback=w.read(w.SCRATCH/'c01-howler-runtime-r1-post-STOP-private-readback-20261010.json')
    runtime_files=readback['complete_runtime_files'];assert len(runtime_files)==55
    for name,record in runtime_files.items():assert w.sha(w.OUT/name)==record['SHA256']
    runtime=w.OUT/'howler-continuation'
    assert w.sha(runtime/'game.sav')==w.sha(state.IMMUTABLE/'game.sav')==state.old.SAVE_SHA
    assert w.read(w.OUT/'STOP.json')['terminal_no_retry'] and not(w.OUT/'howler-new-save-cold').exists()
    assert not(w.OUT/'howler-continuation-verdict-private.json').exists()
    initial,_=state.old.original(state.IMMUTABLE/'game.sav',state.IMMUTABLE/'phase-09-state.bin')
    assert initial['counter']==78 and struct.unpack_from('<H',initial['vars'],0x56)[0]==2
    proof=audit.step_proof();retained_proof=audit.step_proof(w.legacy.ENGINE)
    assert proof==retained_proof
    (OUT/'step-source-proof-private.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n')
    game=w.legacy.verify_game();assert game==accepted['build_verification']
    host=module('howler_step_host',ROOT/'scripts/floor1/howler-continuation-host.py')
    code,_=host.generate(w.git)
    assert hashlib.sha256(code.encode()).hexdigest()==accepted['generated_C_SHA256']
    route=module('howler_step_route',ROOT/'scripts/floor1/howler-continuation-route.py')
    assert route.budget(route.routes()['howler-continuation'])['total']==70625
    for name,text in route.routes().items():assert text==(ROOT/f'scripts/contracts/f1-c01-{name}.route').read_text()
    prior=w.read(w.SCRATCH/'c01-howler-step-offline-terminal-checkpoint-r1-20261010.json')
    assert prior['attempted_test_source']==BOOTSTRAP_BASE and prior['completed_before_failure']['ordinary_ladder_modulo_vectors_asserted']==1024
    for rel in CHANGED[:3]:
        assert hashlib.sha256(subprocess.check_output(['git','show',BOOTSTRAP_BASE+':'+rel],cwd=ROOT)).hexdigest()==w.sha(ROOT/rel)
    counts=dict(prior_step_counter_vectors_reused=1024,step_counter_vectors_executed=0,physical_steps=0,ordinary_updates=0,ladder_transitions=0,
                GAME_STAT_STEPS_delta=0,native_step_transitions=0,retained_phase_checks=0,
                native_retained_phase_checks=0,exact_endpoint_counter_negatives=0,exact_endpoint_poison_negatives=0,
                retained_guide_byte_negatives=0,missing_bootstrap_negative=0)
    # Completed ordinary/ladder/127-boundary vectors are reused by exact source
    # and receipt identity, not repeated or promoted to gameplay acceptance.
    def snap(raw,name):
        p=OUT/(name+'.bin');p.write_bytes(raw);return state.snapshot(p)
    def sync(s,name):
        s=copy.deepcopy(s);s['owned']=state.prior.resources.canonical(s['logical'],struct.pack('<I',s['context']))
        return snap(pack(s),name)
    def native(a,b,kind):
        assert (OUT/'fixture.bin').is_file() and w.sha(OUT/'fixture.bin')==bootstrap_SHA256
        (OUT/'native-before.bin').write_bytes(pack(a));(OUT/'native-after.bin').write_bytes(pack(b))
        p=subprocess.run([str(w.ACCEPTED/'inert'),'--transition',str(OUT/'native-before.bin'),str(OUT/'native-after.bin'),str(kind)],
                         cwd=OUT,env=w.legacy.ENV,capture_output=True,timeout=10)
        assert p.returncode==0,(kind,p.stdout,p.stderr)
        assert w.sha(OUT/'fixture.bin')==bootstrap_SHA256
    def walk(s,mapnum,pos,facing):
        kind=state.route_step(s['map'],s['position'],[35,mapnum],pos)
        step=state.step_counters(s['counter'],struct.unpack_from('<H',s['vars'],0x56)[0],kind)
        t=copy.deepcopy(s);t.update(counter=step['counter'],map=[35,mapnum],position=pos,section=213 if mapnum==0 else 214,facing=facing)
        v=bytearray(t['vars']);struct.pack_into('<H',v,0x54,step['counter']);struct.pack_into('<H',v,0x56,step['poison'])
        if mapnum!=s['map'][1]:struct.pack_into('<H',v,2,0)
        t['vars']=bytes(v);t=sync(t,'synthetic-walk');native(s,t,1);counts['native_step_transitions']+=1
        if mapnum==0 and struct.unpack_from('<H',t['vars'],2)[0]==0:
            v=bytearray(t['vars']);struct.pack_into('<H',v,2,1);u=sync(dict(t,vars=bytes(v)),'synthetic-temp');native(t,u,1);t=u
            counts['native_step_transitions']+=1
        counts['physical_steps']+=1;counts['ordinary_updates']+=step['step_script_updates']
        counts['ladder_transitions']+=kind=='ladder';counts['GAME_STAT_STEPS_delta']+=step['GAME_STAT_STEPS_delta']
        return t,kind
    outbound=[([4,4],1,2),([37,26],0,2)]+[([x,26],0,4) for x in range(38,52)]+[([51,27],0,1)]
    inbound=[([51,26],0,2)]+[([x,26],0,3) for x in range(50,37,-1)]+[([4,3],1,3),([4,4],1,1),([4,5],1,1)]
    s=sync(state.old.expected(initial),'synthetic-initial');kinds=[]
    # setup() always reads a complete CoSnapshot from cwd/fixture.bin, even
    # though --transition subsequently replaces co.last/co.before with argv[2]
    # and installs argv[3]. Supply the intended synthetic initial fixture only.
    bootstrap=pack(s);assert len(bootstrap)==3324
    assert hashlib.sha256(bootstrap).hexdigest()==prior_files['synthetic-initial.bin']
    with (OUT/'fixture.bin').open('xb') as f:f.write(bootstrap)
    bootstrap_SHA256=w.sha(OUT/'fixture.bin')
    assert (OUT/'fixture.bin').read_bytes()==(OUT/'synthetic-initial.bin').read_bytes()
    inert_source=(w.ACCEPTED/'inert.c').read_text()
    contract='FILE*f=fopen("fixture.bin","rb");assert(f&&fread(&co.last,1,sizeof co.last,f)==sizeof co.last&&!fclose(f));'
    assert contract in inert_source and 'setup();struct CoSnapshot before={0},after={0},actual={0};' in inert_source
    assert 'co.last=co.before=before;' in inert_source and 'installSnapshot(&after);result=co_read(&mock,&actual);' in inert_source
    missing=OUT/'missing-bootstrap-negative';missing.mkdir(mode=0o700)
    def no_core_dump():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    p=subprocess.run([str(w.ACCEPTED/'inert'),'--transition',str(OUT/'synthetic-initial.bin'),str(OUT/'synthetic-initial.bin'),'1'],
        cwd=missing,env=w.legacy.ENV,capture_output=True,timeout=10,preexec_fn=no_core_dump)
    assert p.returncode==-signal.SIGABRT and not p.stdout and b'setup:' in p.stderr
    assert b'f&&fread(&co.last,1,sizeof co.last,f)==sizeof co.last&&!fclose(f)' in p.stderr
    assert not list(missing.iterdir()) and w.sha(OUT/'fixture.bin')==bootstrap_SHA256
    counts['missing_bootstrap_negative']=1
    w.write(OUT/'bootstrap-contract-private.json',dict(PASS=True,inert_source_SHA256=w.sha(w.ACCEPTED/'inert.c'),
        inert_executable_SHA256=w.sha(w.ACCEPTED/'inert'),bootstrap_fixture_SHA256=bootstrap_SHA256,fixture_bytes=3324,
        fixture_origin='same synthetic initial expectation as preserved failed r1; derived only from verified Guard input and explicit native Continue expectation',
        original_Guard_Save_SHA256=state.old.SAVE_SHA,missing_fixture_exit_code=p.returncode,
        missing_fixture_stderr=p.stderr.decode(),missing_fixture_directory_stays_empty=True,
        no_actual_snapshots_changed=True,no_core_initialization=True))
    for pos,mapnum,facing in outbound:s,kind=walk(s,mapnum,pos,facing);kinds.append(kind)
    assert tuple(kinds)==state.LEG_TRANSITIONS[0] and s['counter']==94 and struct.unpack_from('<H',s['vars'],0x56)[0]==2
    # Actual battle snapshots; no invented reward/save/endpoint bytes.
    trace=(runtime/'complete-field-trace-private.bin').read_bytes();assert len(trace)==4090*3340
    records=[(struct.unpack_from('<4I',trace,off),trace[off+16:off+3340]) for off in range(0,len(trace),3340)]
    first=next(i for i,(hdr,_) in enumerate(records) if hdr[1]==9)
    header,before_raw=records[first-1];assert header==(2748,1,3324,0) and records[first][0]==(2749,9,3324,0)
    # Phase-begin co_read/co_dump follows the last field read without runFrame.
    assert 'co.before=current;co.kind=phaseKinds[phaseSeq]' in code and 'co_dump(&current,"before")' in code
    before=snap(before_raw,'retained-Howler-before-extracted');after=state.snapshot(runtime/'phase-00-state.bin')
    assert before['counter']==94 and before['position']==[51,27]
    state.validate('howler',before,after);native(before,after,9)
    counts['retained_phase_checks']+=1;counts['native_retained_phase_checks']+=1
    repeat=state.snapshot(runtime/'phase-01-state.bin');state.validate('howler-repeat',after,repeat);state.same(after,repeat);native(after,repeat,1)
    counts['retained_phase_checks']+=1;counts['native_retained_phase_checks']+=1
    assert struct.unpack_from('<H',repeat['vars'],0x56)[0]==0
    s=copy.deepcopy(repeat);kinds=[]
    for pos,mapnum,facing in inbound:s,kind=walk(s,mapnum,pos,facing);kinds.append(kind)
    assert tuple(kinds)==state.LEG_TRANSITIONS[1] and s['counter']==110 and struct.unpack_from('<H',s['vars'],0x56)[0]==0
    assert counts['physical_steps']==counts['GAME_STAT_STEPS_delta']==34 and counts['ordinary_updates']==32 and counts['ladder_transitions']==2
    guide_before=state.snapshot(runtime/'before-state.bin');guide=state.snapshot(runtime/'current-state.bin')
    state.validate('guide-howler',guide_before,guide);native(guide_before,guide,4)
    counts['retained_phase_checks']+=1;counts['native_retained_phase_checks']+=1
    assert state.endpoint_counters()==(110,0)
    assert guide['saved']==initial['saved'] and guide['saved']!=guide['party'],'actual unsaved endpoint only'
    for counter in range(128):
        if counter==110:continue
        a=copy.deepcopy(guide_before);b=copy.deepcopy(guide)
        for v in (a,b):
            v['counter']=counter;raw=bytearray(v['vars']);struct.pack_into('<H',raw,0x54,counter);v['vars']=bytes(raw)
        # Keep the stationary relation valid; exact endpoint must still reject.
        state.base.validate('guide-howler',a,b)
        reject('exact-endpoint-wrong-counter',lambda a=a,b=b:state.validate('guide-howler',a,b))
        counts['exact_endpoint_counter_negatives']+=1
    for poison in (1,2,3):
        a=copy.deepcopy(guide_before);b=copy.deepcopy(guide)
        for v in (a,b):
            raw=bytearray(v['vars']);struct.pack_into('<H',raw,0x56,poison);v['vars']=bytes(raw)
        state.base.validate('guide-howler',a,b)
        reject('exact-endpoint-wrong-poison',lambda a=a,b=b:state.validate('guide-howler',a,b))
        counts['exact_endpoint_poison_negatives']+=1
    for off in range(3324):
        raw=bytearray(pack(guide));raw[off]^=1
        reject('complete-retained-guide-byte',lambda raw=bytes(raw):state.validate('guide-howler',guide_before,snap(raw,'negative')))
        counts['retained_guide_byte_negatives']+=1
    closure=w.validator.derive(w.execution_environment());tools=dict(w.read(w.SCRATCH/'c01a-journal-admission-r3-20261010/freeze.json')['tool_files'])
    tools.update(closure['files'])
    for p,h in tools.items():assert w.sha(p)==h
    # Refresh identities only in this offline receipt. Never alter old acceptance.
    reject('historical-accepted-helper-gate-rejects-new-source',w.reviewed)
    assert w.read(w.AUTHORITY)['scope']['source_commit']==BASE
    reject('old-source-wiring-receipt-rejects-new-source',w.wiring_receipt)
    reject('old-source-runtime-authority-rejects-new-source',lambda:w.verify_authority(
        w.read(w.AUTHORITY),w.scope(source),w.sha(w.OFFLINE/'offline-admission-private.json')))
    reject('consumed-STOP94-lifecycle-rejects-continuation',lambda:w.verify_lifecycle(w.MODES[0],{p.name for p in w.OUT.iterdir()}))
    claims={k:len(list(w.SCRATCH.glob(p))) for k,p in (
        ('opening','c01-*/opening-exclusive-claim.json'),('cold','c01-*/cold-exclusive-claim.json'),
        ('howler','c01-howler-continuation-*/howler-continuation-exclusive-claim.json'))}
    assert claims==dict(opening=5,cold=2,howler=1)
    for p,h in fixed.items():assert w.sha(p)==h
    for name,record in runtime_files.items():assert w.sha(w.OUT/name)==record['SHA256']
    assert w.current_source()==source;w.no_active_process()
    receipt=dict(schema='c01-howler-step-predictor-offline-correction/v1',PASS=True,offline_only=True,
        base_commit=BASE,bootstrap_base_commit=BOOTSTRAP_BASE,tested_source_commit=source,source_status_at_start='',changed_source_pins={p:w.sha(ROOT/p) for p in CHANGED},
        bootstrap_fixture_SHA256=bootstrap_SHA256,bootstrap_contract_receipt_SHA256=w.sha(OUT/'bootstrap-contract-private.json'),
        historical_helper_pins=historical,current_helper_pins=refreshed,accepted_artifacts_rehashed=len(accepted['artifacts']),
        inherited_observer_and_ELF_proofs_reused=True,generated_C_SHA256=accepted['generated_C_SHA256'],observer_SHA256=accepted['observer_SHA256'],
        complete_current_source_dependencies=w.dependencies(),wiring_files={p:w.sha(ROOT/p) for p in w.WIRING},
        validator_derivation=closure,validator_manifest_SHA256=hashlib.sha256(w.canonical(closure['files']).encode()).hexdigest(),
        complete_current_tool_files=tools,build_verification=game,step_source_proof=proof,counts=counts,cases=cases,
        actual_retained_checks=['Howler: complete source-earned transition','resolved repeat: complete exact state','guide: complete recovery plus all final endpoint assertions'],
        actual_retained_phase_paths=['phase-00-state.bin','phase-01-state.bin','before-state.bin','current-state.bin'],
        extracted_Howler_before=dict(trace_SHA256=w.sha(runtime/'complete-field-trace-private.bin'),record_header=list(header),
                                     snapshot_SHA256=w.sha(OUT/'retained-Howler-before-extracted.bin')),
        protected_history_rehashed=len(protected),runtime_files_preserved=runtime_files,immutable_receipts={str(p):h for p,h in fixed.items()},
        actual_claim_counts=claims,original_Guard_Save_SHA256=state.old.SAVE_SHA,runtime_PASS=False,
        STOP94_preserved=True,export_failure_preserved=True,new_emulators=0,new_runtime_freezes=0,new_runtime_claims=0,
        new_Save_actions=0,new_cold_processes=0,new_builds=0,new_compression_operations=0,
        runtime_admission=False,next_dependency='independent review before a separately named continuation',independent_backup_verified=False)
    w.write(OUT/'offline-correction-receipt-private.json',receipt)
    print(json.dumps(dict(PASS=True,tested_source_commit=source,counts=counts,negative_cases=len(cases),
                         receipt_SHA256=w.sha(OUT/'offline-correction-receipt-private.json'),runtime='CLOSED'),sort_keys=True))
if __name__=='__main__':
    try:main()
    except BaseException as error:
        if _owned_output and not(OUT/'offline-STOP-private.json').exists():
            w.write(OUT/'offline-STOP-private.json',dict(reason=repr(error),terminal_no_retry=True,
                source_commit=w.git('rev-parse','HEAD'),new_emulators=0,new_Save_actions=0,new_cold_processes=0))
        raise
