"""Separate source-proven effective OAM flip adapter; original STOP host retained."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    p=ROOT/'scripts/floor1/v01-overworld-host.py';s=importlib.util.spec_from_file_location('original_character_host',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    code,base=m.generate(git)
    old='*pose=found;*flip=(core->busRead8(core,sprite+63)&1);'
    assert code.count(old)==1
    code=code.replace(old,'*pose=found;*flip=(attr1>>12)&1;')
    assert 'sprite->oam.matrixNum |= (((hFlip ^ sprite->hFlip) & 1) << 3);' in (ROOT/'engine/src/sprite.c').read_text()
    return code,base
