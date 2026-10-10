"""Reviewed exact projection of two accepted literal narrative blocks."""
from pathlib import Path
import hashlib,re,subprocess
BASE='ce43420b1c76210f0fa4aaee18c0e195b9354b2d'
MAIN='bdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7'
ORIGIN='e5032830315e162d65dbe66cf698153333b60618'
FILE='engine/data/maps/DCC_Boss/scripts.inc'
LABELS=('DCC_Boss_Text_Intro','DCC_Boss_Text_Prepared')
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root)
def verify(root):
    names=['engine/data/maps/DCC_'+s for s in ('Entrance','Vestibule','Service','Corridor','Boss','Exit')]
    def tree(rev):
        return dict((line.split('\t')[1],line.split('\t')[0]) for line in git(root,'ls-tree','-r','-t',rev,'--',*names).decode().splitlines() if any(line.split('\t')[1].startswith(n) for n in names))
    old,current=tree(BASE),tree('HEAD');assert old.keys()==current.keys()
    assert all(old[n].split()[:2]==current[n].split()[:2] for n in old)
    assert [n for n in old if ' blob ' in old[n] and old[n]!=current[n]]==[FILE]
    assert [n for n in old if ' tree ' in old[n] and old[n]!=current[n]]==[str(Path(FILE).parent)]
    before=git(root,'show',BASE+':'+FILE).decode();actual=(root/FILE).read_text()
    assert actual==git(root,'show',MAIN+':'+FILE).decode()==git(root,'show','HEAD:'+FILE).decode()==git(root,'show',ORIGIN+':'+FILE).decode()
    def blocks(raw):
        starts=list(re.finditer(r'^(\w+)::?\s*$',raw,re.M))
        return {m[1]:raw[m.start():starts[i+1].start() if i+1<len(starts) else len(raw)] for i,m in enumerate(starts)}
    a,b=blocks(before),blocks(actual);assert a.keys()==b.keys()
    assert tuple(n for n in a if a[n]!=b[n])==LABELS
    projected=actual
    for name in LABELS:
        assert all(line.lstrip().startswith('.string') for line in b[name].splitlines()[1:] if line.strip())
        assert projected.count(b[name])==1
        projected=projected.replace(b[name],a[name])
    assert projected==before
    return {'PASS':True,'exact_main_narrative_labels':LABELS,'complete_other_legacy_files_and_blocks_exact':True,'whole_file_immutable_base_projection_exact':True,'current_file_SHA256':hashlib.sha256(actual.encode()).hexdigest()}
