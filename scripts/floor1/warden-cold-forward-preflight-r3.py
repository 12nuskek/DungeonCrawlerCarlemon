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
OUT = SCRATCH / 'c01-warden-cold-forward-preflight-r3-20261011'
SUMMARY = SCRATCH / 'c01-warden-cold-forward-summary-r3-20261011'
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


def sha(path):
    path = Path(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_size <= 8*1024**2, 'bounded regular preflight operand')
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    after = path.lstat()
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_size, s.st_mtime_ns)
    require(identity(before) == identity(after), 'operand changed during hash')
    return digest


def module(name, relative):
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
    raw = COPY_CACHE.read_bytes()
    require(raw[:4] == importlib.util.MAGIC_NUMBER == bytes.fromhex('cb0d0d0a'), 'pinned bytecode magic')
    flags, timestamp, size = struct.unpack('<III', raw[4:16])
    require(flags == 0 and timestamp == (int(COPY.stat().st_mtime) & 0xffffffff) and
            size == (COPY.stat().st_size & 0xffffffff), 'exact existing timestamp-header metadata')
    stream = io.BytesIO(raw[16:])
    decoded = marshal.load(stream)
    require(type(decoded) is types.CodeType and stream.read() == b'', 'complete code payload and marshal EOF')
    require(decoded.co_filename == COPY_LABEL, 'exact observed compilation label; never normalize filenames')
    fresh = compile(COPY.read_bytes(), COPY_LABEL, 'exec', flags=0, dont_inherit=True, optimize=0)
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
    for path, pin in {**R2_PINS, **HISTORICAL_PINS}.items():
        require(sha(path) == pin, 'unchanged r2 failure/discovery evidence')
    prior = json.loads(R2_STOP.read_bytes())
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
    require(not git('status', '--porcelain'), 'clean committed source-only preflight')
    require(git('rev-parse', 'HEAD').decode().strip() == reviewed_source, 'explicit independently reviewed source commit')
    require(git('merge-base', BASE, 'HEAD').decode().strip() == BASE, 'published review-base ancestry')
    require(set(git('diff', '--name-only', BASE, 'HEAD').decode().splitlines()) == set(DIRECT_FILES), 'exact four-file source-only preparation')
    reviewed_files = {}
    for rel in DIRECT_FILES:
        data = (ROOT / rel).read_bytes()
        require(git('cat-file', 'blob', reviewed_source + ':' + rel) == data, 'exact reviewed helper/documentation Git bytes')
        reviewed_files[ROOT / rel] = hashlib.sha256(data).hexdigest()
    reused = []
    for rel, pin, blob, cache_pin in RGB:
        source = ROOT / rel
        cache = Path(importlib.util.cache_from_source(str(source)))
        data = source.read_bytes()
        require(sha(source) == pin and sha(cache) == cache_pin and
                git('rev-parse', BASE + ':' + rel).decode().strip() == blob and
                git('cat-file', 'blob', blob) == data, 'unchanged exact Git/source/cache operands for reused RGB evidence')
        reused.append(dict(source_path=source, source_SHA256=pin, Git_blob_SHA1=blob, source_commit=BASE,
                           cache_path=cache, cache_SHA256=cache_pin, success_reference_SHA256=R2_PINS[R2_STOP],
                           evidence_kind='prior sealed partial-preflight control flow; no new RGB comparison'))
    return prior, reused, reviewed_files


