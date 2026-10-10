"""Separately named ordinary route; historical inputs remain immutable."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def routes():
    old=module('gc_old_route',ROOT/'scripts/floor1/continuous-opening-route.py').routes()
    lines=old['opening'].splitlines()
    a=lines.index('phase begin potion');b=lines.index('item 13 1',a)+1
    del lines[a:b]
    lines=lines[:lines.index('phase end guide-guard')+1]
    lines=[x for x in lines if x!='item 13 1'] # Actual audited consumption determines inventory.
    a=lines.index('phase begin guard');b=lines.index('phase end guard')
    assert lines[a:b].count('pilot offensive 36000')==1
    lines[a:b]=[x.replace('pilot offensive 36000','pilot donut-heal 36000') for x in lines[a:b]]
    # Native Save entry2, with no preceding field Start menu to change cursor0.
    lines+=['duo healthy','uses 8 40 2 40','expect 35 1 4 5 7','phase begin save',
      'step 1 8 -','step 120 0 -','co start 0','step 1 128 -','step 20 0 -','co start 1',
      'step 1 128 -','step 20 0 -','co start 2','step 1 1 -','co save-ready',
      'step 1 1 -','co save-success','step 1 0 saved-success.ppm','step 600 0 -',
      'ready','phase end save','step 1 0 saved.ppm','quit']
    cold=old['cold'].replace('expect 35 4 8 6 7','expect 35 1 4 5 7')
    return {'opening':'\n'.join(lines)+'\n','cold':cold}
