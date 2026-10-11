"""One separately reviewed Continue-only cold from the actual Warden Save.

The completed two-mode root and its STOP are immutable inputs, never resumed.
Import and offline proposals grant no authority. No observer is rebuilt here.
"""
from pathlib import Path
import contextlib, fcntl, hashlib, importlib.util, json, os, shutil, subprocess, time

if not __debug__:
    raise RuntimeError('enabled full-state checks required')
ROOT = Path(__file__).resolve().parents[2]

def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

old = module('cold_original_supervisor', 'scripts/floor1/warden-runtime-supervisor.py')
p = module('cold_preserved_representation', 'scripts/floor1/warden-rgb-production.py')
b, require, sha, read = old.b, old.require, old.sha, old.read
BASE = 'ac982c73f2d452328008e6c7ca264991ea46f781'
EARNED_SOURCE = '3eeb8d71e81e7f193d010f598786feacd7c0c19b'
SAVE_SHA = '1364b226eaac3721beca190cc0510fef0d606f6eaaf603369fc27d7565923d53'
STATE_SHA = 'ad4353347e2b10f2f28f238f3942ac5d97079a4bdea75f8190316058a375ae38'
OLD_STOP_SHA = 'ab5a2fe1b10592c83d62f1a725ae729eb0994e769955a84603db4a04944255a5'
PRESERVED_SHA = 'a3e6a8e88ff26264a23e77f298dffa4604ab1c5fa50f45a2f36730976dd28aea'
MAPPING_SHA = 'c800e581a99e4a2975a52dedb1ee5849bd245426832e788040877fefd0d0e835'
ROUTE_SHA = '29400d7b31937b4f4c38231bbe8172e7c108b60ff9a908cdf4d5cd9253672fac'
MODE = 'warden-new-save-cold'
OUT = b.SCRATCH / 'c01-warden-cold-only-runtime-r1-20261011'
OFFLINE = b.SCRATCH / 'c01-warden-cold-only-offline-r1-20261011'
AUTHORITY = b.SCRATCH / 'c01-warden-cold-only-authority-r1-20261011.json'
REVIEW = b.SCRATCH / 'c01-warden-cold-only-source-review-r1-20261011.json'
CONTRACT = ROOT / 'scripts/contracts/f1-c01-warden-cold-only-r1.json'
PRESERVED = p.OFFLINE / 'actual-preservation-final-handoff-private.json'
SAVE = old.OUT / 'warden-continuation/game.sav'
STATE = old.OUT / 'warden-continuation/phase-05-state.bin'
ROUTE = old.OUT / (MODE + '.route')
FILES = ('scripts/floor1/warden-cold-only-supervisor-r1.py',
         'scripts/run-f1-c01-warden-cold-only-r1.py',
         'scripts/test-warden-cold-only-offline-r1.py',
         'scripts/contracts/f1-c01-warden-cold-only-r1.json',
         'docs/floor1/c01-warden-cold-only-r1-contract.md')
ENTRY_FILES = (FILES[1], FILES[0], 'scripts/floor1/warden-continuation-state.py')
COPY_FILES = ('observer.c', 'observer', 'game.sym', 'actual-Warden-success-input.sav',
              'expected-final-state.bin', MODE + '.route', 'source-contract.json',
              'offline-admission-private.json', 'source-checkpoint.tar')
NATIVE_FILES = ('game.sav', 'expected-final-state.bin', 'current-state.bin',
                'runtime.log', 'errors.log', 'frame-index.bin', 'motion-000.rgb',
                'motion-001.rgb', 'cold.ppm', 'complete-field-trace-private.bin',
                'complete-battle-trace-private.bin', 'input-binding-private.json',
                'capacity-before-process-private.json', 'process-started.json')
VERDICT_KEYS = {'PASS', 'PID', 'assertions', 'battle_attempts', 'battle_frames', 'captures',
                'deferred', 'frames', 'full_14_sector_live_disk_verified', 'handoff_files',
                'independent_backup_verified', 'mode', 'process_clock', 'source_commit',
                'valid', 'wall_seconds'}
IO_METHODS = ('authority', 'locked', 'admit', 'inputs', 'claim', 'launch', 'wait',
              'native_result', 'persist', 'stop', 'terminal')

