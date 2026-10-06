"""Export approved native battle masters and cleaned native exploration pixels.

Source, conversion recipe and approvals: docs/art-references/README.md.
Battle poses are static; duplicated frames satisfy upstream animation contracts.
"""
from pathlib import Path
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/art-references/native-candidates/assets'
TARGET = ROOT / 'engine/graphics/dcc'

def export():
    for name in ('carl', 'donut'):
        destination = TARGET / name
        for source in (SOURCE / name).iterdir():
            if source.suffix in ('.png', '.pal'):
                shutil.copyfile(source, destination / source.name)
        front = Image.open(destination / 'front.png')
        small = front.resize((32, 32), Image.Resampling.NEAREST)
        icon = Image.new('P', (32, 64), 0)
        icon.putpalette(front.getpalette())
        icon.paste(small, (0, 0))
        icon.paste(small, (0, 32))
        icon.save(destination / 'icon.png', bits=4, transparency=0)

def export_world():
    masters = ROOT / 'scripts/content/masters'
    for name, frames, height, target in (
        ('carl', ['down', 'up', 'left', 'down-1', 'down-2', 'up-1', 'up-2', 'left-1', 'left-2'], 32,
         ROOT / 'engine/graphics/object_events/pics/people/carl/walking.png'),
        ('donut', ['down', 'up', 'left'], 16, TARGET / 'donut/overworld.png'),
    ):
        palette = Image.open(SOURCE / name / 'front.png').getpalette()
        atlas = Image.new('P', (16 * len(frames), height), 0)
        atlas.putpalette(palette)
        for index, frame in enumerate(frames):
            rows = (masters / f'{name}-{frame}.txt').read_text().splitlines()
            assert len(rows) == height and all(len(row) == 16 for row in rows)
            pixels = [0 if c == '.' else int(c, 16) for row in rows for c in row]
            tile = Image.new('P', (16, height), 0)
            tile.putpalette(palette)
            tile.putdata(pixels)
            atlas.paste(tile, (index * 16, 0))
        atlas.save(target, bits=4, transparency=0)
        shutil.copyfile(SOURCE / name / 'normal.pal',
                        ROOT / f'engine/graphics/object_events/palettes/{name}.pal')

if __name__ == '__main__':
    export()
    export_world()
