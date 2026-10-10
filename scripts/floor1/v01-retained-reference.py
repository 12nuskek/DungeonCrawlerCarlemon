"""Explicit candidate-only oracle binding and conservative storage preflight.

Reads original bytes; never prepares/executes a host or reconstructs a reference.
The failed newer baseline can supply partial diagnostics, never the PASS oracle.
"""
from pathlib import Path
import hashlib, importlib.util, json, os, re, struct, subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'f3ceae890dbf9821ffade08c3cba4de40af31aa9'
SEED = '030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c'
ROUTE = 'afbd80b02d9d5acb9f63669f967fac3edc8eb00a2d2352e778f4114acb51bc27'
RAW = '849a1585f27b0de4a0e68e4036d88986847a9ece3f72dc8377dfec4214fae13d'
FINISH = '6ee2fb2d533d763cd4f3dd4da9a29a2833139ef1810a935b236947c1d20b1e1a'
META = 'd3a7b2037d7ea77104a9c9a7b2aa73b846a49ed788e927ffb4488ac3b4baca55'
FRAMES = '53421101e851ecc158d6a0b4065eb94ef26e96f7d9588b3b6b692b718d21c134'
SNAP = 'b6d56f9d7fd3441f85f1ae5390ba6684397a26ad74b87ec8262e3c60d8e8fdd9'
CONTROLS = '1b1801a0e9433340b04ffc3dd97067963c1fa26eddd67d16f40890d05d6b3396'
FILE_PINS = {
    'identity.json':'a24d6a164f6b00f864d21c89802a974d02e78eaca157ff320ce9e93b768dcb5c',
    'execution-claim.json':'15a30e67cf6958dec9ad01a2ef2bbd3de8b663ee7f9877e3c83df3be4ee12e6c',
    'summary.json':'d42966bcebd3f20e46e697db8fbd7f2b7efbed242336d0b35423b7d6eae1b4f2',
    'replay.log':'db045a82264158e10cd4a9ab8c7fc4abb647b968c2bdfc7a5018a64b8ce6ad71',
    'input.route':ROUTE, 'ordinary.sav':SEED, 'native-boundary-trace.bin':RAW,
}

def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(1048576): digest.update(block)
    return digest.hexdigest()

def scan(path):
    meta, snapshots, controls, frames, finish = (hashlib.sha256() for _ in range(5))
    ordinal = video = count = zero = run = longest = initial_zero = 0
    current_keys = last_keys = last_video = last_input = None
    terminal = False
    with Path(path).open('rb') as stream:
        while header := stream.read(29):
            assert len(header) == 29 and not terminal, 'Incomplete or post-finish record'
            kind, n, v, epoch, c, absolute, keys = struct.unpack('<cQIIIII', header)
            meta.update(header)
            assert n == ordinal
            if kind == b'E':
                assert count == c == 0 and v == video-1 and epoch == absolute == 2044+video
                assert keys == last_keys and last_video == v and last_input == epoch
                finish.update(header); terminal = True
                assert not stream.read(1); break
            assert v == video and epoch == 2045+video
            if current_keys is None: current_keys = keys
            assert keys == current_keys
            if kind == b'B':
                assert c == count and absolute == 2044+video
                data = stream.read(2560); assert len(data) == 2560
                for mon in range(6):
                    party = data[100*mon:100*(mon+1)]; assert not party[19]&1
                    key = struct.unpack_from('<I',party)[0] ^ struct.unpack_from('<I',party,4)[0]
                    checksum = sum(((w^key)&65535)+((w^key)>>16) for (w,) in struct.iter_unpack('<I',party[32:80]))
                    assert checksum&65535 == struct.unpack_from('<H',party,28)[0]
                snapshots.update(data); controls.update(data[2531:2549])
                ordinal += 1; count += 1; last_video = v; last_input = epoch
            elif kind == b'F':
                assert c == count and absolute == 2045+video
                frames.update(header)
                if not count:
                    zero += 1; run += 1
                    if not ordinal: initial_zero += 1
                else: run = 0
                longest = max(longest,run); count = 0; video += 1
                last_keys = keys; current_keys = None
            else: raise AssertionError('Unknown typed record')
    assert terminal, 'Complete original typed finish required'
    result = dict(boundaries=ordinal,frames=video,total_zero_frames=zero,
                  maximum_consecutive_zero_frames=longest,initial_zero_frames=initial_zero,
                  all_metadata_SHA256=meta.hexdigest(),snapshot_SHA256=snapshots.hexdigest(),
                  snapshot_controls_SHA256=controls.hexdigest(),frame_metadata_SHA256=frames.hexdigest(),
                  typed_finish_SHA256=finish.hexdigest(),typed_finish_complete=True)
    assert (ordinal,video,zero,longest,initial_zero)==(15379,15627,248,12,0)
    assert [result[k] for k in ['all_metadata_SHA256','snapshot_SHA256','snapshot_controls_SHA256','frame_metadata_SHA256','typed_finish_SHA256']] == [META,SNAP,CONTROLS,FRAMES,FINISH]
    return result

