"""Exact archive-backed frame proposal and consumer primitives; no implicit writes."""
from pathlib import Path, PurePosixPath
import hashlib
import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import threading
import zlib

ROOT = Path(__file__).resolve().parents[2]
SCRATCH = Path('/workspace/scratch')
FRAMES = SCRATCH / 'new-input-visual-pair-20261010'
ARCHIVE = FRAMES / 'new-input-pair-private-evidence.tar.gz'
ARCHIVE_SHA = 'f43bdc3b80c55a3b566c1f4058e2ece2844ec6c051164c7605ab73c2843dbcd3'
MANIFEST = FRAMES / 'private-retention-manifest.json'
MANIFEST_SHA = '2800fe68cd6978934b08f9cec1a7fcd54816d14ec264e52d5aec2779c44dbe76'
BASE = '61c181d6fe67a9b9987351e63daf353449826ce7'
PREP = SCRATCH / 'v01-frame-archive-proposal-r1-20261011'
TESTS = SCRATCH / 'v01-frame-archive-offline-r1-20261011'
OUT = SCRATCH / 'v01-frame-archive-replacement-r1-20261011'
AUTHORITY = SCRATCH / 'v01-frame-archive-authority-r1-20261011.json'
COUNT = 31254
CASE_COUNT = 15627
HEADER = b'P6\n240 160\n255\n'
PIXELS = 240 * 160 * 3
FRAME_BYTES = len(HEADER) + PIXELS
ALLOCATED = 3712475136
METADATA_CAP = 64 * 1024**2
AUDIT_RESERVE = 128 * 1024**2
SELECTED_RESTORE_CAP = 2 * 118784 + 3 * 4096
CAP = METADATA_CAP + AUDIT_RESERVE + SELECTED_RESTORE_CAP
WARDEN = 17694519296
FILES = ('scripts/floor1/v01-frame-archive.py', 'scripts/floor1/v01-frame-archive-controller.py',
         'scripts/prepare-v01-frame-archive-r1.py', 'scripts/retained-v01-frames.py',
         'scripts/test-v01-frame-archive-offline.py', 'docs/floor1/v01-frame-archive-proposal-r1-contract.md')
WARDEN_INPUTS = (SCRATCH / 'c01-warden-native-dialogue-state-inputs-r1-20261011.json',
                 SCRATCH / 'c01-warden-finalization-offline-inputs-r6-20261011.json')
SPEC = importlib.util.spec_from_file_location('accepted_frame_helpers', ROOT / 'scripts/floor1/howler-rgb-preservation-controller.py')
accepted = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(accepted)
engine = accepted.engine
require = engine.require


def digest(path):
    return engine.digest(Path(path))


def git(*args):
    return accepted.scope.accepted.git(*args)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def identity(path):
    path = Path(path)
    before = engine.identity(path)
    links = path.lstat().st_nlink
    return {key: str(value) if key in ('device', 'inode', 'mode', 'uid', 'mtime_ns') else value
            for key, value in dict(before, nlink=links).items()}


def identity_schema(row):
    require(set(row) == {'device', 'inode', 'mode', 'uid', 'mtime_ns', 'bytes', 'allocated_bytes', 'nlink'}, 'complete exact metadata')
    for key in ('device', 'inode', 'mode', 'uid', 'mtime_ns'):
        require(type(row[key]) is str and re.fullmatch(r'0|[1-9][0-9]*', row[key]), 'integer-safe decimal metadata: ' + key)
    for key in ('bytes', 'allocated_bytes', 'nlink'):
        require(type(row[key]) is int and row[key] >= 0, 'integer metadata: ' + key)


def check_file(path, row):
    identity_schema(row['identity'])
    require(identity(path) == row['identity'] and digest(path) == row['SHA256'] and
            identity(path) == row['identity'], 'exact protected/input identity and bytes: ' + str(path))


def names():
    return [f'{case}/battle-{i:05}.ppm' for case in ('baseline', 'candidate') for i in range(CASE_COUNT)]


def safe_name(name):
    require(type(name) is str and name and '\\' not in name and ':' not in name and
            not name.startswith('/') and str(PurePosixPath(name)) == name and
            all(part not in ('', '.', '..') for part in name.split('/')), 'unsafe or ambiguous archive member')
    return name


class Blocks:
    """Bounded decoder reader, preserving the accepted independent gzip decoders."""
    def __init__(self, blocks):
        self.blocks, self.pending, self.eof = iter(blocks), bytearray(), False

    def read(self, count):
        require(0 <= count <= 1024**2, 'bounded archive read')
        while len(self.pending) < count and not self.eof:
            try:
                self.pending.extend(next(self.blocks))
            except StopIteration:
                self.eof = True
        data = bytes(self.pending[:count])
        del self.pending[:count]
        return data

    def exact(self, count):
        data = self.read(count)
        require(len(data) == count, 'truncated member/header exact EOF')
        return data


