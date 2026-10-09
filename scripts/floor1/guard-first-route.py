"""Freeze original Guard-first offensive route plus measured approach, no exploration."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def generate():
    historical=(ROOT/'docs/evidence/floor1/g01e/verified-partial-live/guard-first/input.route').read_text().splitlines()
    # Original Save at Howler is replaced by the single final approach Save.
    lines=historical[:historical.index('step 1 8 -',9)]
    lines[8]='step 600 0 boot.ppm'
    pending=['flag 46 0','flag 47 0','flag 48 0','flag 49 0','flag 2138 0','flag 2139 0']
    lines[9:9]=['ready','checkpoint boot','flag 2135 1','growth 9 495 0 9 805 0','duo healthy','uses 8 40 2 40','item 13 1','item 378 2','money remember']+pending
    i=lines.index('step 1 128 -',9);lines[i:i]=['mutation guard']
    i=lines.index('flag 2136 1');lines[i+1:i+1]=['checkpoint guard-win','flag 2137 0','growth 10 627 0 9 937 0','money gain 320','money remember','item 13 1','item 378 2']+pending
    i=lines.index('flag 2137 1');lines[i+1:i+1]=['checkpoint howler-win','flag 2136 1','growth 11 748 0 10 1058 0','money gain 360','money remember','item 13 1','item 378 2']+pending
    i=lines.index('engage 3600',lines.index('flag 2136 1')+1);lines[i-2:i-2]=['mutation howler']
    # Distinct actual captures, preserve original input cadence.
    rest=0;battle=0
    for i,line in enumerate(lines):
        if line=='step 1200 0 battle-start.ppm':battle+=1;lines[i]=f'step 1200 0 {"guard" if battle==1 else "howler"}-start.ppm'
        if line=='step 600 0 battle-result.ppm':lines[i]=f'step 600 0 {"guard" if battle==1 else "howler"}-victory.ppm'
        if line=='step 400 0 guide-rest.ppm':rest+=1;lines[i]=f'step 400 0 guide-{rest}.ppm'
    for who in ('guard','howler'):
        start=lines.index('measure start '+who+'-out');stop=lines.index('measure stop',start)
        lines[stop+1:stop+1]=['mutation heal']
        end=lines.index('uses 8 40 2 40',stop);lines[end+1:end+1]=['checkpoint guide-'+who,'xp remember']+pending
        back=lines.index('measure start '+who+'-back');stop=lines.index('measure stop',back)
        # Real repeat dialogue at the returned actor, no walking or new battle.
        repeat=['no-battle start','step 1 128 -','step 40 0 -','step 1 1 -',f'step 400 0 {who}-resolved.ppm','dialog 3600','ready','step 40 0 -','xp same','money same','no-battle end','checkpoint '+who+'-repeat']
        lines[stop+1:stop+1]=repeat+pending
    spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());geometry=module('gf_geometry',ROOT/'scripts/floor1/relocation-graybox.py');routes=module('gf_routes',ROOT/'scripts/floor1/live-route.py')
    r=routes.Route(spec,geometry,'field',(51,27),1,7)
    r.lines+=['measure start preboss-out'];r.anchor('quiet_door');r.anchor('guide');r.lines+=['measure stop','mutation heal'];r.talk(128,'guide-preboss');r.lines+=['duo healthy','uses 8 40 2 40','checkpoint guide-preboss','measure start preboss-back'];r.anchor('arrival');r.lines+=['approach'];r.anchor('warden_door');r.anchor('warden');r.lines+=['measure stop'];r.step(40,0,'approach.ppm')
    r.lines+=['checkpoint final','growth 11 748 0 10 1058 0','duo healthy','uses 8 40 2 40','item 13 1','item 378 2','flag 2135 1','flag 2136 1','flag 2137 1','xp same','money same']+pending
    r.save();r.lines=[x for x in r.lines if x!='snapshot'];r.lines+=['checkpoint saved','growth 11 748 0 10 1058 0','duo healthy','uses 8 40 2 40','item 13 1','item 378 2','xp same','money same']+pending
    lines+=r.lines+['quit']
    cold=['cold-approach']+historical[:9];cold[-1]='step 600 0 cold.ppm'
    cold+=['ready','checkpoint boot','expect 35 3 8 7 7','growth 11 748 0 10 1058 0','duo healthy','uses 8 40 2 40','item 13 1','item 378 2','flag 2135 1','flag 2136 1','flag 2137 1']+pending+['checkpoint cold','quit']
    assert lines.count('pilot offensive 36000')==2 and lines.count('engage 3600')==2
    assert not any('potion-once' in x or 'snapshot'==x for x in lines)
    return '\n'.join(lines)+'\n','\n'.join(cold)+'\n'
if __name__=='__main__':
    route,cold=generate();(ROOT/'scripts/contracts/f1-g01e-guard-first-current.route').write_text(route);(ROOT/'scripts/contracts/f1-g01e-guard-first-current-cold.route').write_text(cold)
