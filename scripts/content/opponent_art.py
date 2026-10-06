"""Export the reviewed I01 native masters without recoloring shared consumers.

Source/provenance and deterministic conversion live in docs/art-references.
The runtime exporter copies validated native bytes, never re-quantizes images.
"""
from pathlib import Path
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/art-references/opponent-native-candidates'
NAMES = ('scuttler', 'grub', 'guard', 'howler', 'warden')


def export():
    expected = {}
    for line in (SOURCE / 'SHA256SUMS').read_text().splitlines():
        digest, path = line.split(None, 1)
        expected[path.lstrip('*')] = digest
    shared = ROOT / 'engine/graphics/dcc/shared.pal'
    assert shared.read_bytes() == (SOURCE / 'source/existing-shared.pal').read_bytes()
    for name in NAMES:
        files = ['front.png', 'back.png', 'anim_front.png', 'icon.png', 'normal.pal', 'shiny.pal']
        if name != 'grub':
            files.append('overworld.png')
        for filename in files:
            relative = f'assets/{name}/{filename}'
            src = SOURCE / relative
            assert hashlib.sha256(src.read_bytes()).hexdigest() == expected[relative], relative
            dst = ROOT / 'engine/graphics/dcc' / name / filename
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)


if __name__ == '__main__':
    export()
