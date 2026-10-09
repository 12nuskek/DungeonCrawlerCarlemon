"""Pinned Emerald comparison model; no RNG, state writes or walking-gate changes."""
from pathlib import Path
import hashlib,re
SOURCE=Path(__file__).resolve().parents[2]/'engine/src/pokemon.c'
SOURCE_SHA256='df008d2d381b70f30998e476ed1f7183871580ea037d0fc5832bea11beb9c064'
text=SOURCE.read_text();assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA256
MODIFIERS={}
for name in ('GROW_LEVEL','WALKING'):
 row=re.search(r'\[FRIENDSHIP_EVENT_'+name+r'\]\s*=\s*\{\s*(\d+),\s*(\d+),\s*(\d+)\}',text)
 assert row;MODIFIERS[name]=tuple(map(int,row.groups()))
assert MODIFIERS=={'GROW_LEVEL':(5,3,2),'WALKING':(1,1,1)}
for native in ('if (friendship > 99)','if (friendship > 199)','mod = (150 * mod) / 100;',
               'GetMonData(mon, MON_DATA_POKEBALL, NULL) == ITEM_LUXURY_BALL',
               'GetMonData(mon, MON_DATA_MET_LOCATION, NULL) == GetCurrentRegionMapSectionId()',
               'if (friendship > MAX_FRIENDSHIP)'):
 assert native in text

def target(friendship,*,event,met_location,section,ball,hold_effect=0):
 """One native event's result; walking may legitimately skip it via engine RNG."""
 assert type(friendship) is int and 0<=friendship<=255
 assert event in MODIFIERS and type(section) is int and 0<=section<=255
 assert type(met_location) is int and 0<=met_location<=255 and 0<=ball<=15
 mod=MODIFIERS[event][int(friendship>99)+int(friendship>199)]
 if mod>0 and hold_effect==27:mod=150*mod//100 # native friendship held effect
 value=friendship+mod
 if mod>0:value+=int(ball==11)+int(met_location==section)
 return max(0,min(255,value))

def level_ups(friendship,*,levels,met_location,section,ball,held_item,pokerus):
 """Route restriction remains no held item/no Pokerus; update band each level."""
 assert held_item==0 and pokerus==0,'source EV multipliers'
 assert type(levels) is int and 0<=levels<=100
 for _ in range(levels):
  friendship=target(friendship,event='GROW_LEVEL',met_location=met_location,section=section,ball=ball)
 return friendship
