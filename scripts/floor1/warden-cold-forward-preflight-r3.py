"""SOURCE ONLY until separately reviewed. No import-time checks or comparisons.

The compilation filename is an observed code label, never distributor provenance.
Only copy bytecode is freshly compared; RGB success is reused from the sealed r2
control-flow record with exact unchanged source/cache/Git operands.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import io
import json
import marshal
import os
import signal
import stat
import struct
import subprocess
import sys
import sysconfig
import types
import warnings

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path('/workspace/scratch')
BASE = 'c7a30533b26f4ef8955f55d32a3907853ad29da1'
OUT = SCRATCH / 'c01-warden-cold-forward-preflight-r5-20261011'
SUMMARY = SCRATCH / 'c01-warden-cold-forward-summary-r5-20261011'
R2 = SCRATCH / 'c01-warden-cold-forward-preflight-r2-20261011'
R2_STOP = R2 / 'STOP-source-correspondence-private.json'
R2_PINS = {
    R2_STOP: '5a6b160b0021e92516ffd2cdd6723c3e586ddcc9ebf74f642c019b26f37e8aca',
    R2 / 'failed-source-correspondence-preflight.py': '6d1d33885a80c299cc0e2ba9b3edf1f359631602912e6af2690579841f09b885',
    R2 / 'dependency-discovery-diagnosis-preserved-private.json': 'b9cbbeff00d6c3738567be92d1c67e8fa15ff17a67d6ebfaec23fdc4c875d4f8',
}
HISTORICAL_PINS = {
    SCRATCH / 'c01-warden-cold-only-offline-r1-20261011/STOP-offline-private.json': 'e4b12e40182b0c5d3c4465ad009ff60b7905bf737cded6c1816283e0ecf91f36',
    SCRATCH / 'c01-warden-cold-only-offline-r1-20261011/failure-review-handoff-private.json': '430487a80acae3ba7d234f65abe5ae9c1eaca4204fc78037ceffadfc028d091f',
    SCRATCH / 'c01-warden-cold-only-offline-r1-20261011/hosted-source-readback-private.json': 'ddcadca3767be2f9f6b05be95059c1e3ab048ec89177d21b8dbf4bc60d29462b',
    SCRATCH / 'c01-warden-continuation-runtime-r2-20261011/STOP.json': 'ab5a2fe1b10592c83d62f1a725ae729eb0994e769955a84603db4a04944255a5',
}
R4_PINS = {
    SCRATCH / 'c01-warden-cold-forward-outer-r4-20261011/STOP-outer-private.json': '2784a9064583b8a3ecb3c183e0905155a686216bf783d2759ce101ce8b0b9424',
    SCRATCH / 'c01-warden-cold-forward-outer-r4-20261011/failure-review-handoff-private.json': 'fd4534ac949c0636c24407c7bb63383b66415878234566c021a607aa9d9c4be0',
}
PYTHON = Path('/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12')
PYTHON_SHA = 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7'
COPY = PYTHON.parent.parent / 'lib/python3.12/copy.py'
COPY_CACHE = COPY.parent / '__pycache__/copy.cpython-312.pyc'
COPY_LABEL = '/home/runner/work/_temp/codex-primary-runtime-work/linux-x64/build/codex-primary-runtime/dependencies/python/lib/python3.12/copy.py'
RGB = (
    ('scripts/floor1/rgb-preservation.py', 'f943f0c1212014b9743da345c42db74b65256ab29e03851f72245524856b7d71',
     'b5f841632f729c2683f961fe2baaab94223ac0cf',
     '2f674c880340b523f44bfcc73a0b66446a2d8ddad25e26d760d54f8ffd45eebe'),
    ('scripts/floor1/rgb-preservation-expanded.py', '5ef40e5409ccb7cfb51987a57699892f73660515cb9367a636be8d413d98b14b',
     '5425fb1829e677890a440e845a5be2188cf6ab44',
     '2d2d31574fd0ce182e045639ed194a97cfe50c4e324b9e73bfb3eab1660b0e6d'),
)
ADDITIONS = {
    COPY: 'cbd25547933176fcf6bb05c2adc9f4796d15ac20b9b82dcf890daea7203daeab',
    COPY_CACHE: '007041c9cc7c0f48d2a521105789f0317bea94729e8304af6c5be5017b3e429a',
    ROOT / 'scripts/floor1/__pycache__/rgb-preservation.cpython-312.pyc': RGB[0][3],
    ROOT / 'scripts/floor1/__pycache__/rgb-preservation-expanded.cpython-312.pyc': RGB[1][3],
}
CODE_FIELDS = ('co_argcount', 'co_cellvars', 'co_code', 'co_consts', 'co_exceptiontable',
    'co_filename', 'co_firstlineno', 'co_flags', 'co_freevars', 'co_kwonlyargcount',
    'co_linetable', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals', 'co_posonlyargcount',
    'co_qualname', 'co_stacksize', 'co_varnames')
PATH_MAPS = (('before_hashes',), ('after_hashes',), ('forward_provider_additions',),
             ('preserved_files',), ('reviewed_source_files',))
PATH_VALUES = (('interpreter', 'path'), ('copy', 'source_path'), ('copy', 'cache_path'),
               ('reused_RGB', '*', 'source_path'), ('reused_RGB', '*', 'cache_path'))
DIRECT_FILES = ('scripts/floor1/warden-cold-receipt-schema-r3.py',
    'scripts/floor1/warden-cold-forward-preflight-r3.py',
    'scripts/test-warden-cold-forward-source-fixtures-r3.py',
    'docs/floor1/c01-cold-forward-source-r3-review.md')


def require(value, reason):
    if not value:
        raise AssertionError(reason)


ROLE_READ_BOUNDS = dict(source=1024**2, cache=1024**2, reviewed_source=1024**2,
    retained_json=8*1024**2, accepted_helper=1024**2, accepted_config=8*1024**2, inventory=8*1024**2)
BLOCK_BYTES = 65536
_OPERANDS, _AUX_OPERANDS, _HASH_CHECKS = {}, {}, []
_INVENTORY_REFERENCE = None
_REVIEWED_SOURCE = None


def identity(info):
    return {key: getattr(info, 'st_'+key) for key in
        ('dev', 'ino', 'mode', 'uid', 'gid', 'size', 'mtime_ns', 'ctime_ns', 'nlink')}


def validate_operand(spec):
    require(type(spec) is dict and set(spec) == {'path', 'role', 'type', 'bytes', 'SHA256'}, 'complete operand descriptor')
    require(type(spec['path']) is str and Path(spec['path']).is_absolute() and
        type(spec['bytes']) is int and spec['bytes'] >= 0 and spec['type'] == 'regular' and
        spec['role'] in {'interpreter', 'used_provider', 'unused_provider', *ROLE_READ_BOUNDS} and
        type(spec['SHA256']) is str and len(spec['SHA256']) == 64 and
        all(c in '0123456789abcdef' for c in spec['SHA256']), 'typed exact operand path/role/size/hash')
    if spec['role'] in ROLE_READ_BOUNDS:
        require(spec['bytes'] <= ROLE_READ_BOUNDS[spec['role']], 'role-specific bounded source/cache/JSON operand')


def hash_operand(spec, retain=False):
    validate_operand(spec)
    require(not retain or spec['role'] in ROLE_READ_BOUNDS, 'binary operands stream without whole-file retention')
    path = Path(spec['path'])
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size == spec['bytes'], 'exact-size regular operand before open')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    chunks, total, digest = [], 0, hashlib.sha256()
    try:
        require(identity(os.fstat(fd)) == identity(before), 'opened operand identity matches path')
        while total < spec['bytes']:
            chunk = os.read(fd, min(BLOCK_BYTES, spec['bytes']-total))
            require(chunk, 'short operand stream before declared size')
            total += len(chunk)
            digest.update(chunk)
            if retain:
                chunks.append(chunk)
        require(os.read(fd, 1) == b'', 'operand stream exact declared EOF')
        require(identity(os.fstat(fd)) == identity(before), 'operand metadata unchanged through EOF')
    finally:
        os.close(fd)
    require(identity(path.lstat()) == identity(before), 'operand path identity/metadata unchanged after close')
    pin = digest.hexdigest()
    require(total == spec['bytes'] and pin == spec['SHA256'], 'exact operand bytes read and pinned hash')
    record = dict(path=spec['path'], role=spec['role'], bytes_read=total, SHA256=pin,
                  exact_EOF=True, block_bytes=BLOCK_BYTES, identity=identity(before))
    _HASH_CHECKS.append(record)
    return (record, b''.join(chunks)) if retain else record


def operand(path):
    key = str(path)
    require(key in _OPERANDS or key in _AUX_OPERANDS, 'operand must be independently declared before use')
    return _OPERANDS[key] if key in _OPERANDS else _AUX_OPERANDS[key]


def sha(path):
    return hash_operand(operand(path))['SHA256']


def read_operand(path):
    return hash_operand(operand(path), retain=True)[1]


def operand_snapshot(manifest):
    records = {path: hash_operand(spec) for path, spec in manifest.items()}
    return ({path: row['SHA256'] for path, row in records.items()},
            {path: row['identity'] for path, row in records.items()})


def load_inventory(path, size, pin, reviewed_source):
    global _OPERANDS, _AUX_OPERANDS, _INVENTORY_REFERENCE, _REVIEWED_SOURCE
    reference = dict(path=str(path), role='inventory', type='regular', bytes=size, SHA256=pin)
    _, raw = hash_operand(reference, retain=True)
    value = json.loads(raw)
    require(type(value) is dict and set(value) == {'schema', 'source_commit', 'direct_operands', 'auxiliary_operands'} and
        value['schema'] == 'c01-cold-forward-exact-operand-manifest/r5' and
        value['source_commit'] == reviewed_source and type(reviewed_source) is str and len(reviewed_source) == 40 and
        all(c in '0123456789abcdef' for c in reviewed_source), 'complete independently reviewed inventory/source schema')
    def manifest(rows):
        require(type(rows) is list, 'operand inventory list')
        result = {}
        for row in rows:
            validate_operand(row)
            require(row['path'] not in result, 'duplicate inventory operand')
            result[row['path']] = row
        return result
    direct, auxiliary = manifest(value['direct_operands']), manifest(value['auxiliary_operands'])
    expected_paths = set(FIXED_OPERANDS) | {str(ROOT/rel) for rel in DIRECT_FILES}
    require(set(direct) == expected_paths and len(direct) == 20, 'all original18 plus two retained r4 failure operands')
    require(all(direct[path] == spec for path, spec in FIXED_OPERANDS.items()), 'exact immutable operands; no discovery admission')
    require(all(direct[str(ROOT/rel)]['role'] == 'reviewed_source' for rel in DIRECT_FILES), 'separate reviewed source operand partition')
    require(auxiliary == AUXILIARY_OPERANDS and not set(direct) & set(auxiliary), 'separate exact accepted helper/config/provider operands')
    _OPERANDS, _AUX_OPERANDS, _INVENTORY_REFERENCE = direct, auxiliary, reference
    _REVIEWED_SOURCE = reviewed_source
    return value


def validate_sealed_r2(prior):
    require(set(prior['interpreter']) == {'path', 'SHA256', 'version', 'cache_tag', 'magic', 'optimization', 'build'}, 'complete actual sealed interpreter schema')
    require(prior['interpreter']['path'] == str(PYTHON) and prior['interpreter']['SHA256'] == PYTHON_SHA and
        prior['interpreter']['magic'] == 'cb0d0d0a' and type(prior['interpreter']['optimization']) is int and
        prior['interpreter']['optimization'] == 0, 'sealed interpreter fields preserved without replacement')
    require(json.dumps(prior['actual_metadata'], sort_keys=True) == json.dumps(SEALED_R2_METADATA, sort_keys=True),
            'complete typed actual sealed bytecode diagnostic schema')


def validate_identity(value, size):
    require(type(value) is dict and set(value) == {'dev','ino','mode','uid','gid','size','mtime_ns','ctime_ns','nlink'} and
        all(type(number) is int for number in value.values()) and value['size'] == size and
        stat.S_ISREG(value['mode']) and value['nlink'] > 0, 'complete typed regular operand identity')


def validate_interpreter_record(value, sealed):
    require(json.dumps(value, sort_keys=True) == json.dumps(sealed, sort_keys=True),
            'complete typed interpreter object without field replacement')


FIXED_OPERANDS = {'/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12': {'SHA256': 'fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7',
                                                                                  'bytes': 30894944,
                                                                                  'path': '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12',
                                                                                  'role': 'interpreter',
                                                                                  'type': 'regular'},
 '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/__pycache__/copy.cpython-312.pyc': {'SHA256': '007041c9cc7c0f48d2a521105789f0317bea94729e8304af6c5be5017b3e429a',
                                                                                                                   'bytes': 9861,
                                                                                                                   'path': '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/__pycache__/copy.cpython-312.pyc',
                                                                                                                   'role': 'cache',
                                                                                                                   'type': 'regular'},
 '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/copy.py': {'SHA256': 'cbd25547933176fcf6bb05c2adc9f4796d15ac20b9b82dcf890daea7203daeab',
                                                                                          'bytes': 8412,
                                                                                          'path': '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/copy.py',
                                                                                          'role': 'source',
                                                                                          'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/__pycache__/rgb-preservation-expanded.cpython-312.pyc': {'SHA256': '2d2d31574fd0ce182e045639ed194a97cfe50c4e324b9e73bfb3eab1660b0e6d',
                                                                                                            'bytes': 18938,
                                                                                                            'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/__pycache__/rgb-preservation-expanded.cpython-312.pyc',
                                                                                                            'role': 'cache',
                                                                                                            'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/__pycache__/rgb-preservation.cpython-312.pyc': {'SHA256': '2f674c880340b523f44bfcc73a0b66446a2d8ddad25e26d760d54f8ffd45eebe',
                                                                                                   'bytes': 23535,
                                                                                                   'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/__pycache__/rgb-preservation.cpython-312.pyc',
                                                                                                   'role': 'cache',
                                                                                                   'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/rgb-preservation-expanded.py': {'SHA256': '5ef40e5409ccb7cfb51987a57699892f73660515cb9367a636be8d413d98b14b',
                                                                                   'bytes': 9890,
                                                                                   'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/rgb-preservation-expanded.py',
                                                                                   'role': 'source',
                                                                                   'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/rgb-preservation.py': {'SHA256': 'f943f0c1212014b9743da345c42db74b65256ab29e03851f72245524856b7d71',
                                                                          'bytes': 10468,
                                                                          'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/rgb-preservation.py',
                                                                          'role': 'source',
                                                                          'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-forward-outer-r4-20261011/STOP-outer-private.json': {'SHA256': '2784a9064583b8a3ecb3c183e0905155a686216bf783d2759ce101ce8b0b9424',
                                                                                          'bytes': 1611,
                                                                                          'path': '/workspace/scratch/c01-warden-cold-forward-outer-r4-20261011/STOP-outer-private.json',
                                                                                          'role': 'retained_json',
                                                                                          'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-forward-outer-r4-20261011/failure-review-handoff-private.json': {'SHA256': 'fd4534ac949c0636c24407c7bb63383b66415878234566c021a607aa9d9c4be0',
                                                                                                      'bytes': 44100,
                                                                                                      'path': '/workspace/scratch/c01-warden-cold-forward-outer-r4-20261011/failure-review-handoff-private.json',
                                                                                                      'role': 'retained_json',
                                                                                                      'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/STOP-source-correspondence-private.json': {'SHA256': '5a6b160b0021e92516ffd2cdd6723c3e586ddcc9ebf74f642c019b26f37e8aca',
                                                                                                              'bytes': 5276,
                                                                                                              'path': '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/STOP-source-correspondence-private.json',
                                                                                                              'role': 'retained_json',
                                                                                                              'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/dependency-discovery-diagnosis-preserved-private.json': {'SHA256': 'b9cbbeff00d6c3738567be92d1c67e8fa15ff17a67d6ebfaec23fdc4c875d4f8',
                                                                                                                            'bytes': 722332,
                                                                                                                            'path': '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/dependency-discovery-diagnosis-preserved-private.json',
                                                                                                                            'role': 'retained_json',
                                                                                                                            'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/failed-source-correspondence-preflight.py': {'SHA256': '6d1d33885a80c299cc0e2ba9b3edf1f359631602912e6af2690579841f09b885',
                                                                                                                'bytes': 4715,
                                                                                                                'path': '/workspace/scratch/c01-warden-cold-forward-preflight-r2-20261011/failed-source-correspondence-preflight.py',
                                                                                                                'role': 'source',
                                                                                                                'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/STOP-offline-private.json': {'SHA256': 'e4b12e40182b0c5d3c4465ad009ff60b7905bf737cded6c1816283e0ecf91f36',
                                                                                           'bytes': 272,
                                                                                           'path': '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/STOP-offline-private.json',
                                                                                           'role': 'retained_json',
                                                                                           'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/failure-review-handoff-private.json': {'SHA256': '430487a80acae3ba7d234f65abe5ae9c1eaca4204fc78037ceffadfc028d091f',
                                                                                                     'bytes': 16465,
                                                                                                     'path': '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/failure-review-handoff-private.json',
                                                                                                     'role': 'retained_json',
                                                                                                     'type': 'regular'},
 '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/hosted-source-readback-private.json': {'SHA256': 'ddcadca3767be2f9f6b05be95059c1e3ab048ec89177d21b8dbf4bc60d29462b',
                                                                                                     'bytes': 525,
                                                                                                     'path': '/workspace/scratch/c01-warden-cold-only-offline-r1-20261011/hosted-source-readback-private.json',
                                                                                                     'role': 'retained_json',
                                                                                                     'type': 'regular'},
 '/workspace/scratch/c01-warden-continuation-runtime-r2-20261011/STOP.json': {'SHA256': 'ab5a2fe1b10592c83d62f1a725ae729eb0994e769955a84603db4a04944255a5',
                                                                              'bytes': 268,
                                                                              'path': '/workspace/scratch/c01-warden-continuation-runtime-r2-20261011/STOP.json',
                                                                              'role': 'retained_json',
                                                                              'type': 'regular'}}
AUXILIARY_OPERANDS = {'/usr/bin/git': {'SHA256': '356db14e102d68a1a37d8a1ac577dfd678d45d46e92f468bef8b7154e7bfdc60',
                  'bytes': 4082768,
                  'path': '/usr/bin/git',
                  'role': 'used_provider',
                  'type': 'regular'},
 '/usr/bin/ldd': {'SHA256': '000d7da9106552c273ce983e21c6b0a742037d0b2a7e3aad264881de746862bf',
                  'bytes': 5356,
                  'path': '/usr/bin/ldd',
                  'role': 'unused_provider',
                  'type': 'regular'},
 '/usr/bin/x86_64-linux-gnu-gcc-14': {'SHA256': 'a23ecab8ff08f09ad8c80602c2c5df7f49e09c25905cb8975902e101bf72635f',
                                      'bytes': 1162264,
                                      'path': '/usr/bin/x86_64-linux-gnu-gcc-14',
                                      'role': 'unused_provider',
                                      'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/warden-runtime-bindings.py': {'SHA256': 'ac77966b8c5bd7c979a2027e9988f51ab137f46fa6fe7f1669a7368eb273dffe',
                                                                                 'bytes': 11768,
                                                                                 'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/warden-runtime-bindings.py',
                                                                                 'role': 'accepted_helper',
                                                                                 'type': 'regular'},
 '/workspace/DungeonCrawlerCarlemon/scripts/floor1/warden-runtime-retention.py': {'SHA256': '9f12b6bbe855356d11a8347875ffb7127e9bc5ca7621571055918703a7ae7843',
                                                                                  'bytes': 5396,
                                                                                  'path': '/workspace/DungeonCrawlerCarlemon/scripts/floor1/warden-runtime-retention.py',
                                                                                  'role': 'accepted_helper',
                                                                                  'type': 'regular'},
 '/workspace/scratch/c01-warden-finalization-offline-inputs-r6-20261011.json': {'SHA256': '852d58aac1e3f013f2f4f54fd09192be1344826c2bf256c6de000569409a05f8',
                                                                                'bytes': 151036,
                                                                                'path': '/workspace/scratch/c01-warden-finalization-offline-inputs-r6-20261011.json',
                                                                                'role': 'accepted_config',
                                                                                'type': 'regular'}}
SEALED_R2_METADATA = {'SHA256': '007041c9cc7c0f48d2a521105789f0317bea94729e8304af6c5be5017b3e429a',
 'compiled': False,
 'decoded_filename': '/home/runner/work/_temp/codex-primary-runtime-work/linux-x64/build/codex-primary-runtime/dependencies/python/lib/python3.12/copy.py',
 'decoded_type': 'code',
 'diagnosis_only': True,
 'executed': False,
 'flags_timestamp_size': [0, 1788486253, 8412],
 'path': '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/__pycache__/copy.cpython-312.pyc',
 'preflight_asserted_filename': '/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/copy.py',
 'trailing_marshal_bytes': 0}


def module(name, relative):
    sha(ROOT / relative)  # Exact declared helper source before the accepted loader.
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def normalize(value):
    if type(value) is types.CodeType:
        # Include co_lnotab while suppressing only its expected deprecation notice.
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            fields = tuple(sorted(k for k in dir(value) if k.startswith('co_') and not callable(getattr(value, k))))
            require(fields == tuple(sorted(CODE_FIELDS)), 'complete pinned interpreter code-field schema')
            result = {key: normalize(getattr(value, key)) for key in CODE_FIELDS}
        result['decoded_co_lines'] = normalize(tuple(value.co_lines()))
        result['decoded_co_positions'] = normalize(tuple(value.co_positions()))
        return ['code', result]
    if type(value) in (tuple, list):
        return [type(value).__name__, [normalize(item) for item in value]]
    if type(value) is frozenset:
        return ['frozenset', sorted([normalize(item) for item in value], key=lambda item: json.dumps(item, sort_keys=True))]
    if type(value) is bytes:
        return ['bytes', value.hex()]
    if type(value) is float:
        return ['float', value.hex()]
    if type(value) is complex:
        return ['complex', value.real.hex(), value.imag.hex()]
    if value is Ellipsis:
        return ['ellipsis']
    require(value is None or type(value) in (str, int, bool), 'unsupported decoded code constant')
    return [type(value).__name__, value]


def copy_correspondence():
    require(sha(COPY) == ADDITIONS[COPY] and sha(COPY_CACHE) == ADDITIONS[COPY_CACHE], 'exact independently reviewed copy operands')
    raw = read_operand(COPY_CACHE)
    require(raw[:4] == importlib.util.MAGIC_NUMBER == bytes.fromhex('cb0d0d0a'), 'pinned bytecode magic')
    flags, timestamp, size = struct.unpack('<III', raw[4:16])
    require(flags == 0 and timestamp == (int(COPY.stat().st_mtime) & 0xffffffff) and
            size == (COPY.stat().st_size & 0xffffffff), 'exact existing timestamp-header metadata')
    stream = io.BytesIO(raw[16:])
    decoded = marshal.load(stream)
    require(type(decoded) is types.CodeType and stream.read() == b'', 'complete code payload and marshal EOF')
    require(decoded.co_filename == COPY_LABEL, 'exact observed compilation label; never normalize filenames')
    fresh = compile(read_operand(COPY), COPY_LABEL, 'exec', flags=0, dont_inherit=True, optimize=0)
    actual, expected = normalize(decoded), normalize(fresh)
    require(actual == expected, 'complete recursive decoded/fresh copy code structure')
    require(sha(COPY) == ADDITIONS[COPY] and sha(COPY_CACHE) == ADDITIONS[COPY_CACHE], 'unchanged copy operands after comparison')
    return dict(source_path=COPY, cache_path=COPY_CACHE, source_SHA256=ADDITIONS[COPY],
        cache_SHA256=ADDITIONS[COPY_CACHE], exact_compilation_filename=COPY_LABEL,
        label_is_authenticated_distribution_provenance=False, header=dict(magic=raw[:4].hex(),
        flags=flags, timestamp=timestamp, source_size=size), marshal_EOF=True,
        optimization=0, dont_inherit=True, compiler_flags=0, code_fields=list(CODE_FIELDS),
        complete_recursive_structure_equal=True, lines_positions_compared=True,
        structure_SHA256=hashlib.sha256(json.dumps(actual, sort_keys=True, separators=(',', ':')).encode()).hexdigest())


def source_inputs(reviewed_source):
    require(__debug__ and sys.flags.optimize == 0 and sys.dont_write_bytecode, 'enabled checks, optimize0 and -B required')
    require(Path(sys.executable) == PYTHON and sha(PYTHON) == PYTHON_SHA, 'exact pinned interpreter bytes')
    for path, pin in {**R2_PINS, **HISTORICAL_PINS, **R4_PINS}.items():
        require(sha(path) == pin, 'unchanged r2 failure/discovery evidence')
    prior = json.loads(read_operand(R2_STOP))
    validate_sealed_r2(prior)
    require(prior['PASS'] is False and prior['source_correspondence_preflight_attempts'] == 1 and
            prior['source_results_supported_by_control_flow'] == dict(
                rgb_sources_exact_pinned_Git_blobs=True, copy_source_exact_official_CPython_v3_12_14=True,
                rgb_bytecodes_complete_structure_checks_reached_and_passed=True,
                copy_bytecode_complete_structure_check_reached=False), 'exact prior partial success and terminal failure')
    require(not os.path.lexists(R2 / 'checkpoint-private.json'), 'missing fourth summary remains absent')
    require(sys.version == prior['interpreter']['version'] and sys.implementation.cache_tag == prior['interpreter']['cache_tag'] and
            {key: sysconfig.get_config_var(key) for key in prior['interpreter']['build']} == prior['interpreter']['build'], 'exact pinned interpreter version/build')
    require(importlib.util.find_spec('copy').origin == str(COPY) and sysconfig.get_path('stdlib') == str(COPY.parent), 'exact installed official-source module origin')
    require(prior['official_source_url'] == 'https://raw.githubusercontent.com/python/cpython/v3.12.14/Lib/copy.py' and
            prior['actual_metadata']['decoded_filename'] == COPY_LABEL and
            prior['actual_metadata']['SHA256'] == ADDITIONS[COPY_CACHE], 'sealed official comparison and observed label binding')
    b = module('preflight_r3_bindings', 'scripts/floor1/warden-runtime-bindings.py')
    env = dict(b.git_environment(), GIT_OPTIONAL_LOCKS='0')
    git = lambda *args: subprocess.check_output([b.provider('git'), *args], cwd=ROOT, env=env, timeout=10)
    def blob_bytes(reference, path):
        size = int(git('cat-file', '-s', reference))
        require(size == operand(path)['bytes'] and size <= ROLE_READ_BOUNDS['source'], 'declared exact bounded Git source blob')
        data = git('cat-file', 'blob', reference)
        require(len(data) == size, 'complete bounded Git blob output')
        return data
    require(not git('status', '--porcelain'), 'clean committed source-only preflight')
    require(git('rev-parse', 'HEAD').decode().strip() == reviewed_source, 'explicit independently reviewed source commit')
    require(git('merge-base', BASE, 'HEAD').decode().strip() == BASE, 'published review-base ancestry')
    require(set(git('diff', '--name-only', BASE, 'HEAD').decode().splitlines()) == set(DIRECT_FILES), 'exact four-file source-only preparation')
    reviewed_files = {}
    for rel in DIRECT_FILES:
        data = read_operand(ROOT / rel)
        require(blob_bytes(reviewed_source + ':' + rel, ROOT/rel) == data, 'exact reviewed helper/documentation Git bytes')
        reviewed_files[ROOT / rel] = hashlib.sha256(data).hexdigest()
    reused = []
    for rel, pin, blob, cache_pin in RGB:
        source = ROOT / rel
        cache = Path(importlib.util.cache_from_source(str(source)))
        data = read_operand(source)
        require(sha(source) == pin and sha(cache) == cache_pin and
                git('rev-parse', BASE + ':' + rel).decode().strip() == blob and
                blob_bytes(blob, source) == data, 'unchanged exact Git/source/cache operands for reused RGB evidence')
        reused.append(dict(source_path=source, source_SHA256=pin, Git_blob_SHA1=blob, source_commit=BASE,
                           cache_path=cache, cache_SHA256=cache_pin, success_reference_SHA256=R2_PINS[R2_STOP],
                           evidence_kind='prior sealed partial-preflight control flow; no new RGB comparison'))
    return prior, reused, reviewed_files


def validate_receipt(value):
    require(type(value) is dict and set(value) == {'schema', 'record_kind', 'PASS', 'source_commit', 'before_hashes',
        'after_hashes', 'forward_provider_additions', 'preserved_files', 'interpreter', 'copy',
        'reviewed_source_files', 'reused_RGB', 'failure_history', 'execution', 'provenance',
        'operand_manifest', 'auxiliary_operand_manifest', 'inventory_reference', 'actual_r2_metadata',
        'before_operand_metadata', 'after_operand_metadata', 'auxiliary_before_hashes', 'auxiliary_after_hashes',
        'auxiliary_before_metadata', 'auxiliary_after_metadata', 'operand_hash_checks',
        'inventory_before_check', 'inventory_after_check'}, 'complete forward-correspondence receipt schema')
    require(value['schema'] == 'c01-cold-forward-source-correspondence/r5' and value['PASS'] is True, 'successful explicit forward correspondence only')
    require(value['record_kind'] in ('source-consistency', 'new-summary') and
            value['source_commit'] == _REVIEWED_SOURCE and type(value['source_commit']) is str and len(value['source_commit']) == 40 and
            all(c in '0123456789abcdef' for c in value['source_commit']), 'new record kind and full reviewed source identity')
    require(value['operand_manifest'] == _OPERANDS and value['auxiliary_operand_manifest'] == _AUX_OPERANDS and
        value['inventory_reference'] == _INVENTORY_REFERENCE, 'complete exact independent operand declarations')
    preserved = {**R2_PINS, **HISTORICAL_PINS, **R4_PINS}
    require(value['preserved_files'] == {str(path): pin for path, pin in preserved.items()}, 'complete exact earlier evidence references')
    sources = value['reviewed_source_files']
    require(type(sources) is dict and set(sources) == {str(ROOT / rel) for rel in DIRECT_FILES} and
            sources == {str(ROOT/rel): _OPERANDS[str(ROOT/rel)]['SHA256'] for rel in DIRECT_FILES},
            'complete independently declared reviewed source hash map')
    require(value['forward_provider_additions'] == {str(path): pin for path, pin in ADDITIONS.items()}, 'exact four reviewed additions; discovery cannot admit itself')
    operands = {str(path): pin for path, pin in {**ADDITIONS, **preserved, PYTHON: PYTHON_SHA}.items()}
    operands.update({str(ROOT / rel): pin for rel, pin, _, _ in RGB})
    operands.update(sources)
    require(value['before_hashes'] == value['after_hashes'] == operands, 'complete before/after exact operand preservation')
    require(value['before_operand_metadata'] == value['after_operand_metadata'] and
        set(value['before_operand_metadata']) == set(_OPERANDS), 'direct operand identity preserved across comparison')
    require(value['auxiliary_before_hashes'] == value['auxiliary_after_hashes'] ==
        {path: row['SHA256'] for path, row in _AUX_OPERANDS.items()} and
        value['auxiliary_before_metadata'] == value['auxiliary_after_metadata'] and
        set(value['auxiliary_before_metadata']) == set(_AUX_OPERANDS), 'separate accepted helper/config/provider preservation')
    for path, metadata in {**value['before_operand_metadata'], **value['auxiliary_before_metadata']}.items():
        validate_identity(metadata, operand(path)['bytes'])
    require(value['inventory_before_check'] == value['inventory_after_check'], 'reviewed inventory bytes and identity preserved')
    require(type(value['operand_hash_checks']) is list and 0 < len(value['operand_hash_checks']) <= 256, 'complete bounded hash-check records')
    declared = {**_OPERANDS, **_AUX_OPERANDS, _INVENTORY_REFERENCE['path']: _INVENTORY_REFERENCE}
    require({check['path'] for check in value['operand_hash_checks']} == set(declared), 'all direct/auxiliary/inventory operands represented in hash checks')
    require(value['inventory_before_check']['path'] == value['inventory_after_check']['path'] == _INVENTORY_REFERENCE['path'], 'inventory checks bind the independently reviewed manifest')
    for check in value['operand_hash_checks'] + [value['inventory_before_check'],value['inventory_after_check']]:
        require(set(check) == {'path','role','bytes_read','SHA256','exact_EOF','block_bytes','identity'} and
            check['path'] in declared and check['role'] == declared[check['path']]['role'] and
            type(check['bytes_read']) is int and check['bytes_read'] == declared[check['path']]['bytes'] and
            check['SHA256'] == declared[check['path']]['SHA256'] and check['exact_EOF'] is True and
            check['block_bytes'] == BLOCK_BYTES, 'declared role/size/hash and complete exact stream EOF record')
        validate_identity(check['identity'], declared[check['path']]['bytes'])
    prior = json.loads(read_operand(R2_STOP))
    validate_sealed_r2(prior)
    require(json.dumps(value['actual_r2_metadata'], sort_keys=True) == json.dumps(prior['actual_metadata'], sort_keys=True),
            'exact complete typed sealed diagnostic object retained')
    validate_interpreter_record(value['interpreter'], prior['interpreter'])
    expected_RGB = [dict(source_path=str(ROOT / rel), source_SHA256=pin, Git_blob_SHA1=blob, source_commit=BASE,
        cache_path=str(Path(importlib.util.cache_from_source(str(ROOT / rel)))), cache_SHA256=cache_pin,
        success_reference_SHA256=R2_PINS[R2_STOP], evidence_kind='prior sealed partial-preflight control flow; no new RGB comparison')
        for rel, pin, blob, cache_pin in RGB]
    require(value['reused_RGB'] == expected_RGB, 'complete unchanged RGB references; no repeated comparison')
    copied = value['copy']
    require(type(copied) is dict and set(copied) == {'source_path', 'cache_path', 'source_SHA256',
        'cache_SHA256', 'exact_compilation_filename', 'label_is_authenticated_distribution_provenance',
        'header', 'marshal_EOF', 'optimization', 'dont_inherit', 'compiler_flags', 'code_fields',
        'complete_recursive_structure_equal', 'lines_positions_compared', 'structure_SHA256'}, 'complete copy structure receipt schema')
    require(copied['source_path'] == str(COPY) and copied['cache_path'] == str(COPY_CACHE) and
        copied['source_SHA256'] == ADDITIONS[COPY] and copied['cache_SHA256'] == ADDITIONS[COPY_CACHE] and
        copied['exact_compilation_filename'] == COPY_LABEL and copied['complete_recursive_structure_equal'] is True and
        copied['label_is_authenticated_distribution_provenance'] is False and
        copied['header'] == dict(magic='cb0d0d0a', flags=0, timestamp=1788486253, source_size=8412) and
        all(type(copied['header'][key]) is int for key in ('flags', 'timestamp', 'source_size')) and
        copied['marshal_EOF'] is True and copied['dont_inherit'] is True and
        type(copied['optimization']) is int and copied['optimization'] == 0 and
        type(copied['compiler_flags']) is int and copied['compiler_flags'] == 0 and
        copied['code_fields'] == list(CODE_FIELDS) and copied['lines_positions_compared'] is True and
        type(copied['structure_SHA256']) is str and len(copied['structure_SHA256']) == 64 and
        all(c in '0123456789abcdef' for c in copied['structure_SHA256']), 'exact observed label/header and complete recursive comparison')
    expected_execution = dict(copy_in_memory_compilations=1, RGB_comparisons=0,
        compiled_code_executed=0, caches_changed=0, emulators=0, Save_actions=0, cold_processes=0,
        runtime_authorities=0, provider_admission_into_cold_proposal=False)
    require(json.dumps(value['execution'], sort_keys=True) == json.dumps(expected_execution, sort_keys=True), 'typed no-runtime/no-admission counters')
    expected_failures = failure_history()
    require(json.dumps(value['failure_history'], sort_keys=True) == json.dumps(expected_failures, sort_keys=True), 'typed earlier failures retained')
    require(value['provenance'] == 'forward correspondence only; no historical provider continuity or authenticated distributor build claim', 'exact forward-only provenance')


def failure_history():
    return dict(preflight_failures=2,
        filename_assumption_failure=dict(count=1, STOP_SHA256=R2_PINS[R2_STOP]),
        operand_size_failure=dict(count=1, STOP_SHA256=R4_PINS[SCRATCH/'c01-warden-cold-forward-outer-r4-20261011/STOP-outer-private.json'],
            handoff_SHA256=R4_PINS[SCRATCH/'c01-warden-cold-forward-outer-r4-20261011/failure-review-handoff-private.json']),
        closure_suite_failure=dict(count=1, STOP_SHA256=HISTORICAL_PINS[SCRATCH/'c01-warden-cold-only-offline-r1-20261011/STOP-offline-private.json']),
        missing_summary_serialization_failure=dict(count=1, missing_path=str(R2/'checkpoint-private.json'),
            error='TypeError: keys must be str, int, float, bool or None, not PosixPath'),
        prior_auxiliary_metadata_query_failures=1, missing_prior_summary=True, failures_reset=False)


def main(reviewed_source, inventory_path, inventory_size, inventory_sha):
    # Future separately authorized invocation only. No discovery or suite is called.
    load_inventory(inventory_path, inventory_size, inventory_sha, reviewed_source)
    for spec in _AUX_OPERANDS.values():
        hash_operand(spec)
    schema = module('preflight_r5_receipt_schema', 'scripts/floor1/warden-cold-receipt-schema-r3.py')
    require(not os.path.lexists(OUT) and not os.path.lexists(SUMMARY), 'fresh r5 preflight and distinctly named new summary')
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('bounded60-second source preflight')))
    signal.alarm(60)
    prior, reused, reviewed_files = source_inputs(reviewed_source)
    inventory_before = hash_operand(_INVENTORY_REFERENCE)
    before, before_meta = operand_snapshot(_OPERANDS)
    aux_before, aux_before_meta = operand_snapshot(_AUX_OPERANDS)
    result = copy_correspondence()
    after, after_meta = operand_snapshot(_OPERANDS)
    aux_after, aux_after_meta = operand_snapshot(_AUX_OPERANDS)
    inventory_after = hash_operand(_INVENTORY_REFERENCE)
    require(after == before and after_meta == before_meta and aux_after == aux_before and
        aux_after_meta == aux_before_meta and inventory_after == inventory_before, 'all exact bytes and file identities preserved')
    receipt = dict(schema='c01-cold-forward-source-correspondence/r5', record_kind='source-consistency',
        PASS=True, source_commit=reviewed_source, reviewed_source_files=reviewed_files,
        operand_manifest=_OPERANDS, auxiliary_operand_manifest=_AUX_OPERANDS, inventory_reference=_INVENTORY_REFERENCE,
        actual_r2_metadata=prior['actual_metadata'], before_operand_metadata=before_meta, after_operand_metadata=after_meta,
        auxiliary_before_hashes=aux_before, auxiliary_after_hashes=aux_after,
        auxiliary_before_metadata=aux_before_meta, auxiliary_after_metadata=aux_after_meta,
        operand_hash_checks=list(_HASH_CHECKS),
        inventory_before_check=inventory_before, inventory_after_check=inventory_after,
        before_hashes=before, after_hashes=after, forward_provider_additions=ADDITIONS,
        preserved_files={**R2_PINS, **HISTORICAL_PINS, **R4_PINS}, interpreter=dict(prior['interpreter']), copy=result,
        reused_RGB=reused, failure_history=failure_history(),
        execution=dict(copy_in_memory_compilations=1, RGB_comparisons=0, compiled_code_executed=0,
        caches_changed=0, emulators=0, Save_actions=0, cold_processes=0, runtime_authorities=0,
        provider_admission_into_cold_proposal=False), provenance='forward correspondence only; no historical provider continuity or authenticated distributor build claim')
    # Serialize both complete payloads before either destination is created.
    summary = dict(receipt)
    summary['record_kind'] = 'new-summary'
    encoded = schema.prepare_bundle({'source-consistency-private.json': receipt,
        'new-summary-private.json': summary}, path_key_maps=PATH_MAPS,
        path_value_fields=PATH_VALUES, validate=validate_receipt)
    schema.write_prepared_bundle(OUT, {'source-consistency-private.json': encoded['source-consistency-private.json']}, validate=validate_receipt)
    schema.write_prepared_bundle(SUMMARY, {'new-summary-private.json': encoded['new-summary-private.json']}, validate=validate_receipt)
    first_readback = schema.readback_prepared(OUT, {'source-consistency-private.json': encoded['source-consistency-private.json']}, validate=validate_receipt)
    second_readback = schema.readback_prepared(SUMMARY, {'new-summary-private.json': encoded['new-summary-private.json']}, validate=validate_receipt)
    require(first_readback['source-consistency-private.json']['SHA256'] == hashlib.sha256(encoded['source-consistency-private.json']).hexdigest() and
        second_readback['new-summary-private.json']['SHA256'] == hashlib.sha256(encoded['new-summary-private.json']).hexdigest(),
        'both fsynced persisted payloads fully read/schema/byte/hash verified before success')
    signal.alarm(0)
    print('PASS forward correspondence only; cold admission/runtime CLOSED', reviewed_source,
          hashlib.sha256(encoded['source-consistency-private.json']).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewed-source', required=True)
    parser.add_argument('--inventory', required=True)
    parser.add_argument('--inventory-bytes', required=True, type=int)
    parser.add_argument('--inventory-sha256', required=True)
    args = parser.parse_args()
    main(args.reviewed_source, args.inventory, args.inventory_bytes, args.inventory_sha256)
