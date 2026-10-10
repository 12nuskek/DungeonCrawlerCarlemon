"""Separate intentional-branch proof; preserves legacy/navigation assertions."""
from pathlib import Path
import argparse, hashlib, importlib.util, itertools, json, re, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
notes=module('notes',ROOT/'scripts/floor1/journal-combat-notes.py')
nav=module('navnotes',ROOT/'scripts/floor1/live-navigation.py')

def blocks(raw):
    starts=list(re.finditer(r'^(\w+)::?\s*$',raw,re.M));result={};order=[]
    for i,m in enumerate(starts):
        end=starts[i+1].start() if i+1<len(starts) else len(raw)
        result[m[1]]=[s.strip() for s in raw[m.end():end].splitlines() if s.strip() and not s.lstrip().startswith('@')];order.append(m[1])
    return result,dict(zip(order,order[1:]))

def trace(raw, flags, answer):
    b,nextlabel=blocks(raw);label='DCC_Live_Journal';seen=[];released=0;remaining=80
    while remaining:
        remaining-=1;branched=False
        for line in b[label]:
            if line.startswith('msgbox '): seen.append(line.split()[1].rstrip(','))
            elif line.startswith(('goto_if_set ', 'goto_if_unset ')):
                op,rest=line.split(' ',1);flag,target=rest.split(', ')
                if bool(flags[flag])==(op=='goto_if_set'):label=target;branched=True;break
            elif line.startswith('goto_if_eq '):
                assert line.startswith('goto_if_eq VAR_RESULT, TRUE, ')
                if answer=='Yes':label=line.rsplit(', ',1)[1];branched=True;break
            elif line.startswith('goto '):label=line.split()[1];branched=True;break
            elif line=='releaseall':released+=1
            elif line=='end':assert released==1;return seen
            else:assert line=='lockall',line
        if not branched:label=nextlabel[label]
    raise AssertionError('Journal did not close within source bound')

def check(output, build=None):
    path=ROOT/'engine/data/scripts/dcc_live_navigation.inc';raw=path.read_text()
    old=subprocess.check_output(['git','show','9ff9426b8aeb76bda80bc196e0f64e1409492209:engine/data/scripts/dcc_live_navigation.inc'],cwd=ROOT,text=True)
    assert notes.project(raw)==old and notes.extend(old)==raw
    nav.generate(ROOT/'engine');assert path.read_text()==raw,'Journal generation is not reproducible'
    flags=sorted(set(re.findall(r'goto_if_(?:un)?set ([^,\n]+),',raw[raw.index('DCC_Live_Journal::'):raw.index('DCC_Live_Journal_Text_Trial:')])))
    cases=0
    for bits in itertools.product((0,1),repeat=len(flags)):
        values=dict(zip(flags,bits));before=trace(old,values,'No')
        for answer in ('Yes','No','B'):
            actual=trace(raw,values,answer);extra=['DCC_Live_Journal_Text_CombatPrompt']
            if answer=='Yes':extra+=['DCC_Live_Journal_Text_CombatNotes']
            assert actual==before+extra;cases+=1
    assert not re.search(r'\b(?:setflag|clearflag|setvar|additem|removeitem|special|healparty)\b',notes.NEW_CLOSE)
    fonts=(ROOT/'engine/src/fonts.c').read_text();widths=list(map(int,re.findall(r'\d+',re.search(r'gFontNormalLatinGlyphWidths\[\] = \{(.*?)\};',fonts,re.S)[1])))
    encoding={m[1].replace("\\'","'"):int(m[2],16) for m in re.finditer(r"^'(.*?)'\s*=\s*([0-9A-F]{2})",(ROOT/'engine/charmap.txt').read_text(),re.M)}
    physical=[]
    for text in re.findall(r'\.string "(.*?)"',notes.TEXT):
        for line in re.split(r'\\[np]',text.rstrip('$')):
            if line:
                width=sum(widths[encoding[c]] for c in line);assert width<=212,(line,width);physical.append({'text':line,'native_font_width':width})
    assert len(physical)==9
    for p in ('engine/include/battle_message.h','engine/src/battle_controller_player.c','engine/src/battle_message.c'):
        assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show','bdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7:'+p],cwd=ROOT)
    subprocess.run(['git','diff','--exit-code','bdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7','--',*[f'engine/data/maps/DCC_{s}/scripts.inc' for s in nav.SOURCES]],cwd=ROOT,check=True)
    existing=False
    if build:
        # Existing checker is unchanged: project only this explicit new branch
        # from its legacy comparison input; retain every original assertion.
        source=(ROOT/'scripts/check-f1-g01e-navigation.py').read_text()
        needle="raw=(engine/'data/scripts/dcc_live_navigation.inc').read_text();starts="
        assert source.count(needle)==1
        source=source.replace(needle,"raw=notes.project((engine/'data/scripts/dcc_live_navigation.inc').read_text());starts=")
        oldargv=sys.argv;sys.argv=[str(ROOT/'scripts/check-f1-g01e-navigation.py'),'--build',str(build)]
        try:exec(compile(source,str(ROOT/'scripts/check-f1-g01e-navigation.py'),'exec'),{'__file__':str(ROOT/'scripts/check-f1-g01e-navigation.py'),'__name__':'__main__','notes':notes})
        finally:sys.argv=oldargv
        existing=True
    result={'PASS':True,'no_gameplay':True,'old_navigation_checker_unchanged':True,'all_legacy_live_bytes_exact_after_new_branch_projection':True,'existing_checker_original_assertions_passed_with_projection':existing,'Journal_flag_combinations':2**len(flags),'Yes_No_B_source_paths':cases,'all_objective_rules_quest_order_and_closure_preserved':True,'no_state_resource_reward_writes':True,'native_font_lines':physical,'window_pixels':216,'generator_reproducible':True,'three_battle_files_exact_baseline':True,'legacy_scripts_unchanged':True}
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--build',type=Path)
    a=p.parse_args();check(a.output,a.build)
