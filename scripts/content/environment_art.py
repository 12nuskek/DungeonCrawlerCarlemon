"""Authoritative game export from accepted native PNG masters.

The reference package is partial: its original main sheet and optional packed
output are absent. This exporter needs only the staged accepted PNG masters.
It does not claim source-sheet reproduction or recreate/publish omitted files.
"""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/art-references/environment-native-candidates/native'
PROPS = ['rubble', 'warning_sign', 'workbench', 'quest_tag', 'cache_sealed', 'storage_rack']

def export_props():
    target = ROOT / 'engine/graphics/dcc/environment'
    target.mkdir(parents=True, exist_ok=True)
    for name in PROPS:
        shutil.copyfile(SOURCE / 'world_shared' / (name+'.png'), target / (name+'.png'))

if __name__ == '__main__':
    export_props()
