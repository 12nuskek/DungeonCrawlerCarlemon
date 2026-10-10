"""Offline route proof, retained-record roundtrip and bounded parser checks.

The separately run C stress fixture executes file/counter operations only. This
runner recompiles it and verifies its identity before reusing that stress log;
it invokes only its record-replay mode, never the compiled gameplay host.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, io, json, re, subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '4c1a28006465be9bdc9a6363a03339dcc8b7a98c'
ROUTE_SHA = 'afbd80b02d9d5acb9f63669f967fac3edc8eb00a2d2352e778f4114acb51bc27'
TRACE_SHA = 'aac0963fde9fbd6237f44dd8082ddca59f6b40627a8b6857a017c82673b8669a'

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk := stream.read(1048576):
            digest.update(chunk)
    return digest.hexdigest()

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise AssertionError('Invalid format must fail closed')

def main():
    parser = argparse.ArgumentParser()
    for name in ('output', 'fixture', 'stress-log', 'trace'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    fmt = module('capacity_format', ROOT/'scripts/floor1/v01-native-timeline-format.py')
    code, _ = module('capacity_host', ROOT/'scripts/floor1/v01-battle-host.py').generate(git)
    # The later explicit storage contract adds reviewed hooks; retain a byte
    # proof against the compiled capacity host for all surrounding policy code.
    module('capacity_storage_binding',ROOT/'scripts/floor1/v01-retained-reference.py').legacy_host(code,git)
    assert code.count('bv_native_frame(&native,') == 1 and 'core->runFrame(core);' not in code
    assert code.count('core->setKeys(') == 13
    assert code.count('if(visual.recording && visual.frames>=36000)') == 1
    ready = code.split('if (!strcmp(line,"ready\\n")) {', 1)[1].split('continue;', 1)[0]
    assert 'WARDEN_FRAME' not in ready
    route = ROOT/'scripts/contracts/f1-v01-battle.route'
    assert sha(route) == ROUTE_SHA
    lines = route.read_text().splitlines()
    assert lines.count('visual start') == lines.count('visual finish') == 1
    assert lines[-2:] == ['visual finish', 'quit']
    boot = [int(line.split()[1]) for line in lines[:lines.index('visual start')] if line.startswith('step ')]
    assert boot == [720, 1, 360, 1, 180, 1, 180, 1, 600]
    before = lines[:lines.index('visual start')]
    assert not any(line.split()[0] in {'engage', 'pilot', 'dialog', 'field-menu', 'choice-ready', 'potion'} for line in before)
    assert sum(boot) == fmt.PREVISUAL_FRAMES == 2044
    assert fmt.VISUAL_FRAMES == 36000 and fmt.FRAME_CALLS == 38044
    assert fmt.LIMIT == 155828295
    bound = dict(boot_steps=boot, previsual_frame_calls=sum(boot), visual_guard=36000,
                 maximum_frame_calls=fmt.FRAME_CALLS, per_frame_buffer_records=fmt.BUFFER_RECORDS,
                 instruction_reservation=fmt.INSTRUCTION_RESERVE, terminal_overhead=fmt.TERMINAL_RECORDS,
                 total_record_ceiling=fmt.LIMIT, record_bytes=fmt.RECORD.size,
                 maximum_file_bytes=16 + fmt.LIMIT * fmt.RECORD.size, allocated_buffer_bytes=4096*184,
                 scope='Pinned route only; per-frame overflow/I/O remain fatal. No observed-density assumption.')
    (out/'route-bound.json').write_text(json.dumps(bound, indent=2)+'\n')
    fixture = out/'capacity-fixture'
    with (out/'build.log').open('w') as log:
        subprocess.run(['cc', '-DUSE_DEBUGGERS', '-std=gnu11', '-O2', '-Wall', '-Wextra', '-Werror',
                        '-I'+str(ROOT/'scripts/floor1'), str(ROOT/'scripts/floor1/v01-native-timeline-capacity-fixture.c'),
                        '-lmgba', '-o', str(fixture)], stdout=log, stderr=subprocess.STDOUT, check=True)
        assert sha(fixture) == sha(args.fixture), 'Reused stress result must belong to identical fixture binary'
        stress = json.loads(args.stress_log.read_text().splitlines()[-1])
        assert stress == dict(cases=352, frame_calls=38044, total_limit=fmt.LIMIT,
                             max_file_bytes=bound['maximum_file_bytes'], buffer_bytes=753664, CPU_instructions=0)
        (out/'host.c').write_text(code)
        subprocess.run(['cc', '-DUSE_DEBUGGERS', '-std=gnu11', '-Wall', '-Wextra', '-Werror',
                        str(out/'host.c'), '-lmgba', '-o', str(out/'host')],
                       stdout=log, stderr=subprocess.STDOUT, check=True)
    assert sha(args.trace) == TRACE_SHA
    replayed = out/'replayed-actual-private.bin'
    replay = subprocess.run([str(fixture), '--replay', str(args.trace.resolve()), str(replayed)],
                            capture_output=True, text=True, check=True)
    replay_result = json.loads(replay.stdout)
    assert replay_result['replayed_records'] == 999932 and replay_result['max_buffer_records'] == 104
    assert replayed.stat().st_mode & 0o777 == 0o600
    count = 0
    with args.trace.open('rb') as original, replayed.open('rb') as corrected:
        old_header, new_header = fmt.read_header(original), fmt.read_header(corrected)
        assert old_header['magic'] == 'BVTIME01' and new_header['magic'] == 'BVTIME02'
        old_rows, new_rows = fmt.records(original, old_header), fmt.records(corrected, new_header)
        for row in old_rows:
            assert row == next(new_rows)
            count += 1
        assert next(new_rows, None) is None and count == 999932
    assert sha(args.trace) == TRACE_SHA
    with args.trace.open('rb') as original, replayed.open('rb') as corrected:
        original.seek(16); corrected.seek(16)
        while chunk := original.read(1048576):
            assert chunk == corrected.read(len(chunk))
        assert not corrected.read(1)
    # Complete-record/parser faults, including crossing the old total cap.
    cases = 0
    header = b'BVTIME02' + __import__('struct').pack('<II', 46, fmt.LIMIT)
    frame = fmt.RECORD.pack(6, 2, *([0]*44))
    observation = fmt.RECORD.pack(1, 1, *([0]*44))
    finish = fmt.RECORD.pack(7, 2, *([0]*44))
    def decode(data):
        stream = io.BytesIO(data); return list(fmt.records(stream, fmt.read_header(stream)))
    for size in range(16):
        rejected(lambda: decode(header[:size])); cases += 1
    for size in range(1, 184):
        rejected(lambda: decode(header + frame[:size])); cases += 1
    for wrong in (b'BVTIME03', b'BVTIME00'):
        rejected(lambda: decode(wrong + header[8:])); cases += 1
    for words, limit in ((45, fmt.LIMIT), (46, fmt.LIMIT-1), (46, fmt.LIMIT+1), (46, 1000000)):
        rejected(lambda: decode(b'BVTIME02'+__import__('struct').pack('<II', words, limit))); cases += 1
    for event, phase in ((0, 2), (10, 2), (1, 2), (3, 2), (6, 1)):
        rejected(lambda: decode(header + fmt.RECORD.pack(event, phase, *([0]*44)))); cases += 1
    assert len(decode(header + observation*4095 + frame + finish)) == 4097; cases += 1
    rejected(lambda: decode(header + observation*4097)); cases += 1
    rejected(lambda: decode(header + finish + frame)); cases += 1
    assert decode(header + observation) and decode(header) == []; cases += 1
    class RepeatedFrames:
        def __init__(self): self.remaining = 1000001; self.max_read = 0
        def read(self, size):
            self.max_read = max(self.max_read, size)
            if not self.remaining: return b''
            self.remaining -= 1; return frame
    historical = {'magic':'BVTIME01', 'words':46, 'limit':1000000}
    repeated = RepeatedFrames()
    rejected(lambda: sum(1 for _ in fmt.records(repeated, historical))); assert repeated.max_read == 184; cases += 1
    repeated = RepeatedFrames()
    assert sum(1 for _ in fmt.records(repeated, new_header)) == 1000001 and repeated.max_read == 184; cases += 1
    result = dict(result='PASS offline derived-capacity/streaming roundtrip/parser/host compilation',
                  frozen_checkpoint=BASE, writer_stress=stress, parser_cases=cases,
                  retained_trace_SHA256=TRACE_SHA, corrected_trace_SHA256=sha(replayed),
                  decoded_records_identical=count, payload_byte_identical=True, replay=replay_result,
                  host_source_SHA256=sha(out/'host.c'), host_binary_SHA256=sha(out/'host'),
                  fixture_binary_SHA256=sha(fixture), reused_stress_log_SHA256=sha(args.stress_log),
                  installed_library_SHA256=sha('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'),
                  route_SHA256=sha(route), source_SHA256={str(p.relative_to(ROOT)):sha(p) for p in
                      [ROOT/'scripts/floor1/v01-native-timeline.h', ROOT/'scripts/floor1/v01-native-timeline-format.py',
                       ROOT/'scripts/floor1/v01-native-timeline-capacity-fixture.c', Path(__file__).resolve()]},
                  CPU_instructions_executed=0, gameplay_host_invocations=0, ROMs_loaded=0, Saves_loaded=0,
                  new_execution_claims=0, execution_counts={'baselines':6, 'candidates':3},
                  scope='Offline capacity correction only; no historical cause/remedy or gameplay acceptance.')
    (out/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