def expected_contract():
    return dict(schema='c01-Warden-earned-Save-Continue-only/v1', preparation_base=BASE,
        earned_source=EARNED_SOURCE, input_Save_SHA256=SAVE_SHA, input_state_SHA256=STATE_SHA,
        old_STOP_SHA256=OLD_STOP_SHA, preservation_handoff_SHA256=PRESERVED_SHA,
        mapping_SHA256=MAPPING_SHA, route_SHA256=ROUTE_SHA, native_mode=MODE,
        frames=2044, encounters=0, wall_seconds=600, reservation_bytes=old.RESERVATION,
        claims=1, first_failure_terminal=True, retry=False, native_TV_WATCH=2193,
        TV_WATCH_expected=True, TV_START_expected=False, expected_map=[35, 4],
        expected_position=[8, 6], expected_facing=1, expected_section=218,
        expected_counter=20, expected_poison=1, complete_fourteen_sectors=True,
        complete_disk_live_post_Continue=True, unchanged_Save=True,
        game_source=b.GAME_SOURCE, engine_tree=b.ENGINE_TREE, ROM_SHA256=b.ROM_SHA,
        ELF_SHA256=b.ELF_SHA, observer_SHA256='9aff6f4c610913e178c9ff312f24639292967130e6e997bc3a4b2115dad2b58b',
        observer_source_SHA256='b7e16d840b78951cc357f22f0a8ab7246775596d31c42ec944fe352c76625af5',
        execution_permitted=False)

def contract():
    value = read(CONTRACT)
    require(old.canonical(value) == old.canonical(expected_contract()), 'exact immutable cold-only contract')
    return value

def lineage():
    require(sha(old.OUT / 'STOP.json') == OLD_STOP_SHA, 'old terminal STOP changed')
    require(sha(p.s.HANDOFF) == p.s.HANDOFF_SHA, 'actual Warden handoff changed')
    h = read(p.s.HANDOFF)
    f = read(old.OUT / 'freeze.json')
    require(f['source_commit'] == h['tested_source_commit'] == h['published_source_commit'] == EARNED_SOURCE,
            'actual earned source lineage')
    require(sha(old.OUT / 'freeze.json') == h['freeze_SHA256'], 'actual Warden freeze lineage')
    require(sha(old.AUTHORITY) == f['authority_SHA256'] == h['authority_SHA256'],
            'original consumed authority retained as lineage only')
    v = old.verify_continuation_handoff(f)
    require(set(v) == VERDICT_KEYS and v['mode'] == 'warden-continuation' and
            v['PID'] == 214005 and sha(old.OUT / 'warden-continuation-verdict-private.json') == h['actual_continuation_verdict_SHA256'],
            'complete exact native success handoff schema')
    require(sha(SAVE) == SAVE_SHA and sha(STATE) == STATE_SHA and sha(ROUTE) == ROUTE_SHA,
            'unchanged actual Save/state/route lineage')
    old.state.cold_equivalence(old.state.snapshot(STATE), old.state.snapshot(STATE), SAVE)
    paths = (p.s.HANDOFF, old.OUT / 'freeze.json', old.AUTHORITY,
             old.OUT / 'warden-continuation-exclusive-claim.json',
             old.OUT / 'warden-continuation-verdict-private.json',
             old.OUT / 'warden-continuation/process-started.json',
             old.OUT / 'warden-continuation/input-binding-private.json',
             old.OUT / 'warden-continuation/runtime.log', old.OUT / 'warden-continuation/errors.log',
             SAVE, STATE, ROUTE, old.OUT / 'STOP.json')
    return {str(path): sha(path) for path in paths}

