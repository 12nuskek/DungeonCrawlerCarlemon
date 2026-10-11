#!/usr/bin/env python3
"""Write a private review proposal, never freeze/execute preservation or gameplay."""
from pathlib import Path
import importlib.util
import json
import os
import stat
import subprocess
import sys

PATH = Path(__file__).resolve().parent / 'floor1/rgb-howler-preservation-scope.py'
SPEC = importlib.util.spec_from_file_location('howler_scope_proposal', PATH)
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)
engine = scope.engine
OUT = scope.PREPARATION
PRIOR_42 = scope.accepted.OUT
HANDOFF = scope.SCRATCH / 'c01-howler2-runtime-final-handoff-private-r1-20261011.json'
DISCONNECT = dict(
    notification_UTC='2026-10-11T02:52:00Z',
    status_checkpoint_source=scope.BASE,
    retained_untracked_sources=list(scope.SOURCE_FILES[:2]),
    preparation_processes=0, preservation_processes=0,
    output_directories_existed=False, recordings_accessible=17,
    raw_bytes_accessible=scope.RAW_BYTES, Saves_accessible=3,
    accessibility_was_not_hash_verification=True,
    recovery='same executor confirmed; existing source retained; no replay or replacement',
)


def read(path):
    return json.loads(path.read_text())


def check_hash(path, expected):
    actual = engine.digest(path)
    scope.require(actual == expected, 'accepted historical hash differs: ' + str(path))
    return actual


def metadata_usage():
    paths = [OUT, *OUT.rglob('*')]
    files = [p for p in paths if not stat.S_ISDIR(p.lstat().st_mode)]
    # The retained inert symlink negative is counted by lstat, never followed.
    logical = sum(p.lstat().st_size for p in files)
    allocated = sum(p.lstat().st_blocks * 512 for p in paths)
    scope.require(len(files) <= scope.METADATA_FILES and
                  logical <= scope.METADATA_CAP and
                  allocated <= scope.METADATA_CAP + scope.METADATA_FILES * scope.BLOCK + 2 * scope.BLOCK,
                  'bounded preparation metadata/fixture allocation')
    return dict(file_count=len(files), logical_bytes=logical, allocated_bytes=allocated)


def write(name, obj):
    data = (json.dumps(obj, indent=2, sort_keys=True) + '\n').encode()
    usage = metadata_usage()
    scope.require(usage['logical_bytes'] + len(data) <= scope.METADATA_CAP,
                  'bounded proposal metadata write')
    with (OUT / name).open('xb') as file:
        os.chmod(OUT / name, 0o600)
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
    metadata_usage()


def accepted_preservation():
    prior_31 = scope.accepted.prior_admission()
    contract = read(PRIOR_42 / 'preservation-contract.json')
    mapping = read(PRIOR_42 / 'representation-mapping-private.json')
    one = read(PRIOR_42 / 'verification-pass1-private.json')
    two = read(PRIOR_42 / 'verification-pass2-private.json')
    result = read(PRIOR_42 / 'preservation-result-private.json')
    handoff_path = scope.SCRATCH / 'floor1-rgb-expanded-preservation-r2-final-handoff-20261010.json'
    handoff = read(handoff_path)
    scope.require(contract['source_commit'] == handoff['source_commit'] ==
                  'efa8015a255539c1d65ebd7ea71f7d4c0cd959d4' and handoff['PASS'] is True,
                  'accepted 42-file source/result identity')
    for name, expected in handoff['private_receipt_hashes'].items():
        check_hash(PRIOR_42 / name, expected)
    for rel, expected in contract['source_files_SHA256'].items():
        check_hash(scope.ROOT / rel, expected)
        blob = subprocess.check_output(['git', 'show', contract['source_commit'] + ':' + rel], cwd=scope.ROOT)
        scope.require(engine.hashlib.sha256(blob).hexdigest() == expected, 'accepted source blob identity')
    engine.code_check(contract)
    origin, dependencies = scope.accepted.decoder_dependencies()
    scope.require(origin == contract['zlib_module_origin'] and
                  dependencies == contract['tool_dependencies_SHA256'] and
                  engine.zlib.ZLIB_RUNTIME_VERSION == contract['zlib_version'] and
                  subprocess.check_output([str(engine.GZIP), '--version'], text=True).splitlines()[0] ==
                  contract['gzip_version'] and not os.environ.get('GZIP'),
                  'accepted fixed codec/provider/dependency identity')
    scope.accepted.validate_layout(mapping['chunks'])
    contract_hash = engine.digest(PRIOR_42 / 'preservation-contract.json')
    mapping_hash = engine.digest(PRIOR_42 / 'representation-mapping-private.json')
    for receipt, label in ((one, 'pass1-zlib'), (two, 'pass2-independent-gzip')):
        scope.accepted.receipt_check(receipt, label, contract_hash, mapping_hash, mapping['chunks'])
    scope.require(one['pid'] != two['pid'] and result['PASS'] is True and
                  result['replaced_file_count'] == 42, 'accepted two-pass 42-file replacement result')
    replaced = {r['raw_path'] for r in mapping['chunks']}
    replaced.update(read(scope.accepted.PRIOR / 'preservation-result-private.json')['replaced_paths'])
    scope.require(len(replaced) == 73 and all(not Path(p).exists() for p in replaced),
                  '73 earlier completed replacements remain historical')
    # Recheck retained representations and ledgers by SHA, without repeating a
    # codec test or a decoded-byte pass. Originals removed historically stay gone.
    for root in (scope.accepted.PRIOR, PRIOR_42):
        previous = read(root / 'representation-mapping-private.json')
        for row in previous['chunks']:
            check_hash(root / row['compressed_relative_path'], row['compressed_SHA256'])
            check_hash(root / row['frame_hashes_relative_path'], row['frame_hashes_SHA256'])
    return contract, replaced, dict(
        prior_31_admission=prior_31, accepted_42_source=contract['source_commit'],
        accepted_42_handoff_SHA256=engine.digest(handoff_path),
        accepted_42_contract_SHA256=contract_hash, accepted_42_mapping_SHA256=mapping_hash,
        prior_replaced_files=73, prior_codec_tests_repeated=False,
        prior_decoded_verification_passes_repeated=False,
        retained_replacements_and_ledgers_SHA256_rechecked=True,
    )


