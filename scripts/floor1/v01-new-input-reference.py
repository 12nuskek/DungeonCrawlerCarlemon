"""Independent complete typed B/F/E validation for a new input, without historical oracle pins."""
from pathlib import Path
import hashlib, struct

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
    assert terminal, 'Complete new-input typed finish required'
    assert 0 < video <= 36000 and 0 < ordinal <= 36000*4096
    result = dict(boundaries=ordinal,frames=video,total_zero_frames=zero,
                  maximum_consecutive_zero_frames=longest,initial_zero_frames=initial_zero,
                  all_metadata_SHA256=meta.hexdigest(),snapshot_SHA256=snapshots.hexdigest(),
                  snapshot_controls_SHA256=controls.hexdigest(),frame_metadata_SHA256=frames.hexdigest(),
                  typed_finish_SHA256=finish.hexdigest(),typed_finish_complete=True)
    return result
