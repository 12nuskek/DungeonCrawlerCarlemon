"""Exact 13-chunk Warden proposal; real preservation entrypoints remain closed."""
from pathlib import Path
import importlib.util
import types

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path('/workspace/scratch')
BASE = '3eeb8d71e81e7f193d010f598786feacd7c0c19b'
PREPARATION = SCRATCH / 'warden-rgb-preservation-preparation-r1-20261011'
OFFLINE = SCRATCH / 'warden-rgb-preservation-offline-r1-20261011'
VISUAL = SCRATCH / 'warden-evidence-review-r1-20261011'
PROPOSED_OUTPUT = SCRATCH / 'warden-rgb-preservation-r1-20261011'
AUTHORITY = SCRATCH / 'warden-rgb-preservation-authority-r1-20261011.json'
RUNTIME = SCRATCH / 'c01-warden-continuation-runtime-r2-20261011'
HANDOFF = SCRATCH / 'c01-warden-runtime-admission-r2-20261011/runtime-result-handoff-private.json'
HANDOFF_SHA = '8d5345c8db1a0ad13e7e57c54784967ca389ad53338a8eb2f52ffdbf98e36098'
FRAME, FRAMES, CHUNKS, RAW_BYTES = 115200, 24207, 13, 2788646400
CAP = 2941345792
FILES = ('scripts/floor1/rgb-warden-preservation-scope.py',
         'scripts/prepare-warden-rgb-preservation-r1.py',
         'scripts/test-warden-rgb-preservation-offline.py',
         'docs/floor1/warden-rgb-preservation-r1-contract.md')


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


bindings = module('warden_preservation_bindings', 'scripts/floor1/warden-runtime-bindings.py')
accepted = module('warden_preservation_arithmetic', 'scripts/floor1/rgb-howler-preservation-scope.py')
engine, require = accepted.engine, accepted.require
BLOCK, METADATA_CAP, METADATA_FILES, AUDIT_RESERVE = (
    accepted.BLOCK, accepted.METADATA_CAP, accepted.METADATA_FILES, accepted.AUDIT_RESERVE)
round_block, gzip_bound = accepted.round_block, accepted.gzip_bound


def definitions():
    return [dict(recording='Warden-continuation-PASS', chunk=i, first_frame=2000*i+1,
                 last_frame=min(2000*(i+1), FRAMES), frames=min(2000, FRAMES-2000*i),
                 raw_path=str(RUNTIME / 'warden-continuation' / f'motion-{i:03}.rgb'),
                 compressed_relative_path=f'Warden-continuation-PASS/motion-{i:03}.rgb.gz',
                 frame_hashes_relative_path=f'Warden-continuation-PASS/motion-{i:03}.rgb.frame-sha256.bin',
                 historical_manifest_path=str(HANDOFF)) for i in range(CHUNKS)]


# Rebind only this imported instance's data. Accepted source files and completed
# operations stay untouched; their exact arithmetic/receipt functions are reused.
accepted.FRAMES, accepted.CHUNKS, accepted.RAW_BYTES = FRAMES, CHUNKS, RAW_BYTES
accepted.definitions = definitions
validate_scope, storage_cap, check_entry, pair_check = (
    accepted.validate_scope, accepted.storage_cap, accepted.check_entry, accepted.pair_check)


def closed(*args, **kwargs):
    raise RuntimeError('CLOSED: preparation only; separate preservation wiring/review required')


def inert_controller(proposal, proposal_hash):
    """Adapt accepted barrier only for its in-memory IO model, never LocalIO."""
    controller = module('warden_inert_barrier', 'scripts/floor1/howler-rgb-preservation-controller.py')
    facade = types.SimpleNamespace(CHUNKS=CHUNKS, FRAMES=FRAMES, RAW_BYTES=RAW_BYTES,
        FRAME=FRAME, METADATA_CAP=METADATA_CAP, METADATA_FILES=METADATA_FILES,
        BLOCK=BLOCK, AUDIT_RESERVE=AUDIT_RESERVE, round_block=round_block,
        gzip_bound=gzip_bound, storage_cap=storage_cap, validate_scope=validate_scope,
        pair_check=pair_check, accepted=types.SimpleNamespace(git=bindings.git))
    controller.scope, controller.CAP = facade, proposal['storage']['all_inclusive_cap_bytes']
    controller.OUT, controller.OFFLINE = PROPOSED_OUTPUT, OFFLINE
    controller.PROPOSAL_SHA, controller.FILES = proposal_hash, FILES
    validate = controller.validate_contract
    def validate_bound(contract, original):
        validate(contract, original)
        for key in ('actual_runtime_handoff_SHA256', 'historical_protection_refs',
                    'visual_review_SHA256', 'source_base', 'runtime_history'):
            require(contract[key] == original[key], 'immutable evidence/history binding: ' + key)
    controller.validate_contract = validate_bound
    replace = controller.replace_originals
    def virtual_replace(io, *args):
        require(getattr(io, 'inert_only', False) is True, 'only inert model removals permitted')
        return replace(io, *args)
    controller.replace_originals = virtual_replace
    # No real filesystem/authority/codec worker operation is exposed here.
    for name in ('LocalIO', 'freeze', 'execute', 'verify_worker', 'run_verifier',
                 'admission', 'accepted_inputs', 'authority_check', 'record_stop'):
        setattr(controller, name, closed)
    return controller


def metadata_usage():
    paths = [p for root in (VISUAL, PREPARATION, OFFLINE) if root.exists()
             for p in (root, *root.rglob('*'))]
    files = [p for p in paths if not p.is_dir()]
    require(all(not p.is_symlink() for p in paths), 'no metadata symlinks')
    logical = sum(p.stat().st_size for p in files)
    allocated = sum(p.stat().st_blocks*512 for p in paths)
    require(len(files) <= METADATA_FILES and logical <= METADATA_CAP and
            allocated <= METADATA_CAP + METADATA_FILES*BLOCK + 6*BLOCK,
            'aggregate bounded preparation/visual/inert metadata')
    return dict(files=len(files), logical_bytes=logical, allocated_bytes=allocated)
