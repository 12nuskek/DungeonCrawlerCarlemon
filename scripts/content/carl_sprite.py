"""Original E01 pixel artwork, authored as indexed pixels, not traced/recoloured.

Nine 16x32 walking frames; right-facing uses the engine's left-frame mirroring.
Simple brown hair, bare torso/feet and heart-patterned white shorts are an
adaptation sketch, pending S02 art review. PNG writer uses only Python stdlib.
"""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[2] / 'engine'
COLORS = [(0, 0, 0), (48, 32, 32), (89, 52, 38), (142, 88, 56),
          (244, 183, 136), (211, 137, 99), (255, 212, 160), (237, 236, 215),
          (170, 178, 180), (204, 50, 66), (135, 31, 48), (255, 255, 239),
          (52, 65, 75), (99, 106, 106), (0, 0, 0), (0, 0, 0)]
FRONT = [
    '....11111111....', '...1222222221...', '..122233322221..',
    '..123333333321..', '..124444444421..', '..144144441441..',
    '...4444444444...', '...1544554451...', '....15555551....',
    '....14444441....', '..114466664411..', '.14444666644441.',
    '.14544444444541.', '.14544444444541.', '.14544444444541.',
    '..554444444455..', '..111777777111..', '...1779779771...',
    '...1777977971...', '...1777777771...', '...1888118881...',
    '....155..551....', '....144..441....', '...1444..4441...',
]
BACK = [
    '....11111111....', '...1222222221...', '..122233322221..',
    '..122333333221..', '..122222222221..', '..122222222221..',
    '...1222222221...', '...1555555551...', '....15555551....',
    '....14444441....', '..114466664411..', '.14444666644441.',
    '.14544444444541.', '.14544444444541.', '.14544444444541.',
    '..554444444455..', '..111777777111..', '...1779777771...',
    '...1777979771...', '...1777777971...', '...1888118881...',
    '....155..551....', '....144..441....', '...1444..4441...',
]
LEFT = [
    '.....111111.....', '....12222221....', '...1223332221...',
    '...1233332221...', '...1444432221...', '...1441442221...',
    '..14444444221...', '...154444551....', '....1555551.....',
    '.....144441.....', '....14664441....', '....144464441...',
    '....145454441...', '....145454441...', '....145454441...',
    '.....5544441....', '....17777771....', '....17977771....',
    '....17797771....', '....17777771....', '....18811881....',
    '.....55.551.....', '.....44.441.....', '....4444441.....',
]
def frame(rows, step=0):
    assert len(rows) == 24 and all(len(row) == 16 for row in rows)
    pixels = [[0]*16 for _ in range(32)]
    for y, row in enumerate(rows):
        for x, value in enumerate(row):
            pixels[y+5][x] = 0 if value == '.' else int(value, 16)
    # Hand-authored alternating foot placement, keeping each 16x32 frame bounded.
    if step:
        foot = 5 if step == 1 else 9
        for x in range(foot, foot+3): pixels[29][x] = 4
        for x in range(foot, foot+3): pixels[28][x] = 5
    return pixels
frames = [frame(FRONT), frame(BACK), frame(LEFT), frame(FRONT,1), frame(FRONT,2),
          frame(BACK,1), frame(BACK,2), frame(LEFT,1), frame(LEFT,2)]
def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind+data))
raw = b''.join(b'\0' + bytes(v for f in frames for v in f[y]) for y in range(32))
png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>2I5B',144,32,8,3,0,0,0))
png += chunk(b'PLTE', bytes(c for rgb in COLORS for c in rgb))
png += chunk(b'tRNS', b'\0'+b'\xff'*15) + chunk(b'IDAT',zlib.compress(raw)) + chunk(b'IEND', b'')
target = ROOT/'graphics/object_events/pics/people/carl/walking.png'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(png)
(ROOT/'graphics/object_events/palettes/carl.pal').write_text(
    'JASC-PAL\n0100\n16\n'+'\n'.join(' '.join(map(str, rgb)) for rgb in COLORS)+'\n')
