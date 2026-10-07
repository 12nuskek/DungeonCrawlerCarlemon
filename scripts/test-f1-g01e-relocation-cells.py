#!/usr/bin/env python3
"""Host check of the exact C relocation functions against all legacy cells.

Real committed legacy geometry/events supply the header adapter. This supplements
GBA controller migration acceptance; it does not prove ARM ABI/spawn/save behavior.
"""
from pathlib import Path
import json,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
assert not git('status','--porcelain'),'Commit first'
head=git('rev-parse','HEAD');spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
source=git('show',head+':engine/src/crawler_save.c')
def function(name, text=source):
    a=text.rfind('\n',0,text.index(name))+1;start=text.index('{',a);depth=1;b=start+1
    while depth:
        if text[b]=='{':depth+=1
        if text[b]=='}':depth-=1
        b+=1
    return text[a:b]+'\n'
code='#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\ntypedef uint8_t u8;typedef int8_t s8;typedef uint8_t bool8;typedef uint16_t u16;typedef int16_t s16;typedef uint32_t u32;\n#define TRUE 1\n#define FALSE 0\n#define WARP_ID_NONE -1\n#define MAPGRID_COLLISION_MASK 0xC00\n#define MAP_GROUP(x) (((x)>>8)&255)\n#define MAP_NUM(x) ((x)&255)\n'
old_names=list(spec['legacy_object_destinations']);layouts=json.loads((ROOT/'engine/data/layouts/layouts.json').read_text())['layouts'];vectors=[];headers=[]
for n,name in enumerate(old_names):code+=f'#define MAP_{name.upper()} {0x2200+n}\n'
for key,m in spec['production_identity_proposal']['maps'].items():code+=f'#define MAP_{m["name"].upper()} {0x2300+m["map_num"]}\n'
code+='struct WarpData {s8 mapGroup,mapNum,warpId;u8 padding;s16 x,y;};\nstruct MapLayout {int32_t width,height;const u16 *map;};\nstruct WarpEvent {s16 x,y;};\nstruct ObjectEventTemplate {s16 x,y;};\nstruct MapEvents {u8 warpCount,objectEventCount;const struct WarpEvent *warps;const struct ObjectEventTemplate *objectEvents;};\nstruct MapHeader {const struct MapLayout *mapLayout;const struct MapEvents *events;};\n'
for n,name in enumerate(old_names):
    model=json.loads((ROOT/'engine/data/maps'/name/'map.json').read_text());layout=next(m for m in layouts if m['name']==name+'_Layout');w,h=layout['width'],layout['height'];raw=(ROOT/'engine'/layout['blockdata_filepath']).read_bytes();words=struct.unpack('<'+'H'*(w*h),raw);actors={(o['x'],o['y']) for o in model['object_events']};warps=model['warp_events']
    code+=f'static const u16 tiles{n}[]={{'+','.join(str(v) for v in words)+'};\n'
    code+=f'static const struct WarpEvent warps{n}[]={{'+','.join('{'+f'{v["x"]},{v["y"]}'+'}' for v in warps)+'};\n'
    code+=f'static const struct ObjectEventTemplate objects{n}[]={{'+','.join('{'+f'{x},{y}'+'}' for x,y in actors)+'};\n'
    code+=f'static const struct MapLayout layout{n}={{{w},{h},tiles{n}}};\nstatic const struct MapEvents events{n}={{{len(warps)},{len(actors)},warps{n},objects{n}}};\n'
    headers.append('{'+f'&layout{n},&events{n}'+'}')
    positions=[(x,y) for y in range(-2,h+2) for x in range(-2,w+2)]+[(-32768,-32768),(32767,32767)]
    for index in [-128,-1,*range(len(warps)),127]:
        for x,y in positions:
            nx,ny=(warps[index]['x'],warps[index]['y']) if 0<=index<len(warps) else (x,y)
            rule=spec['legacy_position_rules'][n];key=rule['new'];dest=spec['maps'][key]['anchors'][rule['fallback_anchor']]
            if n==3 and nx>=8 and 0<=nx<w and 0<=ny<h and not words[ny*w+nx]&0xC00 and (nx,ny) not in actors:dest=spec['maps']['field']['anchors']['howler']
            num=spec['production_identity_proposal']['maps'][key]['map_num'];vectors.append((n,index,x,y,num,*dest))
