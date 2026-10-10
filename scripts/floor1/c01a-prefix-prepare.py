"""Freeze retained builds/real Save/full original streams for two partial claims."""
from pathlib import Path
import json,shutil,hashlib,subprocess,os
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-diagnostic-prefix-pair-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
CERTROOT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2)+'\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def allocated():return sum(p.stat().st_size for root in [OLD,CERTROOT,OUT] for p in root.rglob('*') if p.is_file())
def prepare(offline):
    assert not git('status','--porcelain') and not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    f=json.loads((CERTROOT/'freeze.json').read_text());cert=json.loads((CERTROOT/'retained-baseline-acceptance.json').read_text())
    tool=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009');tools=dict(f['tool_files']);manifest=json.loads((tool/'tool-root-manifest.json').read_text())
    for name in ['usr/bin/arm-none-eabi-objdump','usr/bin/arm-none-eabi-as']:
        row=[r for r in manifest if r['path']==name];assert len(row)==1 and sha(tool/'root'/name)==row[0]['SHA256'];tools[str(tool/'root'/name)]=row[0]['SHA256']
    assert cert['PASS'] and sha(CERTROOT/'retained-baseline-acceptance.json')==f['retained_baseline_certificate_SHA256']
    for p,h in f['tool_files'].items():assert sha(p)==h
    for p,h in f['original_r4_artifacts_SHA256'].items():assert sha(OLD/p)==h
    proof=json.loads((offline/'offline-proof.json').read_text());assert proof['PASS']
    for p,h in proof['source_SHA256'].items():assert sha(ROOT/p)==h
    for n in ['observer.c','observer']:shutil.copyfile(offline/n,OUT/n)
    assert sha(OUT/'observer.c')==proof['observer_source_SHA256'] and sha(OUT/'observer')==proof['observer_binary_SHA256']
    full=(ROOT/'scripts/contracts/f1-c01a-ui-r3.route').read_bytes();assert hashlib.sha256(full).hexdigest()==f['route_SHA256']
    prefix=b''.join(full.splitlines(keepends=True)[:27]);assert prefix.splitlines()[-3:]==[b'step 1 1 -',b'step 24 0 -',b'ui wait move 0 900']
    builds={};cases={}
    for case in ['baseline','candidate']:
        ident=json.loads((OLD/case/'identity.json').read_text());out=OUT/case;out.mkdir()
        assert sha(ident['ROM'])==ident['ROM_SHA256'] and sha(Path(ident['ROM']).with_suffix('.elf'))==ident['ELF_SHA256']
        for n,h in ident['files_SHA256'].items():assert sha(OLD/case/n)==h;shutil.copyfile(OLD/case/n,out/n)
        (out/'input.route').write_bytes(prefix);(out/'visual-mode.bin').write_bytes(b'\1') # Both compare against certified original.
        (out/'game.sym').write_text((OLD/case/'game.sym').read_text()+(OUT/(case+'-diagnostic.sym')).read_text())
        shutil.copyfile(OUT/(case+'-diagnostic-bindings.json'),out/'diagnostic-bindings.json')
        for n,h in cert['reference_stream_SHA256'].items():assert sha(OLD/'baseline'/n)==h;shutil.copyfile(OLD/'baseline'/n,out/('expected-'+n));assert sha(out/('expected-'+n))==h
        assert sha(out/'game.sav')==sha(f['Save_path'])==f['Save_SHA256']
        record=dict(ident,diagnostic_prefix=True,overall_process=6 if case=='baseline' else 7,baseline_attempt=5,candidate_attempt=1 if case=='baseline' else 2,
          observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),files_SHA256={p.name:sha(p) for p in out.iterdir() if p.is_file()})
        write(out/'identity.json',record);cases[case]=sha(out/'identity.json');builds[case]={k:record[k] for k in ['source','engine_tree','ROM_SHA256','ELF_SHA256','observer_source_SHA256','observer_binary_SHA256','Save_SHA256','overall_process','baseline_attempt','candidate_attempt']}
    storage=dict(f['storage']);storage.update(diagnostic_per_case=970103304,diagnostic_pair=1940206608,diagnostic_frames_max=925,diagnostic_buffer_records=4096,diagnostic_words=64,
      diagnostic_normal_records=925*4096,diagnostic_terminal_reserve_records=1,pair_archive_max=2*1024**3)
    # Retain the larger20GiB original reservation. Its composite envelope covers
    # both new sidecars too, without adding a second native reference writer.
    per_case=sum(storage[k] for k in ['RGB_capture_max_per_case','native_detail_file_max','native_reference_max_per_case','supplemental_reference_max_per_case','edge_bytes_max_per_case','clips_max_per_case','logs_max_per_case','diagnostic_per_case'])
    envelope=2*per_case+storage['pair_archive_max']+64*1024**2;assert envelope<=storage['pair_total_reserved_bytes']
    available=os.statvfs(OUT).f_bavail*os.statvfs(OUT).f_frsize;used=allocated();remaining=max(0,storage['pair_total_reserved_bytes']-used);assert available>=remaining,(available,remaining)
    preserved={str(p):sha(p) for p in [OLD/'STOP.json',OLD/'private-evidence.tar.gz',CERTROOT/'STOP.json',CERTROOT/'private-evidence.tar.gz',CERTROOT/'retained-baseline-acceptance.json',Path(f['Save_path'])]}
    freeze=dict(helper_commit=git('rev-parse','HEAD'),starting_checkpoint='f5c56a4a9a7f2ce51b087668bd8c58c2efb2c02b',base=f['base'],cases=cases,builds=builds,
      Save_path=f['Save_path'],Save_SHA256=f['Save_SHA256'],full_route_SHA256=f['route_SHA256'],prefix_route_SHA256=hashlib.sha256(prefix).hexdigest(),prefix_commands=27,
      reference_stream_SHA256=cert['reference_stream_SHA256'],certificate_SHA256=sha(CERTROOT/'retained-baseline-acceptance.json'),preserved_inputs=preserved,tool_files=tools,
      offline_proof_SHA256=sha(offline/'offline-proof.json'),storage=storage,envelope_bytes=envelope,pre_execution_storage={'allocated_retained_and_new_bytes':used,'available_bytes':available,'required_remaining_bytes':remaining},
      dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts},
      counts_before={'baselines':4,'candidates':1,'processes':5},diagnostic_claim_only=True,first_failure_stop=True,no_automatic_retry=True,no_Save=True)
    write(OUT/'freeze.json',freeze);write(OUT/'freeze-summary.json',{k:v for k,v in freeze.items() if k not in ['dependencies','tool_files','Save_path','preserved_inputs']}|{'freeze_SHA256':sha(OUT/'freeze.json')})
    print('PASS separately named prefix freeze; original full reference/Save/builds copied+verified;20GiB check and sidecar bounds retained; no gameplay')
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--offline',type=Path,required=True);prepare(ap.parse_args().offline)
