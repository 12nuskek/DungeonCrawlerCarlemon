#!/usr/bin/env python3
"""One inert suite: raw TAR bytes in memory, modeled originals, no compressor/removal."""
from pathlib import Path
from unittest import mock
import copy
import hashlib
import importlib.util
import io as streams
import json
import os
import tarfile

PATH = Path(__file__).resolve().parent / 'floor1/v01-frame-archive-controller.py'
SPEC = importlib.util.spec_from_file_location('frame_controller_inert', PATH)
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)
m = c.m


def rows_fixture():
    return [dict(member=name, raw_path=str(m.FRAMES / name), bytes=m.FRAME_BYTES, SHA256='0' * 64,
                 identity=dict(device='27', inode=str(i + 1), mode='384', uid='1000',
                               mtime_ns='1791605082751057979', bytes=m.FRAME_BYTES,
                               allocated_bytes=118784, nlink=1),
                 archive_member=dict(name=name, bytes=m.FRAME_BYTES, ordinal=i, mode='384', uid='1000',
                                     archive_mtime_decimal='1791605082.751057979')) for i, name in enumerate(m.names())]


class VirtualIO:
    def __init__(self, contract, rows):
        self.contract, self.rows = copy.deepcopy(contract), copy.deepcopy(rows)
        self.removed = []
        self.free = 14971453440
        self.changed = False
        self.files = {str(path): '1' * 64 for path in c.required_paths()}
        self.files[str(m.OUT / c.LEDGERS[0])] = self.files[str(m.OUT / c.LEDGERS[1])] = hashlib.sha256(c.ledger(rows)).hexdigest()
        self.operation = dict(pid=100, source_commit=contract['source_commit'], proposal_SHA256='2' * 64)
        self.one = dict(PASS=True, decoder='zlib', target_count=m.COUNT, decoded_frame_bytes=m.COUNT * m.FRAME_BYTES,
                        archive_member_count=32166, archive_member_chain_SHA256='3' * 64,
                        exact_archive_original_frame_hash_EOF=True, originals_retained=True,
                        pid=101, controller_PID=100, source_commit=contract['source_commit'], fresh_process=True,
                        proposal_SHA256='2' * 64, inventory_SHA256='4' * 64,
                        ledger_SHA256=self.files[str(m.OUT / c.LEDGERS[0])])
        self.two = dict(self.one, decoder='gzip', pid=102)
        self.metadata = {'operation-private.json': self.operation, c.RECEIPTS[0]: self.one, c.RECEIPTS[1]: self.two,
                         'zlib-started-private.json': dict(pid=101, controller_PID=100),
                         'gzip-started-private.json': dict(pid=102, controller_PID=100)}
        self.file_calls = self.dir_calls = 0
        self.fail_file = self.fail_dir = None
        self.usage_bytes = 1024**2

    def read(self, name):
        return self.metadata[name]

    def digest(self, path):
        return self.files[str(path)]

    def checks(self):
        m.require(not self.changed, 'inert changed source/provider/archive/protected/original')

    def usage(self):
        m.require(self.usage_bytes <= m.METADATA_CAP, 'inert metadata cap exceeded')
        return dict(logical_bytes=self.usage_bytes, allocated_bytes=self.usage_bytes)

    def available(self):
        return self.free

    def sync_file(self, path):
        m.require(not self.removed, 'sync precedes every modeled removal')
        self.file_calls += 1
        if self.file_calls == self.fail_file:
            raise OSError('inert fsync file failure')

    def sync_dir(self, path):
        m.require(not self.removed, 'directory sync precedes modeled removal')
        self.dir_calls += 1
        if self.dir_calls == self.fail_dir:
            raise OSError('inert directory fsync failure')

    def json(self, name, value):
        m.require(name not in self.metadata, 'exclusive inert metadata')
        self.metadata[name] = value
        self.files[str(m.OUT / name)] = hashlib.sha256(m.encode(value)).hexdigest()
        if not self.removed:
            self.sync_file(m.OUT / name); self.sync_dir(m.OUT)

    def unlink(self, row):
        m.require('synchronization-private.json' in self.metadata, 'durable barrier precedes modeled unlink')
        self.removed.append(row['member'])


