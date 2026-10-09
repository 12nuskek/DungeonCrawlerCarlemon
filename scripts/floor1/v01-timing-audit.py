"""Offline pinned timing mechanisms; never loads a game, Save or resets a core."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, subprocess

ROOT = Path(__file__).resolve().parents[2]
ELFS = {
    'before': ('artifacts/floor1/v01-overworld/build-registered/source/engine/pokeemerald.elf', '2fb481bdb041772fef7aa0ed15deb6a30b7a24c54f9f6d487c2b733fe26fb066'),
    'after': ('artifacts/floor1/v01-battle/build-headers/source/engine/pokeemerald.elf', '0bbce8cce6485cf6860ac19ce3b75b580ca8b2d5735909b40906f64c056eb98f'),
}
VIDEO_SHA = 'c99391529cce6729400ae199ca9ddb65fec7c0d7f1945d214b8941c61e1e694c'
LIB_SHA = 'a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'

def module():
    spec = importlib.util.spec_from_file_location('timing_symbols', ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj

def prepare(output, video):
    output.mkdir(parents=True, exist_ok=True)
    data = video.read_bytes(); assert hashlib.sha256(data).hexdigest() == VIDEO_SHA
    # Entire callback bodies are copied without logic changes; names permit
    # observation and coexistence with installed internal static callbacks.
    text = data.decode(); begin = text.index('void _startHdraw(struct mTiming* timing')
    end = text.index('void GBAVideoWriteDISPSTAT', begin)
    bodies = text[begin:end].replace('_startHdraw', 'audit_hdraw').replace('_startHblank', 'audit_hblank')
    bodies = bodies.replace('void audit_hdraw(', 'static void audit_hdraw_body(').replace('void audit_hblank(', 'static void audit_hblank_body(')
    (output/'video_callbacks.h').write_text('/* Official mGBA 0.10.5 video.c; MPL-2.0. See exact source hash in report. */\n'+bodies)
    assert hashlib.sha256(Path('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5').read_bytes()).hexdigest() == LIB_SHA
    mod = module(); pins = {}
    for name, (relative, digest) in ELFS.items():
        elf = ROOT/relative; assert hashlib.sha256(elf.read_bytes()).hexdigest() == digest
        record = mod.resolve(elf); assert record['entry'] == 0x080008ac
        assert mod.rom_bytes(elf,0x080004be,2) == b'\xb4\xe7'
        wait = mod.rom_bytes(elf, record['entry'], 48)
        (output/(name+'-wait.bin')).write_bytes(wait)
        pins[name] = {'ELF_SHA256': digest, 'Wait_SHA256': hashlib.sha256(wait).hexdigest(), 'native_boundary': record}
    assert (output/'before-wait.bin').read_bytes() == (output/'after-wait.bin').read_bytes()
    subprocess.run(['gcc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(output), str(ROOT/'scripts/floor1/v01-timing-audit-fixture.c'), '-lmgba','-o',str(output/'fixture')], check=True)
    for name in ELFS:
        result = subprocess.run([str(output/'fixture'),str(output/(name+'-wait.bin'))], capture_output=True, text=True)
        (output/(name+'-trace.jsonl')).write_text(result.stdout)
        (output/(name+'-stderr.txt')).write_text(result.stderr)
        result.check_returncode()
    assert (output/'before-trace.jsonl').read_bytes() == (output/'after-trace.jsonl').read_bytes()
    pins.update({'official_video_SHA256':VIDEO_SHA,'installed_library_SHA256':LIB_SHA,'cases_per_ELF':7,'scope':'Synthetic mechanism only. No ROM/Save/reset/gameplay; bus/callback/IRQ-body costs synthetic. No actual STOP117 IRQ/cycle reconstruction.'})
    (output/'mechanism-result.json').write_text(json.dumps(pins,indent=2)+'\n')
    print(json.dumps({'PASS':True,'cases':14,'both_ELFs_identical_trace':True,'scope':pins['scope']}))

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--official-video',type=Path,required=True)
    args=parser.parse_args();prepare(args.output,args.official_video)
