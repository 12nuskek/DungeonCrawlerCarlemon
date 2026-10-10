"""Inert read-only fixtures reject changes beyond the reviewed two literals."""
from pathlib import Path
import importlib.util,json,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
OUT=Path('/workspace/scratch/c01a-journal-admission-r3-20261010')
s=importlib.util.spec_from_file_location('narrativeProof',ROOT/'scripts/floor1/journal-legacy-reference-equivalence.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
real=m.git;captured={}
def recording(root,*args):
    result=real(root,*args);captured[args]=result;return result
m.git=recording;positive=m.verify(ROOT);m.git=real
actual=(ROOT/m.FILE).read_text();rejected=[]
with tempfile.TemporaryDirectory(dir=OUT,prefix='narrative-inert-') as name:
    root=Path(name);path=root/m.FILE;path.parent.mkdir(parents=True)
    cases={
      'extra_literal_block':lambda t:t.replace('AI: A staircase. You earned this one.','AI: Changed staircase.'),
      'changed_instruction':lambda t:t.replace('\tlockall','\treleaseall',1),
      'added_block':lambda t:t+'\nUnreviewed_Block:\n\tend\n',
      'deleted_block':lambda t:t.replace('DCC_Boss_Text_Defeat:', 'Removed_Text_Defeat:'),
      'instruction_in_reviewed_literal':lambda t:t.replace('DCC_Boss_Text_Intro:\n','DCC_Boss_Text_Intro:\n\tend\n'),
    }
    for case,change in cases.items():
        path.write_text(change(actual));m.git=lambda root,*args:captured[args]
        try:m.verify(root)
        except AssertionError:rejected.append(case)
        else:raise AssertionError('Wrong source accepted '+case)
    path.write_text(actual)
    for case in ('main_mismatch','accepted_origin_mismatch','changed_mode','changed_type','added_entry','deleted_entry','other_entry_changed'):
        values=dict(captured)
        if case in ('main_mismatch','accepted_origin_mismatch'):
            key=('show',(m.MAIN if case=='main_mismatch' else m.ORIGIN)+':'+m.FILE);values[key]+=b'\n'
        else:
            key=next(k for k in values if k[:3]==('ls-tree','-r','-t') and k[3]=='HEAD');text=values[key].decode();rows=text.splitlines()
            target=next(i for i,line in enumerate(rows) if line.endswith('\t'+m.FILE))
            if case=='changed_mode':rows[target]=rows[target].replace('100644','100755',1)
            elif case=='changed_type':rows[target]=rows[target].replace(' blob ',' tree ',1)
            elif case=='added_entry':rows.append(rows[target].replace(m.FILE,m.FILE+'.extra'))
            elif case=='deleted_entry':rows.pop(target)
            else:
                i=next(i for i,line in enumerate(rows) if ' blob ' in line and not line.endswith('\t'+m.FILE));metadata,p=rows[i].split('\t');parts=metadata.split();parts[2]='0'*40;rows[i]=' '.join(parts)+'\t'+p
            values[key]=('\n'.join(rows)+'\n').encode()
        m.git=lambda root,*args:values[args]
        try:m.verify(root)
        except AssertionError:rejected.append(case)
        else:raise AssertionError('Wrong inventory accepted '+case)
m.git=real;assert len(rejected)==12
receipt={'PASS':True,'no_emulator':True,'actual_source_equivalence':positive,'negative_cases_rejected':rejected,'historical_checker_unchanged':True}
(OUT/'narrative-reference-negative-proof.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PASS real source proof and12 inert source/inventory negatives')
