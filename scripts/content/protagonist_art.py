"""Export the approved S02 native battle masters; exploration integration pending.

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

if __name__ == '__main__':
    export()
