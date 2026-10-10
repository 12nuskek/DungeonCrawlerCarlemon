"""Continuous ordinary inputs; old contract wrappers/claims are never called."""
from pathlib import Path
import importlib.util,json
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def routes():
 fresh=(ROOT/'docs/evidence/floor1/g01e/verified-partial-live/fresh-trial/input.route').read_text().splitlines()
 fresh=fresh[:fresh.index('flag 37 1')+1];fresh=[x for x in fresh if x!='snapshot']
 def wrap(lines,name,start,end):
  i=lines.index(start);j=lines.index(end)+1
  return lines[:i]+['phase begin '+name]+lines[i:j]+['phase end '+name]+lines[j:]
 fresh=wrap(fresh,'trial','engage 3600','flag 37 1')
 # The face direction preceding engage is ordinary, without party/reward mutation.
 fresh=wrap(fresh,'guide-initial','step 400 0 guide-rest.ppm','uses 8 40 2 40')
 fresh=wrap(fresh,'supply','step 400 0 supply.ppm','item 13 2')
 # Begin before A can execute the source mutation, rather than at capture.
 for name,capture in [('guide-initial','guide-rest'),('supply','supply'),('note','note')]:
  if name=='note':fresh=wrap(fresh,name,'step 400 0 note.ppm','flag 36 1')
  i=fresh.index('phase begin '+name);fresh.pop(i);fresh.insert(i-1,'phase begin '+name)
 fresh.insert(fresh.index('ready')+1,'phase end boot')
 live=module('co_route_live',ROOT/'scripts/floor1/live-route.py');geo=module('co_route_geometry',ROOT/'scripts/floor1/relocation-graybox.py')
 spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
 r=live.Route(spec,geo,'quiet',(10,7),1,7);r.face=128
 r.anchor('rack');r.lines.append('phase begin scrap');r.talk(128,'scrap-box');r.lines+=['phase end scrap','item 378 2','item 13 2','flag 39 1']
 r.lines += ['phase begin potion','step 1 8 -','step 120 0 -','co start 0','step 1 128 -','step 20 0 -','co start 1','step 1 1 -',
  'wait-task bag 3600','co bag-item','step 1 1 -','step 12 0 -','wait-task field-context 3600','co potion-use','step 1 1 -','step 12 0 -',
  'wait-task party 3600','step 1 128 -','step 40 0 -','co potion-recipient','step 1 1 -','wait-task healed 3600','co potion-healed',
  'step 40 0 field-potion.ppm','return-field','ready','phase end potion','item 13 1']
 r.anchor('guide');r.lines.append('phase begin guide-posttrial');r.talk(128,'guide-posttrial');r.lines+=['phase end guide-posttrial','duo healthy','uses 8 40 2 40']
 r.anchor('arrival');r.anchor('guard')
 patrol=(ROOT/'scripts/contracts/f1-g01e-guard-first-current.route').read_text().splitlines()
 patrol=patrol[patrol.index('mutation guard'):patrol.index('checkpoint final')]
 # Preserve all reviewed physical legs, including the final guide visit; discard
 # staged wrappers and old fixed wounded/friendship assertions, not inputs.
 allowed=('step ','expect ','engage ','pilot ','dialog ','measure ','flag ','item ','uses ')
 body=[];phase=None
 for x in patrol:
  if x.startswith('mutation '):
   if phase:body.append('phase end '+phase)
   value=x.split()[1];phase=value if value!='heal' else None
   if phase:body.append('phase begin '+phase)
   continue
  if x.startswith('checkpoint '):
   if phase:body.append('phase end '+phase);phase=None
   continue
  if x.startswith('step 400 0 guide-'):
   name={'guide-1.ppm':'guide-guard','guide-2.ppm':'guide-howler','guide-preboss.ppm':'guide-preboss'}[x.split()[3]]
   # The preceding ordinary A is the mutation edge.
   previous=body.pop();assert previous=='step 1 1 -';body+=['phase begin '+name,previous];phase=name
  if x=='ready' or x=='duo healthy' or x.startswith(allowed):body.append(x)
 # close remaining guide (normally its checkpoint already closed it)
 if phase:body.append('phase end '+phase)
 # Field stability in the host enforces full repeat preservation throughout.
 r.lines+=body
 boss=live.Route(spec,geo,'boss',(8,7),1,7,True);boss.face=128
 boss.lines+=['ready','phase begin boss','step 1 128 -','step 40 0 -','engage 3600','step 1200 0 warden-start.ppm',
  'co boss-start','pilot fortify 30000','step 600 0 warden-result.ppm','dialog 6000','ready','phase end boss']
 boss.lines+=['phase begin boss-repeat','step 1 128 -','step 40 0 -','step 1 1 -','step 400 0 -','pages warden-resolved DCC_Live_Boss_Text_Won','dialog 3600','ready','phase end boss-repeat']
 boss.anchor('stairs')
 for name,no in [('stairs-no',True),('stairs-yes',False)]:
  boss.lines+=['phase begin '+name,'step 1 128 -','step 40 0 -','step 1 1 -','step 400 0 -',
   'pages '+name+' DCC_F1D1Warden_StairsText','co yesno','step 40 0 '+name+'-choice.ppm']
  if no:boss.lines+=['step 1 128 -','step 20 0 -','co choice 1']
  else:boss.lines+=['co choice 0']
  boss.lines+=['step 1 1 -','step 400 0 -']
  if no:boss.lines+=['pages stairs-cancelled DCC_Boss_Text_StairsCancel','dialog 3600','ready','co answer 0']
  else:boss.lines+=['ready','co answer 1'];boss.key='checkpoint';boss.pos=(4,4)
  boss.expect();boss.lines+=['phase end '+name]
 boss.anchor('review');boss.step(1,128);boss.step(40);boss.step(1,1);boss.step(400)
 boss.lines+=['pages opening-checkpoint DCC_F1D1Checkpoint_ReviewText','dialog 3600','ready']
 # Start remembers Bag cursor1. Move once down to the source Save entry2.
 boss.lines+=['phase begin save','step 1 8 -','step 120 0 -','co start 1','step 1 128 -','step 20 0 -','co start 2','step 1 1 -',
  'co save-ready','step 1 1 -','co save-success','step 1 0 saved-success.ppm','step 600 0 -','ready','phase end save','step 1 0 saved.ppm','quit']
 opening='\n'.join(fresh+r.lines+boss.lines)+'\n'
 cold='\n'.join(['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -',
  'step 600 0 cold.ppm','ready','expect 35 4 8 6 7','co cold-verify','quit'])+'\n'
 return {'opening':opening,'cold':cold}
