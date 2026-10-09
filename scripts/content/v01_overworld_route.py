"""Frozen native gait loop and four existing Donut conversations, normal cadence."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def build():
    spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    g=module('character_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
    route=module('character_route',ROOT/'scripts/floor1/live-route.py').Route(spec,g,'boss',(8,7),1,7)
    route.lines=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -',
                 'step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 boot.ppm','ready',
                 'expect 35 3 8 7 7','preserve start']
    route.anchor('arrival');route.anchor('quiet_door');route.follow((2,11));route.step(40,0,'quiet-before.ppm')
    route.lines+=['ready','scene quiet-before','character start','record start directions']
    for label,position in [('north',(2,5)),('east',(9,5)),('south',(9,11)),('west',(2,11))]:
        route.follow(position);route.step(40,0,'carl-'+label+'.ppm');route.lines+=['ready']
    route.lines+=['record stop']
    for label,position,button,facing in [('north',(8,7),128,2),('south',(8,9),64,1),('west',(7,8),16,3),('east',(9,8),32,4)]:
        route.follow(position);route.lines+=['record start talk-'+label,'character talk '+str(facing)]
        # Reuse the existing Route.talk's 1-frame turn/40 idle/A/400 idle and
        # readiness-aware60-frame dialogue pulses without changing its cadence.
        route.talk(button,'talk-'+label)
        route.step(40,0,'donut-'+label+'.ppm');route.lines+=['character talk-check '+str(facing),'record stop','scene donut-'+label]
    route.lines+=['character finish','preserve check','quit']
    (ROOT/'scripts/contracts/f1-v01-overworld.route').write_text('\n'.join(route.lines)+'\n')
    print('Frozen',len(route.lines),'commands; final',route.key,route.pos)
if __name__=='__main__':build()
