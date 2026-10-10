"""New corrected claims only; preserves C01a process1 STOP121 and its wrapper."""
from pathlib import Path
import argparse,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-action-hints-r2-20261010')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['baseline','candidate']);case=p.parse_args().case
    assert json.loads((OUT/'freeze.json').read_text())['first_failure_stop']
    s=importlib.util.spec_from_file_location('r2prior',ROOT/'scripts/test-f1-c01a-ui.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    m.OUT=OUT;m.run(case)