def pax(data):
    values, position = {}, 0
    while position < len(data):
        end = data.find(b' ', position)
        require(end > position and data[position:end].isdigit(), 'invalid PAX length')
        length = int(data[position:end])
        record = data[end + 1:position + length]
        require(length > end - position + 1 and position + length <= len(data) and record.endswith(b'\n'), 'invalid PAX record')
        key, separator, value = record[:-1].partition(b'=')
        require(separator and key == b'mtime' and key not in values and re.fullmatch(rb'[0-9]+(?:\.[0-9]+)?', value), 'unexpected/ambiguous PAX metadata')
        values[key] = value.decode('ascii')
        position += length
    require(position == len(data), 'PAX exact EOF')
    return values


def walk(blocks, consume):
    """Strict entire TAR/GZIP EOF; no extraction or permissive tarfile iteration."""
    stream = Blocks(blocks)
    seen, pending, ordinal, chain = set(), None, 0, hashlib.sha256()
    while True:
        header = stream.exact(512)
        if header == bytes(512):
            require(pending is None and stream.exact(512) == bytes(512), 'two exact TAR end blocks required')
            tail = 0
            while data := stream.read(65536):
                require(not any(data), 'unexpected bytes/member after TAR EOF')
                tail += len(data)
            require(tail % 512 == 0, 'TAR padding EOF alignment')
            return dict(members=ordinal, member_chain_SHA256=chain.hexdigest(), exact_TAR_and_gzip_EOF=True)
        try:
            entry = tarfile.TarInfo.frombuf(header, 'utf-8', 'strict')
        except (tarfile.HeaderError, UnicodeError) as error:
            raise RuntimeError('invalid archive header') from error
        require(type(entry.size) is int and entry.size >= 0, 'member byte count')
        if entry.type == tarfile.XHDTYPE:
            require(entry.name == '././@PaxHeader' and pending is None and entry.size <= 65536, 'bounded fixed PAX metadata header')
            pending = pax(stream.exact(entry.size))
        else:
            safe_name(entry.name)
            require(entry.isreg() and not entry.linkname and entry.name not in seen, 'duplicate/link/unexpected archive member type')
            seen.add(entry.name)
            record = dict(name=entry.name, bytes=entry.size, ordinal=ordinal,
                          mode=str(entry.mode), uid=str(entry.uid),
                          archive_mtime_decimal=pending[b'mtime'] if pending else str(entry.mtime))
            chain.update(encode(record))
            consume(record, stream)
            ordinal += 1
            pending = None
        padding = (-entry.size) % 512
        require(stream.exact(padding) == bytes(padding), 'nonzero archive member padding')


def discard(stream, count):
    while count:
        data = stream.exact(min(count, 65536))
        count -= len(data)


def archive_scan(rows, mode='zlib', compare_originals=False, consumer=None):
    require(mode in ('zlib', 'gzip'), 'fixed independent decoder')
    lookup = {row['member']: row for row in rows}
    require(len(lookup) == len(rows), 'duplicate requested frame')
    found, pixel_hashes = {}, {}
    def consume(meta, stream):
        name = meta['name']
        if name not in lookup:
            discard(stream, meta['bytes'])
            return
        row = lookup[name]
        require(meta['bytes'] == FRAME_BYTES and (row.get('archive_member') is None or meta == row['archive_member']), 'wrong member identity/count/order')
        data = stream.exact(FRAME_BYTES)
        require(data.startswith(HEADER) and hashlib.sha256(data).hexdigest() == row['SHA256'], 'exact native PPM bytes/hash/dimensions')
        if compare_originals:
            check_file(FRAMES / name, row)
            require((FRAMES / name).read_bytes() == data and identity(FRAMES / name) == row['identity'], 'archive-to-original exact frame comparison')
        found[name] = meta
        pixel_hashes[name] = hashlib.sha256(data[len(HEADER):]).digest()
        if consumer:
            consumer(row, data)
    result = walk(engine.zlib_blocks(ARCHIVE) if mode == 'zlib' else engine.gzip_blocks(ARCHIVE), consume)
    require(set(found) == set(lookup), 'missing archive frame member')
    result.update(targets=len(found), pixel_hashes=pixel_hashes, archive_members=found)
    return result


