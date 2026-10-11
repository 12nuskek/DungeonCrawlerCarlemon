#!/usr/bin/env python3
"""One bounded inert admission suite: virtual removals, no real codec/target writes."""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import os
from unittest import mock

PATH = Path(__file__).resolve().parent / 'floor1/howler-rgb-preservation-controller.py'
SPEC = importlib.util.spec_from_file_location('howler_controller_offline', PATH)
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True) + '\n').encode()


def fixture_contract(proposal):
    contract = copy.deepcopy(proposal)
    contract.update(approved_proposal_SHA256=controller.PROPOSAL_SHA,
                    output_root=str(controller.OUT), preservation_only=True,
                    preservation_source_commit=controller.scope.accepted.git('rev-parse', 'HEAD'),
                    status='FROZEN_LOCAL_PRESERVATION_ONLY', preservation_execution_permitted=True)
    contract['source_files_SHA256'].update({p: controller.engine.digest(controller.ROOT / p)
                                          for p in controller.FILES})
    for row in contract['chunks']:
        row['frame_hashes_SHA256'] = sha(b'L' * (32 * row['frames']))
    return contract


class VirtualIO:
    """Inert filesystem model with canonical path strings; never opens those paths."""
    def __init__(self, contract, proposal):
        self.contract, self.proposal = copy.deepcopy(contract), copy.deepcopy(proposal)
        self.preparation = dict(logical_bytes=200000, allocated_bytes=221184)
        self.removed, self.synced_files, self.synced_dirs = [], [], []
        self.files, self.identities = {}, {}
        self.sync_file_calls = self.sync_dir_calls = 0
        self.fail_file_at = self.fail_dir_at = None
        self.changed_raw = self.changed_protected = self.changed_source = False
        self.usage_override = None
        self.free = 10 * 1024**3
        self.mapping = dict(contract_SHA256=sha(encoded(self.contract)),
                            proposal_SHA256=controller.PROPOSAL_SHA, cap_bytes=controller.CAP,
                            output_root=str(controller.OUT), chunks=[])
        for i, original in enumerate(self.contract['chunks']):
            row = dict(original)
            data = b'INERT-GZIP-PLACEHOLDER-' + str(i).encode()
            identity = dict(device=27, inode=10000 + i, bytes=len(data), allocated_bytes=4096,
                            mode=0o600, uid=0, mtime_ns=1)
            row.update(compressed_identity=identity, compressed_SHA256=sha(data))
            self.mapping['chunks'].append(row)
            compressed = str(controller.OUT / row['compressed_relative_path'])
            ledger = str(controller.OUT / row['frame_hashes_relative_path'])
            self.files[compressed] = data
            self.identities[compressed] = identity
            self.files[ledger] = b'L' * (32 * row['frames'])
            self.identities[ledger] = dict(bytes=32 * row['frames'])
        self.files[str(controller.OUT / controller.CONTRACT_NAME)] = encoded(self.contract)
        self.files[str(controller.OUT / controller.MAPPING_NAME)] = encoded(self.mapping)
        results = [dict(recording=r['recording'], chunk=r['chunk'], frames=r['frames'],
                        raw_SHA256=r['raw_SHA256'], compressed_SHA256=r['compressed_SHA256'],
                        exact_frame_bytes=True, exact_EOF=True) for r in self.mapping['chunks']]
        self.one = dict(PASS=True, verification='pass1-zlib', chunks=copy.deepcopy(results),
                        chunk_count=17, frames=28700, decoded_bytes=3306240000,
                        originals_retained=True, pid=101, controller_PID=100,
                        source_commit=self.contract['preservation_source_commit'],
                        fresh_verifier_process=True, no_second_full_decoded_copy=True,
                        contract_SHA256=self.mapping['contract_SHA256'],
                        mapping_SHA256=sha(encoded(self.mapping)))
        self.two = copy.deepcopy(self.one)
        self.two.update(verification='pass2-independent-gzip', pid=102)
        for name, receipt in zip(controller.RECEIPT_NAMES, (self.one, self.two)):
            self.files[str(controller.OUT / name)] = encoded(receipt)
        self.files[str(controller.OUT / 'operation-start-private.json')] = encoded(dict(
                pid=100, source_commit=self.contract['preservation_source_commit'],
                contract_SHA256=self.mapping['contract_SHA256'], preservation_only=True))
        for action, pid in (('verify-zlib', 101), ('verify-gzip', 102)):
            self.files[str(controller.OUT / (action + '-started-private.json'))] = encoded(
                    dict(pid=pid, controller_PID=100))
            self.files[str(controller.OUT / (action + '.log'))] = b'INERT ONLY\n'

    def read(self, name):
        return json.loads(self.files[str(controller.OUT / name)])

    def digest(self, path):
        if str(path) not in self.files:
            raise FileNotFoundError('inert missing evidence')
        return sha(self.files[str(path)])

    def identity(self, path):
        if str(path) not in self.identities:
            raise FileNotFoundError('inert missing identity')
        return self.identities[str(path)]

    def check_raw(self, row):
        controller.require(not self.changed_raw and row['raw_path'] not in self.removed,
                           'inert changed/missing original')

    def protected_check(self, contract):
        controller.require(not self.changed_protected, 'inert changed protected data')

    def source_check(self, contract):
        controller.require(not self.changed_source, 'inert changed source/provider')

    def usage(self):
        if self.usage_override is not None:
            return self.usage_override
        return dict(logical_bytes=sum(len(b) for b in self.files.values()),
                    allocated_bytes=sum(controller.scope.round_block(len(b)) for b in self.files.values()))

    def available(self):
        return self.free

    def sync_file(self, path):
        controller.require(not self.removed, 'synchronization must precede every unlink')
        self.sync_file_calls += 1
        if self.sync_file_calls == self.fail_file_at:
            raise OSError('inert file synchronization failure')
        self.digest(path)
        self.synced_files.append(str(path))

    def sync_dir(self, path):
        controller.require(not self.removed, 'directory synchronization before removal')
        self.sync_dir_calls += 1
        if self.sync_dir_calls == self.fail_dir_at:
            raise OSError('inert directory synchronization failure')
        self.synced_dirs.append(str(path))

    def json(self, name, value):
        path = str(controller.OUT / name)
        controller.require(path not in self.files, 'exclusive inert receipt')
        self.files[path] = encoded(value)
        # Progress writes happen after simulated removal and are still persisted;
        # pre-removal synchronization failures use the same modeled primitive.
        if not self.removed:
            self.sync_file(Path(path))
            self.sync_dir(controller.OUT)

    def unlink_raw(self, row):
        self.check_raw(row)
        controller.require(str(controller.OUT / 'synchronization-complete-private.json') in self.files and
                           str(controller.OUT.parent) in self.synced_dirs, 'persisted barrier required')
        self.removed.append(row['raw_path'])  # A list only: no os.unlink or Path.unlink.


