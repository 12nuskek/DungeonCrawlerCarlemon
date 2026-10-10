"""One committed Journal build, actual ELF binding, and claim9 admission freeze."""
from pathlib import Path
import importlib.util,json,os,shutil,subprocess,struct
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-journal-notes-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
CERT=Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010/retained-baseline-acceptance.json')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
gate=module('journalGate',ROOT/'scripts/floor1/c01a-complete-artifacts.py');sha=gate.sha
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def prepare():
    assert not git('status','--porcelain') and not (OUT/'freeze.json').exists() and not (OUT/'STOP.json').exists()
    revision=git('rev-parse','HEAD');engine=OUT/'candidate-build/source/engine';elf=engine/'pokeemerald.elf'
    assert (OUT/'candidate-build/tested-commit.txt').read_text().strip()==revision
    assert json.loads((OUT/'candidate-build/result.json').read_text())['exit']==0
    old=json.loads((OLD/'freeze.json').read_text());cert=json.loads(CERT.read_text())
    assert cert['PASS'] and sha(CERT)=='2f03fb8b091b2a714ada82becf444c7e7219c244d392b9e740bfc063a88bc95c'
    for n,h in cert['original_r4_artifacts_SHA256'].items():assert sha(OLD/n)==h,n
    for n,h in old['tool_files'].items():assert sha(n)==h,n
    for n,h in dict(cert['named_capture_SHA256'],**cert['numbered_capture_SHA256']).items():assert sha(OLD/'baseline'/n)==h,n
    shutil.copyfile(CERT,OUT/CERT.name)
    code=module('journalTerminal',ROOT/'scripts/floor1/c01a-ui-host-terminal.py').generate(git)
    assert 'busWrite' not in code and __import__('hashlib').sha256(code.encode()).hexdigest()=='1bb218dce0a73cc6d16e2afc0d959104cab0a173495e056e24afb4820ff761ab'
    (OUT/'observer.c').write_text(code)
    retained=Path('/workspace/scratch/c01a-offline-timing-20261010/terminal-fixtures-final/observer-terminal')
    proof=json.loads((retained.parent/'terminal-retention-proof.json').read_text());assert proof['PASS']
    assert sha(retained.parent/'observer-terminal.c')==sha(OUT/'observer.c')
    assert sha(retained)==proof['new_host_binary_SHA256']
    shutil.copyfile(retained,OUT/'observer');os.chmod(OUT/'observer',0o700)
    admission_expected={'SHA256':sha(OUT/'observer'),'mode':0o700,'owner_uid':os.geteuid()}
    admission=module('journalExecutable',ROOT/'scripts/floor1/c01a-prefix-execfile.py').verify_executable(OUT/'observer',admission_expected)
    admission_expected.update(device=admission['device'],inode=admission['inode'])
    out=OUT/'candidate';out.mkdir();prior=json.loads((OLD/'candidate/identity.json').read_text())
    excluded={'game.sym','verified-functions.json','native-boundary.json','native-timeline-points.json'}
    for n,h in prior['files_SHA256'].items():
        assert sha(OLD/'candidate'/n)==h
        if n not in excluded:shutil.copyfile(OLD/'candidate'/n,out/n)
    assert sha(out/'input.route')=='f03cae6c47e866b49209f1a78f6fd2ca34e1653084422b5bab7c3c1e7175b3fa'
    boundary=module('journalBoundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py');native=boundary.write(elf,out/'native-boundary.json')
    assert (native['entry'],native['caller_LR'],native['entry_opcode'])==(0x080008ac,0x080004bf,0xb500)
    nm=str(TOOL/'usr/bin/arm-none-eabi-nm')
    text=subprocess.check_output([nm,'--defined-only',str(elf)],text=True)
    text+=subprocess.check_output(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)],text=True)
    text+=boundary.symbols.export(elf,out/'verified-functions.json');rows=json.loads((out/'verified-functions.json').read_text())
    names={k:v for k,v in prior['native_bindings'].items() if k not in ('uiBagCB2','uiPartyCB2','uiSummaryCB2')}
    for n,i in names.items():
        hit=[r for r in rows if i in r['aliases']];assert len(hit)==1;text+=f"{hit[0]['address']:08x} A {n}\n"
    for n,k in [('Entry','entry'),('Caller','caller_LR'),('Opcode','entry_opcode')]:text+=f"{native[k]:08x} A bv_native{n}\n"
    text+=module('journalTimeline',ROOT/'scripts/floor1/v01-native-timeline-symbols.py').export(elf,out/'native-timeline-points.json')
    (out/'game.sym').write_text(text)
    seed=Path(old['Save_path']);assert sha(seed)==old['Save_SHA256']==sha(out/'game.sav')
    ident=dict(prior,source=revision,engine_tree=git('rev-parse',revision+':engine'),ROM=str(engine/'pokeemerald.gba'),ROM_SHA256=sha(engine/'pokeemerald.gba'),ELF_SHA256=sha(elf),native_bindings=names,observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),overall_process=8,overall_candidate_attempt=3,consumed_claim=9,files_SHA256={})
    write(out/'identity.json',ident)
    profile=module('journalBindings',ROOT/'scripts/floor1/c01a-ui-bindings-r4.py');profile.OLD=OUT
    text,proof=profile.profile('candidate');(out/'game.sym').write_text(text);write(out/'bindings-proof.json',proof)
    ident['native_bindings'].update(profile.CB2)
    required=set(__import__('re').findall(r'strcmp\(symbol,\s*"([^"]+)"\)',code));raw=[x.split() for x in text.splitlines()]
    for n in required-{'gDccCollectionProbe','gDccEquipmentProbe','gDccMembershipProbe','gDccRewardProbe'}:
        hits=[a for a,k,s in raw if s==n];assert hits and (len(set(hits))==1 or n=='Task_DisplayHPRestoredMessage'),n
    for n,h in cert['reference_stream_SHA256'].items():assert sha(OLD/'baseline'/n)==h;shutil.copyfile(OLD/'baseline'/n,out/('expected-'+n))
    ident['files_SHA256']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='identity.json'};write(out/'identity.json',ident)
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    storage=dict(old['storage']);st=os.statvfs(OUT);assert st.f_bavail*st.f_frsize>=storage['pair_total_reserved_bytes']
    freeze=dict(helper_commit=revision,source_checkpoint=revision,base=old['base'],tested=revision,cases={'candidate':sha(out/'identity.json')},Save_path=str(seed),Save_SHA256=sha(seed),route_SHA256=sha(out/'input.route'),dependencies=dependencies,tool_files=old['tool_files'],storage=storage,retained_baseline_certificate_SHA256=sha(CERT),observer_admission=admission,observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),counts_before={'actual_baseline':5,'actual_candidate':2,'actual_total':7,'consumed_baseline':6,'consumed_candidate':2,'consumed_total':8},claim9={'case':'candidate','attempt':3,'process_if_launched':8},full_pixels_without_masks=True,first_failure_stop=True,no_Save=True,conditional_field_probe_separate=True)
    freeze['observer_admission_expected']=admission_expected
    write(OUT/'freeze.json',freeze);print('PASS: actual committed build/ELF/Save/scoped callbacks/full references and executable verified; claim9 frozen; no emulator')
if __name__=='__main__':prepare()
