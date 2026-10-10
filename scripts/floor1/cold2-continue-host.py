"""Same passive observer; restrict mode and bind the separately named cold2 validator."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    s=importlib.util.spec_from_file_location('cold2_original_host',ROOT/'scripts/floor1/conserve-medicine-host.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    code,base=m.generate(git)
    old='if(argc!=5||(strcmp(argv[4],"opening")&&strcmp(argv[4],"cold")))return 2;'
    assert code.count(old)==1
    code=code.replace(old,'if(argc!=5||strcmp(argv[4],"cold"))return 2;')
    old='python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/guard-choice-r2-state.py cold'
    assert code.count(old)==1
    code=code.replace(old,'python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/cold2-continue-state.py cold')
    assert code.count('->runFrame(')==code.count('core->reset(')==1
    assert not any(x in code for x in ('busWrite','loadState','RNG_SEED'))
    return code,base
