"""Exact local Howler preservation wiring; authority is absent until review.

The accepted streaming codec/frame verifier is reused. Historical launchers,
verify_all, removal_barrier and implicit Budget defaults are never invoked.
"""
from pathlib import Path
import copy
import importlib.util
import json
import os
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('howler_rgb_scope', ROOT / 'scripts/floor1/rgb-howler-preservation-scope.py')
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)
engine = scope.engine
require = scope.require
BASE = '50999ee17c20115424d17818ee76a0a1617af73d'
PROPOSAL = scope.PREPARATION / 'proposal-contract-private.json'
PROPOSAL_SHA = '2e7e28ae1bf710f7f114607bae7e070a76c06a509e6a2d6d9b901dcd8de8049b'
OUT = scope.PROPOSED_OUTPUT
OFFLINE = scope.SCRATCH / 'howler-rgb-preservation-controller-offline-r1-20261011'
ADMISSION = OFFLINE / 'controller-admission-private.json'
AUTHORITY = scope.SCRATCH / 'howler-rgb-preservation-execution-authority-r1-20261011.json'
CAP = 3459215360
FINAL_METADATA_RESERVE = scope.METADATA_CAP + scope.METADATA_FILES * scope.BLOCK
FILES = ('scripts/floor1/howler-rgb-preservation-controller.py',
         'scripts/preserve-howler-rgb-r1.py',
         'scripts/test-howler-rgb-preservation-controller-offline.py')
CONTRACT_NAME = 'preservation-contract-private.json'
MAPPING_NAME = 'representation-mapping-private.json'
RECEIPT_NAMES = ('verification-pass1-private.json', 'verification-pass2-private.json')
LABELS = ('pass1-zlib', 'pass2-independent-gzip')
_SYNC_SEAL = object()
_OWNED_OUTPUT = False


def read(path):
    engine.identity(Path(path))
    return json.loads(Path(path).read_text())


def accepted_inputs():
    require(engine.digest(PROPOSAL) == PROPOSAL_SHA, 'accepted proposal identity')
    proposal = read(PROPOSAL)
    checks = read(scope.PREPARATION / 'offline-checks-private.json')
    receipt = read(scope.PREPARATION / 'proposal-preparation-receipt-private.json')
    handoff = read(scope.PREPARATION / 'final-handoff-private.json')
    require(proposal['tested_source_commit'] == checks['source_commit'] == receipt['source_commit'] ==
            handoff['tested_commit'] == handoff['published_commit'] == BASE, 'accepted preparation source')
    require(checks['PASS'] is True and checks['case_count'] == 44 and receipt['PASS'] is True and
            handoff['PASS'] is True and receipt['proposal_SHA256'] == PROPOSAL_SHA,
            'accepted preparation receipt')
    for name, expected in handoff['private_artifact_SHA256'].items():
        engine.identity(scope.PREPARATION / name)
        require(engine.digest(scope.PREPARATION / name) == expected, 'accepted preparation artifact changed')
    require(proposal['chunk_count'] == 17 and proposal['frames'] == 28700 and
            proposal['original_bytes'] == 3306240000 and len(proposal['protected_entries']) == 376 and
            proposal['storage'] == scope.storage_cap(proposal['chunks']) and
            proposal['storage']['all_inclusive_cap_bytes'] == CAP,
            'accepted exact inventory/cap')
    require(receipt['actual_compression'] is False and receipt['actual_decoded_passes'] ==
            receipt['actual_replacements'] == 0 and proposal['runtime_reservation_bytes'] == 17694519296,
            'preservation unstarted; unchanged runtime reservation')
    return proposal


def provider_check(contract):
    engine.code_check(contract)
    origin, dependencies = scope.accepted.decoder_dependencies()
    require(origin == contract['zlib_module_origin'] and dependencies == contract['tool_dependencies_SHA256'] and
            engine.zlib.ZLIB_RUNTIME_VERSION == contract['zlib_version'] and
            subprocess.check_output([str(engine.GZIP), '--version'], text=True).splitlines()[0] == contract['gzip_version'] and
            not os.environ.get('GZIP'), 'strict fixed codec/provider/dependencies')


