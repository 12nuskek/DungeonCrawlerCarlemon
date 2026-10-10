#!/usr/bin/env python3
"""Bounded inert supervisor checks; never freeze or launch the production observer."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,struct,sys,tempfile
from unittest.mock import patch,Mock,call
if not __debug__:raise RuntimeError('offline wiring checks require assertions')
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('howler_wiring_test',ROOT/'scripts/floor1/howler-runtime-supervisor.py');w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
def main():
    head=w.current_source();require=w.require;cases=[]
    require(not w.OUT.exists() and not w.AUTHORITY.exists(),'offline-only boundary: runtime output/authority absent')
    require(not w.OFFLINE.exists(),'one exclusive offline check output')
    w.no_active_process();accepted,tools,game=w.reviewed();history=w.claims();expected=w.scope(head)
    def reject(label,fn):
        try:fn()
        except (AssertionError,RuntimeError):cases.append(label)
        else:raise AssertionError('negative fixture accepted: '+label)
    w.verify_scope(copy.deepcopy(expected),expected);cases.append('complete-exact-source-scope')
    def paths(value,prefix=()):
        if isinstance(value,dict):
            for key,item in value.items():yield from paths(item,(*prefix,key))
        elif isinstance(value,list):
            for key,item in enumerate(value):yield from paths(item,(*prefix,key))
        else:yield prefix
    for i,path in enumerate(paths(expected)):
        bad=copy.deepcopy(expected);cursor=bad
        for key in path[:-1]:cursor=cursor[key]
        value=cursor[path[-1]];cursor[path[-1]]=not value if isinstance(value,bool) else value+1 if isinstance(value,int) else str(value)+'-changed'
        reject('scope-leaf-negative-'+str(i),lambda b=bad:w.verify_scope(b,expected))
    for key in expected:
        bad=copy.deepcopy(expected);del bad[key];reject('scope-missing-'+key,lambda b=bad:w.verify_scope(b,expected))
    reject('scope-extra-field',lambda:w.verify_scope(dict(expected,waiver=True),expected))
    authority=dict(schema='separately-admitted-c01-howler-runtime/v1',scope=expected,wiring_receipt_SHA256='fixture-receipt',stages=['prepare',*w.MODES])
    w.verify_authority(authority,expected,'fixture-receipt');cases.append('exact-authority-shape-inert-only')
    for key,value in [('schema','other'),('scope',dict(expected,trainer=858)),('wiring_receipt_SHA256','other'),('stages',['prepare'])]:
        reject('authority-negative-'+key,lambda k=key,v=value:w.verify_authority(dict(authority,**{k:v}),expected,'fixture-receipt'))
    reject('authority-extra-waiver',lambda:w.verify_authority(dict(authority,waiver=True),expected,'fixture-receipt'))
    reject('runtime-remains-closed-without-authority',w.runtime_authority)
    m,c=w.MODES
    w.verify_lifecycle(m,set());w.verify_lifecycle(c,{m,m+'-exclusive-claim.json',m+'-verdict-private.json'});cases.append('two-exclusive-conditional-mode-lifecycles')
    for mode,present in [(m,{'STOP.json'}),(m,{'PREPARATION-STOP.json'}),(m,{m}),(m,{m+'-exclusive-claim.json'}),(m,{c}),(m,{c+'-exclusive-claim.json'}),(c,set()),(c,{m}),(c,{m,m+'-verdict-private.json'}),('opening',set()),('cold',set())]:
        reject('lifecycle-negative-'+str(len(cases)),lambda mode=mode,present=present:w.verify_lifecycle(mode,present))
    w.capacity(10000408128);cases.append('whole-reservation-exact-boundary');reject('whole-reservation-one-byte-short',lambda:w.capacity(10000408127))
    def footer(frames=70000,valid=69000,deferred=1000,attempts=1,battle=(0,0,35000,0),result=0):
        return f'CONTINUOUS frames={frames} valid={valid} deferred={deferred} attempts={attempts} per-encounter='+','.join(map(str,battle))+f'\nresult={result} assertions=23\n'
    w.parse_footer(footer(),m);w.parse_footer(footer(6000,5000,1000,0,(0,0,0,0)),c);cases.append('production-shaped-complete-native-footers')
    bads=[footer(frames=72001),footer(valid=68999),footer(attempts=0),footer(attempts=2),footer(battle=(1,0,35000,0)),footer(battle=(0,1,35000,0)),footer(battle=(0,0,35000,1)),footer(battle=(0,0,36001,0)),footer(battle=(0,0,0,0)),footer(result=1),footer()+footer(),footer()+'trailing\n',footer().replace('result=0 assertions=23','assertions=23'),footer().replace('assertions=23','assertions=0')]
    for i,bad in enumerate(bads):reject('footer-negative-'+str(i),lambda bad=bad:w.parse_footer(bad,m))
    reject('cold-encounter-negative',lambda:w.parse_footer(footer(6000,5000,1000),c))
    require(w.legacy.reservation()==10000408128 and expected['storage'][m]['limit_bytes']==8837820160 and expected['storage'][c]['limit_bytes']==894152512,'unchanged complete ledger')
    frozen_files={name:accepted['artifacts'][name] for name in w.COPY_FILES};frozen_files.update(w.PROOFS)
    frozen_files.update({mode+'.route':expected['route_SHA256'][mode] for mode in w.MODES})
    frozen_files.update({'execution-contract.md':expected['contract_SHA256'],'wiring-receipt.json':'receipt-fixture','guard-input-verified-copy.sav':expected['Save_SHA256'],'guard-original-saved-state.bin':expected['original_snapshot_SHA256'],'source-checkpoint.tar':'archive-fixture'})
    deps=w.dependencies();frozen=dict(scope=expected,source_commit=head,files=frozen_files,dependencies=deps,tool_files={},authority_SHA256='authority-fixture',executable={'SHA256':expected['observer_SHA256']})
    fixture_hashes={str(w.OUT/name):pin for name,pin in frozen_files.items()};fixture_hashes.update({str(ROOT/name):pin for name,pin in deps.items()});fixture_hashes[str(w.AUTHORITY)]='authority-fixture';fixture_hashes[str(w.OFFLINE/'offline-admission-private.json')]='receipt-fixture'
    with patch.object(w,'dependencies',return_value=deps),patch.object(w,'sha',side_effect=lambda p:fixture_hashes[str(p)]),patch.object(w.execfile,'verify_executable',return_value={'inert':True}):
        w.verify_frozen(frozen,expected);cases.append('complete-reviewed-frozen-binding-inert-metadata')
        for name in frozen_files:
            bad=copy.deepcopy(frozen);bad['files'][name]='changed'
            reject('frozen-file-negative-'+name,lambda bad=bad:w.verify_frozen(bad,expected))
        bad=copy.deepcopy(frozen);del bad['files']['observer'];reject('frozen-file-missing',lambda:w.verify_frozen(bad,expected))
        bad=copy.deepcopy(frozen);bad['executable']['SHA256']='changed';reject('frozen-executable-not-reviewed',lambda:w.verify_frozen(bad,expected))
        bad=copy.deepcopy(frozen);bad['dependencies']={};reject('frozen-source-inventory-missing',lambda:w.verify_frozen(bad,expected))
    with tempfile.TemporaryDirectory(prefix='howler-wiring-inert-') as temporary:
        d=Path(temporary);(d/'runtime.log').write_text('bounded synthetic log\n');w.check_usage(d,m);cases.append('inert-output-accounting')
        (d/'alias').symlink_to('runtime.log');reject('output-symlink-negative',lambda:w.check_usage(d,m));(d/'alias').unlink()
        for label,name,size in [('log-bound','runtime.log',32*1024**2+1),('per-file-bound','large.bin',2*1024**3+1),('whole-output-bound','large.bin',8837820161)]:
            path=d/name
            with path.open('wb') as f:f.truncate(size)
            reject(label,lambda:w.check_usage(d,m));path.unlink()
        # Synthetic capture/index/trace fixture; it is never a gameplay capture.
        frames=3;rgb=b'\x12\x34\x56'*(240*160);(d/'motion-000.rgb').write_bytes(rgb*frames)
        (d/'frame-index.bin').write_bytes(b''.join(struct.pack('<4I',i,0,0,0) for i in range(1,frames+1)))
        names=w.read(w.REGISTRY)['capture_ledger'][c]
        for name in names:(d/name).write_bytes(b'P6\n240 160\n255\n'+rgb)
        (d/'runtime.log').write_text(''.join(f'CAPTURE name={name} absolute=2 width=240 height=160\n' for name in names))
        (d/'complete-field-trace-private.bin').write_bytes(bytes(frames*3340));(d/'complete-battle-trace-private.bin').write_bytes(b'')
        ft=dict(frames=frames,valid=frames,battle_frames=[0,0,0,0]);w.verify_captures(d,ft,c,0);cases.append('synthetic-capture-index-motion-trace-closure')
        index=(d/'frame-index.bin').read_bytes();(d/'frame-index.bin').write_bytes(struct.pack('<I',0)+index[4:]);reject('capture-index-order-negative',lambda:w.verify_captures(d,ft,c,0));(d/'frame-index.bin').write_bytes(index)
        (d/'complete-field-trace-private.bin').write_bytes(bytes(frames*3340-1));reject('capture-trace-count-negative',lambda:w.verify_captures(d,ft,c,0));(d/'complete-field-trace-private.bin').write_bytes(bytes(frames*3340))
        (d/'cold.ppm').write_bytes(b'P6\n240 160\n255\n'+bytes(len(rgb)));reject('capture-pixel-negative',lambda:w.verify_captures(d,ft,c,0))
        with patch.object(w,'OUT',d):
            w.check_root_usage();cases.append('inert-root-headroom-accounting')
            with (d/'headroom.bin').open('wb') as f:f.truncate(256*1024**2+1)
            reject('root-headroom-negative',w.check_root_usage);(d/'headroom.bin').unlink()
            (d/'unapproved').mkdir();reject('unapproved-root-directory-negative',w.check_root_usage);(d/'unapproved').rmdir()
    with patch.object(w.os,'killpg') as kill:
        process=Mock(pid=1234);w.stop_process(process)
        require(kill.call_args_list==[call(1234,w.signal.SIGTERM),call(1234,w.signal.SIGKILL)],'entire process group cleanup')
        cases.append('inert-parent-and-validator-group-cleanup')
    env=w.execution_environment();require(all(x not in env for x in ('PYTHONOPTIMIZE','PYTHONPATH','PYTHONHOME','LD_PRELOAD')),'assertion/loader environment');cases.append('native-validator-assertions-and-library-environment')
    source=(ROOT/w.WIRING[0]).read_text();tree=ast.parse(source);execute=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute')
    require(ast.unparse(execute.body[0]).startswith('head, _ = runtime_authority()'),'authority before mutation')
    require('state.old.original' in source and "'phase-03-state.bin'" in source and 'state.cold_equivalence' in source,'actual original/new Save handoffs')
    require('start_new_session=True' in source and 'os.killpg' in source and 'terminal_no_retry=True' in source,'bounded group supervision source')
    require('source=OUT/\'guard-input-verified-copy.sav\'' in source and "b'\\xff'" not in source,'no blank Save or replay')
    require(not w.OUT.exists() and not w.AUTHORITY.exists() and not w.git('status','--porcelain'),'no runtime output/authority/source mutation')
    w.OFFLINE.mkdir(mode=0o700)
    receipt=dict(PASS=True,tested_source_commit=head,base_commit=w.BASE,scope=expected,wiring_files={name:w.sha(ROOT/name) for name in w.WIRING},cases=cases,case_count=len(cases),accepted_helper_receipt_SHA256=w.sha(w.ACCEPTED/'offline-receipt.json'),accepted_helpers_retested=False,accepted_helper_count=13,accepted_artifact_count=len(accepted['artifacts']),tool_count=len(tools),build_verification=game,actual_prior_claims=history,available_bytes=w.shutil.disk_usage(w.SCRATCH).free,runtime_actions_executed=0,runtime_freezes=0,runtime_claims=0,emulators=0,synthetic_fixture_is_gameplay=False,missing_launch_condition='separate runtime authority after independent wiring review')
    w.write(w.OFFLINE/'offline-admission-private.json',receipt);print('PASS inert Howler supervisor wiring '+str(len(cases))+' cases; runtime CLOSED')
if __name__=='__main__':main()
