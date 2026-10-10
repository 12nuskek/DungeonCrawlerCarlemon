"""One committed Journal build, actual ELF binding, and claim9 admission freeze."""
from pathlib import Path
import importlib.util,json,os,shutil,subprocess,struct
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-journal-admission-r3-20261010')
BUILD=Path('/workspace/scratch/c01a-journal-art-r2-20261010/candidate-build')
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
    OUT.mkdir(exist_ok=True)
    os.environ['PATH']=str(TOOL/'usr/bin')+':'+os.environ['PATH']
    helper_revision=git('rev-parse','HEAD');engine=BUILD/'source/engine';elf=engine/'pokeemerald.elf'
    revision=(BUILD/'tested-commit.txt').read_text().strip()
    assert revision=='4a92a9de70848b9d7275f9f255bb0d2f53232ab8'
    assert git('rev-parse',revision+':engine')==git('rev-parse',helper_revision+':engine')
    subprocess.run(['git','diff','--quiet',revision,helper_revision,'--','scripts/floor1/generate-live-opening.py','scripts/floor1/live-navigation.py','scripts/floor1/journal-combat-notes.py'],cwd=ROOT,check=True)
    assert json.loads((BUILD/'result.json').read_text())['exit']==0
    assert sha(engine/'pokeemerald.gba')=='79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246'
    assert sha(elf)=='7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d'
    for n,h in json.loads((BUILD/'source-inventory.json').read_text()).items():assert sha(BUILD/'source'/n)==h,n
    checks=json.loads((OUT/'notes-complete-offline-proof.json').read_text());assert checks['PASS'] and checks['existing_checker_original_assertions_passed_with_projection'] and checks['accepted_main_legacy_equivalence']['PASS'] and checks['accepted_art_layout_equivalence']['PASS']
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
    excluded={'game.sym','verified-functions.json','native-boundary.json','native-timeline-points.json','edge-profile.json'}
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
    text,proof=profile.profile('candidate');(out/'game.sym').write_text(text);write(out/'bindings-proof.json',proof);write(out/'edge-profile.json',proof)
    assert proof['ELF_SHA256']==sha(elf) and len(proof['points'])==proof['passive_profile_count']==12
    assert json.loads((out/'edge-profile.json').read_text())==json.loads((out/'bindings-proof.json').read_text())
    exported={n:int(a,16) for a,k,n in (line.split() for line in text.splitlines()) if n.startswith('ce_')}
    for i,p in enumerate(proof['points']):
        for key,value in [('pc',p['address']),('op',p['opcode']),('fn',p['function']),('role',p['role']),('kind',p['kind']),('scope',1)]:assert exported[f'ce_{key}{i}']==value
    write(OUT/'fresh-edge-profile-admission.json',{'PASS':True,'actual_ELF_SHA256':sha(elf),'points':12,'both_profile_records_identical':True,'all_exported_symbols_exact':True,'old_profile_excluded':True})
    ident['native_bindings'].update(profile.CB2)
    required=set(__import__('re').findall(r'strcmp\(symbol,\s*"([^"]+)"\)',code));raw=[x.split() for x in text.splitlines()]
    for n in required-{'gDccCollectionProbe','gDccEquipmentProbe','gDccMembershipProbe','gDccRewardProbe'}:
        hits=[a for a,k,s in raw if s==n];assert hits and (len(set(hits))==1 or n=='Task_DisplayHPRestoredMessage'),n
    for n,h in cert['reference_stream_SHA256'].items():assert sha(OLD/'baseline'/n)==h;shutil.copyfile(OLD/'baseline'/n,out/('expected-'+n))
    ident['files_SHA256']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='identity.json'};write(out/'identity.json',ident)
    dependencies={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'scripts').rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    storage=dict(old['storage']);st=os.statvfs(OUT)
    # The original20GiB pair envelope remains. No new baseline will execute:
    # retain that fixed existing case, reserve a complete10GiB candidate case.
    # All original per-file/frame/log/capture bounds remain unchanged.
    retained_bytes=sum(p.stat().st_size for p in OLD.rglob('*') if p.is_file())
    candidate_reserved=storage['pair_total_reserved_bytes']//2
    assert retained_bytes+candidate_reserved<=storage['pair_total_reserved_bytes']
    assert st.f_bavail*st.f_frsize>=candidate_reserved
    freeze=dict(helper_commit=revision,source_checkpoint=revision,base=old['base'],tested=revision,cases={'candidate':sha(out/'identity.json')},Save_path=str(seed),Save_SHA256=sha(seed),route_SHA256=sha(out/'input.route'),dependencies=dependencies,tool_files=old['tool_files'],storage=storage,retained_baseline_certificate_SHA256=sha(CERT),observer_admission=admission,observer_source_SHA256=sha(OUT/'observer.c'),observer_binary_SHA256=sha(OUT/'observer'),counts_before={'actual_baseline':5,'actual_candidate':2,'actual_total':7,'consumed_baseline':6,'consumed_candidate':2,'consumed_total':8},claim9={'case':'candidate','attempt':3,'process_if_launched':8},full_pixels_without_masks=True,first_failure_stop=True,no_Save=True,conditional_field_probe_separate=True)
    freeze['helper_commit']=helper_revision
    freeze['remaining_reservation_check']={'original_pair_envelope_bytes':storage['pair_total_reserved_bytes'],'retained_baseline_fixed_bytes':retained_bytes,'new_candidate_reserved_bytes':candidate_reserved,'available_bytes':st.f_bavail*st.f_frsize,'no_new_baseline_allocation':True,'all_original_per_file_and_frame_bounds_unchanged':True}
    freeze['observer_admission_expected']=admission_expected
    write(OUT/'freeze.json',freeze);print('PASS: actual committed build/ELF/Save/scoped callbacks/full references and executable verified; claim9 frozen; no emulator')
if __name__=='__main__':prepare()
