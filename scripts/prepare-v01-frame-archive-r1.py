#!/usr/bin/env python3
"""One proposal-only freeze; never removes frames or runs future verifiers."""
from pathlib import Path
import importlib.util
import json
import os

PATH = Path(__file__).resolve().parent / 'floor1/v01-frame-archive.py'
SPEC = importlib.util.spec_from_file_location('frame_proposal', PATH)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def main():
    m.require(not m.git('status', '--porcelain') and m.git('merge-base', m.BASE, 'HEAD') == m.BASE,
              'clean committed proposal source ancestry')
    m.require(not any(os.path.lexists(p) for p in (m.PREP, m.OUT, m.AUTHORITY)), 'fresh names; proposal only')
    tests = m.load_json(m.TESTS / 'offline-admission-private.json')
    m.require(tests['PASS'] is True and tests['source_commit'] == m.git('rev-parse', 'HEAD') and
              tests['execution_permitted'] is False, 'tested exact source')
    m.require(m.digest(m.ARCHIVE) == m.ARCHIVE_SHA and m.digest(m.MANIFEST) == m.MANIFEST_SHA,
              'verified historical archive and manifest')
    m.capacity(m.available())
    manifest = m.load_json(m.MANIFEST)
    rows = [dict(member=name, raw_path=str(m.FRAMES / name), bytes=manifest[name]['bytes'],
                 SHA256=manifest[name]['SHA256'], identity=m.identity(m.FRAMES / name)) for name in m.names()]
    m.target_scope(rows)
    # This proposal performs one inventory confirmation. It is not either of
    # the two separately required future verifier-process receipts.
    checked = m.archive_scan(rows, compare_originals=True)
    m.require(checked['members'] == 32166, 'complete historical archive member count')
    for row in rows:
        row['archive_member'] = checked['archive_members'][row['member']]
    targets = {r['raw_path'] for r in rows}
    paths = {str(p) for p in m.FRAMES.rglob('*') if p.is_file() or p.is_symlink()} - targets
    # All other visual evidence, archive, build inputs, and active Warden pins
    # stay untouched. External active providers are pinned separately below.
    for path in m.WARDEN_INPUTS:
        paths.add(str(path))
        config = m.load_json(path)
        paths.update(p for p in set(config['files']) | set(config['protected_history']) if p.startswith('/workspace'))
    historic = m.load_json(m.SCRATCH / 'howler-rgb-preservation-r1-20261011/preservation-contract-private.json')
    paths.update(historic['protected_entries'])
    paths.update(str(p) for p in (m.SCRATCH / 'howler-rgb-preservation-r1-20261011').rglob('*') if p.is_file())
    protected = [dict(path=p, identity=m.identity(Path(p)), SHA256=m.digest(p)) for p in sorted(paths)]
    consumers = m.consumer_admission(paths)
    providers = m.provider_files()
    source = {p: m.digest(m.ROOT / p) for p in m.FILES}
    source.update(historic['source_files_SHA256'])
    m.require(all(m.digest(m.ROOT / p) == sha for p, sha in source.items()), 'exact source/helper closure')
    m.PREP.mkdir(mode=0o700)
    budget = m.engine.Budget(m.PREP, cap=m.CAP, reserve=m.AUDIT_RESERVE + m.SELECTED_RESTORE_CAP)
    for name, values in (('frame-inventory-private.jsonl', rows), ('protected-inventory-private.jsonl', protected)):
        budget.write(m.PREP / name, b''.join(m.encode(row) for row in values))
    budget.json(m.PREP / 'auxiliary-rounding-STOP-preserved-private.json', dict(
        status='HISTORICAL_READ_ONLY_AUXILIARY_STOP', error='AssertionError before hashing',
        first_file='/workspace/scratch/c01a-action-hints-r4-20261010/baseline/actual-native-lossless.mkv',
        actual_mtime_ns='1791605082751057979', rounded_coordinator_mtime_ns='1791605082751058000',
        discrepancy_ns=21, rejected_before_hashing=True, retries=0, changes=0,
        original_preservation_failure=False, resolution='All exact metadata remains decimal strings; no floating serialization'))
    semantics = {case: m.load_json(m.FRAMES / case / 'capture-retention.json') for case in ('baseline', 'candidate')}
    for case, r in semantics.items():
        m.require(r['numbered_frames'] == m.CASE_COUNT and r['terminal_partial_frame_capture'] is False and
                  r['every_lossless_pixel_verified'] is True and r['RGB_SHA256'] == r['decoded_RGB_SHA256'], 'historical capture semantics')
    contract = dict(status='PROPOSED_ONLY_REVIEW_REQUIRED', execution_permitted=False,
                    source_commit=m.git('rev-parse', 'HEAD'), accepted_base=m.BASE,
                    source_files_SHA256=source, provider_files_SHA256=providers,
                    archive=dict(identity=m.identity(m.ARCHIVE), SHA256=m.ARCHIVE_SHA),
                    archive_member_count=checked['members'], archive_member_chain_SHA256=checked['member_chain_SHA256'],
                    strict_tar_and_gzip_EOF=True, manifest_SHA256=m.MANIFEST_SHA,
                    inventory_SHA256=m.digest(m.PREP / 'frame-inventory-private.jsonl'),
                    protected_SHA256=m.digest(m.PREP / 'protected-inventory-private.jsonl'),
                    target_count=m.COUNT, target_logical_bytes=m.COUNT * m.FRAME_BYTES,
                    target_allocated_bytes=m.ALLOCATED, protected_count=len(protected),
                    preparation_root=str(m.PREP), proposed_operation_root=str(m.OUT),
                    cap_bytes=m.CAP, metadata_cap_bytes=m.METADATA_CAP,
                    audit_reserve_bytes=m.AUDIT_RESERVE, selected_restore_cap_bytes=m.SELECTED_RESTORE_CAP,
                    fresh_available_bytes=m.available(), conservative_net_savings_bytes=m.ALLOCATED - m.CAP,
                    peak_new_data_staging_bytes=0, full_restoration_allocated_bytes=m.ALLOCATED,
                    single_frame_restoration_allocated_bytes=118784,
                    exact_metadata_encoding='decimal strings for device/inode/uid/mode/mtime_ns; no float',
                    consumer_admission=consumers, historical_capture_semantics=semantics,
                    offline_admission_SHA256=m.digest(m.TESTS / 'offline-admission-private.json'),
                    future_verifiers=['fresh Python zlib strict TAR/original process', 'fresh GNU gzip strict TAR/original process'],
                    actual_future_verifier_processes=0, actual_replacements=0,
                    archive_modified=False, compression_operations=0, runtime='CLOSED',
                    runtime_reservation_bytes=m.WARDEN, independent_backup_verified=False)
    budget.json(m.PREP / 'proposal-private.json', contract)
    m.recheck(contract, protected, rows)
    budget.check()
    fd = os.open(m.PREP, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    print(json.dumps(dict(PASS=True, source_commit=contract['source_commit'], proposal_SHA256=m.digest(m.PREP / 'proposal-private.json'),
                          inventory_SHA256=contract['inventory_SHA256'], protected_count=len(protected),
                          targets=m.COUNT, future_verifier_processes=0, raw_removals=0, cap_bytes=m.CAP)))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if m.PREP.exists() and not (m.PREP / 'preparation-STOP-private.json').exists():
            m.engine.Budget(m.PREP, cap=m.CAP, reserve=0).json(m.PREP / 'preparation-STOP-private.json', dict(
                PASS=False, error=type(error).__name__ + ': ' + str(error), retry_permitted=False,
                first_failure_terminal=True, originals_retained=True, partial_outputs_retained=True))
        raise
