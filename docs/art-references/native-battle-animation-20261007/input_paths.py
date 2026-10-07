"""Resolve existing repository art by relative path; no copied masters required."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
REFS = json.loads((ROOT / 'input-references.json').read_text())
def source(name):
    return ROOT / REFS['sources'][name]
def baseline(name):
    return ROOT / REFS['baselines'][name]
