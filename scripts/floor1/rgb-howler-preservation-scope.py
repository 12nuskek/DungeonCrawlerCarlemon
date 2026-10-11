"""Preparation-only inventory for 17 retained Howler chunks. No execution API."""
from pathlib import Path
import importlib.util
import os

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path('/workspace/scratch')
PREPARATION = SCRATCH / 'howler-rgb-preservation-preparation-r1-20261011'
PROPOSED_OUTPUT = SCRATCH / 'howler-rgb-preservation-r1-20261011'
BASE = 'cc6a2c1d297ae3f879b11f93f517bf46a6a29ba0'
RUNTIME_RESERVATION = 17694519296
FRAME = 240 * 160 * 3
FRAMES, CHUNKS, RAW_BYTES = 28700, 17, 3306240000
BLOCK = 4096
METADATA_CAP = 16 * 1024**2
METADATA_FILES = 64
AUDIT_RESERVE = 128 * 1024**2
PLANS = (
    ('Howler1-STOP94', 'c01-howler-continuation-r1-20261010',
     'howler-continuation', 12520, 7,
     'c01-howler-runtime-r1-post-STOP-private-readback-20261010.json'),
    ('Howler2-continuation-PASS', 'c01-howler2-continuation-r1-20261011',
     'howler-continuation', 14136, 8,
     'c01-howler2-runtime-final-readback-private-r1-20261011.json'),
    ('Howler2-cold-PASS', 'c01-howler2-continuation-r1-20261011',
     'howler-new-save-cold', 2044, 2,
     'c01-howler2-runtime-final-readback-private-r1-20261011.json'),
)
SPEC = importlib.util.spec_from_file_location(
    'accepted_expanded_preservation', ROOT / 'scripts/floor1/rgb-preservation-expanded.py')
accepted = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(accepted)
engine = accepted.m
require = engine.require
SOURCE_FILES = (
    'scripts/floor1/rgb-howler-preservation-scope.py',
    'scripts/test-howler-rgb-preservation-scope-offline.py',
    'scripts/prepare-howler-rgb-preservation-r1.py',
)


def definitions():
    rows = []
    for label, root, stage, count, chunks, manifest in PLANS:
        for i in range(chunks):
            start = 2000 * i + 1
            frames = min(2000, count - start + 1)
            name = f'motion-{i:03}.rgb'
            rows.append(dict(recording=label, chunk=i, first_frame=start,
                             last_frame=start + frames - 1, frames=frames,
                             raw_path=str(SCRATCH / root / stage / name),
                             compressed_relative_path=f'{label}/{name}.gz',
                             frame_hashes_relative_path=f'{label}/{name}.frame-sha256.bin',
                             historical_manifest_path=str(SCRATCH / manifest)))
        require(start + frames == count + 1, 'source recording totals')
    require(len(rows) == CHUNKS and sum(r['frames'] for r in rows) == FRAMES,
            'source 17-chunk/28700-frame totals')
    return rows


def validate_scope(rows, protected_paths=(), previously_replaced=()):
    require(len(rows) == CHUNKS, 'exactly 17 chunks required')
    protected, replaced = set(protected_paths), set(previously_replaced)
    for row, want in zip(rows, definitions()):
        require(row['raw_path'] not in replaced, 'previously replaced target')
        require(row['raw_path'] not in protected, 'protected target forbidden')
        require(all(row.get(k) == v for k, v in want.items()),
                'wrong scope/order/path/chunk/frame range')
        require(row['raw_identity']['bytes'] == row['frames'] * FRAME,
                'complete RGB24 frame bytes required')
    require(sum(r['raw_identity']['bytes'] for r in rows) == RAW_BYTES,
            'exact 3306240000 raw bytes required')


def check_entry(entry):
    """Read-only identity/hash check, also usable on isolated inert fixtures."""
    path = Path(entry['raw_path'])
    require(engine.identity(path) == entry['raw_identity'], 'modified target identity')
    require(path.stat().st_nlink == 1, 'target hardlink forbidden')
    require(engine.digest(path) == entry['raw_SHA256'], 'modified target bytes')
    require(engine.identity(path) == entry['raw_identity'], 'target changed during read')


