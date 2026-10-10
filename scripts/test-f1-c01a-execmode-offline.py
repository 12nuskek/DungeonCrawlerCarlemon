"""Permission fixtures are inert text files; no compiler, emulator or gameplay."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('execfile', ROOT / 'scripts/floor1/c01a-prefix-execfile.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)

def test(output):
    results = {}
    with tempfile.TemporaryDirectory(prefix='c01a-execmode-') as directory:
        p = Path(directory) / 'observer'
        p.write_bytes(b'inert fixture; never executed\n'); p.chmod(0o700)
        expected = {'SHA256': hashlib.sha256(p.read_bytes()).hexdigest(), 'mode': 0o700, 'owner_uid': os.geteuid()}
        def reject(name, path=p, identity=expected):
            try: module.verify_executable(path, identity)
            except (AssertionError, OSError): results[name] = 'rejected'; return
            raise AssertionError(name + ' unexpectedly accepted')
        results['0700_accepted'] = module.verify_executable(p, expected)
        bound = dict(expected, device=p.stat().st_dev, inode=p.stat().st_ino)
        module.verify_executable(p, bound)
        reject('wrong_frozen_file_identity', identity=dict(bound, inode=bound['inode'] + 1))
        p.chmod(0o600); reject('historical0600_rejected'); p.chmod(0o700)
        reject('missing', p.parent / 'missing')
        reject('nonregular_directory', p.parent)
        fifo = p.parent / 'fifo'; os.mkfifo(fifo); reject('nonregular_fifo', fifo)
        link = p.parent / 'link'; link.symlink_to(p); reject('symlink', link)
        reject('wrong_hash', identity=dict(expected, SHA256='0' * 64))
        reject('wrong_owner', identity=dict(expected, owner_uid=os.geteuid() + 1))
        p.chmod(0o400); reject('non_executable'); p.chmod(0o700)
        module.verify_executable(p, expected)  # preparation check
        p.chmod(0o600); reject('mode_lost_before_admission'); p.chmod(0o700)
        original_access = module.os.access
        module.os.access = lambda *a: False
        try: reject('executable_access_denied_with0700')
        finally: module.os.access = original_access
    proof = {'PASS': True, 'no_gameplay_no_execution_no_compilation': True,
             'fixture_results': results, 'rejected_cases': sum(v == 'rejected' for v in results.values()),
             'source_SHA256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [ROOT / 'scripts/floor1/c01a-prefix-execfile.py', Path(__file__)]}}
    with output.open('x') as f: json.dump(proof, f, indent=2); f.write('\n')
    print(json.dumps(proof, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    test(parser.parse_args().output)