def tar_record(name, data, kind=tarfile.REGTYPE):
    entry = tarfile.TarInfo(name)
    entry.type, entry.size = kind, len(data)
    return entry.tobuf(format=tarfile.USTAR_FORMAT) + data + bytes((-len(data)) % 512)


def main():
    m.require(not m.git('status', '--porcelain') and not any(os.path.lexists(p) for p in (m.TESTS, m.PREP, m.OUT, m.AUTHORITY)), 'clean fresh suite; proposal and replacement unstarted')
    m.TESTS.mkdir(mode=0o700)
    cases, negatives = [], []
    rows = rows_fixture()
    contract = dict(source_commit=m.git('rev-parse', 'HEAD'), target_count=m.COUNT, target_allocated_bytes=m.ALLOCATED,
                    cap_bytes=m.CAP, runtime_reservation_bytes=m.WARDEN, execution_permitted=False,
                    archive=dict(SHA256=m.ARCHIVE_SHA), proposed_operation_root=str(m.OUT),
                    archive_member_count=32166, archive_member_chain_SHA256='3' * 64, inventory_SHA256='4' * 64)
    def reject(name, mutation=None, premature=False, ticket_mutation=None):
        io = VirtualIO(contract, rows)
        if mutation:
            mutation(io)
        try:
            ticket = None if premature else c.synchronize(io, io.contract, io.rows, io.one, io.two)
            if ticket_mutation:
                ticket_mutation(io, ticket)
            c.remove(io, ticket, io.contract, io.rows, io.one, io.two)
        except (RuntimeError, OSError, KeyError, ValueError) as error:
            m.require(not io.removed, 'negative performed premature modeled removal')
            cases.append(name); negatives.append(dict(case=name, error=type(error).__name__ + ': ' + str(error), originals_retained=m.COUNT, modeled_removals=0))
        else:
            raise AssertionError('negative accepted: ' + name)
    reject('premature-removal', premature=True)
    reject('wrong-count', lambda io: io.contract.update(target_count=m.COUNT - 1))
    reject('missing-target', lambda io: io.rows.pop())
    reject('reordered-targets', lambda io: io.rows.reverse())
    reject('duplicate-inode', lambda io: io.rows[1]['identity'].update(inode=io.rows[0]['identity']['inode']))
    reject('hardlinked-original', lambda io: io.rows[0]['identity'].update(nlink=2))
    reject('float-nanosecond-timestamp', lambda io: io.rows[0]['identity'].update(mtime_ns=1791605082751058000.0))
    reject('rounded-integer-timestamp', lambda io: io.rows[0]['identity'].update(mtime_ns=1791605082751058000))
    reject('wrong-member', lambda io: io.rows[0]['archive_member'].update(name='other/frame.ppm'))
    reject('duplicate-member-ordinal', lambda io: io.rows[1]['archive_member'].update(ordinal=io.rows[0]['archive_member']['ordinal']))
    reject('wrong-original-path', lambda io: io.rows[0].update(raw_path='/tmp/unapproved.ppm'))
    reject('wrong-archive', lambda io: io.contract['archive'].update(SHA256='other'))
    reject('wrong-operation-root', lambda io: io.contract.update(proposed_operation_root='/tmp/forbidden'))
    reject('wrong-cap', lambda io: io.contract.update(cap_bytes=m.CAP - 1))
    reject('weakened-Warden-reservation', lambda io: io.contract.update(runtime_reservation_bytes=m.WARDEN - 1))
    reject('unreviewed-execution-flag', lambda io: io.contract.update(execution_permitted=True))
    for key, value in (('PASS', False), ('decoder', 'zlib'), ('target_count', m.COUNT - 1), ('decoded_frame_bytes', 1),
                       ('archive_member_count', 32165), ('archive_member_chain_SHA256', 'wrong'),
                       ('exact_archive_original_frame_hash_EOF', False), ('originals_retained', False),
                       ('pid', 101), ('pid', 100), ('pid', 0), ('controller_PID', 99), ('source_commit', 'other'),
                       ('fresh_process', False), ('proposal_SHA256', 'other'), ('inventory_SHA256', 'other'), ('ledger_SHA256', 'other')):
        reject('bad-receipt-' + key + '-' + str(value), lambda io, key=key, value=value: io.two.update({key: value}))
    reject('actual-child-PID-mismatch', lambda io: io.metadata['gzip-started-private.json'].update(pid=999))
    reject('altered-source-protected-original-or-archive', lambda io: setattr(io, 'changed', True))
    reject('altered-proof-ledger', lambda io: io.files.update({str(m.OUT / c.LEDGERS[1]): 'other'}))
    reject('insufficient-fresh-capacity', lambda io: setattr(io, 'free', m.CAP - 1))
    reject('insufficient-Warden-plus-restore-headroom', lambda io: setattr(io, 'free', m.WARDEN - m.ALLOCATED + m.CAP - 1))
    reject('metadata-cap-exhaustion', lambda io: setattr(io, 'usage_bytes', m.METADATA_CAP + 1))
    for number in (1, len(c.required_paths()), len(c.required_paths()) + 1):
        reject('file-fsync-failure-' + str(number), lambda io, number=number: setattr(io, 'fail_file', number))
    for number in (1, 5, 6):
        reject('directory-fsync-failure-' + str(number), lambda io, number=number: setattr(io, 'fail_dir', number))
    reject('missing-synchronized-coverage', ticket_mutation=lambda io, ticket: ticket.hashes.pop(next(iter(ticket.hashes))))
    reject('modified-sync-receipt', ticket_mutation=lambda io, ticket: io.files.update({str(m.OUT / 'synchronization-private.json'): 'other'}))
    reject('modified-persisted-receipt-after-sync', ticket_mutation=lambda io, ticket: io.metadata.update({c.RECEIPTS[0]: dict(io.one, PASS=False)}))
    reject('modified-persisted-inventory-after-sync', ticket_mutation=lambda io, ticket: io.files.update({str(m.PREP / 'frame-inventory-private.jsonl'): 'other'}))
    io = VirtualIO(contract, rows)
    ticket = c.synchronize(io, io.contract, io.rows, io.one, io.two)
    m.require(c.remove(io, ticket, io.contract, io.rows, io.one, io.two) == m.COUNT and io.removed == m.names(), 'complete ordered modeled-only removal')
    cases.append('positive-complete-synchronized-inert-controller')
    try:
        c.remove(io, ticket, io.contract, io.rows, io.one, io.two)
    except RuntimeError:
        cases.append('one-use-ticket-replay-rejected')
    else:
        raise AssertionError('ticket replay accepted')
    frame = m.HEADER + b'X' * m.PIXELS
    name = m.names()[0]
    synthetic = dict(member=name, SHA256=hashlib.sha256(frame).hexdigest())
    raw = tar_record(name, frame) + bytes(1024)
    with mock.patch.object(m.engine, 'zlib_blocks', return_value=iter([raw])):
        checked = m.archive_scan([synthetic])
    m.require(checked['targets'] == 1 and checked['exact_TAR_and_gzip_EOF'], 'strict synthetic parser positive')
    cases.append('positive-strict-in-memory-native-PPM-TAR')
    timestamp = '1791605082.751057979'
    record = ('mtime=' + timestamp + '\n').encode()
    length = len(record) + 3
    while len(str(length).encode() + b' ' + record) != length:
        length = len(str(length).encode() + b' ' + record)
    pax_bytes = str(length).encode() + b' ' + record
    pax_tar = tar_record('././@PaxHeader', pax_bytes, tarfile.XHDTYPE) + raw
    with mock.patch.object(m.engine, 'zlib_blocks', return_value=iter([pax_tar])):
        parsed = m.archive_scan([synthetic])
    m.require(parsed['archive_members'][name]['archive_mtime_decimal'] == timestamp, 'PAX decimal timestamp preserved exactly')
    cases.append('positive-strict-PAX-decimal-metadata')
    parser_negatives = [('duplicate-member', tar_record(name, frame) * 2 + bytes(1024)),
                        ('unsafe-parent-path', tar_record('../escape.ppm', frame) + bytes(1024)),
                        ('unsafe-absolute-path', tar_record('/escape.ppm', frame) + bytes(1024)),
                        ('symlink-member', tar_record(name, b'', tarfile.SYMTYPE) + bytes(1024)),
                        ('hardlink-member', tar_record(name, b'', tarfile.LNKTYPE) + bytes(1024)),
                        ('wrong-member-missing-target', tar_record('baseline/battle-00001.ppm', frame) + bytes(1024)),
                        ('altered-native-bytes', tar_record(name, frame[:-1] + b'Y') + bytes(1024)),
                        ('wrong-native-header', tar_record(name, b'X' + frame[1:]) + bytes(1024)),
                        ('truncated-member', raw[:2000]), ('missing-second-EOF-block', raw[:-512]),
                        ('unexpected-post-TAR-member', raw + tar_record('late', b'bad')), ('bad-padding-EOF', raw + b'X'),
                        ('ambiguous-dot-name', tar_record('baseline/./battle-00000.ppm', frame) + bytes(1024)),
                        ('malformed-PAX-length', tar_record('././@PaxHeader', b'2 mtime=1\n', tarfile.XHDTYPE) + raw),
                        ('duplicate-PAX-fields', tar_record('././@PaxHeader', pax_bytes * 2, tarfile.XHDTYPE) + raw),
                        ('repeated-PAX-header', tar_record('././@PaxHeader', pax_bytes, tarfile.XHDTYPE) * 2 + raw)]
    for label, fixture in parser_negatives:
        with mock.patch.object(m.engine, 'zlib_blocks', return_value=iter([fixture])):
            try:
                m.archive_scan([synthetic])
            except RuntimeError as error:
                cases.append('parser-' + label); negatives.append(dict(case='parser-' + label, error=str(error), actual_frames_touched=0))
            else:
                raise AssertionError('unsafe parser accepted: ' + label)
    exact = '1791605082751057979'
    m.require(json.loads(m.encode(dict(mtime_ns=exact)))['mtime_ns'] == exact, 'exact nanosecond decimal round trip')
    cases.append('exact-21ns-STOP-timestamp-preserved-as-decimal-string')
    for free, extra, concurrent in ((m.CAP + m.WARDEN + m.SELECTED_RESTORE_CAP - 1, m.SELECTED_RESTORE_CAP, True),
                                    (m.CAP + m.WARDEN + m.ALLOCATED - 1, m.ALLOCATED, True)):
        try:
            m.capacity(free, extra, concurrent)
        except RuntimeError:
            cases.append('insufficient-restoration-plus-reservation-' + str(extra))
        else:
            raise AssertionError('restore capacity admitted below bound')
    with mock.patch.object(m, 'load_json', return_value=dict(preserved_reservation_bytes=m.WARDEN, files={str(m.FRAMES / name): 'sha'}, protected_history={})):
        try:
            m.consumer_admission({str(m.FRAMES / name)})
        except RuntimeError:
            cases.append('active-Warden-frame-consumer-rejected')
        else:
            raise AssertionError('active consumer overlap admitted')
    for request in ([], [name] * 2, [name, m.names()[1], m.names()[2]], ['../escape']):
        try:
            m.retained_frames({}, [], request)
        except RuntimeError:
            cases.append('bounded-adapter-request-rejection-' + str(len(cases)))
        else:
            raise AssertionError('bad adapter request accepted')
    # Adapter retention checks use ordered archive pixel hashes and immutable
    # old RGB digests, modeled FFV1 stdout only. No decoder is actually started.
    pixel_frames = [b'A' * m.PIXELS, b'B' * m.PIXELS]
    pixel_hashes = {f'{case}/battle-{i:05}.ppm': hashlib.sha256(frame).digest()
                    for case in ('baseline', 'candidate') for i, frame in enumerate(pixel_frames)}
    ordered = hashlib.sha256(b''.join(pixel_frames)).hexdigest()
    historic = dict(numbered_frames=2, terminal_partial_frame_capture=False,
                    every_lossless_pixel_verified=True, lossless_SHA256='clip', RGB_SHA256=ordered, decoded_RGB_SHA256=ordered)
    class FakeDecoder:
        def __init__(self, payload):
            self.stdout, self.stderr = streams.BytesIO(payload), streams.BytesIO()
        def poll(self): return 0
        def wait(self, timeout=None): return 0
        def kill(self): pass
    for label, payload in (('positive', b''.join(pixel_frames)), ('wrong-order', b''.join(reversed(pixel_frames))),
                           ('altered-pixels', b'X' + b''.join(pixel_frames)[1:]), ('truncated', pixel_frames[0]),
                           ('extra-EOF-frame', b''.join(pixel_frames) + b'X')):
        with mock.patch.object(m, 'CASE_COUNT', 2), mock.patch.object(m, 'check_file'), \
             mock.patch.object(m, 'archive_scan', return_value=dict(pixel_hashes=pixel_hashes)), \
             mock.patch.object(m, 'load_json', return_value=historic), mock.patch.object(m, 'digest', return_value='clip'), \
             mock.patch.object(m.subprocess, 'Popen', side_effect=lambda *a, **kw: FakeDecoder(payload)):
            try:
                result = m.check_capture_retention(dict(archive={}), [])
            except RuntimeError:
                m.require(label != 'positive', 'positive inert retained-video check failed')
                cases.append('retained-video-' + label + '-rejected')
            else:
                m.require(label == 'positive' and all(r['directory_restorations'] == 0 for r in result), 'altered retained-video accepted')
                cases.append('positive-retained-video-ordered-pixels-without-restoration')
    providers = m.provider_files()
    fixture = m.TESTS / 'inert-sync.fixture'
    fixture.write_bytes(b'keep')
    primitive = object.__new__(c.LocalIO)
    primitive.sync_file(fixture); primitive.sync_dir(m.TESTS)
    with mock.patch.object(c.os, 'fsync', side_effect=OSError('inert synchronization failure')):
        try:
            primitive.sync_file(fixture)
        except OSError:
            cases.append('actual-inert-fsync-failure-retains-file')
        else:
            raise AssertionError('fsync failure swallowed')
    m.require(fixture.read_bytes() == b'keep' and not m.git('status', '--porcelain') and
              not any(os.path.lexists(p) for p in (m.PREP, m.OUT, m.AUTHORITY)), 'source and all real frames untouched')
    result = dict(PASS=True, source_commit=m.git('rev-parse', 'HEAD'), accepted_base=m.BASE,
                  cases=cases, case_count=len(cases), rejected_cases=negatives,
                  target_count=m.COUNT, cap_bytes=m.CAP, original_allocated_bytes=m.ALLOCATED,
                  exact_metadata_encoding='canonical decimal strings', source_files_SHA256={p: m.digest(m.ROOT / p) for p in m.FILES},
                  provider_files_SHA256=providers, parser_fixtures_in_memory=True, modeled_removals_only=True,
                  real_unlinks=0, compression_processes=0, actual_verifier_processes=0, actual_consumer_decoder_processes=0,
                  gameplay_processes=0, runtime_claims=0, execution_permitted=False, first_failure_terminal=True,
                  private_output_cap_bytes=4 * 1024**2)
    m.engine.Budget(m.TESTS, cap=4 * 1024**2, reserve=0).json(m.TESTS / 'offline-admission-private.json', result)
    primitive.sync_dir(m.TESTS)
    print(f'PASS {len(cases)} inert checks; actual compression/verifiers/removals/gameplay=0')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if m.TESTS.exists() and not (m.TESTS / 'offline-STOP-private.json').exists():
            m.engine.Budget(m.TESTS, cap=4 * 1024**2, reserve=0).json(m.TESTS / 'offline-STOP-private.json', dict(
                PASS=False, error=type(error).__name__ + ': ' + str(error), retry_permitted=False,
                first_failure_terminal=True, all_actual_originals_retained=True))
        raise