def authority_check(authority, head, admission_hash):
    expected = dict(status='APPROVED_FOR_ONE_LOCAL_PRESERVATION', preservation_only=True,
                    source_commit=head, proposal_SHA256=PROPOSAL_SHA,
                    controller_admission_SHA256=admission_hash, output_root=str(OUT),
                    chunk_count=17, cap_bytes=CAP, execution_limit=1,
                    runtime_authority=False, split_storage=False, cache_cleanup=False,
                    parent_review_verified=True)
    require(authority == expected, 'separate exact controller review/authority required')


def admission():
    proposal = accepted_inputs()
    head = scope.accepted.git('rev-parse', 'HEAD')
    require(not scope.accepted.git('status', '--porcelain') and
            scope.accepted.git('merge-base', BASE, head) == BASE, 'clean reviewed source ancestry')
    checked = read(ADMISSION)
    require(checked['PASS'] is True and checked['source_commit'] == head and
            checked['proposal_SHA256'] == PROPOSAL_SHA and checked['cap_bytes'] == CAP and
            checked['execution_permitted'] is False and
            set(checked['source_files_SHA256']) == set(FILES), 'exact offline controller admission')
    for rel, expected in checked['source_files_SHA256'].items():
        require(engine.digest(ROOT / rel) == expected, 'admitted controller source changed')
    authority_check(read(AUTHORITY), head, engine.digest(ADMISSION))
    require(not (OUT / 'preservation-STOP-private.json').exists() and
            not (OUT / 'preservation-result-private.json').exists(), 'terminal operation cannot resume/retry')
    provider_check(proposal)
    return proposal, head, checked


def validate_contract(contract, proposal):
    require(contract['approved_proposal_SHA256'] == PROPOSAL_SHA and contract['output_root'] == str(OUT) and
            contract['preservation_only'] is True and contract['runtime'] == 'CLOSED' and
            contract['runtime_reservation_bytes'] == 17694519296, 'contract source/scope/runtime binding')
    require(contract['status'] == 'FROZEN_LOCAL_PRESERVATION_ONLY' and
            contract['preservation_execution_permitted'] is True and
            contract['runtime_authority'] is False and contract['runtime_freeze'] is False,
            'local preservation contract only')
    for key in ('width', 'height', 'pixel_format', 'bytes_per_frame', 'chunk_count', 'frames',
                'original_bytes', 'format', 'compress_command', 'decoder_pass1', 'decoder_pass2',
                'gzip_version', 'gzip_executable_SHA256', 'python_executable_SHA256', 'zlib_version',
                'zlib_module_origin', 'tool_dependencies_SHA256'):
        require(contract[key] == proposal[key], 'immutable approved codec/inventory: ' + key)
    require(set(contract['source_files_SHA256']) == set(proposal['source_files_SHA256']) | set(FILES) and
            all(contract['source_files_SHA256'][p] == h for p, h in proposal['source_files_SHA256'].items()),
            'complete unchanged source identity inventory')
    require(contract['storage'] == proposal['storage'] == scope.storage_cap(contract['chunks']) and
            contract['storage']['all_inclusive_cap_bytes'] == CAP, 'exact explicit 3459215360 cap')
    require(contract['protected_entries'] == proposal['protected_entries'] and
            contract['recordings'] == proposal['recordings'] and
            contract['previously_replaced_paths'] == proposal['previously_replaced_paths'], 'immutable protected scope')
    scope.validate_scope(contract['chunks'], contract['protected_entries'], contract['previously_replaced_paths'])
    for row, original in zip(contract['chunks'], proposal['chunks']):
        require(set(row) == set(original) | {'frame_hashes_SHA256'} and
                all(row[k] == v for k, v in original.items()), 'approved original identity/hash changed')