def representation():
    require(sha(PRESERVED) == PRESERVED_SHA, 'accepted preservation handoff changed')
    h = read(PRESERVED)
    require(h['PASS'] and h['source'] == BASE and h['Save_SHA256'] == SAVE_SHA and
            h['actual_controllers'] == 1 and h['actual_fresh_complete_verifiers'] == 2 and
            h['actual_verifier_PIDs'] == [216608, 216695], 'completed exact local preservation')
    for path, entry in h['private_artifacts'].items():
        p.check_entry(path, entry)
    mapping = read(p.OUT / p.c.MAPPING_NAME)
    require(sha(p.OUT / p.c.MAPPING_NAME) == MAPPING_SHA and len(mapping['chunks']) == 13,
            'missing/changed compressed evidence mapping')
    rows = [json.loads(line) for line in (p.OUT / p.PROGRESS).read_bytes().splitlines()]
    require(rows == [dict(removed_path=row['raw_path'], compressed_SHA256=row['compressed_SHA256'],
        raw_SHA256=row['raw_SHA256'], completed_removals=i+1) for i, row in enumerate(mapping['chunks'])],
        'complete durable replacement journal')
    require(all(not os.path.lexists(row['raw_path']) for row in mapping['chunks']),
            'only accepted compressed representation; no raw restoration')
    prep = p.accepted_inputs()
    p.LocalIO().protected_check(prep)
    require(p.metadata_usage() == dict(files=58, logical_bytes=4945744, allocated_bytes=5140480),
            'accepted combined preservation metadata unchanged')
    return dict(handoff_SHA256=PRESERVED_SHA, mapping_SHA256=MAPPING_SHA,
        artifacts=h['private_artifacts'], chunks=mapping['chunks'], frames=24207,
        original_bytes=2788646400, protected_entries=prep['protected_entries'],
        historical_protection_refs=prep['historical_protection_refs'],
        ordering_limit='reviewed controller/sealed barrier/journal; no independent per-unlink syscall trace',
        independent_backup_verified=False)

def derive_validator(env):
    # Reuse the reviewed import-only probe with these exact new entry files.
    path = ROOT / 'scripts/floor1/warden-runtime-validator-closure.py'
    code = ('import importlib.util; s=importlib.util.spec_from_file_location("cold_probe",' + repr(str(path)) +
            '); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); v.ENTRY_FILES=' + repr(ENTRY_FILES) + '; v.probe()')
    result = subprocess.run([b.provider('python3'), '-B', '-c', code], cwd=ROOT,
                            env=env, capture_output=True, text=True, timeout=30)
    require(result.returncode == 0 and not result.stderr and len(result.stdout) < 8*1024**2,
            'exact cold helper import derivation')
    probe = json.loads(result.stdout)
    require(probe['entry_files'] == list(ENTRY_FILES) and probe['entry_points_executed'] == probe['emulators'] == 0,
            'import-only cold helper closure')
    adapter = module('cold_validator_link_adapter', 'scripts/floor1/warden-runtime-validator-closure.py')
    adapter._probe = probe
    return adapter.derive(env)

