"""Proposed one-operation removal controller. Absent review authority closes execution."""
from pathlib import Path
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys

SPEC = importlib.util.spec_from_file_location('frame_archive_core', Path(__file__).with_name('v01-frame-archive.py'))
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)
SEAL = object()
RECEIPTS = ('verification-zlib-private.json', 'verification-gzip-private.json')
LEDGERS = ('verification-zlib-private.jsonl', 'verification-gzip-private.jsonl')
STOP_RESERVE = 2 * 1024**2
OWNED = False


def ledger(rows):
    return b''.join(m.encode(dict(member=r['member'], SHA256=r['SHA256'], bytes=m.FRAME_BYTES,
                                exact_original_bytes=True, exact_frame_hash=True, exact_member_EOF=True)) for r in rows)


def admission():
    contract, rows, protected = m.proposal()
    tests = m.load_json(m.TESTS / 'offline-admission-private.json')
    m.require(tests['PASS'] is True and tests['source_commit'] == contract['source_commit'] and
              m.digest(m.TESTS / 'offline-admission-private.json') == contract['offline_admission_SHA256'] and
              tests['execution_permitted'] is False, 'exact inert admission')
    authority = m.load_json(m.AUTHORITY)
    expected = dict(status='APPROVED_FOR_ONE_ARCHIVE_BACKED_FRAME_REPLACEMENT',
                    source_commit=contract['source_commit'], proposal_SHA256=m.digest(m.PREP / 'proposal-private.json'),
                    offline_admission_SHA256=contract['offline_admission_SHA256'], output_root=str(m.OUT),
                    archive_SHA256=m.ARCHIVE_SHA, target_count=m.COUNT, cap_bytes=m.CAP,
                    execution_limit=1, runtime_authority=False, compression=False, parent_review_verified=True)
    m.require(authority == expected and not (m.OUT / 'STOP-private.json').exists() and
              not (m.OUT / 'result-private.json').exists(), 'separate reviewed exact authority; no resume/retry')
    return contract, rows, protected


