"""Frozen native fortify controller plus read-only graphics/state observations."""
from pathlib import Path
import hashlib,importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    def module(name,path):
        s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    code,base=module('battle_visual_prior',ROOT/'scripts/floor1/warden-fairness-host.py').generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='b2030b4da242f14d9993cbb00493dd9bb02c746fc12ce75cd994b11b760f0c71'
    replace=module('battle_visual_replace',ROOT/'scripts/floor1/recovery-host.py').replace_once
    addition=(ROOT/'scripts/floor1/party-resource-canonical.h').read_text()+'\n'+(ROOT/'scripts/floor1/v01-battle-observer.h').read_text()
    code=replace(code,'int main(int argc, char **argv)',addition+'\nint main(int argc, char **argv)')
    code=replace(code,'    FILE *symbols=fopen(argv[3], "r");','    struct BattleVisual visual={0};\n    FILE *symbols=fopen(argv[3], "r");')
    fields={'gSprites':'sprites','gBattlerSpriteIds':'ids','gHealthboxSpriteIds':'healthboxes','sSpriteTileAllocBitmap':'tiles','sSpritePaletteTags':'palettes','sHeapStart':'heapStart','sHeapSize':'heapSize','sDccBattlePoses':'poseState','gPlttBufferUnfaded':'unfaded','gMonSpritesGfxPtr':'gfx'}
    point='        if (!strcmp(symbol,"gTasks")) tasks=addr;'
    code=replace(code,point,point+'\n'+''.join(f'        if (!strcmp(symbol,"{name}")) visual.a.{field}=addr;\n' for name,field in fields.items()))
    point='    while (fscanf(symbols, "%x %c %127s", &addr, &type, symbol)==3) {'
    code=replace(code,point,point+'\n        bv_symbol(&visual,addr,type,symbol);')
    point='    core->runFrame(core); \\\n'
    code=replace(code,point,point+r'''    if(visual.recording){ \
        if(visual.frames>=36000)exit(109); \
        unsigned vr=bv_trace(core,&visual,party,mons,saveptr,save2ptr,mainstate,results,currentMove,attacker,defender,outcome,controls); \
        if(!vr)vr=bv_sample(core,&visual,mainstate,mons,results,animationActive,animationActor,currentMove,pixels,width,height); \
        if(vr){capture("visual-stop.ppm",pixels,width,height);fprintf(stderr,"Battle visual stop reason=%u frame=%u; no further frames\n",vr,visual.frames);printf("result=%u assertions=%u\n",vr,checks);exit(vr);} \
        visual.frames++; \
    } \
''')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=replace(code,point,point+r'''
        if(!strcmp(line,"visual input-exact\n")){
            unsigned sb=core->busRead32(core,saveptr),context=core->busRead32(core,core->busRead32(core,save2ptr)+0xAC);
            unsigned char expected[600],actual[600],ef[300],af[300],eo[1272],ao[1272],ec[4],counter[2];
            if(!fieldLock || !fieldCallback || !scriptStatus || core->busRead8(core,fieldLock) || core->busRead8(core,scriptStatus)!=2
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u) || (core->busRead8(core,mainstate+0x439)&2)
                || core->busRead8(core,count)!=2 || core->busRead8(core,sb+0x234)!=2){result=111;break;}
            for(unsigned i=0;i<600;i++)actual[i]=core->busRead8(core,party+i);
            for(unsigned i=0;i<300;i++)af[i]=core->busRead8(core,sb+0x1270+i);
            for(unsigned i=0;i<1272;i++)ao[i]=core->busRead8(core,sb+0x490+i);
            if(bv_load("expected-party.bin",expected,600)||bv_load("expected-flags.bin",ef,300)||bv_load("expected-owned.bin",eo,1272)
                ||bv_load("expected-context.bin",ec,4)||bv_load("expected-counter.bin",counter,2)
                ||memcmp(actual,expected,600)||memcmp(af,ef,300)||!resource_equal(eo,resource_word(ec),ao,context)
                ||core->busRead16(core,sb+0x13f0)!=(unsigned)(counter[0]|counter[1]<<8)){result=111;break;}
            checks+=4;printf("PASS retained ordinary input exact600 party/count300 flags1272 logical resources/counter; native field ready\n");continue;
        }
        if(!strcmp(line,"visual start\n")){unsigned vr=bv_begin(&visual);if(vr){result=vr;break;}checks++;continue;}
        if(!strcmp(line,"visual ready\n")){
            if(!visual.recording || !(core->busRead8(core,mainstate+0x439)&2) || core->busRead8(core,results+0x13)!=0){result=110;break;}
            visual.enforced=1;checks++;continue;
        }
        if(!strcmp(line,"visual finish\n")){unsigned vr=bv_finish(&visual);if(vr){result=vr;break;}checks+=8;continue;}
''')
    assert code.count('core->runFrame(core);')==1 and 'busWrite' not in code
    return code,base