def build_proposal():
    head = b.git('rev-parse', 'HEAD')
    require(not b.git('status', '--porcelain') and b.git('branch', '--show-current') == old.BRANCH,
            'clean committed cold-only source')
    require(b.git('merge-base', BASE, head) == BASE and set(b.git('diff', '--name-only', BASE, head).splitlines()) == set(FILES),
            'focused five-file cold-only delta')
    contract()
    earned, preserved = lineage(), representation()
    parent = read(p.PRODUCTION)
    sources = dict(parent['source_files_SHA256'])
    sources.update({rel: sha(ROOT / rel) for rel in FILES})
    config = read(b.CONFIG)
    env = b.environment(Path(config['tool_root']))
    require(env == parent['environment'], 'unchanged exact provider environment')
    closure = derive_validator(env)
    project = {str(Path(path).relative_to(ROOT)): pin for path, pin in closure['files'].items() if Path(path).is_relative_to(ROOT)}
    require(set(project) <= set(sources) and all(sources[rel] == pin for rel, pin in project.items()),
            'complete existing plus new helper source closure; no dropped dependency')
    tree = {}
    for row in b.git_bytes('ls-tree', '-rz', head).split(b'\0'):
        if row:
            fields, rel = row.split(b'\t')
            mode, kind, oid = fields.split()
            require(kind == b'blob', 'tracked source blob required')
            tree[rel.decode()] = oid.decode()
    tracked, runtime = set(sources) & set(tree), set(sources) - set(tree)
    original = read(b.ACCEPTED / 'offline-receipt-private.json')
    frozen = read(old.OUT / 'freeze.json')
    require(len(sources) == 2681 and len(tracked) == 2666 and len(runtime) == 15 and
            runtime <= set(frozen['source_files']), 'complete tracked/sealed runtime partition')
    for rel, pin in sources.items():
        data = (ROOT / rel).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin, 'current cold source byte hash')
        if rel in tracked:
            require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == tree[rel], 'actual tracked commit blob')
        else:
            require(pin == frozen['source_files'][rel] == config['files'][str(ROOT / rel)] == original['input_pins'][str(ROOT / rel)],
                    'original sealed runtime receipt chain')
    prep = read(p.s.PREPARATION / 'proposal-contract-private.json')
    tools = b.merge_exact(prep['actual_provider_files_SHA256'], closure['files'], parent['codec']['tool_dependencies_SHA256'])
    for path, pin in tools.items():
        require(sha(path) == pin, 'current exact provider/helper byte closure')
    artifacts = {name: sha(old.OUT / name) for name in ('observer.c', 'observer', 'game.sym')}
    require(artifacts['observer'] == expected_contract()['observer_SHA256'] and
            artifacts['observer.c'] == expected_contract()['observer_source_SHA256'], 'unchanged tested observer; no rebuild')
    return dict(schema='c01-cold-only-offline-proposal/v1', source_commit=head, source_base=BASE,
        direct_files=list(FILES), source_files=sources, tracked_files=sorted(tracked),
        sealed_runtime_files=sorted(runtime), provider_files=tools, validator_closure=closure,
        provider_environment=env, python3_alias=b.python_alias(env), contract=contract(),
        contract_SHA256=sha(CONTRACT), lineage=earned, representation=preserved,
        input_Save_SHA256=SAVE_SHA, input_state_SHA256=STATE_SHA, route_SHA256=ROUTE_SHA,
        observer_artifacts=artifacts, runtime_output=str(OUT), authority_path=str(AUTHORITY),
        reservation_bytes=old.RESERVATION, execution_permitted=False, runtime='CLOSED', retry=False)

def authority_template(receipt, receipt_sha):
    return dict(status='APPROVED_ONE_SEPARATE_CONTINUE_ONLY_COLD', source_commit=receipt['source_commit'],
        offline_receipt_SHA256=receipt_sha, proposal_SHA256=receipt['proposal_SHA256'],
        contract_SHA256=receipt['proposal']['contract_SHA256'], output_root=str(OUT),
        input_Save_SHA256=SAVE_SHA, claims=1, encounters=0, frames=2044, wall_seconds=600,
        reservation_bytes=old.RESERVATION, parent_review_verified=True, retry=False)

def validate_gate(proposal, current, authority, receipt, receipt_sha, present):
    require(receipt['PASS'] is True and receipt['execution_permitted'] is False and
            receipt['positive_first'] is True and old.canonical(receipt['proposal']) == old.canonical(proposal) and
            receipt['source_commit'] == proposal['source_commit'] and
            receipt['proposal_SHA256'] == old.digest(proposal), 'complete exact offline admission')
    require(old.canonical(current) == old.canonical(proposal), 'stale/changed source/provider/Save/lineage/representation')
    require(old.canonical(authority) == old.canonical(authority_template(receipt, receipt_sha)), 'wrong/consumed separate cold authority')
    require(not {'STOP.json', 'PREPARATION-STOP.json', 'exclusive-claim.json', MODE, 'verdict-private.json'} & set(present),
            'one-use cold lifecycle; first failure/result/claim terminal')

def parse_footer(log):
    footer = old.parse_footer(log, MODE)
    require(footer['frames'] == 2044 and footer['battle_attempts'] == 0 and footer['battle_frames'] == [0, 0, 0, 0],
            'exact2044-frame zero-encounter cold result')
    require(log.count('PASS full native Warden continuation cold\n') == 1,
            'complete native cold helper result')
    return footer