def main():
    scope.require(len(sys.argv) == 1, 'preparation only; no action/execute arguments')
    scope.require(not scope.accepted.git('status', '--porcelain'), 'clean committed proposal source')
    scope.require(not scope.PROPOSED_OUTPUT.exists(), 'proposed execution output must remain absent')
    scope.require(OUT.is_dir() and not (OUT / 'preparation-STOP-private.json').exists() and
                  not (OUT / 'proposal-contract-private.json').exists(), 'one fresh preparation after inert admission')
    checks = read(OUT / 'offline-checks-private.json')
    head = scope.accepted.git('rev-parse', 'HEAD')
    scope.require(checks['PASS'] is True and checks['source_commit'] == head, 'exact new inert check source')
    for rel, expected in checks['source_files_SHA256'].items():
        check_hash(scope.ROOT / rel, expected)
    prior, replaced, preservation_history = accepted_preservation()
    handoff = read(HANDOFF)
    scope.require(handoff['PASS'] is True and handoff['tested_commit'] ==
                  handoff['published_commit'] == '25634620d5a721f1c6c913f8e59188a2958deee9',
                  'accepted Howler2 runtime source identity')
    for name, expected in handoff['private_receipt_hashes'].items():
        check_hash(Path(name), expected)
    root2 = scope.SCRATCH / scope.PLANS[1][1]
    freeze2 = read(root2 / 'freeze.json')
    manifest1 = scope.SCRATCH / scope.PLANS[0][5]
    check_hash(manifest1, freeze2['prior_claims']['files'][str(manifest1)])
    historical_hashes = {str(HANDOFF): engine.digest(HANDOFF), str(manifest1): engine.digest(manifest1)}
    rows, recordings, protected = [], [], {}
    for label, base, stage, count, chunks, name in scope.PLANS:
        parent, manifest = scope.SCRATCH / base, scope.SCRATCH / name
        data = read(manifest)
        historical_hashes[str(manifest)] = engine.digest(manifest)
        if label == 'Howler1-STOP94':
            check_hash(parent / 'STOP.json', data['STOP_SHA256'])
            check_hash(parent / 'freeze.json', data['freeze_SHA256'])
            for path, expected in data['external_receipts_SHA256'].items():
                check_hash(Path(path), expected)
                historical_hashes[path] = expected
        wants = [r for r in scope.definitions() if r['recording'] == label]
        directory = parent / stage
        scope.require(sorted(str(p) for p in directory.glob('motion*.rgb')) ==
                      sorted(r['raw_path'] for r in wants), 'exact live 17-file inventory')
        for want in wants:
            path = Path(want['raw_path'])
            retained = data['complete_runtime_files'][str(path.relative_to(parent))]
            row = dict(want, raw_identity=engine.identity(path), raw_SHA256=retained['SHA256'])
            scope.require(row['raw_identity']['bytes'] == retained['bytes'], 'historical raw byte count')
            scope.check_entry(row)
            rows.append(row)
        index = directory / 'frame-index.bin'
        retained_index = data['complete_runtime_files'][str(index.relative_to(parent))]
        engine.index_check(index, count)
        check_hash(index, retained_index['SHA256'])
        for relative, retained in data['complete_runtime_files'].items():
            path = parent / relative
            if path in {Path(r['raw_path']) for r in wants}:
                continue
            # Only entries belonging to this exact stage, not another stage's raw files.
            if not path.is_relative_to(directory):
                continue
            scope.require(path.stat().st_size == retained['bytes'], 'historical protected byte count')
            check_hash(path, retained['SHA256'])
            protected[str(path)] = dict(identity=engine.identity(path), SHA256=retained['SHA256'])
        recordings.append(dict(recording=label, frames=count, chunks=chunks,
                               original_bytes=count * scope.FRAME,
                               index_path=str(index), index_SHA256=retained_index['SHA256'],
                               historical_manifest_path=str(manifest),
                               historical_manifest_SHA256=historical_hashes[str(manifest)],
                               native_frame_numerator=16777216, native_frame_denominator=280896,
                               sample_interval_native_frames=1, original_chunk_frames=2000))
    targets = {Path(r['raw_path']) for r in rows}
    roots = {scope.SCRATCH / p[1] for p in scope.PLANS} | {
        scope.accepted.PRIOR, scope.accepted.FAILED, PRIOR_42}
    remaining = {p for root in roots for p in root.rglob('*') if p.is_file()}
    remaining.update(p for p in scope.SCRATCH.rglob('*.rgb') if not p.is_relative_to(OUT))
    remaining.update(Path(p) for p in historical_hashes)
    remaining.add(HANDOFF)
    for path in sorted(remaining - targets):
        if str(path) not in protected:
            protected[str(path)] = dict(identity=engine.identity(path), SHA256=engine.digest(path))
    scope.validate_scope(rows, protected, replaced)
    cap = scope.storage_cap(rows)
    scope.require(cap == checks['storage_cap'], 'tested exact capacity derivation')
    free = scope.available_workspace()
    scope.require(free >= cap['all_inclusive_cap_bytes'], 'full worst-case local preservation cap unavailable')
    scope.require(not scope.accepted.git('status', '--porcelain') and
                  scope.accepted.git('rev-parse', 'HEAD') == head, 'source stable during proposal')
    write('disconnect-checkpoint-preserved-private.json', DISCONNECT)
    source_hashes = dict(prior['source_files_SHA256'])
    source_hashes.update(checks['source_files_SHA256'])
    proposal = dict(
        name='Howler remaining 17 RGB local preservation r1', status='PROPOSAL_ONLY_REVIEW_REQUIRED',
        preparation_only=True, preservation_execution_permitted=False,
        base_commit=scope.BASE, tested_source_commit=head, source_files_SHA256=source_hashes,
        offline_receipt_SHA256=engine.digest(OUT / 'offline-checks-private.json'),
        proposal_directory=str(OUT), proposed_preservation_output=str(scope.PROPOSED_OUTPUT),
        output_exclusivity='Must remain absent until separately reviewed preservation admission; no overwrite/resume',
        authorization=dict(standing_local_approval_UTC='2026-10-10T21:42:24Z',
                           cleanup_approval_UTC='2026-10-11T02:50:13Z',
                           transcript='Authenticated parent delegation retained privately',
                           scope='local only; two complete passes; this increment is preparation only'),
        width=240, height=160, pixel_format='RGB24', bytes_per_frame=scope.FRAME,
        chunk_count=scope.CHUNKS, frames=scope.FRAMES, original_bytes=scope.RAW_BYTES,
        raw_allocated_bytes=sum(r['raw_identity']['allocated_bytes'] for r in rows),
        chunks=rows, recordings=recordings, protected_entries=protected,
        historical_input_receipts_SHA256=historical_hashes,
        historical_inputs_verified_by_full_SHA256=True,
        previous_preservation=preservation_history, previously_replaced_paths=sorted(replaced),
        protected_scope='All non-target files in both Howler parent roots, prior31/failed-expanded-r1/completed42 roots; all other scratch RGB; immutable receipt inputs. All other paths outside the mutation allowlist.',
        future_mutation_allowlist=dict(create_only=[str(scope.PROPOSED_OUTPUT)],
                                      unlink_only_after_two_complete_passes=[r['raw_path'] for r in rows]),
        format=prior['format'], compress_command=prior['compress_command'],
        decoder_pass1=prior['decoder_pass1'], decoder_pass2=prior['decoder_pass2'],
        gzip_version=prior['gzip_version'], gzip_executable_SHA256=prior['gzip_executable_SHA256'],
        python_executable_SHA256=prior['python_executable_SHA256'],
        zlib_version=prior['zlib_version'], zlib_module_origin=prior['zlib_module_origin'],
        tool_dependencies_SHA256=prior['tool_dependencies_SHA256'],
        accepted_verifier_implementation_SHA256=prior['source_files_SHA256']['scripts/floor1/rgb-preservation.py'],
        decoder_block_bytes=65536,
        frame_comparison_buffer_bound_bytes=4 * scope.FRAME + 2 * 65536,
        full_decoded_copies=0,
        source_adapter_role='17-file inventory/receipt/cap only; historical 31/42 launchers and removal barriers unchanged',
        future_launcher='Not implemented or admitted. Separate reviewed wiring must use this exact scope/cap and the accepted complete verifiers; never invoke historical 31/42 launchers.',
        storage=cap, available_workspace_bytes_at_proposal=free,
        future_capacity_checks='Fresh /workspace available bytes must cover full cap before any preservation admission, after inventory and before operation; originals retained throughout. Bound logical and allocated output plus audit reserve; metadata/file ceilings enforced, first failure terminal.',
        future_verification='All17 chunks in order: both passes independently reopen raw+gzip, compare EVERY decoded frame byte, frozen frame SHA256, chunk hash/count/dimensions/ranges and exact raw/ledger/decoded EOF; replacement hashes before/after. Pass1 Python zlib; pass2 distinct cold Python PID with GNU gzip -dc. Both bind the same contract/mapping. Recheck target/index/protected/source/tool identities before any replacement.',
        future_replacement_gate='Only after both complete passes and measured all-inclusive positive net savings; recheck cap/protected entries/replacements, then only exact17 redundant raw paths. Do not require, imply or admit Warden capacity. Failure leaves originals and partial outputs; no automatic retry/settings alternative.',
        restoration='gzip -dc emits exact original bytes; concatenate mapped chunks in recorded order. Stream to a consumer; no unreserved full decoded copy.',
        first_failure_terminal=True, retry_permitted=False, all_originals_retained_until_two_complete_passes=True,
        runtime_reservation_bytes=scope.RUNTIME_RESERVATION, runtime_capacity_blocked=True,
        runtime_capacity_shortfall_bytes=max(0, scope.RUNTIME_RESERVATION - free),
        runtime='CLOSED', runtime_authority=False, runtime_freeze=False, runtime_claims=0,
        gameplay_processes=0, new_Save_actions=0, new_cold_processes=0,
        recordings_compressed=0, redundant_raw_files_replaced=0, cache_files_deleted=0,
        cache_cleanup='Seven earlier unreferenced pyc files remain untouched; separate scope and manifest/regeneration recheck required',
        memory_backed_mount_used=False, private_uploads=0, independent_backup_verified=False,
        historical_V01_baseline_candidate=[6, 4], historical_STOP117='visual8536 before expected B8402',
        Library_failures=dict(uploads=5, supported_downloads=1, cause='unknown', recovered_original_bytes=0),
        disconnect_checkpoint_SHA256=engine.digest(OUT / 'disconnect-checkpoint-preserved-private.json'),
    )
    write('proposal-contract-private.json', proposal)
    write('proposal-preparation-receipt-private.json', dict(
        PASS=True, preparation_only=True, source_commit=head,
        proposal_SHA256=engine.digest(OUT / 'proposal-contract-private.json'),
        offline_checks_SHA256=engine.digest(OUT / 'offline-checks-private.json'),
        exact_live_target_count=len(rows), raw_bytes=scope.RAW_BYTES,
        protected_entry_count=len(protected), accepted_input_hashes_verified=True,
        source_files_SHA256=source_hashes, metadata_usage_before_receipt=metadata_usage(),
        all_inclusive_cap_bytes=cap['all_inclusive_cap_bytes'], originals_retained=True,
        actual_compression=False, actual_decoded_passes=0, actual_replacements=0,
        runtime='CLOSED', next='Independent review of private proposal; future launcher/admission remains absent'))
    print('PASS preparation only: 17 historical raw hashes checked; proposal=' +
          engine.digest(OUT / 'proposal-contract-private.json') +
          ' cap=' + str(cap['all_inclusive_cap_bytes']))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT.exists() and not (OUT / 'preparation-STOP-private.json').exists():
            with (OUT / 'preparation-STOP-private.json').open('x') as file:
                json.dump(dict(PASS=False, error=type(error).__name__ + ': ' + str(error),
                               first_failure_terminal=True, retry_permitted=False,
                               partial_outputs_retained=True), file, indent=2)
        raise