code+='static const struct MapHeader headers[]={'+','.join(headers)+'};\nstatic unsigned lookups=0;\nstatic const struct MapHeader *Overworld_GetMapHeaderByGroupAndId(u16 group,u16 num){if(group!=34||num>=6)abort();lookups++;return &headers[num];}\n'
code+=function('IsLegacy')+function('LegacyCellLegal')+function('RemapLegacy')
code+='#define ARRAY_COUNT(a) (sizeof(a)/sizeof((a)[0]))\n#define VAR_DCC_LAYOUT_VERSION 0x404E\n'
code+=git('show',head+':engine/src/data/dcc_map_counts.h')
code+='struct SaveAdapter {struct WarpData location,continueGameWarp;u16 mapLayoutId;};\nstatic struct SaveAdapter saveState;\nstatic struct SaveAdapter *gSaveBlock1Ptr=&saveState;\nstatic u16 version;static u8 useContinue;\nstatic u16 VarGet(u16 n){if(n!=0x404E)abort();return version;}\nstatic u32 UseContinueGameWarp(void){return useContinue;}\n'
code+=function('DccIsMap',git('show',head+':engine/src/crawler_identity.c'))+function('IsLive')+function('ValidIdentity')+function('ValidSchema')+function('DccContinueSupported')
code+='static unsigned schemaChecks(void){unsigned n=0,j;const u16 versions[]={0,1,2,65535};for(j=0;j<4;j++){struct SaveAdapter before;memset(&saveState,0,sizeof(saveState));saveState.location.mapGroup=0;saveState.location.mapNum=0;saveState.mapLayoutId=1;version=versions[j];useContinue=0;before=saveState;if(!DccContinueSupported()||memcmp(&before,&saveState,sizeof(before)))abort();n++;saveState.continueGameWarp.mapGroup=0;saveState.continueGameWarp.mapNum=0;useContinue=1;if(!DccContinueSupported())abort();n++;}saveState.location.mapGroup=36;useContinue=0;if(DccContinueSupported())abort();n++;saveState.location.mapGroup=34;saveState.location.mapNum=6;if(DccContinueSupported())abort();n++;saveState.location.mapNum=0;version=2;if(DccContinueSupported())abort();n++;version=0;if(!DccContinueSupported())abort();n++;saveState.location.mapGroup=35;version=0;if(DccContinueSupported())abort();n++;version=1;if(!DccContinueSupported())abort();n++;saveState.location.mapGroup=0;saveState.mapLayoutId=65535;if(DccContinueSupported())abort();n++;printf("PASS %u schema vectors incl stock nonmembers/all four version values; exact C guard bodies; host adapter only\\n",n);return n;}\n'
code+='static const int16_t vectors[][7]={'+','.join('{'+','.join(str(v) for v in row)+'}' for row in vectors)+'};\n'
code+='int main(void){unsigned i;for(i=0;i<sizeof(vectors)/sizeof(vectors[0]);i++){const int16_t *v=vectors[i];struct WarpData w={34,v[0],v[1],0xAB,v[2],v[3]};RemapLegacy(&w);if(w.mapGroup!=35||w.mapNum!=v[4]||w.warpId!=-1||w.padding!=0xAB||w.x!=v[5]||w.y!=v[6]){fprintf(stderr,"vector %u failed\\n",i);return 1;}}if(lookups!=i)return 2;{struct WarpData untouched[]={{-1,-1,-1,0xAB,-1,-1},{0,0,0,0xAB,0,0},{35,1,-1,0xAB,4,5},{34,6,-1,0xAB,4,5},{127,127,127,0xAB,32767,32767}};unsigned j;for(j=0;j<sizeof(untouched)/sizeof(untouched[0]);j++){struct WarpData before=untouched[j];RemapLegacy(&untouched[j]);if(memcmp(&before,&untouched[j],sizeof(before)))return 3;}}if(lookups!=i)return 4;printf("PASS %u relocation vectors +5 nonmember/dummy records; exact C functions; host header adapter only\\n",i);schemaChecks();return 0;}\n'
out=Path(tempfile.mkdtemp(prefix='cells-',dir=ROOT/'artifacts/floor1/g01e'));(out/'tested-commit.txt').write_text(head+'\n');(out/'exact-functions.c').write_text(code)
subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror','-Wno-sign-compare','-fsanitize=address,undefined',str(out/'exact-functions.c'),'-o',str(out/'cells')],check=True)
with (out/'result.log').open('w') as log:subprocess.run([str(out/'cells')],stdout=log,stderr=subprocess.STDOUT,check=True)
(out/'identity.json').write_text(json.dumps(dict(source=head,vectors=len(vectors),nonmembers=5,schema_vectors=15,all_legacy_maps=6,method='Exact committed C function/guard/membership bodies compiled on host against actual old map/collision/object/warp data and generated map-count register, contract expected legal semantic anchors. Address/undefined sanitizers. Supplement only; not GBA ABI/emulator/controller/spawn/ordinary stock-save acceptance.'),indent=2)+'\n')
print(out);print((out/'result.log').read_text().strip())
