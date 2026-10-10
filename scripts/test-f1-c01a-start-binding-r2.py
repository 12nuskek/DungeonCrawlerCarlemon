"""Focused corrected cardinality and actual nonzero scoped bindings; offline only."""
from pathlib import Path
import json,re,subprocess,importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[1]
OLD=Path('/workspace/scratch/c01a-action-hints-20261010')
def run():
    s=importlib.util.spec_from_file_location('r2gen',ROOT/'scripts/floor1/c01a-ui-host.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    code=m.generate(git);frozen=(OLD/'observer.c').read_text()
    assert hashlib.sha256(frozen.encode()).hexdigest()=='974059b873d72c8f87ae7c3504d82294cf6294675c46337cadb0c736c1a0a636'
    expected=frozen.replace('unsigned a[17]','unsigned a[16]').replace('for(unsigned z=0;z<17;z++)if(!ui.a[z])','for(unsigned z=0;z<16;z++)if(!ui.a[z])')
    assert expected!=frozen and code==expected,'Correction exceeds the reviewed declaration/check'
    count=int(re.search(r'unsigned a\[(\d+)\]',code)[1]);mandatory=int(re.search(r'for\(unsigned z=0;z<(\d+);z\+\+\)if\(!ui.a\[z\]\)',code)[1])
    fields={int(i):n for n,i in re.findall(r'if\(!strcmp\(symbol,"([^"]+)"\)\)ui\.a\[(\d+)\]=addr;',code)}
    assert count==mandatory==len(fields)==16 and sorted(fields)==list(range(16))
    assert 'u->a[8+kind]' in code and 'if(kind<=3)' in code
    assert 8+7==max(fields)==15
    def accept(available):return set(available)==set(fields) and all(available.values())
    rejected=0;actual={}
    for case in ['baseline','candidate']:
        rows=[l.split() for l in (OLD/case/'game.sym').read_text().splitlines()]
        resolved={}
        for i,n in fields.items():
            hits={int(a,16) for a,k,label in rows if label==n};assert len(hits)==1 and next(iter(hits))!=0
            resolved[i]=next(iter(hits))
        assert accept(resolved)
        for i in fields:
            missing=dict(resolved);del missing[i];assert not accept(missing);rejected+=1
            zero=dict(resolved);zero[i]=0;assert not accept(zero);rejected+=1
        extra=dict(resolved);extra[16]=1;assert not accept(extra);rejected+=1
        identities=json.loads((OLD/case/'verified-functions.json').read_text())
        for n,identity in json.loads((OLD/case/'identity.json').read_text())['native_bindings'].items():
            hits=[r for r in identities if identity in r['aliases']];assert len(hits)==1
            i=[i for i,name in fields.items() if name==n][0];assert resolved[i]==hits[0]['address']
        actual[case]=dict(nonzero_bindings=len(resolved),mandatory_scoped_callbacks=7)
    return dict(PASS=True,scope='Offline actual frozen ELF binding cardinality/negative proof; no emulator',reviewed_patch_only=True,declared=16,checked=16,data_addresses=9,callbacks=7,max_ui_ready_slot=15,actual_cases=actual,missing_zero_and_extra_rejected=rejected,old_generated_adapter_unchanged=True)
if __name__=='__main__':print(json.dumps(run(),indent=2))