def inventory_check(rows, protected_entries, previously_replaced):
    validate_scope(rows, protected_entries, previously_replaced)
    for row in rows:
        check_entry(row)
    engine.protected_check(dict(protected_entries=protected_entries, recordings=[]))


def round_block(n):
    return ((n + BLOCK - 1) // BLOCK) * BLOCK


def gzip_bound(n):
    # gzip 1.13 manual: 5 bytes per 32 KiB input block. RFC1952 fixed header
    # and trailer: 10+8 bytes with -n -c. Allow one additional terminal block.
    require(type(n) is int and n >= 0, 'nonnegative integer codec input')
    return n + 18 + 5 * ((n + 32767) // 32768 + 1)


def storage_cap(rows):
    validate_scope(rows)
    replacements = sum(round_block(gzip_bound(r['frames'] * FRAME)) for r in rows)
    ledgers = sum(round_block(32 * r['frames']) for r in rows)
    components = dict(
        replacement_allocated_bound_bytes=replacements,
        frame_ledgers_allocated_bound_bytes=ledgers,
        extra_allocation_block_per_stream_bytes=2 * CHUNKS * BLOCK,
        metadata_and_inert_fixture_cap_bytes=METADATA_CAP,
        metadata_allocation_rounding_bytes=METADATA_FILES * BLOCK,
        six_output_and_preparation_directories_bytes=6 * BLOCK,
        one_pending_codec_write_bytes=65536 + BLOCK,
        external_source_docs_Git_audit_reserve_bytes=AUDIT_RESERVE,
    )
    return dict(components=components, all_inclusive_cap_bytes=round_block(sum(components.values())),
                worst_case_compressed_logical_bytes=sum(gzip_bound(r['frames'] * FRAME) for r in rows),
                frame_ledger_logical_bytes=32 * FRAMES,
                formula='per chunk: n + 18 + 5*(ceil(n/32768)+1); no savings assumed',
                sources=['https://manpages.debian.org/trixie/gzip/gzip.1.en.html',
                         'https://www.rfc-editor.org/rfc/rfc1952.html'],
                output_block_bytes=BLOCK, metadata_file_limit=METADATA_FILES,
                metadata_logical_limit_bytes=METADATA_CAP,
                decoded_file_copies=0, originals_duplicated=0)


def receipt_check(receipt, label, contract_hash, mapping_hash, rows):
    require(receipt['PASS'] is True and receipt['verification'] == label and
            receipt['chunk_count'] == CHUNKS and receipt['frames'] == FRAMES and
            receipt['decoded_bytes'] == RAW_BYTES and receipt['originals_retained'] is True,
            'incomplete 17-chunk verification')
    require(receipt['contract_SHA256'] == contract_hash and
            receipt['mapping_SHA256'] == mapping_hash, 'verification identity binding')
    keys = ('recording', 'chunk', 'frames', 'raw_SHA256', 'compressed_SHA256')
    require([[x[k] for k in keys] for x in receipt['chunks']] ==
            [[x[k] for k in keys] for x in rows], 'verification chunk mapping')
    require(all(x['exact_frame_bytes'] is True and x['exact_EOF'] is True
                for x in receipt['chunks']), 'incomplete decoded byte/frame/EOF verification')


def pair_check(one, two, contract_hash, mapping_hash, rows):
    validate_scope(rows)
    for receipt, label in ((one, 'pass1-zlib'), (two, 'pass2-independent-gzip')):
        receipt_check(receipt, label, contract_hash, mapping_hash, rows)
    require(type(one['pid']) is int and type(two['pid']) is int and
            one['pid'] > 0 and two['pid'] > 0 and one['pid'] != two['pid'],
            'two distinct verifier processes required')


def available_workspace():
    stat = os.statvfs(SCRATCH)
    require(stat.f_frsize == BLOCK and not stat.f_flag & os.ST_RDONLY,
            'reviewed writable workspace filesystem/block identity required')
    return stat.f_bavail * stat.f_frsize