def validate_receipt(value):
    require(type(value) is dict and set(value) == {'schema', 'record_kind', 'PASS', 'source_commit', 'before_hashes',
        'after_hashes', 'forward_provider_additions', 'preserved_files', 'interpreter', 'copy',
        'reviewed_source_files', 'reused_RGB', 'failure_history', 'execution', 'provenance'}, 'complete forward-correspondence receipt schema')
    require(value['schema'] == 'c01-cold-forward-source-correspondence/r3' and value['PASS'] is True, 'successful explicit forward correspondence only')
    require(value['record_kind'] in ('source-consistency', 'new-summary') and
            type(value['source_commit']) is str and len(value['source_commit']) == 40 and
            all(c in '0123456789abcdef' for c in value['source_commit']), 'new record kind and full reviewed source identity')
    preserved = {**R2_PINS, **HISTORICAL_PINS}
    require(value['preserved_files'] == {str(path): pin for path, pin in preserved.items()}, 'complete exact earlier evidence references')
    sources = value['reviewed_source_files']
    require(type(sources) is dict and set(sources) == {str(ROOT / rel) for rel in DIRECT_FILES} and
            all(type(pin) is str and len(pin) == 64 and all(c in '0123456789abcdef' for c in pin) for pin in sources.values()), 'complete reviewed source hash map')
    require(value['forward_provider_additions'] == {str(path): pin for path, pin in ADDITIONS.items()}, 'exact four reviewed additions; discovery cannot admit itself')
    operands = {str(path): pin for path, pin in {**ADDITIONS, **preserved, PYTHON: PYTHON_SHA}.items()}
    operands.update({str(ROOT / rel): pin for rel, pin, _, _ in RGB})
    operands.update(sources)
    require(value['before_hashes'] == value['after_hashes'] == operands, 'complete before/after exact operand preservation')
    prior = json.loads(R2_STOP.read_bytes())
    require(json.dumps(value['interpreter'], sort_keys=True) == json.dumps(prior['interpreter'], sort_keys=True), 'complete typed interpreter version/build/origin receipt')
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
    expected_failures = dict(prior_inert_suite_failures=1, prior_correspondence_failures=1,
        prior_summary_serialization_failures=1, missing_prior_summary=True, failures_reset=False)
    require(json.dumps(value['failure_history'], sort_keys=True) == json.dumps(expected_failures, sort_keys=True), 'typed earlier failures retained')
    require(value['provenance'] == 'forward correspondence only; no historical provider continuity or authenticated distributor build claim', 'exact forward-only provenance')


def main(reviewed_source):
    # Future separately authorized invocation only. No discovery or suite is called.
    schema = module('preflight_r3_receipt_schema', 'scripts/floor1/warden-cold-receipt-schema-r3.py')
    require(not os.path.lexists(OUT) and not os.path.lexists(SUMMARY), 'fresh r3 preflight and distinctly named new summary')
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('bounded60-second source preflight')))
    signal.alarm(60)
    prior, reused, reviewed_files = source_inputs(reviewed_source)
    operands = dict(ADDITIONS)
    operands[PYTHON] = PYTHON_SHA
    operands.update(R2_PINS)
    operands.update(HISTORICAL_PINS)
    operands.update(reviewed_files)
    for rel, pin, _, cache_pin in RGB:
        operands[ROOT / rel] = pin
        operands[Path(importlib.util.cache_from_source(str(ROOT / rel)))] = cache_pin
    before = {path: sha(path) for path in operands}
    require(before == operands, 'exact independently pinned preflight input set')
    result = copy_correspondence()
    after = {path: sha(path) for path in operands}
    require(after == before, 'all source/cache/interpreter/evidence bytes unchanged')
    receipt = dict(schema='c01-cold-forward-source-correspondence/r3', record_kind='source-consistency',
        PASS=True, source_commit=reviewed_source, reviewed_source_files=reviewed_files,
        before_hashes=before, after_hashes=after, forward_provider_additions=ADDITIONS,
        preserved_files={**R2_PINS, **HISTORICAL_PINS}, interpreter=dict(prior['interpreter'], path=PYTHON), copy=result,
        reused_RGB=reused, failure_history=dict(prior_inert_suite_failures=1, prior_correspondence_failures=1,
        prior_summary_serialization_failures=1, missing_prior_summary=True, failures_reset=False),
        execution=dict(copy_in_memory_compilations=1, RGB_comparisons=0, compiled_code_executed=0,
        caches_changed=0, emulators=0, Save_actions=0, cold_processes=0, runtime_authorities=0,
        provider_admission_into_cold_proposal=False), provenance='forward correspondence only; no historical provider continuity or authenticated distributor build claim')
    # Serialize both complete payloads before either destination is created.
    summary = dict(receipt)
    summary['record_kind'] = 'new-summary'
    encoded = schema.prepare_bundle({'source-consistency-private.json': receipt,
        'new-summary-private.json': summary}, path_key_maps=PATH_MAPS,
        path_value_fields=PATH_VALUES, validate=validate_receipt)
    schema.write_bundle(OUT, {'source-consistency-private.json': receipt}, path_key_maps=PATH_MAPS,
        path_value_fields=PATH_VALUES, validate=validate_receipt)
    schema.write_bundle(SUMMARY, {'new-summary-private.json': summary}, path_key_maps=PATH_MAPS,
        path_value_fields=PATH_VALUES, validate=validate_receipt)
    signal.alarm(0)
    print('PASS forward correspondence only; cold admission/runtime CLOSED', reviewed_source,
          hashlib.sha256(encoded['source-consistency-private.json']).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewed-source', required=True)
    main(parser.parse_args().reviewed_source)
