"""Actual completed r3 pair pixels; corrected native atlas rule from reviewed r2."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
if __name__=='__main__':
    s=importlib.util.spec_from_file_location('c01r3pixels',ROOT/'scripts/floor1/c01a-ui-native-pixels-r2.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.OUT=OUT
    r=m.verify();(OUT/'actual-pixel-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='actual_glyph_cases'},indent=2))
