"""STOP117 offline compile, installed synthetic interpreter and JSON fixtures.

Run inside pinned dcc-party-resource. Never invokes the gameplay host or loads
a ROM/Save. Exact synthetic headers/key values stay in the private fixture dir;
the result/log are safe projections without those bytes or values.
"""
from pathlib import Path
import argparse, hashlib, json, stat, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    subprocess.run([sys.executable, str(ROOT / 'scripts/test-f1-v01-native-runtime.py'),
                    '--output', str(out / 'runtime')], check=True)
    private = out / 'private-fixture-output'
    private.mkdir(mode=0o700)
    compiler = ['cc', '-DUSE_DEBUGGERS', '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                '-I' + str(ROOT / 'scripts/floor1')]
    with (out / 'diagnostic-build.log').open('w') as log:
        subprocess.run(compiler + [str(ROOT / 'scripts/floor1/v01-native-boundary-diagnostic-fixture.c'),
                                   '-lmgba', '-o', str(out / 'diagnostics-fixture')],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    with (out / 'diagnostic-fixture.log').open('w') as log:
        subprocess.run([str(out / 'diagnostics-fixture')], cwd=private,
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    origins = {}
    cases = list(private.glob('case-*-safe.json'))
    assert len(cases) == 193, len(cases)
    private_only = {'actual_typed29_hex', 'expected_typed29_hex', 'unread_header_bytes',
                    'keys_at_frame_start', 'observed_keys', 'observed_keys_available', 'trailing_byte'}
    for safe_path in sorted(cases):
        private_path = safe_path.with_name(safe_path.name.replace('-safe.json', '-private.json'))
        safe_data = json.loads(safe_path.read_text())
        private_data = json.loads(private_path.read_text())
        for path in (safe_path, private_path):
            assert stat.S_IMODE(path.stat().st_mode) == 0o600
        assert not private_only.intersection(safe_data)
        assert {k: v for k, v in private_data.items() if k not in private_only} == {
            k: v for k, v in safe_data.items() if k != 'typed29_headers_keys_trailer'}
        assert safe_data['reason'] == 117 and safe_data['first_failure']
        assert safe_data['CPU_available'] == 1
        actual = bytes.fromhex(private_data['actual_typed29_hex'])
        expected = bytes.fromhex(private_data['expected_typed29_hex'])
        assert len(actual) == len(expected) == 29
        actual_length = safe_data['actual_header']['available_bytes']
        expected_length = safe_data['expected_header']['available_bytes']
        prefix = min(actual_length, expected_length)
        difference = next((i for i in range(prefix) if actual[i] != expected[i]),
                          prefix if actual_length != expected_length else 29)
        assert safe_data['first_differing_header_offset'] == difference
        assert actual[actual_length:] == bytes(29-actual_length)
        assert expected[expected_length:] == bytes(29-expected_length)
        for header, data, length in [('actual_header', actual, actual_length),
                                     ('expected_header', expected, expected_length)]:
            decoded = safe_data[header]
            for key, start, width in [('kind_byte', 0, 1), ('ordinal', 1, 8),
                                      ('video_epoch', 9, 4), ('input_epoch', 13, 4),
                                      ('boundary_count', 17, 4), ('absolute_frame', 21, 4)]:
                if length >= start+width:
                    assert decoded[key] == int.from_bytes(data[start:start+width], 'little')
                else:
                    assert key not in decoded
            assert not {'keys', 'key_values'}.intersection(decoded)
        origins[safe_data['origin']] = origins.get(safe_data['origin'], 0) + 1
    assert len(origins) == 10
    # Production retention entry uses the same schema and file privacy.
    for name in ['visual-stop-native-boundary-private.json', 'visual-stop-native-boundary.json']:
        path = private / name
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        data = json.loads(path.read_text())
        assert data['origin'] == 'metadata_read_short' and data['header_read_length'] == 0
    result = json.loads((out / 'runtime/result.json').read_text())
    result.update({
        'result': 'PASS STOP117 all origins, first-failure retention, JSON redaction/privacy, installed synthetic interpreter regressions and host compile only',
        'diagnostic_cases': len(cases), 'diagnostic_origins': origins,
        'all_typed_B_F_E_header_byte_mutations': 87,
        'actual_installed_hardware_header_mutations': 29,
        'all_short_header_lengths_EOF_and_EIO': 58,
        'JSON_exact_private_and_safe_projection_cases': len(cases),
        'first_failure_immutable_no_stream_CPU_sequence_advancement_cases': len(cases),
        'diagnostics_fixture_binary_SHA256': sha(out / 'diagnostics-fixture'),
        'retention': 'Exact headers/key values in mode0600 files, exclusive create; safe projection decoded non-key fields only; synthetic inputs only; private fixtures excluded from Git',
        'historical_STOP117': 'Actual failed header remains missing; offline implementation cannot retrospectively recover it or prove alignment cause',
        'historical_executions': {'baselines': 5, 'candidates': 2},
    })
    for relative in ['scripts/floor1/v01-native-boundary-diagnostics.h',
                     'scripts/floor1/v01-native-boundary-diagnostic-fixture.c',
                     'scripts/test-f1-v01-native-diagnostics.py']:
        result['source_SHA256'][relative] = sha(ROOT / relative)
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ['result', 'diagnostic_cases', 'diagnostic_origins',
                                           'host_SHA256', 'host_binary_SHA256', 'gameplay_host_invocations',
                                           'ROMs_loaded', 'Saves_loaded', 'new_execution_claims']}))


if __name__ == '__main__':
    main()