def target_scope(rows):
    require([r['member'] for r in rows] == names() and len(rows) == COUNT, 'exact ordered 31254-target scope')
    for row in rows:
        require(row['raw_path'] == str(FRAMES / row['member']) and row['bytes'] == FRAME_BYTES and
                re.fullmatch(r'[0-9a-f]{64}', row['SHA256']), 'exact raw frame path/count/hash')
        identity_schema(row['identity'])
        require(row['identity']['bytes'] == FRAME_BYTES and row['identity']['nlink'] == 1, 'complete original regular frame; no hardlinks')
        if 'archive_member' in row:
            meta = row['archive_member']
            require(meta['name'] == row['member'] and meta['bytes'] == FRAME_BYTES and
                    type(meta['ordinal']) is int and 0 <= meta['ordinal'] < 32166,
                    'exact archive member path/frame identity')
    require(sum(r['identity']['allocated_bytes'] for r in rows) == ALLOCATED, 'exact unique raw allocation')
    require(len({(r['identity']['device'], r['identity']['inode']) for r in rows}) == COUNT, 'distinct original inodes')
    if all('archive_member' in r for r in rows):
        require(len({r['archive_member']['ordinal'] for r in rows}) == COUNT, 'unambiguous archive target ordinals')


def load_json(path):
    identity(path)
    return json.loads(Path(path).read_text())


def load_lines(path):
    identity(path)
    with Path(path).open() as file:
        return [json.loads(line) for line in file]


def available():
    s = os.statvfs(SCRATCH)
    require(s.f_frsize == 4096 and not s.f_flag & os.ST_RDONLY, 'writable reviewed workspace device')
    return s.f_bavail * s.f_frsize


def capacity(free, extra=0, concurrent_warden=False):
    require(type(free) is int and type(extra) is int and extra >= 0 and
            free >= CAP + extra + (WARDEN if concurrent_warden else 0), 'insufficient metadata/restore/reservation capacity')


def consumer_admission(protected_paths):
    targets = {str(FRAMES / name) for name in names()}
    pins = {}
    for path in WARDEN_INPUTS:
        config = load_json(path)
        require(config['preserved_reservation_bytes'] == WARDEN, 'unchanged Warden reservation')
        required = set(config['files']) | set(config['protected_history'])
        require(not required & targets, 'Warden requires target restoration')
        require(all(path in protected_paths for path in required if path.startswith('/workspace')), 'complete active Warden/history protected closure')
        pins[str(path)] = digest(path)
    return dict(required_target_restorations=0, whole_directory_restore_concurrent_with_Warden=False,
                Warden_input_configs_SHA256=pins, historical_full_capture_encoder='Dormant; use adapter retention check or separate full restoration admission',
                exact_original_inode_restoration=False, selected_restore_limit=2, selected_restore_cap_bytes=SELECTED_RESTORE_CAP)


def provider_files():
    origin, dependencies = accepted.scope.accepted.decoder_dependencies()
    require(origin == 'built-in' and zlib.ZLIB_RUNTIME_VERSION == '1.3.2', 'accepted built-in zlib provider')
    # FFmpeg is used only by the optional read-only retained-video consumer.
    binary = Path('/usr/bin/ffmpeg')
    dependencies[str(binary.resolve())] = digest(binary)
    text = subprocess.check_output(['ldd', str(binary)], text=True)
    for token in re.findall(r'(?:=>\s*)?(/[^\s()]+)', text):
        path = Path(token).resolve()
        dependencies[str(path)] = digest(path)
    for module in (tarfile, json, subprocess, threading):
        path = Path(module.__file__).resolve()
        dependencies[str(path)] = digest(path)
    return dependencies


def proposal():
    contract = load_json(PREP / 'proposal-private.json')
    rows = load_lines(PREP / 'frame-inventory-private.jsonl')
    protected = load_lines(PREP / 'protected-inventory-private.jsonl')
    require(contract['source_commit'] == git('rev-parse', 'HEAD') and not git('status', '--porcelain'), 'clean proposed source')
    require(contract['archive']['SHA256'] == ARCHIVE_SHA and contract['manifest_SHA256'] == MANIFEST_SHA and
            contract['cap_bytes'] == CAP and contract['runtime_reservation_bytes'] == WARDEN and
            contract['execution_permitted'] is False and contract['target_count'] == COUNT, 'exact proposal authority/scope/cap')
    require(digest(PREP / 'frame-inventory-private.jsonl') == contract['inventory_SHA256'] and
            digest(PREP / 'protected-inventory-private.jsonl') == contract['protected_SHA256'], 'immutable mapping/protected inventory')
    target_scope(rows)
    require({row['raw_path'] for row in rows}.isdisjoint({r['path'] for r in protected}), 'protected targets forbidden')
    return contract, rows, protected


