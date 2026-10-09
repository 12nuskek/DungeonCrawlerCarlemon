"""Frozen ordinary walking route: equivalent scenes, pillar collision, no battle."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def build():
    spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    g=module('v01_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
    route=module('v01_route',ROOT/'scripts/floor1/live-route.py').Route(spec,g,'boss',(8,7),1,7)
    route.lines=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -',
                 'step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 boot.ppm','ready',
                 'expect 35 3 8 7 7','preserve start','scene boot']
    def view(label):
        route.step(40,0,label+'.ppm');route.lines+=['ready','scene '+label];route.expect()
    route.anchor('arrival')
    route.anchor('junction');view('junction')
    route.lines+=['record start'];route.follow((26,24));route.follow((34,24));route.follow((29,26))
    # Existing blocking pillar edge at30,26; real right input must not move.
    route.step(24,16,'pillar-blocked.ppm');route.face=16;route.lines+=['ready'];route.expect()
    route.anchor('junction');route.lines+=['record stop'];view('junction-return')
    route.anchor('quiet_door');view('quiet-door')
    route.anchor('guide');view('quiet-guide')
    route.follow((5,7));view('quiet-mat')
    route.anchor('arrival');view('safe-doorway')
    route.follow((37,28));view('safe-approach')
    route.anchor('workshop_door');view('workshop-door')
    route.anchor('workbench');view('workshop-bench')
    route.anchor('cache');view('workshop-cache')
    route.anchor('arrival');view('optional-cue')
    route.follow((45,42));view('optional-approach')
    route.follow((43,42));view('final')
    route.lines+=['preserve check','quit']
    target=ROOT/'scripts/contracts/f1-v01-environment.route';target.write_text('\n'.join(route.lines)+'\n')
    print('Frozen',len(route.lines),'commands; final',route.key,route.pos)
if __name__=='__main__':build()
