#!/usr/bin/env python3
"""Review-closed r3 preparation gate. This increment has no execution path."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PROOF=Path('/workspace/scratch/c01-medicine-transaction-offline-r3-20261010')
AGGREGATE=PROOF/'aggregate-final'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def identities(aggregate=AGGREGATE):
 runner=module('tx_gate_retained',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
 host=module('tx_gate_host',ROOT/'scripts/floor1/guard-choice-r3-host.py');code,_=host.generate(git)
 receipt=json.loads((aggregate/'admission-receipt.json').read_text())
 assert receipt['PASS'] and receipt['full_aggregate'] and receipt['gameplay_processes']==0
 assert receipt['review_state']=='CLOSED' and receipt['native_sampling_admitted'] is False
 for rel,h in receipt['dependencies'].items():assert sha(ROOT/rel)==h,('source',rel)
 for rel,h in receipt['artifacts'].items():assert sha(aggregate/rel)==h,('offline artifact',rel)
 assert hashlib.sha256(code.encode()).hexdigest()==receipt['generated_host_SHA256']==sha(aggregate/'observer.c')
 assert sha(aggregate/'observer')==receipt['observer_executable_SHA256']
 actual=json.loads((PROOF/'transaction-proof-private.json').read_text())
 assert actual['PASS'] and actual['ELF_SHA256']==runner.ELF_SHA==sha(runner.ENGINE/'pokeemerald.elf')
 library=runner.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'
 assert actual['libmgba_SHA256']==sha(library)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
 assert sha(PROOF/'transaction-bindings.h')==actual['bindings_SHA256']
 return {'validator':sha(ROOT/'scripts/floor1/medicine-transaction.h'),'generator':sha(ROOT/'scripts/floor1/guard-choice-r3-host.py'),
  'proof_script':sha(ROOT/'scripts/floor1/medicine-transaction-proof.py'),'generated_observer':sha(aggregate/'observer.c'),
  'compiled_observer':sha(aggregate/'observer'),'ELF':runner.ELF_SHA,'library':sha(library),
  'compiled_context_proof':sha(PROOF/'transaction-proof-private.json'),'compiled_bindings':sha(PROOF/'transaction-bindings.h'),
  'aggregate_receipt':sha(aggregate/'admission-receipt.json')}
def verify_closed(record,expected):
 assert set(record)=={'schema','review_state','identities','processes_authorized'}
 assert record['schema']=='c01-medicine-transaction-r3/hash-bound/v1'
 assert record['review_state']=='CLOSED_PENDING_INDEPENDENT_REVIEW'
 assert record['processes_authorized']==0 and record['identities']==expected
 return {'review_state':record['review_state'],'processes_authorized':0}
def prepare(output):
 record=json.loads((PROOF/'transaction-admission-private.json').read_text())
 verify_closed(record,identities())
 # Even an altered reusable boolean cannot enable a freeze/claim/process here.
 raise RuntimeError('r3 preparation CLOSED: independent transaction/context review and separate runtime authorization required; no output, freeze, claim, or process created')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();prepare(a.output)
