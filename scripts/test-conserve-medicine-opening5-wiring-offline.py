#!/usr/bin/env python3
"""Named runtime admission negatives; no preparation, claim or emulator."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,required=True);args=p.parse_args();d=args.artifacts;d.mkdir()
    file=ROOT/'scripts/test-f1-c01-conserve-medicine-opening5-r1.py'
    s=importlib.util.spec_from_file_location('opening5_wiring_offline',file);w=importlib.util.module_from_spec(s);s.loader.exec_module(w)
    assert not w.OUT.exists();a=w.reviewed();record=w.scope();w.verify_scope(record);cases=[]
    def reject(name,fn):
        try:fn()
        except (AssertionError,TypeError):cases.append(name)
        else:raise AssertionError('admission waiver accepted: '+name)
    for key in w.PINS:
        bad=copy.deepcopy(record);bad['identities'][key]='0'*64;reject('identity '+key,lambda b=bad:w.verify_scope(b))
    for key,value in [('schema','legacy'),('reviewed_source_commit','0'*40),('reviewed_publication_commit','0'*40),('output_directory',str(w.OUT)+'-retry'),('opening_ordinal',4),('opening_claims_allowed',2),('conditional_cold_claims_allowed',2),('opening_frame_limit',72001),('cold_frame_limit',6001),('encounter_frame_limit',36001),('contract_SHA256','0'*64)]:
        bad=copy.deepcopy(record);bad[key]=value;reject(key,lambda b=bad:w.verify_scope(b))
    for key in ('opening_claims_allowed','conditional_cold_claims_allowed'):
        bad=copy.deepcopy(record);bad[key]=True;reject('boolean '+key,lambda b=bad:w.verify_scope(b))
    for mode in ('opening','cold'):
        bad=copy.deepcopy(record);bad['route_SHA256'][mode]='0'*64;reject('route '+mode,lambda b=bad:w.verify_scope(b))
    bad=copy.deepcopy(record);bad['native_sampling_admitted']=True;reject('legacy reusable boolean',lambda:w.verify_scope(bad))
    reject('boolean only',lambda:w.verify_scope(True));reject('empty record',lambda:w.verify_scope({}))
    for key in record:
        bad=copy.deepcopy(record);bad.pop(key);reject('removed '+key,lambda b=bad:w.verify_scope(b))
    reserve=w.runner.reservation();w.capacity(reserve,reserve);reject('short full reservation',lambda:w.capacity(reserve-1,reserve))
    w.WIRING=d/'file-binding-only-fixture.json';w.WIRING.write_text('{"fixture_only":"never execution admission"}\n')
    copied=('observer.c','observer','game.sym','actual-ELF-bindings-private.json','native-ABI.s','native-ABI.o')
    identities={str(w.OUT/name):a['artifacts'][name] for name in copied}
    for mode,h in record['route_SHA256'].items():identities[str(w.OUT/(mode+'.route'))]=h
    for name,h in [('transaction-proof-private.json',w.PINS['compiled_context_proof']),('transaction-bindings.h',w.PINS['compiled_bindings']),('execution-contract.md',w.sha(w.CONTRACT)),('source-checkpoint.tar','1'*64),('reviewed-execution-binding.json','2'*64),('opening5-wiring-offline-receipt.json',w.sha(w.WIRING))]:identities[str(w.OUT/name)]=h
    w.verify_files({'files':identities},a)
    for path in identities:
        bad=dict(identities);bad.pop(path);reject('removed frozen '+Path(path).name,lambda b=bad:w.verify_files({'files':b},a))
        if Path(path).name not in ('source-checkpoint.tar','reviewed-execution-binding.json'):
            bad=dict(identities);bad[path]='0'*64;reject('changed frozen '+Path(path).name,lambda b=bad:w.verify_files({'files':b},a))
    for path in (w.OUT,w.OUT/'opening-exclusive-claim.json',w.OUT/'cold-exclusive-claim.json'):assert not path.exists()
    command=['python3','-O',str(file),'--stage','prepare'];q=subprocess.run(command,capture_output=True,text=True);(d/'optimized-rejection.log').write_text(q.stdout+q.stderr);assert q.returncode==1 and 'requires enabled checks' in q.stderr and not w.OUT.exists();cases.append('optimized CLI rejects before output')
    # No changed observer source or recompilation: exact admitted code/executable
    # plus all original aggregate dependencies are read and verified by reviewed().
    host=w.module('opening5_offline_host',ROOT/'scripts/floor1/conserve-medicine-host.py');code,_=host.generate(w.git)
    assert hashlib.sha256(code.encode()).hexdigest()==w.PINS['generated_observer'];assert w.sha(w.AGGREGATE/'observer')==w.PINS['compiled_observer']
    files={str(f.relative_to(ROOT)):w.sha(f) for f in (file,Path(__file__),w.CONTRACT)}
    receipt={'PASS':True,'reviewed_source_commit':w.REVIEWED_SOURCE,'reviewed_published_commit':w.REVIEWED_PUBLICATION,'tested_wiring_source_commit':w.git('rev-parse','HEAD'),'source_files':files,'reviewed_identities':w.PINS,'named_scope_NEGATIVES':len(cases),'cases':cases,'generated_C_unchanged':True,'compiled_observer_reused_exact':True,'fresh_policy_aggregate_required_and_verified':True,'preserved_closed_gate_cases':37,'new_output_freeze_claim_or_emulator':0,'reservation_bytes':reserve}
    assert len(cases)==len(w.PINS)+60
    w.write(d/'receipt.json',receipt);print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
