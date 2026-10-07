#!/usr/bin/env python3
"""Meaningful negative cache test plus complete clean-archive byte inventory."""
import hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=root)
assert not git('status','--porcelain').strip(),'Commit first'
revision=git('rev-parse','HEAD').decode().strip();out=Path(tempfile.mkdtemp(prefix='provenance-',dir=root/'artifacts/floor1/g01'))
loader=importlib.util.spec_from_file_location('snapshot',root/'scripts/floor1/committed-snapshot.py');snap=importlib.util.module_from_spec(loader);loader.loader.exec_module(snap)
cache=out/'dirty-cache';(cache/'engine/src').mkdir(parents=True)
seed=cache/'engine/src/untracked_cache_contaminant.c';seed.write_text('#error UNTRACKED_CACHE_CONTAMINATION\n')
rejected=False
try:snap.snapshot(root,revision,out/'must-not-build',str(cache))
except ValueError as error:rejected=True;message=str(error)
assert rejected and not (out/'must-not-build').exists() and seed.read_text()=='#error UNTRACKED_CACHE_CONTAMINATION\n'
clean=out/'committed';snap.snapshot(root,revision,clean)
assert not (clean/'engine/src/untracked_cache_contaminant.c').exists()
tracked=git('ls-tree','-r','--name-only',revision,'engine').decode().splitlines();actual=sorted(str(p.relative_to(clean)) for p in (clean/'engine').rglob('*') if p.is_file());assert actual==sorted(tracked)
# Git's blob hash verifies all source bytes, not merely a file count or suffix list.
entries=git('ls-tree','-r',revision,'engine').decode().splitlines()
for row in entries:
    meta,path=row.split('\t');blob=meta.split()[2]
    assert subprocess.check_output(['git','hash-object',str(clean/path)],cwd=root,text=True).strip()==blob,path
c_sources=[p for p in actual if p.startswith('engine/src/') and p.endswith('.c')]
result={'tested_source':revision,'seed':'engine/src/untracked_cache_contaminant.c','negative_result':'dirty optional engine cache rejected before snapshot/make; seed preserved','message':message,'clean_engine_files':len(actual),'clean_c_sources':len(c_sources),'all_engine_blob_hashes_match_commit':True,'cached_engine_inputs_copied':0,'runtime':'N/A tool provenance; actual clean diagnostic build checked separately'}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print('Evidence:',out);print(json.dumps(result))
assert not git('status','--porcelain').strip()
