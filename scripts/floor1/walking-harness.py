"""Read-only frame measurement for ordinary overworld walking routes."""
def instrument(code):
    code=code.replace('maplayout=0, addr;', 'maplayout=0, overworld=0, fade=0, addr;')
    code=code.replace('if (!strcmp(symbol,"gBackupMapLayout"))', 'if (!strcmp(symbol,"CB2_Overworld")) overworld=addr;\n        if (!strcmp(symbol,"gPaletteFade")) fade=addr;\n        if (!strcmp(symbol,"gBackupMapLayout"))')
    code=code.replace('int result=0;\n    while', 'int result=0;\n    unsigned measuring=0, measured=0, walkFrames=0, tileSteps=0, mapChanges=0, previousMap=0;\n    int previousX=0,previousY=0;\n    char measureName[128];\n    while')
    point='        if (!strcmp(line,"quit\\n")) break;'
    code=code.replace(point,point+'''
        if (!strncmp(line,"measure start ",14)) {
            if (measuring || sscanf(line,"measure start %127s %c",measureName,&extra)!=1 || !overworld || !fade) {result=13;break;}
            unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;
            previousMap=(core->busRead8(core,sb+4)<<8)|core->busRead8(core,sb+5);
            previousX=(short)core->busRead16(core,obj+0x10);previousY=(short)core->busRead16(core,obj+0x12);
            measuring=1;measured=walkFrames=tileSteps=mapChanges=0;continue;
        }
        if (!strcmp(line,"measure stop\\n")) {
            if (!measuring) {result=13;break;}
            printf("MEASURE name=%s frames=%u walking=%u tiles=%u warps=%u\\n",measureName,measured,walkFrames,tileSteps,mapChanges);
            measuring=0;continue;
        }
''')
    point='for (unsigned i=0;i<frames;i++) core->runFrame(core);'
    assert code.count(point)==1
    code=code.replace(point,'''for (unsigned i=0;i<frames;i++) {
                core->runFrame(core);
                if (measuring) {
                    unsigned sb=core->busRead32(core,saveptr), obj=objects+core->busRead8(core,avatar+5)*0x24;
                    unsigned map=(core->busRead8(core,sb+4)<<8)|core->busRead8(core,sb+5);
                    int x=(short)core->busRead16(core,obj+0x10),y=(short)core->busRead16(core,obj+0x12);
                    unsigned flags=core->busRead8(core,avatar),run=core->busRead8(core,avatar+2),transition=core->busRead8(core,avatar+3);
                    unsigned field=(core->busRead32(core,mainstate+4)&~1u)==(overworld&~1u) && !(flags&64) && !(core->busRead8(core,fade+7)&128);
                    measured++;
                    if (field && run==2 && transition) walkFrames++;
                    if (field && map!=previousMap) mapChanges++;
                    else if (field && run==2 && abs(x-previousX)+abs(y-previousY)==1) tileSteps++;
                    if (field) {previousMap=map;previousX=x;previousY=y;}
                }
            }''')
    assert 'busWrite' not in code
    return code
