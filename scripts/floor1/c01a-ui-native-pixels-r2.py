"""Read actual emulator RGB captures; verify native glyphs and unchanged pixels."""
from pathlib import Path
import re,json,hashlib,importlib.util
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-action-hints-r2-20261010')
def glyph_mask(text,width):
    source=(ROOT/'engine/src/fonts.c').read_text();widths=list(map(int,re.findall(r'\d+',re.search(r'gFontNarrowLatinGlyphWidths\[\] = \{(.*?)\};',source,re.S)[1])))
    charmap={c:int(h,16) for c,h in re.findall(r"^'([^']*)'\s*=\s*([0-9A-Fa-f]+)",(ROOT/'engine/charmap.txt').read_text(),re.M)}
    atlas=Image.open(ROOT/'engine/graphics/fonts/latin_narrow.png');mask=bytearray(width*16);pen=0
    for c in text:
        g=charmap[c];w=widths[g];assert pen+w<=width
        for y in range(15):
            for x in range(w):
                value=atlas.getpixel((16*(g%16)+x,16*(g//16)+y));assert value in (0,1,2,3)
                if value==3:value=0 # Native sFontHalfRowOffsets maps box3 to background0.
                mask[(y+1)*width+pen+x]=value
        pen+=w
    return bytes(mask),pen

def check_glyph(path,text,box):
    image=Image.open(path).convert('RGB');x,y,w,h=box;actual=image.crop((x,y,x+w,y+h)).tobytes();mask,advance=glyph_mask(text,w)
    colors={i:actual[3*mask.index(i):3*mask.index(i)+3] for i in (0,1,2)};assert len(set(colors.values()))==3,(path,text,'Native three text colors missing')
    expected=b''.join(colors[i] for i in mask);assert expected==actual,(path,text,'Native glyph bitmap/window mismatch')
    return dict(text=text,advance=advance,box=box,RGB_SHA256=hashlib.sha256(actual).hexdigest(),actual_native_pixels_match_source=True)

def verify():
    for case in ['baseline','candidate']:assert json.loads((OUT/case/'runtime-result.json').read_text())['PASS']
    shots={'carl-strike':'ONE FOE','carl-brace':'SELF DEF+','carl-return':'ONE FOE','donut-spark':'BOTH FOES','donut-weaken':'ALL FOES ATK-','donut-return':'BOTH FOES','spark-one':'BOTH FOES','spark-empty':'BOTH FOES','spark-empty-return':'BOTH FOES','weaken-after-empty':'ALL FOES ATK-'}
    glyphs={}
    for name,hint in shots.items():
        glyphs[name]=dict(label=check_glyph(OUT/'candidate'/(name+'.ppm'),'USES',(168,120,32,16)),hint=check_glyph(OUT/'candidate'/(name+'.ppm'),hint,(168,136,64,16)),baseline_label=check_glyph(OUT/'baseline'/(name+'.ppm'),'PP',(168,120,32,16)))
        # Native current/max numbers must be pixel-identical, including zero.
        a=Image.open(OUT/'baseline'/(name+'.ppm')).convert('RGB');b=Image.open(OUT/'candidate'/(name+'.ppm')).convert('RGB')
        assert a.crop((200,120,232,136)).tobytes()==b.crop((200,120,232,136)).tobytes()
    baseline=sorted((OUT/'baseline').glob('battle-*.ppm'));candidate=sorted((OUT/'candidate').glob('battle-*.ppm'));assert len(baseline)==len(candidate)
    differs=0;outside=0;matched=0;allhash=hashlib.sha256()
    for pa,pb in zip(baseline,candidate):
        assert pa.name==pb.name;a=Image.open(pa).convert('RGB');b=Image.open(pb).convert('RGB');aa=a.tobytes();bb=b.tobytes()
        if aa!=bb:differs+=1
        # Only the existing authored PP label and type pane may change pixels.
        for y in range(160):
            ranges=[(0,168),(200,240)] if 120<=y<136 else ([(0,168),(232,240)] if 136<=y<152 else [(0,240)])
            for lo,hi in ranges:
                sa=aa[3*(y*240+lo):3*(y*240+hi)];sb=bb[3*(y*240+lo):3*(y*240+hi)]
                assert sa==sb,(pa.name,y,lo,hi,'Unexpected pixels outside authored panes')
                matched+=hi-lo;allhash.update(sa)
    return dict(PASS=True,scope='Actual native emulator RGB/source glyph masks and every frame outside existing label/type panes; not human comprehension/perceptual playback',frames=len(baseline),frames_with_authored_pane_difference=differs,all_other_pixels_equal=matched,matched_RGB_SHA256=allhash.hexdigest(),actual_glyph_cases=glyphs,current_max_number_pixels_identical=True,non_authored_fallback_scope='Existing offline all65536 helper/native-fallback pane proof reused unchanged; no fabricated gameplay move.')
if __name__=='__main__':
    r=verify();(OUT/'actual-pixel-proof.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='actual_glyph_cases'},indent=2))