def verify(directory, seed):
    directory = Path(directory).resolve(); seed = Path(seed).resolve()
    assert (directory/'native-boundary-trace.bin').is_file(), 'Original complete reference unavailable; stop without reconstruction'
    for name, digest in FILE_PINS.items(): assert sha(directory/name)==digest, name
    assert sha(seed)==SEED and (directory/'errors.log').stat().st_size==0
    identity = json.loads((directory/'identity.json').read_text())
    claim = json.loads((directory/'execution-claim.json').read_text())
    summary = json.loads((directory/'summary.json').read_text())
    public = ROOT/'docs/evidence/floor1/v01/battle/native-boundary-validation'
    assert identity==claim==json.loads((public/'before-identity.json').read_text())
    assert summary==json.loads((public/'before-summary.json').read_text())
    assert identity['source']==summary['execution_source']==SOURCE
    assert summary['native_exit']==summary['errors_bytes']==0 and summary['assertions']==42
    assert identity['input_Save_SHA256']==summary['output_Save_SHA256']==SEED
    engine = ROOT/'artifacts/floor1/v01-overworld/build-registered/source/engine'
    for key, path in [('ROM_SHA256',engine/'pokeemerald.gba'),('ELF_SHA256',engine/'pokeemerald.elf'),
                      ('host_SHA256',directory/'observer.c'),('binary_SHA256',directory/'playtest'),
                      ('symbols_SHA256',directory/'game.sym'),('verified_functions_SHA256',directory/'verified-functions.json'),
                      ('native_boundary_SHA256',directory/'native-boundary.json')]:
        assert sha(path)==identity[key], key
    assert (engine.parent.parent/'tested-commit.txt').read_text().strip()==identity['game_build']=='4938927da512543ca9aeea9527c103c84955e632'
    tree = subprocess.check_output(['git','rev-parse',identity['game_build']+':engine'],cwd=ROOT,text=True).strip()
    assert tree==identity['engine_tree']=='76001ee128785714b7c15aef6d9c95630587d0a9'
    assert sha(ROOT/'scripts/contracts/f1-v01-battle.route')==ROUTE
    for name, digest in identity['fixture_SHA256'].items(): assert sha(directory/name)==digest
    assert (directory/'native-boundary-trace.bin').stat().st_size==40269443
    parsed = scan(directory/'native-boundary-trace.bin')
    return dict(contract='candidate-only retained original complete PASS oracle; explicit opt-in',
                original_execution=SOURCE,reference_SHA256=RAW,reference_bytes=40269443,
                original_build_identity=identity,original_file_SHA256=FILE_PINS,
                complete_reference=parsed,active_chunks=parsed['total_zero_frames']+2,
                startup_chunks=2044+parsed['initial_zero_frames']+2,
                legacy_acceptance_restored=False,new_baseline_executions=0,new_candidate_executions=0,
                partial_baseline_role='Matching diagnostics only through13956; never PASS oracle')

def format_upper(code):
    # Every integer/pointer field uses at most24 characters. Controlled strings
    # are bounded by the host's512-byte command buffer (symbols are smaller).
    formats = re.findall(r'(?:printf|fprintf)\((?:stderr,)?\s*"((?:\\.|[^"\\])*)"',code)
    return sum(len(f)+24*len(re.findall(r'%(?!%)[^a-z]*[a-z]',f))+512*f.count('%s') for f in formats)