def main():
    controller.require(not controller.scope.accepted.git('status', '--porcelain'), 'clean committed suite source')
    controller.require(not controller.OFFLINE.exists() and not controller.OUT.exists() and
                       not controller.AUTHORITY.exists(), 'fresh inert suite; actual execution closed')
    proposal = controller.accepted_inputs()
    controller.provider_check(proposal)
    out = controller.OFFLINE
    out.mkdir(mode=0o700)
    cases = []
    negative_receipts = []
    original_proposal_hash = controller.engine.digest(controller.PROPOSAL)
    contract = fixture_contract(proposal)

    def reject(name, mutation=None, ticket_mutation=None, premature=False):
        io = VirtualIO(contract, proposal)
        if mutation:
            mutation(io)
        # Persist the modeled metadata mutation, so coverage negatives exercise
        # the actual receipt/schema gate rather than a stale in-memory object.
        for filename, value in ((controller.CONTRACT_NAME, io.contract),
                                (controller.MAPPING_NAME, io.mapping),
                                (controller.RECEIPT_NAMES[0], io.one),
                                (controller.RECEIPT_NAMES[1], io.two)):
            io.files[str(controller.OUT / filename)] = encoded(value)
        try:
            ticket = None if premature else controller.synchronize_barrier(
                    io, io.contract, proposal, io.mapping, io.one, io.two)
            if ticket_mutation:
                ticket_mutation(io, ticket)
            controller.replace_originals(io, ticket, io.contract, proposal, io.mapping, io.one, io.two)
        except (RuntimeError, OSError, KeyError, ValueError) as error:
            controller.require(io.removed == [], 'negative performed a simulated premature unlink')
            cases.append(name)
            negative_receipts.append(dict(case=name, error=type(error).__name__ + ': ' + str(error),
                                          virtual_originals_retained=17, virtual_unlinks=0,
                                          file_sync_calls=io.sync_file_calls, directory_sync_calls=io.sync_dir_calls))
        else:
            raise AssertionError('negative accepted: ' + name)

    reject('premature-removal-without-synchronized-ticket', premature=True)
    reject('wrong-output-root', lambda io: io.contract.update(output_root='/tmp/forbidden'))
    reject('wrong-contract-cap', lambda io: io.contract['storage'].update(all_inclusive_cap_bytes=3758096384))
    reject('wrong-mapping-cap', lambda io: io.mapping.update(cap_bytes=3758096384))
    reject('wrong-proposal-identity', lambda io: io.contract.update(approved_proposal_SHA256='other'))
    reject('wrong-source-inventory', lambda io: io.contract['source_files_SHA256'].pop(controller.FILES[0]))
    reject('wrong-codec-settings', lambda io: io.contract['compress_command'].append('-9'))
    reject('missing-mapping-chunk', lambda io: io.mapping['chunks'].pop())
    reject('reordered-mapping-chunks', lambda io: io.mapping['chunks'].reverse())
    reject('wrong-raw-scope', lambda io: io.mapping['chunks'][0].update(raw_path='/tmp/unapproved.rgb'))
    reject('changed-original-hash-binding', lambda io: io.contract['chunks'][0].update(raw_SHA256='other'))
    reject('changed-protected-scope', lambda io: io.contract['protected_entries'].pop(next(iter(io.contract['protected_entries']))))
    reject('changed-protected-data', lambda io: setattr(io, 'changed_protected', True))
    reject('changed-original-data', lambda io: setattr(io, 'changed_raw', True))
    reject('changed-source-or-provider', lambda io: setattr(io, 'changed_source', True))
    reject('missing-replacement', lambda io: io.files.pop(str(controller.OUT / io.mapping['chunks'][0]['compressed_relative_path'])))
    reject('changed-replacement-hash', lambda io: io.files.update({str(controller.OUT / io.mapping['chunks'][0]['compressed_relative_path']): b'changed'}))
    reject('changed-ledger-hash', lambda io: io.files.update({str(controller.OUT / io.mapping['chunks'][0]['frame_hashes_relative_path']): b'changed'}))
    for key, value in (('PASS', False), ('chunk_count', 16), ('frames', 28699),
                       ('decoded_bytes', 3306239999), ('originals_retained', False),
                       ('contract_SHA256', 'other'), ('mapping_SHA256', 'other'),
                       ('pid', 101), ('pid', 0), ('pid', -1), ('pid', 100),
                       ('controller_PID', 99), ('fresh_verifier_process', False),
                       ('no_second_full_decoded_copy', False), ('source_commit', 'other')):
        reject('receipt-negative-' + key + '-' + str(value), lambda io, key=key, value=value: io.two.update({key: value}))
    reject('partial-EOF-receipt', lambda io: io.two['chunks'][0].update(exact_EOF=False))
    reject('partial-byte-comparison-receipt', lambda io: io.two['chunks'][0].update(exact_frame_bytes=False))
    reject('missing-receipt-chunk', lambda io: io.two['chunks'].pop())
    reject('reordered-receipt-chunks', lambda io: io.two['chunks'].reverse())
    reject('actual-child-PID-mismatch', lambda io: io.files.update({str(controller.OUT / 'verify-gzip-started-private.json'): encoded(dict(pid=999, controller_PID=100))}))
    reject('controller-contract-mismatch', lambda io: io.files.update({str(controller.OUT / 'operation-start-private.json'): encoded(dict(pid=100, source_commit=io.contract['preservation_source_commit'], contract_SHA256='other', preservation_only=True))}))
    reject('no-positive-savings', lambda io: setattr(io, 'usage_override', dict(logical_bytes=3221225472, allocated_bytes=3221225472)))
    reject('all-inclusive-cap-exceeded', lambda io: setattr(io, 'usage_override', dict(logical_bytes=controller.CAP, allocated_bytes=controller.CAP)))
    reject('audit-capacity-unavailable', lambda io: setattr(io, 'free', 0))
    for at in (1, len(controller.synchronized_paths(VirtualIO(contract, proposal).mapping)), 44):
        reject('file-fsync-failure-' + str(at), lambda io, at=at: setattr(io, 'fail_file_at', at))
    for at in (1, 5, 6):
        reject('directory-fsync-failure-' + str(at), lambda io, at=at: setattr(io, 'fail_dir_at', at))
    reject('missing-synchronized-coverage', ticket_mutation=lambda io, ticket: ticket.hashes.pop(next(iter(ticket.hashes))))
    reject('receipt-modified-after-synchronization', ticket_mutation=lambda io, ticket: io.files.update({str(controller.OUT / controller.RECEIPT_NAMES[0]): b'changed'}))
    reject('synchronization-record-modified', ticket_mutation=lambda io, ticket: io.files.update({str(controller.OUT / 'synchronization-complete-private.json'): b'changed'}))

    io = VirtualIO(contract, proposal)
    legacy_free = VirtualIO(contract, proposal)
    legacy_free.free = 1024**3
    accounting = controller.barrier_checks(legacy_free, legacy_free.contract, proposal,
                                          legacy_free.mapping, legacy_free.one, legacy_free.two)
    controller.require(accounting['runtime_capacity_admitted'] is False,
                       'preservation barrier must not inherit a runtime reservation')
    cases.append('positive-preservation-barrier-without-legacy-runtime-capacity-gate')
    ticket = controller.synchronize_barrier(io, io.contract, proposal, io.mapping, io.one, io.two)
    expected_paths = {str(p) for p in controller.synchronized_paths(io.mapping)}
    controller.require(expected_paths <= set(io.synced_files), 'all mapped replacements/ledgers/receipts synchronized')
    controller.replace_originals(io, ticket, io.contract, proposal, io.mapping, io.one, io.two)
    controller.require(io.removed == [r['raw_path'] for r in proposal['chunks']], 'exact virtual 17-file removal order')
    cases.append('positive-complete-synchronized-virtual-controller-only')
    try:
        controller.replace_originals(io, ticket, io.contract, proposal, io.mapping, io.one, io.two)
    except RuntimeError:
        cases.append('one-use-ticket-replay-rejected')
    else:
        raise AssertionError('ticket replay accepted')

    # Actual filesystem synchronization primitives on a fresh four-byte inert
    # file only; failures are injected, evidence retained, no unlink is called.
    fixture = out / 'inert-sync.fixture'
    fixture.write_bytes(b'keep')
    primitive = object.__new__(controller.LocalIO)
    primitive.sync_file(fixture)
    primitive.sync_dir(out)
    cases.append('actual-inert-file-and-directory-fsync-primitives')
    for method, operand in ((primitive.sync_file, fixture), (primitive.sync_dir, out)):
        with mock.patch.object(controller.os, 'fsync', side_effect=OSError('inert forced synchronization failure')):
            try:
                method(operand)
            except OSError:
                cases.append('actual-inert-fsync-failure-' + method.__name__)
            else:
                raise AssertionError('synchronization failure swallowed')
    try:
        list(controller.engine.frame_blocks([b'X' * (controller.scope.FRAME - 1)], 1))
    except RuntimeError:
        cases.append('actual-inert-stream-partial-frame-EOF')
    else:
        raise AssertionError('partial frame EOF accepted')
    controller.require(fixture.read_bytes() == b'keep', 'inert sync fixture retained')
    positive = 100 + controller.FINAL_METADATA_RESERVE + 1
    controller.require(controller.measured_space_savings(100, positive) == positive - 100,
                       'measured positive reclamation after final metadata reserve')
    cases.append('positive-inert-final-capacity-counter')
    for after in (100, 99, 100 + controller.FINAL_METADATA_RESERVE):
        try:
            controller.measured_space_savings(100, after)
        except RuntimeError:
            cases.append('no-final-measured-reclamation-' + str(after))
        else:
            raise AssertionError('unobserved actual reclamation accepted')
    controller.require(controller.engine.digest(controller.PROPOSAL) == original_proposal_hash and
                       not controller.OUT.exists() and not controller.AUTHORITY.exists(),
                       'proposal unchanged; actual preservation unstarted')
    controller.require(not controller.scope.accepted.git('status', '--porcelain'), 'source unchanged during suite')
    pins = {p: controller.engine.digest(controller.ROOT / p) for p in controller.FILES}
    result = dict(PASS=True, source_commit=controller.scope.accepted.git('rev-parse', 'HEAD'),
                  accepted_base=controller.BASE, proposal_SHA256=controller.PROPOSAL_SHA,
                  cap_bytes=controller.CAP, chunk_count=17, frames=28700, raw_bytes=3306240000,
                  protected_entries=376, case_count=len(cases), cases=cases,
                  pre_removal_negative_receipts=negative_receipts,
                  source_files_SHA256=pins, accepted_source_files_SHA256=proposal['source_files_SHA256'],
                  codec_provider_identities_rechecked=True, accepted_verifier_reused=True,
                  codec_or_full_recording_tests_repeated=False, virtual_removals_only=True,
                  real_unlinks=0, compressors_started=0, actual_verifier_processes=0,
                  actual_preservation_processes=0, runtime_claims=0, gameplay_processes=0,
                  execution_authority_created=False, preservation_output_created=False,
                  execution_permitted=False, independent_review_required=True,
                  first_failure_terminal=True, offline_fixture_cap_bytes=4 * 1024**2)
    with controller.ADMISSION.open('x') as file:
        os.chmod(controller.ADMISSION, 0o600)
        json.dump(result, file, indent=2)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
    primitive.sync_dir(out)
    usage = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    controller.require(usage < 4 * 1024**2, 'bounded inert suite output')
    print(f'PASS {len(cases)} inert controller/admission checks; real compression/verifiers/unlinks=0')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if controller.OFFLINE.exists() and not (controller.OFFLINE / 'offline-STOP-private.json').exists():
            with (controller.OFFLINE / 'offline-STOP-private.json').open('x') as file:
                json.dump(dict(PASS=False, error=type(error).__name__ + ': ' + str(error),
                               first_failure_terminal=True, retry_permitted=False,
                               partial_outputs_retained=True), file, indent=2)
        raise