def check_root_usage():
    budget = old.storage()['processes']['cold']
    total = 0
    for path in OUT.iterdir():
        require(not path.is_symlink(), 'no cold output aliases')
        if path.is_dir():
            require(path.name == MODE, 'only one cold directory')
            files = list(path.rglob('*'))
            require(all(not x.is_symlink() for x in files), 'no cold evidence aliases')
            sizes = [x.stat() for x in files if x.is_file()]
            require(max(sum(s.st_size for s in sizes), sum(s.st_blocks*512 for s in sizes)) <= budget['bytes'], 'unchanged cold storage bound')
            require(all(s.st_size <= budget['per_file_limit_bytes'] for s in sizes), 'cold file bound')
            require(all(x.stat().st_size <= budget['per_log_bytes'] for x in files if x.name.endswith('.log')), 'cold log bound')
        else:
            total += max(path.stat().st_size, path.stat().st_blocks*512)
    require(total <= 256*1024**2, 'cold source/root headroom bound')

# Isolate only the reviewed clock/capacity helpers' two data bindings. The original
# supervisor instance used by lineage() retains its old root and terminal STOP.
timing = module('cold_isolated_runtime_clock', 'scripts/floor1/warden-runtime-supervisor.py')
timing.OUT, timing.check_root_usage = OUT, check_root_usage

def verify_frozen(frozen, receipt, authority_sha):
    proposal = receipt['proposal']
    require(set(frozen) == {'source_commit', 'proposal_SHA256', 'files', 'executable', 'authority_SHA256'}, 'complete separate cold freeze schema')
    require(frozen['source_commit'] == proposal['source_commit'] and frozen['proposal_SHA256'] == receipt['proposal_SHA256'] and
            frozen['authority_SHA256'] == authority_sha and set(frozen['files']) == set(COPY_FILES), 'exact separate cold freeze binding')
    expected = dict(proposal['observer_artifacts'])
    expected.update({'actual-Warden-success-input.sav': SAVE_SHA, 'expected-final-state.bin': STATE_SHA,
                     MODE+'.route': ROUTE_SHA, 'source-contract.json': proposal['contract_SHA256'],
                     'offline-admission-private.json': sha(OFFLINE/'offline-admission-private.json')})
    for name, pin in frozen['files'].items():
        require(sha(OUT/name) == pin and (name == 'source-checkpoint.tar' or expected[name] == pin), 'frozen cold file changed')
    require(frozen['executable']['SHA256'] == proposal['observer_artifacts']['observer'], 'frozen observer hash')
    old.execfile.verify_executable(OUT/'observer', frozen['executable'])

def input_binding(proposal):
    return dict(input_Save_SHA256=SAVE_SHA, actual_new_Save=True, source_state_SHA256=STATE_SHA,
                earned_source=EARNED_SOURCE, lineage_SHA256=old.digest(proposal['lineage']))

def validate_launch_records(records, frozen, receipt, pid, clock):
    require(set(records) == {'binding','claim','capacity','started','hashes'}, 'complete launch evidence schema')
    pins = records['hashes']
    require(set(pins) == {'freeze','binding','claim','capacity'}, 'complete launch evidence hash set')
    require(records['binding'] == input_binding(receipt['proposal']), 'exact actual earned input binding')
    require(records['claim'] == dict(source_commit=frozen['source_commit'], mode=MODE,
        freeze_SHA256=pins['freeze'], input_binding_SHA256=pins['binding'], route_SHA256=ROUTE_SHA,
        limit=1, terminal_on_failure=True), 'exact actual exclusive cold claim')
    cap = records['capacity']
    require(set(cap) == {'fresh_available_bytes','required_bytes','source_commit','mode','measured_time_ns',
        'measured_immediately_before_creation','prepared_credit'}, 'exact fresh capacity record schema')
    require(cap['required_bytes'] == old.RESERVATION and cap['source_commit'] == frozen['source_commit'] and
        cap['mode'] == MODE and cap['measured_immediately_before_creation'] is True and cap['prepared_credit'] is False and
        type(cap['measured_time_ns']) is int and cap['measured_time_ns'] > 0, 'full fresh capacity provenance; no credit')
    old.capacity(cap['fresh_available_bytes'])
    require(records['started'] == dict(pid=pid, mode=MODE, source_commit=frozen['source_commit'],
        exclusive_claim_SHA256=pins['claim'], capacity_record_SHA256=pins['capacity'],
        creation_monotonic=clock['creation_monotonic'], wall_limit_seconds=600), 'actual PID/claim/capacity/creation clock binding')