def legacy_host(code, git):
    """Prove surrounding host/controller unchanged except reviewed storage hooks."""
    base='268fa9a8e0673824ff47e191e7be5777e8b6489e'
    old_timeline=git('show',base+':scripts/floor1/v01-native-timeline.h')+'\n'
    old_runtime=git('show',base+':scripts/floor1/v01-native-boundary-runtime.h')+'\n'
    current_timeline=(ROOT/'scripts/floor1/v01-native-timeline.h').read_text().replace('#include "v01-native-timeline-storage.h"',(ROOT/'scripts/floor1/v01-native-timeline-storage.h').read_text())
    current_runtime=(ROOT/'scripts/floor1/v01-native-boundary-runtime.h').read_text()
    strip=lambda text:text.replace('#include "v01-native-boundary-adapter.h"','').replace('#include "v01-native-boundary-diagnostics.h"','').replace('#include "v01-native-timeline.h"','')
    assert code.count(current_timeline)==code.count(strip(current_runtime))==1
    code=code.replace(current_timeline,old_timeline).replace(strip(current_runtime),strip(old_runtime))
    code=code.replace('    if(bv_tl_storage_enable(&timeline,"native-timeline-summary-private.bin"))return 119;\n','')
    code=code.replace('if(visual.recording && visual.frames>=36000){bv_tl_flush(&timeline,109,0);exit(109);}','if(visual.recording && visual.frames>=36000)exit(109);')
    code=code.replace('bv_native_retain_failure(&native);bv_tl_flush(&timeline,vr,0);','bv_native_retain_failure(&native);')
    code=code.replace('    if(result)bv_tl_flush(&timeline,result,0);\n','')
    code=code.replace('    bv_tl_flush(&timeline,51,0); \\\n','')
    assert hashlib.sha256(code.encode()).hexdigest()=='64a924e8ec7130040b822a500f93b4692751b65008e83bb767c2b31a51c841de'
    return code

