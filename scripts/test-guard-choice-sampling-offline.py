#!/usr/bin/env python3
"""Independent instruction-cut audit plus unchanged full offline regression."""
from pathlib import Path
import importlib.util,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01-medicine-sampling-audit-r1-20261010')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 runner=module('audit_runner',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
 proof=module('audit_proof',ROOT/'scripts/floor1/medicine-sampling-proof.py').native_proof(OUT)
 aggregate=OUT/'aggregate-final'
 # Exactly one new aggregate directory; no implicit retries or emulator launch.
 with (OUT/'aggregate-final.log').open('x') as f:
  subprocess.run([sys.executable,str(ROOT/'scripts/test-guard-choice-r2-offline.py'),'--artifacts',str(aggregate)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
 admitted=json.loads((aggregate/'admission-receipt.json').read_text());assert admitted['PASS'] and admitted['gameplay_processes']==0
 # Bind each instruction-cut PC to this same retained ELF; do not invoke mCore.
 names={'RESTORED':'Task_DisplayHPRestoredMessage','RUN_TEXT':'RunTextPrinters','CLOSE':'Task_ClosePartyMenu','CLOSE_FADE':'Task_ClosePartyMenuAndSetCB2','COPY':'memcpy'}
 defines=''.join('#define AUDIT_'+name+' '+hex(proof['functions'][fn]['address'])+'u\n' for name,fn in names.items())
 text=(ROOT/'scripts/floor1/guard-choice-r2-inert.c').read_text().replace('OBSERVER',str(aggregate/'inert-observer.c'))
 marker='int main(int argc,char**argv){';assert text.count(marker)==1
 text=text.replace(marker,defines+(ROOT/'scripts/floor1/medicine-sampling-inert.h').read_text()+'\n'+marker+'\n if(argc==2&&!strcmp(argv[1],"--sampling-audit")){samplingAudit();return 0;}')
 (OUT/'sampling-inert-final.c').write_text(text)
 subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-I'+str(runner.TOOL/'usr/include'),str(OUT/'sampling-inert-final.c'),'-L'+str(runner.TOOL/'usr/lib/x86_64-linux-gnu'),'-lmgba','-o',str(OUT/'sampling-inert-final')],check=True)
 split=OUT/'split-fixtures-final';split.mkdir();(split/'fixture.bin').write_bytes((aggregate/'fixture.bin').read_bytes())
 with (OUT/'split-boundaries-final.log').open('x') as f:subprocess.run([str(OUT/'sampling-inert-final'),'--sampling-audit'],cwd=split,env=runner.ENV,stdout=f,stderr=subprocess.STDOUT,check=True)
 log=(OUT/'split-boundaries-final.log').read_text();pattern=r'^SAMPLING_CUT name=(\S+) order=(\d+) recipient=(\d+) quantity=(\d+) record=(\d+) copied=(\d+) next_pc=([0-9a-f]+) reason=(\d+) full_party_source_bytes=1 key=0$'
 rows=[dict(zip(('boundary','order','recipient','quantity','record','copied','next_pc','reason'),m)) for m in re.findall(pattern,log,re.M)];assert len(rows)==1280,len(rows)
 summary={}
 for row in rows:
  item=summary.setdefault(row['boundary'],{'fixtures':0,'guard_reasons':{}});item['fixtures']+=1;reason=row['reason'];item['guard_reasons'][reason]=item['guard_reasons'].get(reason,0)+1
 assert set(summary)=={'printer-created-before-restored-func','printer-inactive-before-task-destroy','fade-active-before-close-func','party-copy-before-CB2','exit-published-before-cleanup'}
 for rel,h in admitted['artifacts'].items():assert runner.sha(aggregate/rel)==h,('aggregate artifact changed by split fixtures',rel)
 for rel,h in admitted['dependencies'].items():assert runner.sha(ROOT/rel)==h,('aggregate source dependency changed',rel)
 receipt={'offline_audit_PASS':True,'stable_full_aggregate_PASS':True,'gameplay_processes':0,'exclusive_claims':0,'runtime_freeze':False,'opening_claims_processes':[3,3],'cold_claims_processes':[0,0],'native_sampling_admitted':False,'source_start_commit':'66a07ff6ccd77f2f4a4c2889364c657bfae45cd1','generated_observer_SHA256':admitted['generated_host_SHA256'],'observer_executable_SHA256':admitted['observer_executable_SHA256'],'split_boundary_fixtures':len(rows),'summary':summary,'actual_frozen_route_cut_occurrence_proven':False,'proof_class':proof['class'],'aggregate_artifact_hashes_verified_after_split_fixtures':True,'source_dependency_hashes':runner.dependencies(),'artifact_hashes':{p.name:runner.sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in ('sampling-admission.json','audit-driver.log','audit-final.log')},'blocked_next_runtime_reason':'The frame API does not provide callback atomicity; source-correct split states fail current strict guard. Keep runtime blocked until reviewed narrow PC/task/source-byte transaction admission or a valid observation exclusion proof.'}
 runner.write(OUT/'sampling-admission.json',receipt);print(json.dumps({k:v for k,v in receipt.items() if k not in ('source_dependency_hashes','artifact_hashes')},sort_keys=True))
if __name__=='__main__':main()
