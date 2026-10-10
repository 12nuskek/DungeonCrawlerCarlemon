"""Offline native-font/window fit and source-scope guards; no emulator run."""
from pathlib import Path
import re,json,subprocess,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE='bdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7'
def check():
    text=(ROOT/'engine/src/battle_message.c').read_text()
    strings={n:s for n,s in re.findall(r'const u8 (gText_(?:MoveInterfaceUses|Dcc\w+Hint))\[\] = _\("([^"]+)"\);',text)}
    assert list(strings.values())==['USES','ONE FOE','SELF DEF+','BOTH FOES','ALL FOES ATK-']
    charmap={c:int(h,16) for c,h in re.findall(r"^'([^']*)'\s*=\s*([0-9A-Fa-f]+)", (ROOT/'engine/charmap.txt').read_text(),re.M)}
    widths=list(map(int,re.findall(r'\d+',re.search(r'gFontNarrowLatinGlyphWidths\[\] = \{(.*?)\};',(ROOT/'engine/src/fonts.c').read_text(),re.S)[1])))
    image=Image.open(ROOT/'engine/graphics/fonts/latin_narrow.png')
    fit={}
    for name,s in strings.items():
        pen=0;ink=[]
        for c in s:
            glyph=charmap[c];w=widths[glyph]
            for y in range(15):
                for x in range(w):
                    if image.getpixel(((glyph%16)*16+x,(glyph//16)*16+y)) in (1,2):ink.append((pen+x,1+y))
            pen+=w
        limit=32 if s=='USES' else 64
        assert pen<=limit and ink and max(x for x,y in ink)<limit and max(y for x,y in ink)<16
        fit[name]=dict(text=s,advance=pen,window=[limit,16],ink_bounds=[min(x for x,y in ink),min(y for x,y in ink),max(x for x,y in ink),max(y for x,y in ink)])
    native=['src/data/battle_moves.h','src/data/text/move_descriptions.h','src/battle_bg.c','src/text.c','src/party_menu.c','src/item_menu.c','src/pokemon.c','include/constants/moves.h']
    for path in native:
        assert (ROOT/'engine'/path).read_bytes()==subprocess.check_output(['git','show',BASE+':engine/'+path],cwd=ROOT),path
    controller=(ROOT/'engine/src/battle_controller_player.c').read_text()
    previous=subprocess.check_output(['git','show',BASE+':engine/src/battle_controller_player.c'],cwd=ROOT,text=True)
    def function(source,name):
        start=source.index('static '+('const u8 *' if name=='MoveSelectionGetHint' else 'void ')+name+'(void)\n{')
        # Ignore prototypes.
        start=source.index('\n{',start)
        end=source.index('\n}',start)+2
        return source[start:end]
    # Number rendering remains byte identical. The existing type fallback remains verbatim.
    assert function(controller,'MoveSelectionDisplayPPNumber')==function(previous,'MoveSelectionDisplayPPNumber')
    fallback=previous[previous.index('    txtPtr = StringCopy(gDisplayedStringBattle, gText_MoveInterfaceType);'):]
    fallback=fallback[:fallback.index('\n}')]
    assert fallback in controller
    helper=controller[controller.index('static const u8 *MoveSelectionGetHint(u16 move)\n{'):]
    helper=helper[:helper.index('\n}')]
    assert set(re.findall(r'case (MOVE_\w+):',helper))=={'MOVE_DCC_STRIKE','MOVE_DCC_BRACE','MOVE_DCC_SPARK','MOVE_DCC_WEAKEN'}
    assert 'default: return NULL;' in helper and not re.search(r'(?<![=!<>])=(?!=)',helper)
    refresh=r'            // Refresh only when crossing authored/native label contexts.\n            if \(\(MoveSelectionGetHint\(moveInfo->moves\[previousCursor\]\) != NULL\)\n             != \(MoveSelectionGetHint\(moveInfo->moves\[gMoveSelectionCursor\[gActiveBattler\]\]\) != NULL\)\)\n                MoveSelectionDisplayPPString\(\);\n'
    normalized,n=re.subn(refresh,'',controller);assert n==4
    normalized=normalized.replace('    u8 previousCursor = gMoveSelectionCursor[gActiveBattler];\n','')
    begin=normalized.index('static void HandleInputChooseMove(void)\n{');end=normalized.index('\n}',begin)+2
    pbegin=previous.index('static void HandleInputChooseMove(void)\n{');pend=previous.index('\n}',pbegin)+2
    assert normalized[begin:end]==previous[pbegin:pend], 'Native input, target selection, timing and emissions changed'
    return dict(PASS=True,scope='Offline glyph geometry/source guards; not emulator pixels or runtime acceptance',base=BASE,fit=fit,unchanged_native_files=native,unchanged_number_format=True,unchanged_input_except_context_label_draw=True,native_fallback_verbatim=True)
if __name__=='__main__':print(json.dumps(check(),indent=2))