def recheck(contract, protected, originals=None):
    require(git('rev-parse', 'HEAD') == contract['source_commit'] and not git('status', '--porcelain'), 'exact clean source')
    for path, sha in contract['source_files_SHA256'].items():
        require(digest(ROOT / path) == sha, 'source changed')
    for path, sha in contract['provider_files_SHA256'].items():
        require(digest(path) == sha, 'provider changed')
    require(provider_files() == contract['provider_files_SHA256'] and not os.environ.get('GZIP'), 'provider closure/settings changed')
    check_file(ARCHIVE, contract['archive'])
    require(digest(MANIFEST) == MANIFEST_SHA, 'historical manifest changed')
    for row in protected:
        check_file(row['path'], row)
    if originals is not None:
        for row in originals:
            check_file(row['raw_path'], row)


def retained_frames(contract, rows, members):
    require(0 < len(members) <= 2 and len(set(members)) == len(members), 'at most two explicitly requested frames')
    selected = [row for row in rows if row['member'] in members]
    require(len(selected) == len(members), 'exact approved member request')
    check_file(ARCHIVE, contract['archive'])
    data = {}
    archive_scan(selected, consumer=lambda row, frame: data.update({row['member']: frame}))
    check_file(ARCHIVE, contract['archive'])
    return data


def materialize(contract, rows, members, output):
    require(len(members) <= 2, 'bounded selected materialization only')
    output = Path(output)
    require(output.is_absolute() and output.parent.resolve() == SCRATCH and not os.path.lexists(output), 'fresh explicit workspace materialization directory')
    capacity(available(), SELECTED_RESTORE_CAP, concurrent_warden=True)
    frames = retained_frames(contract, rows, members)
    output.mkdir(mode=0o700)
    provenance = []
    for row in rows:
        if row['member'] not in frames:
            continue
        path = output / row['member'].replace('/', '-')
        with path.open('xb') as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(frames[row['member']]); file.flush(); os.fsync(file.fileno())
        os.utime(path, ns=(int(row['identity']['mtime_ns']), int(row['identity']['mtime_ns'])))
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        provenance.append(dict(member=row['member'], restored_path=str(path), SHA256=digest(path),
                               archive_SHA256=ARCHIVE_SHA, original_identity=row['identity'],
                               restored_identity=identity(path), restored_bytes=True,
                               original_inode_recreated=False, historical_receipts_modified=False))
    require(sum(p.stat().st_blocks * 512 for p in output.iterdir()) <= SELECTED_RESTORE_CAP - 8192, 'selected-frame allocation bound')
    engine.Budget(output, cap=SELECTED_RESTORE_CAP, reserve=0).json(output / 'restoration-provenance-private.json', provenance)
    fd = os.open(output, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return provenance


def check_capture_retention(contract, rows):
    """Verify ordered old FFV1 pixels against archive members without restoring directories."""
    check_file(ARCHIVE, contract['archive'])
    pixels = archive_scan(rows)['pixel_hashes']
    results = []
    for case in ('baseline', 'candidate'):
        historic = load_json(FRAMES / case / 'capture-retention.json')
        require(historic['numbered_frames'] == CASE_COUNT and historic['terminal_partial_frame_capture'] is False and
                historic['every_lossless_pixel_verified'] is True, 'unchanged historical capture semantics')
        clip = FRAMES / case / 'actual-native-lossless.mkv'
        require(digest(clip) == historic['lossless_SHA256'], 'immutable old lossless clip')
        proc = subprocess.Popen(['/usr/bin/ffmpeg', '-v', 'error', '-i', str(clip), '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        errors = []
        def drain_error():
            data = proc.stderr.read(4097)
            if data:
                errors.append(data)
            if len(data) > 4096 and proc.poll() is None:
                proc.kill()
        reader = threading.Thread(target=drain_error, daemon=True)
        timer = threading.Timer(1800, lambda: proc.kill() if proc.poll() is None else None)
        timer.daemon = True
        reader.start(); timer.start()
        aggregate = hashlib.sha256()
        try:
            for i in range(CASE_COUNT):
                data = engine.read_exact(proc.stdout, PIXELS)
                require(len(data) == PIXELS and hashlib.sha256(data).digest() == pixels[f'{case}/battle-{i:05}.ppm'], 'ordered exact archived frame pixels')
                aggregate.update(data)
            require(not proc.stdout.read(1), 'retained clip exact EOF')
            require(proc.wait(timeout=30) == 0, 'retained clip decoder exit')
            reader.join(timeout=10)
            require(not reader.is_alive() and not errors and aggregate.hexdigest() == historic['RGB_SHA256'] == historic['decoded_RGB_SHA256'], 'historical ordered RGB digest')
        finally:
            timer.cancel()
            if proc.poll() is None:
                proc.kill(); proc.wait()
            reader.join(timeout=10)
            proc.stdout.close(); proc.stderr.close()
        results.append(dict(case=case, frames=CASE_COUNT, ordered_RGB_SHA256=aggregate.hexdigest(), directory_restorations=0, source='retained archive and existing FFV1 pixels; historical receipts unchanged'))
    check_file(ARCHIVE, contract['archive'])
    return results