def validate_mapping(contract, mapping, contract_hash):
    require(mapping['contract_SHA256'] == contract_hash and mapping['proposal_SHA256'] == PROPOSAL_SHA and
            mapping['cap_bytes'] == CAP and mapping['output_root'] == str(OUT), 'mapping contract/scope/cap binding')
    scope.validate_scope(mapping['chunks'], contract['protected_entries'], contract['previously_replaced_paths'])
    for row, original in zip(mapping['chunks'], contract['chunks']):
        require(set(row) == set(original) | {'compressed_identity', 'compressed_SHA256'} and
                all(row[k] == v for k, v in original.items()), 'complete unchanged original/ledger mapping')
        require(row['compressed_identity']['bytes'] <= scope.gzip_bound(row['frames'] * scope.FRAME),
                'fixed codec worst-case byte bound')


def preparation_usage():
    paths = [scope.PREPARATION, *scope.PREPARATION.rglob('*')]
    # The accepted inert symlink negative is retained and counted without following it.
    return dict(logical_bytes=sum(p.lstat().st_size for p in paths if not p.is_dir()),
                allocated_bytes=sum(p.lstat().st_blocks * 512 for p in paths))


class LocalIO:
    """Filesystem primitives; inert tests substitute this interface, never real targets."""
    def __init__(self, contract):
        self.contract = contract
        self.removed = []
        self.preparation = preparation_usage()
        # No historical default cap, reservation or removal barrier.
        self.budget = engine.Budget(OUT, cap=CAP,
                                    reserve=scope.AUDIT_RESERVE + max(self.preparation.values()))

    def identity(self, path):
        return engine.identity(path)

    def read(self, name):
        return read(OUT / name)

    def digest(self, path):
        return engine.digest(path)

    def check_raw(self, row):
        scope.check_entry(row)

    def source_check(self, contract):
        require(scope.accepted.git('rev-parse', 'HEAD') == contract['preservation_source_commit'] and
                not scope.accepted.git('status', '--porcelain'), 'exact frozen clean controller source')
        require(self.digest(AUTHORITY) == contract['execution_authority_SHA256'] and
                self.digest(ADMISSION) == contract['controller_admission_SHA256'],
                'frozen authority/admission identity')
        provider_check(contract)

    def protected_check(self, contract):
        engine.protected_check(contract)

    def usage(self):
        usage = self.budget.check()
        streams = {r[k] for r in self.contract['chunks']
                   for k in ('compressed_relative_path', 'frame_hashes_relative_path')}
        metadata = [p for p in OUT.rglob('*') if p.is_file() and str(p.relative_to(OUT)) not in streams]
        require(len(metadata) + sum(p.is_file() or p.is_symlink() for p in scope.PREPARATION.rglob('*')) <=
                scope.METADATA_FILES, 'metadata file count bound')
        require(sum(p.stat().st_size for p in metadata) + self.preparation['logical_bytes'] <=
                scope.METADATA_CAP, 'metadata byte bound')
        return usage

    def available(self):
        require(OUT.stat().st_dev == scope.SCRATCH.stat().st_dev, 'single durable workspace device required')
        return scope.available_workspace()

    def json(self, name, value):
        self.budget.json(OUT / name, value)
        self.sync_dir(OUT)
        self.usage()

    def sync_file(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            require(stat.S_ISREG(os.fstat(fd).st_mode), 'synchronize regular replacement evidence')
            os.fsync(fd)
        finally:
            os.close(fd)

    def sync_dir(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def unlink_raw(self, row):
        self.check_raw(row)
        path = Path(row['raw_path'])
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            # Last path/inode check immediately precedes the only unlink call.
            require(self.identity(path) == row['raw_identity'], 'original changed immediately before unlink')
            operand = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
            require(stat.S_ISREG(operand.st_mode) and operand.st_nlink == 1 and
                    (operand.st_dev, operand.st_ino, operand.st_size, operand.st_mtime_ns) ==
                    tuple(row['raw_identity'][k] for k in ('device', 'inode', 'bytes', 'mtime_ns')),
                    'directory-bound exact original unlink operand')
            os.unlink(path.name, dir_fd=fd)
            self.removed.append(row['raw_path'])
            os.fsync(fd)
        finally:
            os.close(fd)


def verify_replacements(io, mapping):
    for row in mapping['chunks']:
        compressed = OUT / row['compressed_relative_path']
        require(io.identity(compressed) == row['compressed_identity'] and
                io.digest(compressed) == row['compressed_SHA256'], 'replacement identity/hash changed')
        ledger = OUT / row['frame_hashes_relative_path']
        require(io.identity(ledger)['bytes'] == 32 * row['frames'] and
                io.digest(ledger) == row['frame_hashes_SHA256'], 'frame ledger identity/count changed')


def barrier_checks(io, contract, proposal, mapping, one, two):
    validate_contract(contract, proposal)
    require(io.read(CONTRACT_NAME) == contract and io.read(MAPPING_NAME) == mapping and
            io.read(RECEIPT_NAMES[0]) == one and io.read(RECEIPT_NAMES[1]) == two,
            'current persisted contract/mapping/complete receipts required')
    contract_hash, mapping_hash = io.digest(OUT / CONTRACT_NAME), io.digest(OUT / MAPPING_NAME)
    validate_mapping(contract, mapping, contract_hash)
    scope.pair_check(one, two, contract_hash, mapping_hash, mapping['chunks'])
    operation = io.read('operation-start-private.json')
    require(type(operation['pid']) is int and operation['pid'] > 0 and
            operation['source_commit'] == contract['preservation_source_commit'] and
            operation['contract_SHA256'] == contract_hash and operation['preservation_only'] is True,
            'exact admitted controller operation binding')
    for receipt, action in ((one, 'verify-zlib'), (two, 'verify-gzip')):
        require(receipt['source_commit'] == contract['preservation_source_commit'] and
                receipt['controller_PID'] == operation['pid'] and receipt['pid'] != operation['pid'] and
                receipt['fresh_verifier_process'] is True and receipt['no_second_full_decoded_copy'] is True,
                'fresh independent verifier process/source binding')
        started = io.read(action + '-started-private.json')
        require(started['pid'] == receipt['pid'] and started['controller_PID'] == operation['pid'],
                'actual verifier child PID binding')
    io.source_check(contract)
    for row in mapping['chunks']:
        io.check_raw(row)
    io.protected_check(contract)
    verify_replacements(io, mapping)
    usage = io.usage()
    require(max(usage.values()) + max(io.preparation.values()) + scope.AUDIT_RESERVE <= CAP,
            'all-inclusive explicit capacity exceeded')
    raw_logical = sum(r['raw_identity']['bytes'] for r in mapping['chunks'])
    raw_allocated = sum(r['raw_identity']['allocated_bytes'] for r in mapping['chunks'])
    # Keep the entire metadata allowance for progress/result/STOP writes. This
    # conservative remainder cannot turn a small apparent saving into a loss.
    future_metadata = scope.METADATA_CAP + scope.METADATA_FILES * scope.BLOCK + 69632
    logical_net = raw_logical - usage['logical_bytes'] - max(io.preparation.values()) - scope.AUDIT_RESERVE - future_metadata
    allocated_net = raw_allocated - usage['allocated_bytes'] - max(io.preparation.values()) - scope.AUDIT_RESERVE - future_metadata
    require(min(logical_net, allocated_net) > 0, 'no positive all-inclusive measured space savings')
    require(io.available() >= scope.AUDIT_RESERVE + future_metadata, 'remaining all-inclusive audit capacity unavailable')
    return dict(raw_logical_bytes=raw_logical, raw_allocated_bytes=raw_allocated,
                output_usage=usage, preparation_usage=io.preparation,
                audit_reserve_bytes=scope.AUDIT_RESERVE, reserved_remaining_metadata_bytes=future_metadata,
                conservative_positive_net_bytes=min(logical_net, allocated_net),
                projected_available_bytes=io.available() + raw_allocated,
                runtime_capacity_admitted=False)


class SyncedBarrier:
    def __init__(self, io, hashes, accounting, sync_receipt_hash, seal):
        require(seal is _SYNC_SEAL, 'synchronization completion required to mint barrier ticket')
        self.io, self.hashes, self.accounting, self.consumed = io, hashes, accounting, False
        self.sync_receipt_hash = sync_receipt_hash


def synchronized_paths(mapping):
    paths = [OUT / name for name in (CONTRACT_NAME, MAPPING_NAME, *RECEIPT_NAMES,
             'operation-start-private.json', 'verify-zlib-started-private.json',
             'verify-gzip-started-private.json', 'verify-zlib.log', 'verify-gzip.log')]
    paths.extend(OUT / row[key] for row in mapping['chunks']
                 for key in ('compressed_relative_path', 'frame_hashes_relative_path'))
    return paths


def synchronize_barrier(io, contract, proposal, mapping, one, two):
    accounting = barrier_checks(io, contract, proposal, mapping, one, two)
    paths = synchronized_paths(mapping)
    hashes = {str(p): io.digest(p) for p in paths}
    for path in paths:
        io.sync_file(path)
        require(io.digest(path) == hashes[str(path)], 'evidence changed during synchronization')
    for directory in sorted({p.parent for p in paths}, key=lambda p: len(p.parts), reverse=True):
        io.sync_dir(directory)
    io.sync_dir(OUT.parent)
    io.json('synchronization-complete-private.json', dict(PASS=True, synchronized_files_SHA256=hashes,
            contract_SHA256=hashes[str(OUT / CONTRACT_NAME)], mapping_SHA256=hashes[str(OUT / MAPPING_NAME)],
            verifier_PIDs=[one['pid'], two['pid']], all_originals_retained=True))
    # json() synchronizes its file and directory; repeat the complete barrier
    # after synchronization, before minting the one-use removal ticket.
    accounting = barrier_checks(io, contract, proposal, mapping, one, two)
    return SyncedBarrier(io, hashes, accounting,
                         io.digest(OUT / 'synchronization-complete-private.json'), _SYNC_SEAL)


def replace_originals(io, ticket, contract, proposal, mapping, one, two):
    require(isinstance(ticket, SyncedBarrier) and ticket.io is io and not ticket.consumed,
            'premature removal: complete synchronized barrier ticket required')
    require(set(ticket.hashes) == {str(p) for p in synchronized_paths(mapping)} and
            io.digest(OUT / 'synchronization-complete-private.json') == ticket.sync_receipt_hash,
            'complete persisted synchronization coverage required')
    barrier_checks(io, contract, proposal, mapping, one, two)
    for path, expected in ticket.hashes.items():
        require(io.digest(Path(path)) == expected, 'synchronized evidence changed before removal')
    ticket.consumed = True
    for ordinal, row in enumerate(mapping['chunks']):
        io.unlink_raw(row)
        io.json(f'replacement-progress-{ordinal:02}-private.json', dict(
                removed_path=row['raw_path'], compressed_SHA256=row['compressed_SHA256'],
                raw_SHA256=row['raw_SHA256'], completed_removals=ordinal + 1))
    io.protected_check(contract)
    verify_replacements(io, mapping)
    return ticket.accounting


def freeze():
    global _OWNED_OUTPUT
    proposal, head, checked = admission()
    require(not OUT.exists(), 'exclusive new preservation output required')
    scope.inventory_check(proposal['chunks'], proposal['protected_entries'], proposal['previously_replaced_paths'])
    require(scope.available_workspace() >= CAP, 'fresh full cap before inventory')
    OUT.mkdir(mode=0o700)
    _OWNED_OUTPUT = True
    for label, *_ in scope.PLANS:
        (OUT / label).mkdir(mode=0o700)
    contract = copy.deepcopy(proposal)
    contract.update(approved_proposal_SHA256=PROPOSAL_SHA, output_root=str(OUT),
                    preservation_only=True, preservation_source_commit=head,
                    status='FROZEN_LOCAL_PRESERVATION_ONLY', preservation_execution_permitted=True,
                    future_launcher='Exact source-bound preserve-howler-rgb-r1.py; runtime CLOSED',
                    controller_admission_SHA256=engine.digest(ADMISSION),
                    execution_authority_SHA256=engine.digest(AUTHORITY))
    contract['source_files_SHA256'].update(checked['source_files_SHA256'])
    io = LocalIO(contract)
    io.sync_dir(OUT)
    io.sync_dir(OUT.parent)
    for row in contract['chunks']:
        scope.check_entry(row)
        hashes, whole = bytearray(), engine.hashlib.sha256()
        with Path(row['raw_path']).open('rb') as file:
            for _ in range(row['frames']):
                frame = engine.read_exact(file, scope.FRAME)
                require(len(frame) == scope.FRAME, 'complete original frame for frozen ledger')
                whole.update(frame)
                hashes.extend(engine.hashlib.sha256(frame).digest())
            require(not file.read(1), 'original exact EOF at freeze')
        require(whole.hexdigest() == row['raw_SHA256'], 'approved original bytes at freeze')
        scope.check_entry(row)
        row['frame_hashes_SHA256'] = engine.hashlib.sha256(hashes).hexdigest()
        io.budget.write(OUT / row['frame_hashes_relative_path'], hashes)
    validate_contract(contract, proposal)
    io.json(CONTRACT_NAME, contract)
    io.protected_check(contract)
    require(io.available() >= CAP, 'fresh full cap after inventory/freeze')
    print('FROZEN LOCAL PRESERVATION ONLY; runtime CLOSED', flush=True)


def verify_worker(action):
    global _OWNED_OUTPUT
    proposal, head, _ = admission()
    contract, mapping = read(OUT / CONTRACT_NAME), read(OUT / MAPPING_NAME)
    validate_contract(contract, proposal)
    _OWNED_OUTPUT = True
    io = LocalIO(contract)
    io.source_check(contract)
    validate_mapping(contract, mapping, io.digest(OUT / CONTRACT_NAME))
    operation = read(OUT / 'operation-start-private.json')
    require(operation['pid'] == os.getppid() and operation['source_commit'] == head and
            operation['contract_SHA256'] == io.digest(OUT / CONTRACT_NAME) and
            operation['preservation_only'] is True,
            'verifier must be a fresh child of the admitted controller')
    number = 0 if action == 'verify-zlib' else 1
    require(not (OUT / RECEIPT_NAMES[number]).exists(), 'one verifier process per pass; no repetition')
    decoder = engine.zlib_blocks if number == 0 else engine.gzip_blocks
    results = []
    io.protected_check(contract)
    for row in mapping['chunks']:
        io.check_raw(row)
        results.append(engine.verify_chunk(row, OUT, decoder))
        io.usage()
    io.protected_check(contract)
    receipt = dict(PASS=True, verification=LABELS[number], pid=os.getpid(),
                   controller_PID=os.getppid(), source_commit=head, fresh_verifier_process=True,
                   contract_SHA256=io.digest(OUT / CONTRACT_NAME), mapping_SHA256=io.digest(OUT / MAPPING_NAME),
                   chunks=results, chunk_count=17, frames=28700, decoded_bytes=3306240000,
                   originals_retained=True, no_second_full_decoded_copy=True)
    scope.receipt_check(receipt, LABELS[number], io.digest(OUT / CONTRACT_NAME), io.digest(OUT / MAPPING_NAME), mapping['chunks'])
    io.json(RECEIPT_NAMES[number], receipt)


def run_verifier(io, action):
    path = OUT / (action + '.log')
    io.budget.check(65536 + 4096)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1')
    with path.open('xb') as log:
        process = subprocess.Popen([sys.executable, '-B', str(ROOT / 'scripts/preserve-howler-rgb-r1.py'), action],
                                   cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            io.json(action + '-started-private.json', dict(pid=process.pid, controller_PID=os.getpid()))
            require(process.wait(timeout=1800) == 0, 'complete fresh verifier process failed')
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        log.flush()
        os.fsync(log.fileno())
    require(path.stat().st_size <= 65536, 'bounded verifier log')
    io.usage()


def execute():
    global _OWNED_OUTPUT
    proposal, head, _ = admission()
    contract = read(OUT / CONTRACT_NAME)
    validate_contract(contract, proposal)
    _OWNED_OUTPUT = True
    io = LocalIO(contract)
    io.source_check(contract)
    scope.inventory_check(contract['chunks'], contract['protected_entries'], contract['previously_replaced_paths'])
    require(io.available() >= CAP, 'fresh full cap before operation')
    io.json('operation-start-private.json', dict(pid=os.getpid(), source_commit=head,
            available_workspace_bytes_before_operation=io.available(),
            contract_SHA256=io.digest(OUT / CONTRACT_NAME), preservation_only=True))
    mapping = dict(contract_SHA256=io.digest(OUT / CONTRACT_NAME), proposal_SHA256=PROPOSAL_SHA,
                   cap_bytes=CAP, output_root=str(OUT), chunks=[])
    for original in contract['chunks']:
        row = dict(original)
        io.check_raw(row)
        destination = OUT / row['compressed_relative_path']
        engine.compress_once(Path(row['raw_path']), destination, io.budget)
        io.check_raw(row)
        row.update(compressed_identity=io.identity(destination), compressed_SHA256=io.digest(destination))
        mapping['chunks'].append(row)
        require(row['compressed_identity']['bytes'] <= scope.gzip_bound(row['frames'] * scope.FRAME),
                'fixed codec expansion cap')
        io.usage()
    io.json(MAPPING_NAME, mapping)
    for action in ('verify-zlib', 'verify-gzip'):
        run_verifier(io, action)
    one, two = (read(OUT / name) for name in RECEIPT_NAMES)
    ticket = synchronize_barrier(io, contract, proposal, mapping, one, two)
    accounting = replace_originals(io, ticket, contract, proposal, mapping, one, two)
    available_after = io.available()
    before = read(OUT / 'operation-start-private.json')['available_workspace_bytes_before_operation']
    actual_delta = measured_space_savings(before, available_after)
    io.json('preservation-result-private.json', dict(PASS=True, replaced_files=17,
            replaced_paths=io.removed, raw_bytes=3306240000, frames=28700,
            accounting=accounting, available_workspace_bytes=available_after,
            measured_available_bytes_increase_before_final_receipt=actual_delta,
            final_metadata_safety_reserve_bytes=FINAL_METADATA_RESERVE,
            runtime='CLOSED', runtime_capacity_admitted=False, independent_backup_verified=False))


def measured_space_savings(before, after):
    require(type(before) is int and type(after) is int and after - before > FINAL_METADATA_RESERVE,
            'positive actual workspace space reclamation not observed')
    return after - before


def record_stop(action, error):
    # Authority/admission rejection before output creation writes nothing.
    if _OWNED_OUTPUT and OUT.is_dir() and not OUT.is_symlink() and OUT.resolve() == OUT and \
            not (OUT / 'preservation-STOP-private.json').exists():
        remaining = [r['raw_path'] for r in scope.definitions() if Path(r['raw_path']).exists()]
        path = OUT / 'preservation-STOP-private.json'
        with path.open('x') as file:
            json.dump(dict(PASS=False, action=action, error=type(error).__name__ + ': ' + str(error),
                           first_failure_terminal=True, retry_permitted=False,
                           retained_original_paths=remaining, retained_original_count=len(remaining),
                           partial_outputs_retained=True, runtime='CLOSED'), file, indent=2)
            file.flush()
            os.fsync(file.fileno())
        fd = os.open(OUT, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
