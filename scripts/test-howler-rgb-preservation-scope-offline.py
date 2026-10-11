#!/usr/bin/env python3
"""Bounded inert scope checks only. Never run a compressor or gameplay process."""
from pathlib import Path
import copy
import importlib.util
import json
import os

PATH = Path(__file__).resolve().parent / 'floor1/rgb-howler-preservation-scope.py'
SPEC = importlib.util.spec_from_file_location('howler_scope', PATH)
scope = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scope)


def main():
    scope.require(not scope.accepted.git('status', '--porcelain'), 'clean committed source required')
    out = scope.PREPARATION
    scope.require(not out.exists() and not scope.PROPOSED_OUTPUT.exists(), 'fresh preparation only')
    out.mkdir(mode=0o700)
    fixture = out / 'inert-fixtures'
    fixture.mkdir(mode=0o700)
    cases = []

    def reject(name, call):
        try:
            call()
        except (RuntimeError, FileNotFoundError, KeyError):
            cases.append(name)
        else:
            raise AssertionError('negative accepted: ' + name)

    rows = [dict(r, raw_identity={'bytes': r['frames'] * scope.FRAME},
                 raw_SHA256='inert-raw-' + str(i), compressed_SHA256='inert-gzip-' + str(i))
            for i, r in enumerate(scope.definitions())]
    scope.validate_scope(rows)
    cases.append('exact-17-chunk-28700-frame-3306240000-byte-layout')
    reject('wrong-count-missing', lambda: scope.validate_scope(rows[:-1]))
    reject('wrong-count-extra', lambda: scope.validate_scope([*rows, rows[0]]))
    for field, value in (
        ('raw_path', '/workspace/scratch/unapproved/motion-000.rgb'),
        ('recording', 'unapproved-recording'), ('chunk', 1), ('first_frame', 2),
        ('last_frame', 1999), ('frames', 1999),
        ('compressed_relative_path', '../protected.gz'),
        ('frame_hashes_relative_path', '../protected.bin'),
        ('historical_manifest_path', '/workspace/scratch/unapproved-receipt.json'),
    ):
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        reject('wrong-scope-' + field, lambda bad=bad: scope.validate_scope(bad))
    reject('reordered-chunks', lambda: scope.validate_scope(list(reversed(rows))))
    bad = copy.deepcopy(rows)
    bad[0]['raw_identity']['bytes'] -= 1
    reject('wrong-rgb-byte-count', lambda: scope.validate_scope(bad))
    reject('previously-replaced', lambda: scope.validate_scope(rows, previously_replaced=[rows[0]['raw_path']]))
    reject('protected-file-selected', lambda: scope.validate_scope(rows, protected_paths=[rows[0]['raw_path']]))

    raw = fixture / 'target.bin'
    raw.write_bytes(b'ABCD')
    entry = dict(raw_path=str(raw), raw_identity=scope.engine.identity(raw), raw_SHA256=scope.engine.digest(raw))
    scope.check_entry(entry)
    cases.append('inert-identity-positive')
    reject('missing-target', lambda: scope.check_entry(dict(entry, raw_path=str(fixture / 'absent.bin'))))
    alias = fixture / 'alias.bin'
    alias.symlink_to(raw.name)
    reject('symlink-target', lambda: scope.check_entry(dict(entry, raw_path=str(alias))))
    raw.write_bytes(b'WXYZ')
    os.utime(raw, ns=(raw.stat().st_atime_ns, entry['raw_identity']['mtime_ns']))
    reject('modified-target-same-size-and-restored-mtime', lambda: scope.check_entry(entry))
    protected = fixture / 'protected.bin'
    protected.write_bytes(b'keep')
    contract = dict(recordings=[], protected_entries={str(protected):
                    dict(identity=scope.engine.identity(protected), SHA256=scope.engine.digest(protected))})
    scope.engine.protected_check(contract)
    cases.append('inert-protected-file-positive')
    protected.write_bytes(b'fail')
    reject('modified-protected-file', lambda: scope.engine.protected_check(contract))

    chunks = [dict(r, exact_frame_bytes=True, exact_EOF=True) for r in rows]
    one = dict(PASS=True, verification='pass1-zlib', chunk_count=scope.CHUNKS,
               frames=scope.FRAMES, decoded_bytes=scope.RAW_BYTES, originals_retained=True,
               contract_SHA256='inert-contract', mapping_SHA256='inert-mapping', chunks=chunks, pid=101)
    two = dict(one, verification='pass2-independent-gzip', pid=102)
    scope.pair_check(one, two, 'inert-contract', 'inert-mapping', rows)
    cases.append('complete-pair-receipt-positive-no-codec-execution')
    for field, value in (('PASS', False), ('chunk_count', 16), ('frames', 28699),
                         ('decoded_bytes', scope.RAW_BYTES - 1), ('originals_retained', False),
                         ('contract_SHA256', 'other'), ('mapping_SHA256', 'other'),
                         ('verification', 'pass1-zlib'), ('pid', 101), ('pid', 0)):
        bad = dict(two, **{field: value})
        reject('incomplete-pair-' + field + '-' + str(value),
               lambda bad=bad: scope.pair_check(one, bad, 'inert-contract', 'inert-mapping', rows))
    for field, value in (('exact_frame_bytes', False), ('exact_EOF', False),
                         ('raw_SHA256', 'other'), ('compressed_SHA256', 'other'), ('frames', 1)):
        bad = copy.deepcopy(two)
        bad['chunks'][0][field] = value
        reject('incomplete-chunk-' + field,
               lambda bad=bad: scope.pair_check(one, bad, 'inert-contract', 'inert-mapping', rows))
    reject('missing-receipt-chunk', lambda: scope.pair_check(
        one, dict(two, chunks=chunks[:-1]), 'inert-contract', 'inert-mapping', rows))

    for n, expected in ((0, 23), (1, 29), (32768, 32796), (32769, 32802)):
        scope.require(scope.gzip_bound(n) == expected, 'fixed codec ceiling boundary')
        cases.append('gzip-bound-inert-arithmetic-' + str(n))
    cap = scope.storage_cap(rows)
    scope.require(cap['all_inclusive_cap_bytes'] == scope.round_block(sum(cap['components'].values())),
                  'all-inclusive cap component sum')
    scope.require(cap['worst_case_compressed_logical_bytes'] > scope.RAW_BYTES,
                  'no likely-savings assumption')
    scope.require(scope.RUNTIME_RESERVATION == 17694519296, 'unchanged runtime reservation')
    cases.append('cap-and-reservation-arithmetic-only')
    scope.require(not scope.accepted.git('status', '--porcelain'), 'source unchanged during fixtures')
    result = dict(PASS=True, source_commit=scope.accepted.git('rev-parse', 'HEAD'),
                  case_count=len(cases), cases=cases, storage_cap=cap,
                  inert_fixture_logical_bytes=sum(p.lstat().st_size for p in fixture.iterdir()),
                  real_targets_modified=0,
                  recordings_compressed=0, decoded_verification_processes=0,
                  codec_tests_repeated=False, gameplay_processes=0, runtime_claims=0,
                  preparation_only=True, remaining_output_retained=True,
                  source_files_SHA256={p: scope.engine.digest(scope.ROOT / p) for p in scope.SOURCE_FILES})
    with (out / 'offline-checks-private.json').open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(f'PASS {len(cases)} inert scope/identity/pair/cap checks; no compression or execution')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        out = scope.PREPARATION
        if out.exists() and not (out / 'preparation-STOP-private.json').exists():
            with (out / 'preparation-STOP-private.json').open('x') as f:
                json.dump(dict(PASS=False, error=type(error).__name__ + ': ' + str(error),
                               first_failure_terminal=True, retry_permitted=False), f, indent=2)
        raise
