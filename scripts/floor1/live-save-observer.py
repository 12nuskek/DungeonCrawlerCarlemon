"""Generate a read-only mGBA observer; no game/save writes or injected logic."""
def instrument(code):
    code=code.replace('maplayout=0, addr;', 'maplayout=0, menuCallback=0, fieldCallback=0, fieldLock=0, addr;')
    code=code.replace('fade=0, addr;', 'fade=0, menuCallback=0, fieldCallback=0, fieldLock=0, addr;')
    code=code.replace('        if (!strcmp(symbol,"gMain")) mainstate=addr;', '        if (!strcmp(symbol,"gMain")) mainstate=addr;\n        if (!strcmp(symbol,"CB2_MainMenu")) menuCallback=addr;\n        if (!strcmp(symbol,"CB2_Overworld")) fieldCallback=addr;\n        if (!strcmp(symbol,"sLockFieldControls")) fieldLock=addr;')
    point='        if (!strcmp(line,"quit\\n")) break;'
    assert code.count(point)==1
    addition=r'''
        if (!strncmp(line,"dialog ",7)) {
            unsigned limit,elapsed=0;
            if (!fieldLock || sscanf(line,"dialog %u %c",&limit,&extra)!=1 || limit>36000) {result=40;break;}
            while (elapsed<limit && core->busRead8(core,fieldLock)) {
                if (core->busRead8(core,mainstate+0x439)&2) {result=40;break;}
                core->setKeys(core,elapsed%60==0?1:0);core->runFrame(core);elapsed++;total++;
            }
            core->setKeys(core,0);
            if (result || core->busRead8(core,fieldLock)) {result=40;fprintf(stderr,"Dialog exceeded bound\n");break;}
            checks++;printf("PASS dialog frames=%u\n",elapsed);continue;
        }
        if (!strcmp(line,"ready\n")) {
            if (!fieldLock || !fieldCallback || core->busRead8(core,fieldLock)
                || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u)) {result=40;fprintf(stderr,"Field controls not ready\n");break;}
            checks++;printf("PASS ready\n");continue;
        }
        if (!strcmp(line,"menu\n")) {
            unsigned cb=core->busRead32(core,mainstate+4)&~1u;
            if (!menuCallback || cb!=(menuCallback&~1u)) {result=40;fprintf(stderr,"Not main menu:callback=%x expected=%x\n",cb,menuCallback);break;}
            checks++;printf("PASS menu\n");continue;
        }
        if (!strcmp(line,"snapshot\n")) {
            unsigned sb=core->busRead32(core,saveptr), sb2=core->busRead32(core,save2ptr), first=1;
            printf("STATE {\"group\":%u,\"map\":%u,\"layout\":%u,\"version\":%u,\"loop\":%u,\"pos\":[%d,%d],\"callback\":%u,\"avatar\":%u,\"warps\":[",
                core->busRead8(core,sb+4),core->busRead8(core,sb+5),core->busRead16(core,sb+0x32),core->busRead16(core,sb+0x1438),
                (core->busRead8(core,sb+0x1276)>>1)&1,(short)core->busRead16(core,sb),(short)core->busRead16(core,sb+2),core->busRead32(core,mainstate+4),core->busRead8(core,avatar+5));
            for (unsigned w=0;w<5;w++) {
                unsigned a=sb+4+8*w;
                printf("%s[%d,%d,%d,%d,%d]",w?",":"",(signed char)core->busRead8(core,a),(signed char)core->busRead8(core,a+1),(signed char)core->busRead8(core,a+2),(short)core->busRead16(core,a+4),(short)core->busRead16(core,a+6));
            }
            printf("],\"objects\":[");
            for (unsigned i=0;i<16;i++) {
                unsigned a=objects+36*i;
                if (!(core->busRead8(core,a)&1)) continue;
                printf("%s{\"slot\":%u,\"player\":%u,\"local_id\":%u,\"group\":%u,\"map\":%u,\"gfx\":%u,\"pos\":[%d,%d],\"initial\":[%d,%d],\"previous\":[%d,%d],\"facing\":%u}",first?"":",",i,core->busRead8(core,a+2)&1,core->busRead8(core,a+8),core->busRead8(core,a+10),core->busRead8(core,a+9),core->busRead8(core,a+5),(short)core->busRead16(core,a+16)-7,(short)core->busRead16(core,a+18)-7,(short)core->busRead16(core,a+12)-7,(short)core->busRead16(core,a+14)-7,(short)core->busRead16(core,a+20)-7,(short)core->busRead16(core,a+22)-7,core->busRead8(core,a+24)&15);first=0;
            }
            printf("],\"regions\":{");
            const unsigned addresses[]={sb+0x34,sb+0x238,sb+0x490,sb+0xA30,sb+0xC70,sb+0x1270,sb+0x139C,party,sb2+0xAC};
            const unsigned sizes[]={512,600,0x5A0,0x240,0x600,300,512,200,4};
            const char *labels[]={"map_view","saved_party","inventory_money","saved_objects","templates","flags","vars","live_duo","encryption_key"};
            for (unsigned r=0;r<9;r++) {
                printf("%s\"%s\":\"",r?",":"",labels[r]);
                for (unsigned i=0;i<sizes[r];i++) printf("%02x",core->busRead8(core,addresses[r]+i));
                printf("\"");
            }
            printf("}}\n");checks++;continue;
        }
'''
    result=code.replace(point,point+addition)
    assert 'busWrite' not in result
    return result
