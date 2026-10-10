#!/usr/bin/env python3
"""Independent cold-process byte reconstruction. Never deletes originals."""
from pathlib import Path
import importlib.util,json
P=Path(__file__).resolve().parent/'floor1/rgb-preservation.py'
s=importlib.util.spec_from_file_location('rgb_preservation_independent',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
if __name__=='__main__':
    m.require(not (m.OUT/'verification-pass2-private.json').exists(),'independent verification is not repeatable')
    contract=json.loads((m.OUT/'preservation-contract.json').read_text());mapping=json.loads((m.OUT/'representation-mapping-private.json').read_text())
    result=m.verify_all(contract,mapping,m.gzip_blocks,'pass2-independent-gzip')
    m.Budget(m.OUT).json(m.OUT/'verification-pass2-private.json',result)
    print('PASS independent full gzip reconstruction; all originals retained',flush=True)
