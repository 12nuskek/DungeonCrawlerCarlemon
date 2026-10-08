#!/usr/bin/env python3
"""Supplementary exact-source checks; never substitutes for native runtime."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT,text=True).strip()
p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);a=p.parse_args();build=a.build.resolve();source=build/'source';engine=source/'engine'
compiled=(build/'tested-commit.txt').read_text().strip();head=git('rev-parse','HEAD');subprocess.run(['git','diff','--quiet',compiled,head,'--','engine','scripts/floor1/live-navigation.py','scripts/floor1/generate-live-opening.py'],cwd=ROOT,check=True)
nav=module('nav',ROOT/'scripts/floor1/live-navigation.py');original=nav.blocks(engine)
raw=(engine/'data/scripts/dcc_live_navigation.inc').read_text();starts=list(re.finditer(r'^(\w+)::?\s*$',raw,re.M));count=0;preserved_texts=0
for i,m in enumerate(starts):
    end=starts[i+1].start() if i+1<len(starts) else len(raw);block=raw[m.start():end].rstrip()+'\n';old=m[1].replace('DCC_Live_','DCC_',1)
    normalized=re.sub(r'\bDCC_Live_', 'DCC_',block)
    if old not in nav.TEXT:
        assert normalized==original[old],old
        if '.string' in original[old]:preserved_texts+=1
        else:count+=1
    else:assert '.string' in normalized and normalized.count('.string')==1
# All six archived script sources and geometry/save/combat source remain untouched.
base='ce43420b1c76210f0fa4aaee18c0e195b9354b2d'
unchanged=['engine/data/maps/DCC_'+s for s in nav.SOURCES]+['engine/data/layouts','engine/src/crawler.c','engine/src/crawler_save.c','engine/src/data/dcc_opening.h','engine/include/global.h']
subprocess.run(['git','diff','--quiet',base,head,'--',*unchanged],cwd=ROOT,check=True)
tracked=git('ls-tree','-r','--name-only',compiled,'--','engine').splitlines()
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={name:digest(source/name) for name in tracked}
subprocess.run(['python3',str(source/'scripts/floor1/generate-live-opening.py'),'--root',str(source)],check=True)
assert before=={name:digest(source/name) for name in tracked},'Generation changed committed bytes'
# Engine's actual font/window configuration: font normal, x0, spacing0, 27 tiles.
fonts=(engine/'src/fonts.c').read_text();widths=list(map(int,re.findall(r'\d+',re.search(r'gFontNormalLatinGlyphWidths\[\] = \{(.*?)\};',fonts,re.S)[1])))
charmap=(engine/'charmap.txt').read_text();encoding={m[1].replace("\\'","'"):int(m[2],16) for m in re.finditer(r"^'(.*?)'\s*=\s*([0-9A-F]{2})",charmap,re.M)}
menu=(engine/'src/menu.c').read_text();assert re.search(r'sStandardTextBox_WindowTemplates.*?\.width = 27,',menu,re.S)
assert 'printer.x = 0;' in menu and 'printer.letterSpacing = 0;' in menu
line_widths=[]
for label,text in nav.TEXT.items():
    for line in re.split(r'\\[np]',text.replace("\\'","'").rstrip('$')):
        width=sum(widths[encoding[c]] for c in line);assert width<=212,(label,width);line_widths.append(width)
# Compile the actual dispatch function verbatim with signed WarpData fields.
# Exhaust all identities (including negative signed representations) under UBSan.
start=(engine/'src/start_menu.c').read_text();function=re.search(r'static const u8 \*GetDccJournalScript\(void\)\n\{.*?\n\}',start,re.S)[0]
contract=json.loads((source/'scripts/contracts/f1-g01d-relocation.json').read_text());definitions='\n'.join('#define MAP_'+m['name'].upper()+' '+str((35<<8)|m['map_num']) for m in contract['production_identity_proposal']['maps'].values())
c='''#include <stdint.h>
#include <assert.h>
typedef uint8_t u8;
struct Save {struct {int8_t mapGroup, mapNum;} location;} save;
struct Save *gSaveBlock1Ptr=&save;
const u8 DCC_Journal[]={0},DCC_Live_Journal[]={1};
'''+definitions+'\n'+function+'''
int main(void) {
 for(unsigned group=0;group<256;group++)for(unsigned number=0;number<256;number++) {
  save.location.mapGroup=(int8_t)group;save.location.mapNum=(int8_t)number;
  assert(GetDccJournalScript()==(group==35 && number<5?DCC_Live_Journal:DCC_Journal));
 }
 return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='dispatch-',dir=build) as temp:
    d=Path(temp);(d/'check.c').write_text(c);subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-fno-sanitize-recover=all',str(d/'check.c'),'-o',str(d/'check')],check=True);subprocess.run([str(d/'check')],check=True)
result=dict(compiled_source=compiled,runner_source=head,non_text_blocks_identical=count,unchanged_text_blocks_identical=preserved_texts,changed_text_labels=len(nav.TEXT),physical_lines=len(line_widths),maximum_width=max(line_widths),window_width=216,generated_engine_files_identical=len(tracked),dispatch_identities=65536,dispatch_method='Verbatim C, exhaustive host-only UBSan; legacy contexts migrate on Continue, so no claimed legacy runtime fallback.',legacy_and_geometry_save_combat_unchanged=True)
(build/'navigation-source-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