class LocalIO:
    def __init__(self, contract, rows, protected):
        self.contract, self.rows, self.protected = contract, rows, protected
        self.removed = []

    def digest(self, path):
        m.identity(path)
        return m.digest(path)

    def read(self, name):
        return m.load_json(m.OUT / name)

    def checks(self):
        m.recheck(self.contract, self.protected, self.rows)
        m.require(m.digest(m.PREP / 'proposal-private.json') == self.read('operation-private.json')['proposal_SHA256'] and
                  m.digest(m.AUTHORITY) == self.read('operation-private.json')['authority_SHA256'], 'frozen proposal/authority binding')
        m.require(m.digest(m.PREP / 'frame-inventory-private.jsonl') == self.contract['inventory_SHA256'] and
                  m.digest(m.PREP / 'protected-inventory-private.jsonl') == self.contract['protected_SHA256'], 'frozen inventories changed')

    def usage(self):
        usage = [m.engine.usage(p) for p in (m.PREP, m.TESTS, m.OUT)]
        result = {key: sum(r[key] for r in usage) for key in ('logical_bytes', 'allocated_bytes')}
        m.require(max(result.values()) <= m.METADATA_CAP, 'all metadata/verification/staging bound')
        return result

    def available(self):
        return m.available()

    def sync_file(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            m.require(stat.S_ISREG(os.fstat(fd).st_mode), 'regular synchronized evidence')
            os.fsync(fd)
        finally:
            os.close(fd)

    def sync_dir(self, path):
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def write(self, path, data):
        self.usage()
        m.require(path.parent == m.OUT and not os.path.lexists(path), 'exclusive operation metadata only')
        reserve = 0 if path.name == 'STOP-private.json' else STOP_RESERVE
        m.require(max(self.usage().values()) + len(data) + 4096 + reserve <= m.METADATA_CAP, 'metadata write and terminal STOP bound')
        with path.open('xb') as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(data); file.flush(); os.fsync(file.fileno())
        self.sync_dir(m.OUT)
        self.usage()

    def json(self, name, value):
        self.write(m.OUT / name, m.encode(value))

    def unlink(self, row):
        m.check_file(row['raw_path'], row)
        path = Path(row['raw_path'])
        fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            m.require(m.identity(path) == row['identity'], 'last original inode/mtime/link check')
            s = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
            m.require(stat.S_ISREG(s.st_mode) and s.st_nlink == 1 and
                      (str(s.st_dev), str(s.st_ino), s.st_size, str(s.st_mtime_ns)) ==
                      tuple(row['identity'][k] for k in ('device', 'inode', 'bytes', 'mtime_ns')), 'directory-bound exact unlink operand')
            os.unlink(path.name, dir_fd=fd)
            self.removed.append(row['member'])
            os.fsync(fd)
        finally:
            os.close(fd)


def required_paths():
    return [m.ARCHIVE, m.MANIFEST, m.AUTHORITY, m.PREP / 'proposal-private.json',
            m.PREP / 'frame-inventory-private.jsonl', m.PREP / 'protected-inventory-private.jsonl',
            m.TESTS / 'offline-admission-private.json',
            *[m.OUT / name for name in ('operation-private.json', *RECEIPTS, *LEDGERS,
                                      'zlib-started-private.json', 'gzip-started-private.json', 'zlib.log', 'gzip.log')]]


def barrier(io, contract, rows, one, two):
    m.target_scope(rows)
    m.require(contract['target_count'] == m.COUNT and contract['target_allocated_bytes'] == m.ALLOCATED and
              contract['cap_bytes'] == m.CAP and contract['runtime_reservation_bytes'] == m.WARDEN and
              contract['execution_permitted'] is False and contract['archive']['SHA256'] == m.ARCHIVE_SHA and
              contract['proposed_operation_root'] == str(m.OUT), 'exact proposed scope/cap/archive/runtime')
    operation = io.read('operation-private.json')
    m.require(type(operation['pid']) is int and operation['pid'] > 0 and
              operation['source_commit'] == contract['source_commit'], 'actual exclusive controller identity')
    expected_ledger = hashlib.sha256(ledger(rows)).hexdigest()
    for i, (receipt, decoder) in enumerate(((one, 'zlib'), (two, 'gzip'))):
        m.require(io.read(RECEIPTS[i]) == receipt and receipt['PASS'] is True and
                  receipt['decoder'] == decoder and receipt['target_count'] == m.COUNT and
                  receipt['decoded_frame_bytes'] == m.COUNT * m.FRAME_BYTES and
                  receipt['archive_member_count'] == contract['archive_member_count'] and
                  receipt['archive_member_chain_SHA256'] == contract['archive_member_chain_SHA256'] and
                  receipt['exact_archive_original_frame_hash_EOF'] is True and receipt['originals_retained'] is True,
                  'complete ordered archive/original/EOF receipt')
        m.require(type(receipt['pid']) is int and receipt['pid'] > 0 and receipt['pid'] != operation['pid'] and
                  receipt['controller_PID'] == operation['pid'] and receipt['source_commit'] == contract['source_commit'] and
                  receipt['fresh_process'] is True and receipt['proposal_SHA256'] == operation['proposal_SHA256'] and
                  receipt['inventory_SHA256'] == contract['inventory_SHA256'] and
                  receipt['ledger_SHA256'] == expected_ledger == io.digest(m.OUT / LEDGERS[i]), 'verifier PID/source/proposal/mapping/ordered ledger')
        started = io.read(decoder + '-started-private.json')
        m.require(started['pid'] == receipt['pid'] and started['controller_PID'] == operation['pid'], 'actual child PID receipt')
    m.require(one['pid'] != two['pid'], 'two separate complete verifier child processes')
    io.checks()
    usage = io.usage()
    m.capacity(io.available())
    m.require(m.ALLOCATED - m.CAP > 0 and io.available() + m.ALLOCATED - m.CAP >= m.WARDEN,
              'insufficient conservative savings/selected-restoration/Warden headroom')
    return dict(output_usage=usage, conservative_net_savings_bytes=m.ALLOCATED - m.CAP,
                projected_available_after_all_allowances=io.available() + m.ALLOCATED - m.CAP,
                runtime_authority=False, whole_directory_restoration_capacity_admitted=False)


class Ticket:
    def __init__(self, io, hashes, receipt_sha, seal):
        m.require(seal is SEAL, 'synchronization completion required')
        self.io, self.hashes, self.receipt_sha, self.used = io, hashes, receipt_sha, False


def synchronize(io, contract, rows, one, two):
    accounting = barrier(io, contract, rows, one, two)
    hashes = {str(path): io.digest(path) for path in required_paths()}
    for path in required_paths():
        io.sync_file(path)
        m.require(io.digest(path) == hashes[str(path)], 'evidence changed during synchronization')
    for directory in sorted({p.parent for p in required_paths()} | {m.OUT.parent}, key=str):
        io.sync_dir(directory)
    io.json('synchronization-private.json', dict(PASS=True, originals_retained=True, files_SHA256=hashes, accounting=accounting))
    barrier(io, contract, rows, one, two)
    return Ticket(io, hashes, io.digest(m.OUT / 'synchronization-private.json'), SEAL)


def remove(io, ticket, contract, rows, one, two):
    m.require(isinstance(ticket, Ticket) and ticket.io is io and not ticket.used and
              set(ticket.hashes) == {str(p) for p in required_paths()} and
              io.digest(m.OUT / 'synchronization-private.json') == ticket.receipt_sha, 'premature removal or incomplete synchronized ticket')
    barrier(io, contract, rows, one, two)
    for path, sha in ticket.hashes.items():
        m.require(io.digest(Path(path)) == sha, 'synchronized retained evidence changed')
    ticket.used = True
    for i, row in enumerate(rows):
        io.unlink(row)
        # Two durable group milestones; per-file progress would violate the
        # bounded metadata file count. STOP reports actual surviving paths.
        if (i + 1) % m.CASE_COUNT == 0:
            io.json(f'removed-{i + 1}-private.json', dict(completed=i + 1, last_member=row['member']))
    return len(io.removed)


def worker(decoder):
    global OWNED
    contract, rows, protected = admission()
    io = LocalIO(contract, rows, protected)
    operation = io.read('operation-private.json')
    m.require(operation['pid'] == os.getppid(), 'fresh child of exclusive reviewed controller')
    OWNED = True
    io.checks()
    checked = m.archive_scan(rows, mode=decoder, compare_originals=True)
    m.require(checked['members'] == contract['archive_member_count'] and
              checked['member_chain_SHA256'] == contract['archive_member_chain_SHA256'], 'strict full archive identity/EOF')
    i = 0 if decoder == 'zlib' else 1
    data = ledger(rows)
    io.write(m.OUT / LEDGERS[i], data)
    io.checks()
    io.json(RECEIPTS[i], dict(PASS=True, decoder=decoder, pid=os.getpid(), controller_PID=os.getppid(),
            source_commit=contract['source_commit'], fresh_process=True,
            proposal_SHA256=operation['proposal_SHA256'], inventory_SHA256=contract['inventory_SHA256'],
            ledger_SHA256=hashlib.sha256(data).hexdigest(), target_count=m.COUNT,
            decoded_frame_bytes=m.COUNT * m.FRAME_BYTES, archive_member_count=checked['members'],
            archive_member_chain_SHA256=checked['member_chain_SHA256'],
            exact_archive_original_frame_hash_EOF=True, originals_retained=True))


def execute():
    global OWNED
    contract, rows, protected = admission()
    m.require(not os.path.lexists(m.OUT), 'exclusive fresh operation; one attempt only')
    m.recheck(contract, protected, rows)
    m.capacity(m.available())
    m.OUT.mkdir(mode=0o700)
    OWNED = True
    io = LocalIO(contract, rows, protected)
    io.sync_dir(m.OUT.parent)
    io.json('operation-private.json', dict(pid=os.getpid(), source_commit=contract['source_commit'],
            proposal_SHA256=m.digest(m.PREP / 'proposal-private.json'), authority_SHA256=m.digest(m.AUTHORITY),
            before_available_bytes=m.available(), preservation_only=True, runtime_authority=False))
    with (m.OUT / 'exclusive.lock').open('x') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        for decoder in ('zlib', 'gzip'):
            with (m.OUT / (decoder + '.log')).open('xb') as log:
                proc = subprocess.Popen([sys.executable, '-B', __file__, decoder], cwd=m.ROOT,
                                        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONNOUSERSITE='1'), stdout=log, stderr=subprocess.STDOUT)
                try:
                    io.json(decoder + '-started-private.json', dict(pid=proc.pid, controller_PID=os.getpid()))
                    m.require(proc.wait(timeout=1800) == 0, 'first verifier failure; no retry')
                finally:
                    if proc.poll() is None:
                        proc.kill(); proc.wait()
                log.flush(); os.fsync(log.fileno())
            m.require((m.OUT / (decoder + '.log')).stat().st_size <= 65536, 'bounded verifier log')
        one, two = [io.read(name) for name in RECEIPTS]
        ticket = synchronize(io, contract, rows, one, two)
        replaced = remove(io, ticket, contract, rows, one, two)
        m.recheck(contract, protected)
        free = m.available()
        delta = free - io.read('operation-private.json')['before_available_bytes']
        m.require(replaced == m.COUNT and delta > m.CAP, 'actual all-inclusive reclamation not observed')
        io.json('result-private.json', dict(PASS=True, replaced=replaced, measured_free_increase=delta,
                available_workspace_bytes=free, runtime='CLOSED', independent_backup_verified=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('execute', 'zlib', 'gzip'))
    args = parser.parse_args()
    try:
        execute() if args.action == 'execute' else worker(args.action)
    except Exception as error:
        if OWNED and m.OUT.is_dir() and not m.OUT.is_symlink() and m.OUT.resolve() == m.OUT and not (m.OUT / 'STOP-private.json').exists():
            remaining = [name for name in m.names() if os.path.lexists(m.FRAMES / name)]
            io = LocalIO({}, [], [])
            io.json('STOP-private.json', dict(PASS=False, error=type(error).__name__ + ': ' + str(error),
                    first_failure_terminal=True, retry_permitted=False, remaining_original_count=len(remaining),
                    remaining_original_members=remaining, all_partial_artifacts_retained=True, runtime='CLOSED'))
        raise