class LocalIO:
    def __init__(self): self.created_process = None
    def authority(self):
        require(AUTHORITY.is_file(), 'CLOSED: separately reviewed cold-only authority absent')
        identity = p.e.identity(AUTHORITY)
        require(identity['uid'] == os.geteuid() and identity['mode'] == 0o600 and
                AUTHORITY.stat().st_nlink == 1, 'private owned single-link cold authority')
        receipt = read(OFFLINE/'offline-admission-private.json')
        require(old.canonical(read(AUTHORITY)) == old.canonical(authority_template(receipt, sha(OFFLINE/'offline-admission-private.json'))), 'wrong separate cold authority')
        require(dict(os.environ) == receipt['proposal']['provider_environment'], 'exact cold process provider environment')
        require(sha(OFFLINE/'positive-modeled-cold-lifecycle-private.json') == receipt['positive_receipt_SHA256'],
                'sealed positive cold lifecycle proof')
        require(b.git('ls-remote', '--heads', 'origin', old.BRANCH) == receipt['source_commit']+'\trefs/heads/'+old.BRANCH, 'exact published cold source')
        return receipt
    @contextlib.contextmanager
    def locked(self):
        with (OUT/'exclusive.lock').open('r+') as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            yield
    def admit(self, receipt):
        require(not OUT.is_symlink() and OUT.stat().st_mode & 0o777 == 0o700,
                'private separate cold root')
        validate_gate(receipt['proposal'], build_proposal(), read(AUTHORITY), receipt,
                      sha(OFFLINE/'offline-admission-private.json'), {x.name for x in OUT.iterdir()})
        frozen = read(OUT/'freeze.json')
        verify_frozen(frozen, receipt, sha(AUTHORITY))
        check_root_usage()
        old.capacity(shutil.disk_usage(OUT).free)
        return frozen
    def inputs(self, frozen):
        directory = OUT/MODE
        directory.mkdir(mode=0o700)
        for source, target, pin in ((OUT/'actual-Warden-success-input.sav', 'game.sav', SAVE_SHA),
                                    (OUT/'expected-final-state.bin', 'expected-final-state.bin', STATE_SHA)):
            shutil.copyfile(source, directory/target)
            os.chmod(directory/target, 0o600)
            require(sha(directory/target) == pin, 'exact earned cold input copy')
            with (directory/target).open('rb') as file: os.fsync(file.fileno())
        old.write(directory/'input-binding-private.json', input_binding(read(OFFLINE/'offline-admission-private.json')['proposal']))
    def claim(self, frozen):
        old.write(OUT/'exclusive-claim.json', dict(source_commit=frozen['source_commit'], mode=MODE,
            freeze_SHA256=sha(OUT/'freeze.json'), input_binding_SHA256=sha(OUT/MODE/'input-binding-private.json'),
            route_SHA256=ROUTE_SHA, limit=1, terminal_on_failure=True))
    def launch(self, receipt, frozen, clock):
        self.frozen, self.clock = frozen, clock
        directory = OUT/MODE
        config = read(b.CONFIG)
        rom = next(path for path in config['files'] if path.endswith('pokeemerald.gba'))
        old.execfile.verify_executable(OUT/'observer', frozen['executable'])
        with (OUT/(MODE+'.route')).open('rb') as route, (directory/'runtime.log').open('xb') as log, (directory/'errors.log').open('xb') as error:
            process = timing.capacity_before_creation(directory/'capacity-before-process-private.json', MODE,
                frozen['source_commit'], timing.create_process,
                [str(OUT/'observer'), rom, str(directory/'game.sav'), str(OUT/'game.sym'), MODE],
                cwd=directory, stdin=route, stdout=log, stderr=error, env=receipt['proposal']['provider_environment'],
                preexec_fn=timing.process_limits, start_new_session=True, lifecycle_clock=clock)
            self.created_process = process  # Retain ownership if recording its start fails.
        old.write(directory/'process-started.json', dict(pid=process.pid, mode=MODE,
            source_commit=frozen['source_commit'], exclusive_claim_SHA256=sha(OUT/'exclusive-claim.json'),
            capacity_record_SHA256=sha(directory/'capacity-before-process-private.json'),
            creation_monotonic=clock['creation_monotonic'], wall_limit_seconds=600))
        return process
    wait = staticmethod(timing.wait_process)
    stop = staticmethod(timing.stop_process)
    def native_result(self, receipt, process):
        directory = OUT/MODE
        require(read(OUT/'freeze.json') == self.frozen, 'unchanged actual cold freeze')
        verify_frozen(self.frozen, receipt, sha(AUTHORITY))
        records = dict(binding=read(directory/'input-binding-private.json'), claim=read(OUT/'exclusive-claim.json'),
            capacity=read(directory/'capacity-before-process-private.json'), started=read(directory/'process-started.json'),
            hashes=dict(freeze=sha(OUT/'freeze.json'), binding=sha(directory/'input-binding-private.json'),
                        claim=sha(OUT/'exclusive-claim.json'), capacity=sha(directory/'capacity-before-process-private.json')))
        validate_launch_records(records, self.frozen, receipt, process.pid, self.clock)
        require(not (directory/'errors.log').stat().st_size, 'native cold errors')
        footer = parse_footer((directory/'runtime.log').read_text())
        require({x.name for x in directory.iterdir()} == set(NATIVE_FILES), 'complete exact cold evidence namespace')
        require(sha(directory/'game.sav') == sha(SAVE) == SAVE_SHA and sha(directory/'expected-final-state.bin') == sha(STATE) == STATE_SHA,
                'cold Save/state input unchanged')
        old.state.cold_equivalence(old.state.snapshot(directory/'expected-final-state.bin'),
                                   old.state.snapshot(directory/'current-state.bin'), directory/'game.sav')
        captures = old.verify_captures(directory, footer, MODE)
        require(build_proposal() == receipt['proposal'], 'all source/provider/lineage/representation inputs unchanged after cold')
        check_root_usage()
        return dict(footer=footer, captures=captures, full_14_sector_live_disk_verified=True,
                    files={name: sha(directory/name) for name in NATIVE_FILES}, unchanged_Save=True)
    def persist(self, result): old.write(OUT/'verdict-private.json', result)
    def terminal(self, error, process, clock):
        if not (OUT/'STOP.json').exists() and not (OUT/'verdict-private.json').exists():
            old.write(OUT/'STOP.json', dict(PASS=False, source_commit=b.git('rev-parse', 'HEAD'), mode=MODE,
                reason=str(error)[:2000], PID=None if process is None else process.pid,
                process_clock=clock, first_failure_terminal=True, retry=False, actual_processes=int(process is not None)))

