#!/usr/bin/env python3
"""Bounded Howler2 admission fixtures only; no runtime root, authority or process."""
from pathlib import Path
import ast,copy,importlib.util,json,os,struct,sys
from types import SimpleNamespace
from unittest.mock import MagicMock,Mock,patch
if not __debug__:raise RuntimeError('offline assertions required')
ROOT=Path(__file__).resolve().parents[1]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
w=module('howler2_offline_supervisor',ROOT/'scripts/floor1/howler2-runtime-supervisor.py')
owned=False
def main():
    global owned
    head=w.current_source();require=w.require;cases=[]
    require(not w.OUT.exists() and not w.AUTHORITY.exists(),'offline boundary: Howler2 runtime/authority absent')
    require(not w.OFFLINE.exists(),'exclusive offline output')
    w.no_active_process();w.OFFLINE.mkdir(mode=0o700);owned=True
    previous=w.SCRATCH/'c01-howler2-offline-terminal-checkpoint-r1-20261011.json'
    require(w.sha(previous)=='4c332cb2d7d55566a5e08cbbcfa5c81282eea19c825ce37f55729b4380b08b51','prior424-versus425 checkpoint')
    prior_stop=w.read(previous)
    for path,pin in prior_stop['offline_files'].items():require(w.sha(path)==pin,'prior dependency STOP preserved')
    require(w.sha(w.SCRATCH/'c01-howler2-runtime-wiring-offline-r1-20261011.log')==prior_stop['offline_log_SHA256'],'prior failed log preserved')
    require(w.git('merge-base','0748d38aff5eeedb1d8484cf667737757aae8184',head)=='0748d38aff5eeedb1d8484cf667737757aae8184','preserved prior local commit')
    accepted,tools,game=w.reviewed();history=w.claims();expected=w.scope(head)
    require(history['counts']==history['process_counts']==dict(opening=5,cold=2,howler1=1),'actual opening/cold/Howler1 counts')
    require(history['Howler1_native_STOP']==dict(reason=94,frame=12520),'consumed Howler1 native STOP')
    for path,pin in w.read(w.CORRECTION)['immutable_receipts'].items():require(w.sha(path)==pin,'prior failure artifact changed')
    def reject(label,fn):
        try:fn()
        except (AssertionError,RuntimeError):cases.append(label)
        else:raise AssertionError('invalid offline fixture accepted: '+label)
    inventory=w.dependencies();prior_inventory=w.read(w.CORRECTION)['complete_current_source_dependencies']
    require(set(inventory)==set(prior_inventory)|w.NEW_SOURCE,'full accepted inventory set, not count only')
    historical=str(w.HISTORICAL_CONTRACT.relative_to(ROOT));new_contract=str(w.CONTRACT.relative_to(ROOT))
    require(historical in inventory and new_contract in inventory and inventory[historical]==prior_inventory[historical],'both source contracts retained')
    w.verify_dependency_inventory(inventory,prior_inventory);cases.append('complete-historical-and-new-contract-inventory')
    missing_contract=dict(inventory);del missing_contract[historical]
    reject('historical-contract-missing',lambda:w.verify_dependency_inventory(missing_contract,prior_inventory))
    wrong_contract=dict(inventory);wrong_contract[historical]='0'*64
    reject('historical-contract-wrong-content',lambda:w.verify_dependency_inventory(wrong_contract,prior_inventory))
    extra_contract=dict(inventory,unreviewed_contract='0'*64)
    reject('inventory-extra-path',lambda:w.verify_dependency_inventory(extra_contract,prior_inventory))
    same_count=dict(missing_contract,unreviewed_contract='0'*64)
    require(len(same_count)==len(inventory),'same-count inventory fixture')
    reject('inventory-same-count-wrong-path',lambda:w.verify_dependency_inventory(same_count,prior_inventory))
    # Carry over the already-tested bounded execution functions verbatim.
    def functions(path):return {n.name:n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
    old=functions(ROOT/'scripts/floor1/howler-runtime-supervisor.py');new=functions(ROOT/w.WIRING[0])
    changed={'dependencies','scope','reviewed','claims','verify_authority','wiring_receipt','prepare','verify_frozen','verify_continuation_handoff'}
    unchanged=sorted(set(old)-changed)
    for name in unchanged:require(ast.dump(old[name])==ast.dump(new[name]),'unchanged bounded function '+name)
    cases.append('unchanged-bounded-runtime-functions-'+str(len(unchanged)))
    execute=new['execute'];require(ast.unparse(execute.body[0])=='head, _ = runtime_authority()','authority before mutation')
    code=ast.unparse(execute)
    require(code.index('f = admission(mode)')<code.index('d.mkdir'),'admission before claim/directory')
    require('capacity(shutil.disk_usage(OUT).free)\n            process = subprocess.Popen' in code,'full reservation immediately before each Popen')
    require('start_new_session=True' in code and 'terminal_no_retry=True' in code,'unchanged terminal group supervision')
    cases.append('both-mode-full-reservation-before-Popen-source-order')
    old_closure=ast.parse((ROOT/'scripts/floor1/howler-validator-closure.py').read_text())
    new_closure=ast.parse((ROOT/w.WIRING[3]).read_text())
    def without_entry(tree):return ast.dump(ast.Module(body=[n for n in tree.body if not(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ENTRY_FILES' for t in n.targets))],type_ignores=[]))
    require(without_entry(old_closure)==without_entry(new_closure),'same source-derived closure with Howler2 entry files only')
    require(w.validator.ENTRY_FILES==('scripts/run-f1-c01-howler2-r1.py','scripts/floor1/howler2-runtime-supervisor.py','scripts/floor1/howler-continuation-state.py'),'exact Howler2 entry source')
    w.verify_scope(copy.deepcopy(expected),expected);cases.append('complete-Howler2-scope')
    def leaves(value,path=()):
        if isinstance(value,dict):
            for key,v in value.items():yield from leaves(v,(*path,key))
        elif isinstance(value,list):
            for key,v in enumerate(value):yield from leaves(v,(*path,key))
        else:yield path
    for i,path in enumerate(leaves(expected)):
        bad=copy.deepcopy(expected);cursor=bad
        for key in path[:-1]:cursor=cursor[key]
        v=cursor[path[-1]];cursor[path[-1]]=not v if isinstance(v,bool) else v+1 if isinstance(v,int) else str(v)+'-changed'
        reject('scope-leaf-'+str(i),lambda bad=bad:w.verify_scope(bad,expected))
    for key in expected:
        bad=copy.deepcopy(expected);del bad[key];reject('scope-missing-'+key,lambda bad=bad:w.verify_scope(bad,expected))
    reject('scope-extra-waiver',lambda:w.verify_scope(dict(expected,waiver=True),expected))
    authority=dict(schema='separately-admitted-c01-howler2-runtime/v1',scope=expected,wiring_receipt_SHA256='synthetic-receipt',stages=['prepare',*w.MODES])
    w.verify_authority(authority,expected,'synthetic-receipt');cases.append('exact-Howler2-authority-shape-inert')
    for key,value in [('schema','separately-admitted-c01-howler-runtime/v1'),('scope',dict(expected,output=str(w.HOWLER1))),('scope',dict(expected,source_commit=w.TESTED)),('wiring_receipt_SHA256','other'),('stages',['prepare'])]:
        reject('authority-negative-'+key,lambda key=key,value=value:w.verify_authority(dict(authority,**{key:value}),expected,'synthetic-receipt'))
    reject('authority-extra-field',lambda:w.verify_authority(dict(authority,waiver=True),expected,'synthetic-receipt'))
    reject('actual-Howler2-authority-still-absent',w.runtime_authority)
    reject('Howler1-authority-cannot-admit-Howler2',lambda:w.verify_authority(w.read(w.HOWLER1_AUTHORITY),expected,'synthetic-receipt'))
    m,c=w.MODES
    w.verify_lifecycle(m,set());w.verify_lifecycle(c,{m,m+'-exclusive-claim.json',m+'-verdict-private.json'});cases.append('one-conditional-lifecycle-per-mode')
    for mode,present in [(m,{'STOP.json'}),(m,{'PREPARATION-STOP.json'}),(m,{m}),(m,{m+'-exclusive-claim.json'}),(m,{c}),(m,{c+'-exclusive-claim.json'}),(c,set()),(c,{m}),(c,{m,m+'-verdict-private.json'}),(c,{c}),(c,{c+'-exclusive-claim.json'}),('opening',set()),('cold',set())]:
        reject('lifecycle-negative-'+str(len(cases)),lambda mode=mode,present=present:w.verify_lifecycle(mode,present))
    oldw=module('immutable_howler1_gate',ROOT/'scripts/floor1/howler-runtime-supervisor.py')
    reject('Howler1-terminal-lifecycle-remains-closed',lambda:oldw.verify_lifecycle(m,{p.name for p in oldw.OUT.iterdir()}))
    reject('Howler1-accepted-helper-gate-still-rejects-changed-source',oldw.reviewed)
    require(w.storage()==oldw.storage() and w.legacy.reservation()==10000408128,'unchanged complete storage ledger')
    w.capacity(10000408128);reject('whole-reservation-one-byte-short',lambda:w.capacity(10000408127));cases.append('whole-reservation-exact-boundary')
    # Frozen binding fixtures are dictionaries and mocked hashes, never a freeze.
    files={name:accepted['artifacts'][name] for name in w.COPY_FILES};files.update(w.PROOFS)
    files.update({name:w.sha(path) for name,path in w.RECEIPT_FILES.items()})
    files.update({mode+'.route':expected['route_SHA256'][mode] for mode in w.MODES})
    files.update({'execution-contract.json':expected['contract_SHA256'],'wiring-receipt.json':'synthetic-receipt',
        'guard-input-verified-copy.sav':expected['Save_SHA256'],'guard-original-saved-state.bin':expected['original_snapshot_SHA256'],'source-checkpoint.tar':'synthetic-archive'})
    deps=w.dependencies();frozen=dict(scope=expected,source_commit=head,files=files,dependencies=deps,tool_files=tools,
        authority_SHA256='synthetic-authority',executable=dict(SHA256=expected['observer_SHA256']),prior_claims=history,game=game)
    pins={str(w.OUT/name):h for name,h in files.items()};pins.update({str(ROOT/name):h for name,h in deps.items()});pins.update(tools)
    pins[str(w.AUTHORITY)]='synthetic-authority';pins[str(w.OFFLINE/'offline-admission-private.json')]='synthetic-receipt'
    actual_sha=w.sha
    def fixture_sha(path):return pins.get(str(path)) if str(path) in pins else actual_sha(path)
    with patch.object(w,'sha',side_effect=fixture_sha),patch.object(w.execfile,'verify_executable',return_value={'inert':True}):
        w.verify_frozen(frozen,expected);cases.append('complete-frozen-correction-proof-source-tool-binding-inert')
        for name in files:
            bad=copy.deepcopy(frozen);bad['files'][name]='wrong';reject('frozen-file-'+name,lambda bad=bad:w.verify_frozen(bad,expected))
        for key in ('dependencies','tool_files'):
            # Tool inventory equality is required by admission, source by verify_frozen.
            if key=='dependencies':
                bad=copy.deepcopy(frozen);bad[key]={};reject('frozen-source-inventory-missing',lambda:w.verify_frozen(bad,expected))
        bad=copy.deepcopy(frozen);bad['executable']['SHA256']='wrong';reject('frozen-executable-pin',lambda:w.verify_frozen(bad,expected))
        bad=copy.deepcopy(frozen);bad['files']['unreviewed']='wrong';reject('frozen-extra-file',lambda:w.verify_frozen(bad,expected))
    # Conditional Save handoff: mock metadata/read-only validators, no Save bytes.
    d=w.OUT/m;verdict_path=w.OUT/(m+'-verdict-private.json');claim_path=w.OUT/(m+'-exclusive-claim.json')
    metadata={str(verdict_path):dict(PASS=True,source_commit=head,mode=m,battle_attempts=1,PID=1234,input_binding_SHA256='synthetic-binding',handoff_files={n:'synthetic-'+n for n in ('game.sav','runtime.log','errors.log','phase-03-state.bin')}),
        str(claim_path):dict(source_commit=head,mode=m,limit=1,terminal_on_failure=True,freeze_SHA256='synthetic-freeze',binding_SHA256='synthetic-binding'),
        str(d/'process-started.json'):dict(source_commit=head,mode=m,pid=1234,exclusive_claim_SHA256='synthetic-claim'),
        str(d/'input-binding-private.json'):dict(input_Save_SHA256=w.state.old.SAVE_SHA,source_Save_SHA256=w.state.old.SAVE_SHA,actual_new_Save=False)}
    savepins={str(d/name):'synthetic-'+name for name in ('game.sav','runtime.log','errors.log','phase-03-state.bin')}
    savepins.update({str(claim_path):'synthetic-claim',str(d/'input-binding-private.json'):'synthetic-binding',str(w.OUT/'freeze.json'):'synthetic-freeze'})
    baseline=copy.deepcopy(metadata);baseline_pins=dict(savepins);snapshot=object()
    with patch.object(w,'read',side_effect=lambda p:metadata[str(p)]),patch.object(w,'sha',side_effect=lambda p:savepins[str(p)]),\
         patch.object(Path,'read_text',return_value='PASS CONTINUOUS phase=save\n'),patch.object(Path,'stat',return_value=SimpleNamespace(st_size=0)),\
         patch.object(w.state,'snapshot',return_value=snapshot) as decode,patch.object(w.state,'disk_equivalence',return_value={'synthetic':True}) as disk:
        w.verify_continuation_handoff(frozen);decode.assert_called_once_with(d/'phase-03-state.bin');disk.assert_called_once_with(d/'game.sav',snapshot);cases.append('cold-requires-actual-disk-validator-and-original-Guard-input')
        for path,key,value in [(verdict_path,'PASS',False),(verdict_path,'source_commit',w.TESTED),(verdict_path,'mode',c),(verdict_path,'battle_attempts',0),
            (claim_path,'freeze_SHA256','wrong'),(claim_path,'binding_SHA256','wrong'),(claim_path,'source_commit',w.TESTED),(claim_path,'limit',2),(claim_path,'terminal_on_failure',False),
            (d/'process-started.json','pid',1235),(d/'process-started.json','exclusive_claim_SHA256','wrong'),
            (d/'input-binding-private.json','source_Save_SHA256','wrong'),(d/'input-binding-private.json','actual_new_Save',True)]:
            metadata[str(path)][key]=value;reject('actual-Save-handoff-negative-'+str(len(cases)),lambda:w.verify_continuation_handoff(frozen));metadata.clear();metadata.update(copy.deepcopy(baseline))
        del metadata[str(verdict_path)]['handoff_files']['phase-03-state.bin'];reject('actual-saved-state-required',lambda:w.verify_continuation_handoff(frozen));metadata.clear();metadata.update(copy.deepcopy(baseline))
        savepins[str(d/'game.sav')]=w.state.old.SAVE_SHA;metadata[str(verdict_path)]['handoff_files']['game.sav']=w.state.old.SAVE_SHA
        reject('unchanged-Guard-Save-is-not-new-manual-Save',lambda:w.verify_continuation_handoff(frozen));metadata.clear();metadata.update(copy.deepcopy(baseline));savepins.clear();savepins.update(baseline_pins)
        with patch.object(w.state,'disk_equivalence',side_effect=AssertionError('synthetic-invalid-disk')):
            reject('cold-rejects-failed-actual-disk-validation',lambda:w.verify_continuation_handoff(frozen))
    # Run admission itself with a virtual path view; no root/claims or Save files.
    runtime_root=w.OUT
    virtual=MagicMock(spec=Path);virtual.__truediv__.side_effect=lambda name:runtime_root/name
    present=set();events=[];free=10000408128
    virtual.iterdir.side_effect=lambda:[SimpleNamespace(name=n) for n in present]
    frozen_current=copy.deepcopy(frozen)
    def admit_scope():return copy.deepcopy(expected)
    def handoff(f):events.append('actual-Save-handoff')
    with patch.object(w,'OUT',virtual),patch.object(w,'runtime_authority',return_value=(head,{})),patch.object(w,'ensure_terminal_clear'),\
         patch.object(w,'read',return_value=frozen_current),patch.object(w,'scope',side_effect=lambda h:admit_scope()),\
         patch.object(w,'verify_frozen') as verify,patch.object(w,'reviewed',return_value=(accepted,tools,game)),\
         patch.object(w,'sha',side_effect=actual_sha),patch.object(w,'verify_continuation_handoff',side_effect=handoff),\
         patch.object(w.state.old,'original',return_value=(None,None)),patch.object(w,'check_root_usage',side_effect=lambda:events.append('output-bounds')),\
         patch.object(w.shutil,'disk_usage',side_effect=lambda p:SimpleNamespace(free=free)),patch.object(w,'capacity',side_effect=lambda n:(events.append('whole-reservation'),require(n>=10000408128,'full reservation'))):
        for mode in (m,c):
            present.clear()
            if mode==c:present.update((m,m+'-exclusive-claim.json',m+'-verdict-private.json'))
            events.clear();free=10000408128;w.admission(mode)
            require(events==(['actual-Save-handoff'] if mode==c else [])+['output-bounds','whole-reservation'],'whole reservation after required handoff')
            cases.append('admission-full-reservation-'+mode)
            free=10000408127;reject('admission-one-byte-short-'+mode,lambda mode=mode:w.admission(mode));free=10000408128
        frozen_current['tool_files']={};reject('admission-incomplete-tool-manifest',lambda:w.admission(c));frozen_current.clear();frozen_current.update(copy.deepcopy(frozen))
        frozen_current['game']={};reject('admission-changed-game-build',lambda:w.admission(c));frozen_current.clear();frozen_current.update(copy.deepcopy(frozen))
        with patch.object(w,'verify_continuation_handoff',side_effect=AssertionError('synthetic-invalid-Save')):
            reject('admission-no-cold-after-failed-Save',lambda:w.admission(c))
        present.add('STOP.json');reject('admission-terminal-no-retry',lambda:w.admission(m))
    closure=w.validator.derive(w.execution_environment());native=closure['files'];w.validator.verify_manifest(native,w.validator_tools())
    for rel,pin in closure['project_sources'].items():require(w.sha(ROOT/rel)==pin,'fresh Howler2 provider source')
    cases.append('fresh-Howler2-validator-provider-closure')
    require(not closure['Tk_imported'] and closure['entry_points_executed']==closure['emulators']==0,'import-only actual provider discovery')
    missing=dict(native);del missing[str(Path(sys.executable).resolve())]
    reject('missing-genuine-validator-interpreter',lambda:w.validator.verify_manifest(missing,native))
    wiring_fixture=dict(PASS=True,tested_source_commit=head,runtime_actions_executed=0,
        wiring_files={name:w.sha(ROOT/name) for name in w.WIRING},validator_tool_files=native,scope=expected)
    with patch.object(w,'scope',return_value=expected),patch.object(w,'validator_tools',return_value=native):
        w.verify_wiring_record(wiring_fixture,head);cases.append('exact-current-source-admission-record')
        for key,value in [('PASS',False),('tested_source_commit',w.TESTED),('runtime_actions_executed',1),
                          ('wiring_files',{}),('validator_tool_files',{}),('scope',dict(expected,reservation_bytes=0))]:
            reject('current-admission-negative-'+key,lambda key=key,value=value:w.verify_wiring_record(dict(wiring_fixture,**{key:value}),head))
        bad=copy.deepcopy(wiring_fixture);bad['wiring_files'][w.WIRING[0]]='wrong'
        reject('current-admission-changed-supervisor',lambda:w.verify_wiring_record(bad,head))
    for path,pin in history['files'].items():require(w.sha(path)==pin,'history preserved')
    require(not w.OUT.exists() and not w.AUTHORITY.exists() and head==w.current_source(),'no runtime authority/root/source mutation')
    receipt=dict(schema='c01-Howler2-offline-admission/v1',PASS=True,tested_source_commit=head,base_commit=w.BASE,accepted_correction_source=w.TESTED,
        scope=expected,wiring_files={name:w.sha(ROOT/name) for name in w.WIRING},contract_SHA256=w.sha(w.CONTRACT),correction_receipt_SHA256=w.CORRECTION_SHA,
        current_helper_pins=w.read(w.CORRECTION)['current_helper_pins'],native_proof_pins=w.PROOFS,complete_source_dependencies=deps,
        historical_contract=dict(path=historical,SHA256=inventory[historical]),new_contract=dict(path=new_contract,SHA256=inventory[new_contract]),
        full_inventory_missing=[],full_inventory_extra=[],prior_inventory_STOP_checkpoint_SHA256=w.sha(previous),
        complete_tool_files=tools,validator_tool_files=native,validator_source_derivation=closure,
        accepted_artifacts_rehashed=len(accepted['artifacts']),accepted_helpers_retested=False,prior_bounded_functions_reused=unchanged,
        cases=cases,case_count=len(cases),build_verification=game,actual_prior_claims=history,runtime_actions_executed=0,
        actual_runtime_freezes=0,actual_runtime_claims=0,emulators=0,new_Save_actions=0,new_cold_processes=0,new_builds=0,
        runtime_authority_file_created=False,runtime_admitted=False,synthetic_fixtures_are_gameplay=False,
        remaining_dependency='final independent review and separate exact-source Howler2 authority',independent_backup_verified=False)
    w.write(w.OFFLINE/'offline-admission-private.json',receipt)
    w.wiring_receipt();cases_before=len(cases)
    authority['wiring_receipt_SHA256']=w.sha(w.OFFLINE/'offline-admission-private.json')
    w.verify_authority(authority,expected,authority['wiring_receipt_SHA256'])
    w.write(w.OFFLINE/'authority-proposal-private.json',dict(OFFLINE_PROPOSAL_ONLY=True,activation_path=str(w.AUTHORITY),record=authority))
    w.no_active_process();require(not w.OUT.exists() and not w.AUTHORITY.exists(),'runtime remains CLOSED')
    print(json.dumps(dict(PASS=True,tested_source=head,cases=cases_before,receipt_SHA256=w.sha(w.OFFLINE/'offline-admission-private.json'),authority_proposal_SHA256=w.sha(w.OFFLINE/'authority-proposal-private.json'),runtime='CLOSED'),sort_keys=True))
if __name__=='__main__':
    try:main()
    except BaseException as error:
        if owned and not(w.OFFLINE/'offline-STOP-private.json').exists():w.write(w.OFFLINE/'offline-STOP-private.json',dict(reason=repr(error),source=w.git('rev-parse','HEAD'),terminal_no_retry=True,new_runtime_actions=0))
        raise