def working_bound(code, binary_bytes, reference_directory):
    """Measure fixed pinned-ELF symbol/JSON outputs without creating a trial."""
    def module(name, path):
        spec=importlib.util.spec_from_file_location(name,path); result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
    symbols=module('storage_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py')
    boundary=module('storage_boundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
    timeline=module('storage_points',ROOT/'scripts/floor1/v01-native-timeline-symbols.py')
    maximum=0; sizes=[]
    for name,path,digest in [('original','artifacts/floor1/v01-overworld/build-registered/source/engine','2fb481bdb041772fef7aa0ed15deb6a30b7a24c54f9f6d487c2b733fe26fb066'),
                             ('optimized','artifacts/floor1/v01-battle/build-cache-return/source/engine','f31a5a8b2cb1602df378a7ca66b3cee8bbcea86de000536ab6f55acd727d0218')]:
        engine=ROOT/path;elf=engine/'pokeemerald.elf';assert sha(elf)==digest
        functions=symbols.functions(symbols.elf_symbols(elf)); bp=boundary.resolve(elf); tp=timeline.resolve(elf)
        exports=''.join(f"{r['address']:08x} F {r['token']}\n" for r in functions)+symbols.lifecycle_symbols(functions)
        nm=subprocess.check_output(['arm-none-eabi-nm','--defined-only',str(elf)])
        inputs=subprocess.check_output(['python3',str(ROOT/'scripts/battle-input-symbols.py'),str(engine)])
        #21 points×4 fields plus3 native boundary pins and4 RAM pins: each
        # exported line is under128 bytes, checked against the generated names.
        table=dict(function_JSON=len((json.dumps(functions,indent=2)+'\n').encode()),
                   symbol_file=len(nm)+len(inputs)+len(exports.encode())+(21*4+3+4)*128,
                   boundary_JSON=len((json.dumps(bp,indent=2)+'\n').encode()),
                   timeline_JSON=len((json.dumps(tp,indent=2)+'\n').encode()))
        sizes.append({'build':name,**table});maximum=max(maximum,sum(table.values()))
    directory=Path(reference_directory);identity=json.loads((directory/'identity.json').read_text())
    fixed=sum((directory/name).stat().st_size for name in identity['fixture_SHA256'])+(directory/'expected-metadata.json').stat().st_size
    # Existing prepared contract includes a131088-byte Save;32 fixed4096-byte
    # JSON/log/route/diagnostic envelopes cover its small working metadata.
    total=maximum+fixed+len(code.encode())+binary_bytes+131088+32*4096
    return {'upper_bytes':total,'pinned_symbol_outputs':sizes,'fixture_bytes':fixed,
            'host_source_bytes':len(code.encode()),'host_binary_bytes':binary_bytes,
            'Save_bytes':131088,'fixed_metadata_envelopes':32*4096}

def storage_bound(code, prepared_bytes):
    observer = (ROOT/'scripts/floor1/v01-battle-observer.h').read_text()
    # Finish/peak/warning emit only at the route's terminal command; they are
    # covered by the separate command bucket, not charged on every frame.
    observer=observer[:observer.index('static unsigned bv_finish(')]
    start = code.index('        if (!strncmp(line,"pilot ",6))')
    end = code.index('        if (sscanf(line,"step ',start)
    # All these logging sites execute at most4 times per frame (four battlers).
    # Non-frame command logging is separately overbounded by64 native slots
    # times every static format per pinned route command.
    per_frame_log = 4*(format_upper(observer)+format_upper(code[start:end]))
    route_lines = len((ROOT/'scripts/contracts/f1-v01-battle.route').read_text().splitlines())
    log_bytes = 38044*per_frame_log + route_lines*64*format_upper(code)
    static_ppms = set(re.findall(r'"([a-z0-9-]+\.ppm)"',code))
    route_ppms = [line.split()[3] for line in (ROOT/'scripts/contracts/f1-v01-battle.route').read_text().splitlines() if line.startswith('step ') and line.split()[3]!='-']
    helpers = 18+40+128+256+len(static_ppms | set(route_ppms))
    # Helper PNGs only: RGB PPM input has no metadata. Twice its payload bounds
    # PNG scanline filters, zlib compressBound and IDAT/chunk envelopes.
    ppm_bytes = 240*160*3+len(b'P6\n240 160\n255\n')
    budget = dict(startup_detail=32+2046*4096*184,active_detail=32+250*4096*184,
                  summaries=32+38045*184,reference_copy=40269443,
                  capture_files=36000+helpers,helper_exports=helpers,
                  capture_bytes=(36000+helpers)*ppm_bytes,helper_PNG_bytes=helpers*2*ppm_bytes,
                  textual_logs=log_bytes,working_files=prepared_bytes,
                  metadata_files=64*4096,per_frame_text_upper=per_frame_log,
                  route_command_text_upper=64*format_upper(code),startup_chunks=2046,active_chunks=250)
    # Account for filesystem block rounding for every independent file. The
    # metadata allocation above also covers fixed small diagnostic files/dirs.
    block = os.statvfs(ROOT).f_frsize
    round_up = lambda n: ((n+block-1)//block)*block
    budget['filesystem_block_bytes']=block
    budget['required_available_bytes']=sum(round_up(budget[k]) for k in ['startup_detail','summaries','reference_copy','textual_logs','working_files','metadata_files']) + (36000+helpers)*round_up(ppm_bytes) + helpers*round_up(2*ppm_bytes)
    budget['detail_retention']='startup prefix then latest accepted native boundary suffix; not full-history detail'
    return budget

def preflight(budget, path, available=None, credited=0):
    path = Path(path).resolve()
    while not path.exists(): path=path.parent
    if available is None:
        stat=os.statvfs(path); available=stat.f_bavail*stat.f_frsize
    assert 0<=credited<=budget['working_files']+budget['reference_copy']+budget['metadata_files']
    remaining=budget['required_available_bytes']-credited
    assert available>=remaining, 'Insufficient combined storage: fail before preparation/claim/game execution'
    return dict(required_bytes=budget['required_available_bytes'],remaining_bytes=remaining,
                credited_verified_allocated_bytes=credited,available_bytes=available,passed=True)