def validate_result(result, receipt):
    expected = {'PASS', 'source_commit', 'mode', 'PID', 'footer', 'captures', 'files',
                'full_14_sector_live_disk_verified', 'unchanged_Save', 'process_clock',
                'wall_seconds', 'proposal_SHA256', 'independent_backup_verified'}
    require(set(result) == expected and result['PASS'] is True and result['source_commit'] == receipt['source_commit'] and
            result['mode'] == MODE and type(result['PID']) is int and result['PID'] > 0 and
            result['proposal_SHA256'] == receipt['proposal_SHA256'], 'complete exact native cold verdict schema')
    f = result['footer']
    require(set(f) == {'frames','valid','deferred','battle_attempts','battle_frames','assertions'} and
            f['frames'] == 2044 and f['valid']+f['deferred'] == 2044 and f['valid'] > 0 and f['assertions'] > 0 and
            f['battle_attempts'] == 0 and f['battle_frames'] == [0,0,0,0], 'exact cold frame/state/zero-encounter footer')
    require(result['full_14_sector_live_disk_verified'] is True and result['unchanged_Save'] is True and
            set(result['files']) == set(NATIVE_FILES) and result['files']['game.sav'] == SAVE_SHA and
            result['files']['expected-final-state.bin'] == STATE_SHA, 'full sector/state/Save/native output required')
    require(result['captures']['frames'] == 2044 and set(result['captures']['motion_SHA256']) == {'motion-000.rgb','motion-001.rgb'} and
            set(result['captures']['captures_SHA256']) == {'cold.ppm'}, 'complete native cold capture result')
    require(result['captures']['index_SHA256'] == result['files']['frame-index.bin'] and
        all(result['captures']['motion_SHA256'][name] == result['files'][name] for name in ('motion-000.rgb','motion-001.rgb')) and
        result['captures']['captures_SHA256']['cold.ppm'] == result['files']['cold.ppm'], 'native capture/file hash identities')
    require(set(result['captures']) == {'frames','index_SHA256','motion_SHA256','captures_SHA256'} and
            set(result['process_clock']) == {'creation_monotonic','termination_monotonic'}, 'exact cold capture/clock schema')
    require(result['wall_seconds'] == timing.execution_elapsed(result['process_clock']), 'creation-through-exit interval identity')

