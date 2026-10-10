"""Separately freeze executable-mode correction; original failed set immutable."""
from pathlib import Path
import hashlib, importlib.util, json, os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[2]
OUT = Path('/workspace/scratch/c01a-diagnostic-prefix-execmode-r2-20261010')
FAILED = Path('/workspace/scratch/c01a-diagnostic-prefix-pair-20261010')
OLD = Path('/workspace/scratch/c01a-action-hints-r4-20261010')
CERTROOT = Path('/workspace/scratch/c01a-retained-baseline-candidate-20261010')
STORAGE_ROOTS = [OLD, CERTROOT, FAILED, OUT]
spec = importlib.util.spec_from_file_location('execfile', ROOT / 'scripts/floor1/c01a-prefix-execfile.py')
execfile = importlib.util.module_from_spec(spec); spec.loader.exec_module(execfile)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2); f.write('\n')
def git(*a): return subprocess.check_output(['git', *a], cwd=ROOT, text=True).strip()

def prepare():
    assert not git('status', '--porcelain') and not (OUT / 'freeze.json').exists()
    old = json.loads((FAILED / 'freeze.json').read_text())
    assert (FAILED / 'baseline/exclusive-claim.json').exists()
    assert not (FAILED / 'baseline/started-process.json').exists()
    assert (FAILED / 'baseline/runtime.log').stat().st_size == 0
    assert not (FAILED / 'candidate/exclusive-claim.json').exists()
    assert json.loads((FAILED / 'STOP.json').read_text())['no_retry']
    # Every original failed-set file remains byte-exact, not merely its STOP.
    preserved = dict(old['preserved_inputs'])
    preserved.update({str(p): sha(p) for p in FAILED.rglob('*') if p.is_file()})
    for p, h in old['preserved_inputs'].items(): assert sha(p) == h, p
    for p, h in old['tool_files'].items(): assert sha(p) == h, p
    for p, h in old['dependencies'].items(): assert sha(ROOT / p) == h, p
    proof = json.loads((FAILED / 'offline05/offline-proof.json').read_text())
    assert proof['PASS'] and sha(FAILED / 'offline05/offline-proof.json') == old['offline_proof_SHA256']
    mode_proof = json.loads((OUT / 'execmode-offline-proof.json').read_text()); assert mode_proof['PASS']
    for p, h in mode_proof['source_SHA256'].items(): assert sha(ROOT / p) == h, p
    expected = {'SHA256': proof['observer_binary_SHA256'], 'mode': 0o700, 'owner_uid': os.geteuid()}
    source_check = execfile.verify_executable(FAILED / 'offline05/observer', expected)
    shutil.copyfile(FAILED / 'offline05/observer.c', OUT / 'observer.c')
    shutil.copyfile(FAILED / 'offline05/observer', OUT / 'observer')
    # Permission change is exclusively to this newly copied regular observer.
    assert (OUT / 'observer').is_file() and not (OUT / 'observer').is_symlink()
    (OUT / 'observer').chmod(0o700)
    copy_check = execfile.verify_executable(OUT / 'observer', expected)
    expected.update(device=copy_check['device'], inode=copy_check['inode'])
    assert sha(OUT / 'observer.c') == proof['observer_source_SHA256']
    cases = {}; builds = {}
    for case in ('baseline', 'candidate'):
        src = FAILED / case; dst = OUT / case; dst.mkdir()
        i = json.loads((src / 'identity.json').read_text()); assert sha(src / 'identity.json') == old['cases'][case]
        for n, h in i['files_SHA256'].items():
            assert sha(src / n) == h, n; shutil.copyfile(src / n, dst / n); assert sha(dst / n) == h
        assert sha(i['ROM']) == i['ROM_SHA256'] and sha(Path(i['ROM']).with_suffix('.elf')) == i['ELF_SHA256']
        assert sha(dst / 'game.sav') == sha(old['Save_path']) == old['Save_SHA256']
        assert sha(dst / 'input.route') == old['prefix_route_SHA256']
        i.update(overall_process=7 if case == 'baseline' else 8, baseline_attempt=6,
                 candidate_attempt=1 if case == 'baseline' else 2,
                 actual_emulator_process_if_launched=6 if case == 'baseline' else 7,
                 actual_baseline_run_if_launched=5,
                 files_SHA256={p.name: sha(p) for p in dst.iterdir() if p.is_file()})
        write(dst / 'identity.json', i); cases[case] = sha(dst / 'identity.json')
        builds[case] = {k: i[k] for k in ('source', 'engine_tree', 'ROM_SHA256', 'ELF_SHA256',
            'observer_source_SHA256', 'observer_binary_SHA256', 'Save_SHA256', 'overall_process',
            'baseline_attempt', 'candidate_attempt', 'actual_emulator_process_if_launched')}
    used = sum(p.stat().st_size for r in STORAGE_ROOTS for p in r.rglob('*') if p.is_file())
    st = os.statvfs(OUT); available = st.f_bavail * st.f_frsize
    required = max(0, old['storage']['pair_total_reserved_bytes'] - used); assert available >= required
    freeze = dict(old, helper_commit=git('rev-parse', 'HEAD'),
        starting_checkpoint='9bcda7fba27a32cfdada3c3bebce44985a5eebd0',
        cases=cases, builds=builds, preserved_inputs=preserved,
        observer_executable=expected, observer_source_file_check=source_check,
        observer_copy_file_check=copy_check, executable_mode_offline_proof_SHA256=sha(OUT / 'execmode-offline-proof.json'),
        claimed_counts_before={'baseline': 5, 'candidate': 1, 'total': 6},
        actual_counts_before={'baseline': 4, 'candidate': 1, 'total': 5},
        pre_execution_storage={'allocated_retained_and_new_bytes': used, 'available_bytes': available,
                               'required_remaining_bytes': required},
        dependencies={p.relative_to(ROOT).as_posix(): sha(p) for p in (ROOT / 'scripts').rglob('*')
                      if p.is_file() and '__pycache__' not in p.parts})
    # Final read-only mode/bytes/owner/identity/access check immediately before freeze.
    execfile.verify_executable(OUT / 'observer', expected)
    write(OUT / 'freeze.json', freeze)
    write(OUT / 'freeze-summary.json', {k: v for k, v in freeze.items()
        if k not in ('dependencies', 'tool_files', 'Save_path', 'preserved_inputs',
                     'observer_source_file_check', 'observer_copy_file_check')}
        | {'freeze_SHA256': sha(OUT / 'freeze.json')})
    print('PASS separately named executable-mode freeze; observer reused without compilation; no gameplay')

if __name__ == '__main__': prepare()