def execute(io=None):
    io = LocalIO() if io is None else io
    require(all(callable(getattr(io, name, None)) for name in IO_METHODS), 'complete cold-only IO interface')
    receipt = io.authority()
    process, clock, owned = None, {}, False
    try:
        with io.locked():
            owned = True
            frozen = io.admit(receipt)
            io.inputs(frozen)
            io.claim(frozen)
            process = io.launch(receipt, frozen, clock)
            require(io.wait(process, clock) == 0, 'native first failure terminal')
            result = dict(PASS=True, source_commit=receipt['source_commit'], mode=MODE, PID=process.pid,
                **io.native_result(receipt, process), process_clock=clock,
                wall_seconds=timing.execution_elapsed(clock), proposal_SHA256=receipt['proposal_SHA256'],
                independent_backup_verified=False)
            validate_result(result, receipt)
            io.persist(result)
            return result
    except BaseException as error:
        if process is None: process = getattr(io, 'created_process', None)
        io.stop(process)
        if process is not None and 'termination_monotonic' not in clock:
            clock['termination_monotonic'] = time.monotonic()
        if owned: io.terminal(error, process, clock)
        raise

def prepare():
    io = LocalIO()
    receipt = io.authority()  # Refuse before any filesystem write without new authority.
    require(not os.path.lexists(OUT), 'fresh separately named cold root only')
    proposal = build_proposal()
    validate_gate(proposal, proposal, read(AUTHORITY), receipt, sha(OFFLINE/'offline-admission-private.json'), set())
    old.capacity(shutil.disk_usage(b.SCRATCH).free)
    OUT.mkdir(mode=0o700)
    old.sync(OUT.parent)
    try:
        with (OUT/'exclusive.lock').open('xb') as lock:
            os.fchmod(lock.fileno(), 0o600)
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            sources = {name: old.OUT/name for name in ('observer.c','observer','game.sym')}
            sources.update({'actual-Warden-success-input.sav': SAVE, 'expected-final-state.bin': STATE,
                            MODE+'.route': ROUTE, 'source-contract.json': CONTRACT,
                            'offline-admission-private.json': OFFLINE/'offline-admission-private.json'})
            for name, path in sources.items():
                shutil.copyfile(path, OUT/name)
                os.chmod(OUT/name, 0o700 if name == 'observer' else 0o600)
                with (OUT/name).open('rb') as file: os.fsync(file.fileno())
            with (OUT/'source-checkpoint.tar').open('xb') as file:
                subprocess.run([b.provider('git'), 'archive', proposal['source_commit'], 'scripts', FILES[-1]],
                               cwd=ROOT, env=b.git_environment(), stdout=file, check=True, timeout=30)
                file.flush(); os.fsync(file.fileno())
            require((OUT/'source-checkpoint.tar').stat().st_size < 32*1024**2, 'cold source checkpoint bound')
            info = (OUT/'observer').lstat()
            executable = dict(SHA256=proposal['observer_artifacts']['observer'], owner_uid=info.st_uid,
                              mode=0o700, device=info.st_dev, inode=info.st_ino)
            frozen = dict(source_commit=proposal['source_commit'], proposal_SHA256=receipt['proposal_SHA256'],
                files={name: sha(OUT/name) for name in COPY_FILES}, executable=executable, authority_SHA256=sha(AUTHORITY))
            old.write(OUT/'freeze.json', frozen)
            verify_frozen(frozen, receipt, sha(AUTHORITY)); check_root_usage()
    except BaseException as error:
        if not (OUT/'PREPARATION-STOP.json').exists():
            old.write(OUT/'PREPARATION-STOP.json', dict(PASS=False, reason=str(error)[:2000], first_failure_terminal=True, retry=False, actual_processes=0))
        raise
