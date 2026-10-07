/* Real mGBA input-driven gameplay testing; RAM reads only, never RAM patches.
 * Commands: step FRAMES KEYS CAPTURE.ppm (or -), expect GROUP MAP X Y FLAGS,
 * battle IN_BATTLE BATTLERS OUTCOME CARL_PP DONUT_PP TRIAL_WON DONUT_ABILITY, duo healthy,
 * roster CARL_HP DONUT_HP CARL_PP DONUT_PP CARL_STATUS DONUT_STATUS,
 * uses CARL_PP1 CARL_PP2 DONUT_PP1 DONUT_PP2, pocket ID, policy FIXTURE_MASK,
 * support CARL_PP2 DONUT_PP2 CARL_DEF FOE1_ATK FOE2_ATK,
 * growth CARL_LEVEL XP ITEM DONUT_LEVEL XP ITEM; stats CARL_MAXHP ATK DONUT_MAXHP MAGIC;
 * foes HP1 HP2; item ID QUANTITY; flag ID SET.
 * pattern TRAINER TURN FOE_PP0 FOE_PP1 FOE_ATTACK FOE_DEFENSE CARL_ATTACK FOE_LEVEL.
 * tile X Y FULL_MAP_WORD (read current map tile, including collision/elevation).
 * color OBJ_PALETTE_SLOT COLOR_INDEX BGR555_VALUE (read actual hardware palette).
 * engage MAX_FRAMES: advance nearby encounter dialogue with normal A inputs.
 * pilot POLICY MAX_FRAMES: bounded normal-button battle routing; no state writes.
 * quit. Flags are the low three bits (E01 intro/crate and E02 guide) of save byte 0x1274.
 * RAM offsets match the pinned Emerald structs; update when their layouts change.
 * Supply ROM SAVE and `arm-none-eabi-nm -g --defined-only` output paths.
 */
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba/core/version.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <limits.h>

static int number(const char *text, unsigned limit, unsigned *out)
{
    char *end;
    unsigned long value;
    if (*text < '0' || *text > '9') return 0;
    errno=0;
    value=strtoul(text,&end,10);
    if (errno || *end || value>limit) return 0;
    *out=(unsigned)value;
    return 1;
}

// Decode only the saved party attack block; never decrypt or write game RAM in place.
static unsigned party_pp(struct mCore *core, unsigned mon, unsigned slot)
{
    static const unsigned char attacksSlot[24]={1,1,2,3,2,3,0,0,0,0,0,0,2,3,1,1,3,2,2,3,1,1,3,2};
    unsigned personality=core->busRead32(core,mon);
    unsigned key=personality^core->busRead32(core,mon+4);
    return ((core->busRead32(core,mon+0x20+12*attacksSlot[personality%24]+8)^key)>>(8*slot))&255;
}

static unsigned growth_word(struct mCore *core, unsigned mon, unsigned word)
{
    static const unsigned char growthSlot[24]={0,0,0,0,0,0,1,1,2,3,2,3,1,1,2,3,2,3,1,1,2,3,2,3};
    unsigned personality=core->busRead32(core,mon);
    return core->busRead32(core,mon+0x20+12*growthSlot[personality%24]+4*word)
        ^ personality ^ core->busRead32(core,mon+4);
}

static void log_emulator(struct mLogger *logger, int category, enum mLogLevel level,
                         const char *format, va_list args)
{
    (void)logger;
    if (level != mLOG_FATAL && level != mLOG_ERROR) return;
    fprintf(stderr, "%s: ", mLogCategoryName(category));
    vfprintf(stderr, format, args);
    fputc('\n', stderr);
}

static int capture(const char *name, const color_t *pixels, unsigned width, unsigned height)
{
    FILE *out=fopen(name,"wb");
    if (!out) return 11;
    int result=0;
    fprintf(out,"P6\n%u %u\n255\n",width,height);
    for (unsigned i=0;i<width*height;i++) {
        unsigned char rgb[]={pixels[i]&255,(pixels[i]>>8)&255,(pixels[i]>>16)&255};
        if (fwrite(rgb,1,3,out)!=3) {result=12;break;}
    }
    if (fclose(out)) result=12;
    return result;
}

int main(int argc, char **argv)
{
    if (argc != 4) return 2;
    unsigned saveptr=0, objects=0, avatar=0, party=0, count=0, mons=0, battlers=0, outcome=0, mainstate=0, bag=0, probe=0, save2ptr=0, pockets=0, trainer=0, results=0, controls=0, actionCursor=0, moveCursor=0, targetCursor=0, inputAction=0, inputMove=0, inputTarget=0, maplayout=0, addr;
    char type, symbol[128];
    FILE *symbols=fopen(argv[3], "r");
    if (!symbols) return 3;
    while (fscanf(symbols, "%x %c %127s", &addr, &type, symbol)==3) {
        if (!strcmp(symbol,"gBackupMapLayout")) maplayout=addr;
        if (!strcmp(symbol,"gSaveBlock1Ptr")) saveptr=addr;
        if (!strcmp(symbol,"gObjectEvents")) objects=addr;
        if (!strcmp(symbol,"gPlayerAvatar")) avatar=addr;
        if (!strcmp(symbol,"gPlayerParty")) party=addr;
        if (!strcmp(symbol,"gPlayerPartyCount")) count=addr;
        if (!strcmp(symbol,"gBattleMons")) mons=addr;
        if (!strcmp(symbol,"gBattlersCount")) battlers=addr;
        if (!strcmp(symbol,"gBattleOutcome")) outcome=addr;
        if (!strcmp(symbol,"gMain")) mainstate=addr;
        if (!strcmp(symbol,"gBagPosition")) bag=addr;
        if (!strcmp(symbol,"gSaveBlock2Ptr")) save2ptr=addr;
        if (!strcmp(symbol,"gBagPockets")) pockets=addr;
        if (!strcmp(symbol,"gTrainerBattleOpponent_A")) trainer=addr;
        if (!strcmp(symbol,"gBattleResults")) results=addr;
        if (!strcmp(symbol,"gBattlerControllerFuncs")) controls=addr;
        if (!strcmp(symbol,"gActionSelectionCursor")) actionCursor=addr;
        if (!strcmp(symbol,"gMoveSelectionCursor")) moveCursor=addr;
        if (!strcmp(symbol,"gMultiUsePlayerCursor")) targetCursor=addr;
        if (!strcmp(symbol,"DccTestInputAction")) inputAction=addr;
        if (!strcmp(symbol,"DccTestInputMove")) inputMove=addr;
        if (!strcmp(symbol,"DccTestInputTarget")) inputTarget=addr;
        if (!strcmp(symbol,"gDccCollectionProbe") || !strcmp(symbol,"gDccEquipmentProbe") || !strcmp(symbol,"gDccRewardProbe") || !strcmp(symbol,"gDccMembershipProbe")) probe=addr;
    }
    fclose(symbols);
    if (!saveptr || !objects || !avatar || !party || !count || !mons || !battlers || !outcome || !mainstate) return 4;
    FILE *save=fopen(argv[2], "ab+");
    if (!save) return 5;
    fseek(save,0,SEEK_END);
    if (!ftell(save)) for (unsigned i=0;i<131072;i++) fputc(255,save);
    fclose(save);
    struct mLogger logger={.log=log_emulator,.filter=NULL};
    mLogSetDefaultLogger(&logger);
    struct mCore *core=mCoreFind(argv[1]);
    if (!core || !core->init(core)) return 6;
    mCoreConfigInit(&core->config,NULL);
    unsigned width,height;
    core->desiredVideoDimensions(core,&width,&height);
    color_t *pixels=calloc(width*height,sizeof(*pixels));
    if (!pixels) return 7;
    core->setVideoBuffer(core,pixels,width);
    core->setAudioBufferSize(core,1024);
    if (!mCoreLoadFile(core,argv[1]) || !mCoreLoadSaveFile(core,argv[2],false)) return 8;
    core->reset(core);
    printf("mGBA %s; %ux%u; save=%s; read-only RAM diagnostics\n",projectVersion,width,height,argv[2]);
    fflush(stdout);
    char line[256],name[128],extra,ft[32],kt[32];
    unsigned frames,keys,total=0,checks=0,lastPilotIncap=0;
    int result=0;
    while (fgets(line,sizeof(line),stdin)) {
        if (!strcmp(line,"quit\n")) break;
        if (!strncmp(line,"engage ",7)) {
            char limitText[32]; unsigned limit, elapsed=0;
            if (sscanf(line,"engage %31s %c",limitText,&extra)!=1
                || !number(limitText,36000,&limit) || !limit || total>UINT_MAX-limit) {result=34;break;}
            while (elapsed<limit && !(core->busRead8(core,mainstate+0x439)&2)) {
                core->setKeys(core,elapsed%12==0?1:0);
                core->runFrame(core);elapsed++;total++;
            }
            core->setKeys(core,0);
            if (!(core->busRead8(core,mainstate+0x439)&2)) {fprintf(stderr,"engage exceeded frame budget\n");result=35;break;}
            printf("engage completed frames=%u\n",elapsed);checks++;continue;
        }
        if (!strncmp(line,"pilot ",6)) {
            char policy[32], limitText[32]; unsigned limit;
            if (sscanf(line,"pilot %31s %31s %c",policy,limitText,&extra)!=2
                || !number(limitText,36000,&limit) || !limit || total>UINT_MAX-limit
                || !controls || !actionCursor || !moveCursor || !targetCursor
                || !inputAction || !inputMove || !inputTarget || !results
                || (strcmp(policy,"defensive") && strcmp(policy,"fortify") && strcmp(policy,"offensive") && strcmp(policy,"loss"))
                || !(core->busRead8(core,mainstate+0x439)&2)) {result=31;break;}
            unsigned elapsed=0, lastTurn=UINT_MAX, capturedIncap=0;
            lastPilotIncap=0;
            while (elapsed<limit && (core->busRead8(core,mainstate+0x439)&2)) {
                unsigned chp=core->busRead16(core,party+0x56), dhp=core->busRead16(core,party+100+0x56);
                if (!chp && dhp) lastPilotIncap|=1;
                if (chp && !dhp) lastPilotIncap|=2;
                if (!chp && !dhp) lastPilotIncap|=4;
                unsigned turn=core->busRead8(core,results+0x13);
                unsigned key=0, actor=UINT_MAX, menu=0, selection=0;
                if (elapsed%12==0) {
                    key=1; // Advance ordinary battle text when no input menu owns control.
                    for (unsigned b=0;b<=2;b+=2) {
                        unsigned callback=core->busRead32(core,controls+b*4)&~1u;
                        if (callback==inputAction) {
                            unsigned cursor=core->busRead8(core,actionCursor+b);
                            key=(cursor&1)?32:(cursor&2)?64:1;
                            actor=b; menu=1; selection=0; break;
                        }
                        if (callback==inputMove) {
                            unsigned mask=(!chp && dhp)?1:(chp && !dhp)?2:0;
                            if (mask && !(capturedIncap&mask)) {
                                result=capture(mask==1?"pilot-carl-down.ppm":"pilot-donut-down.ppm",pixels,width,height);
                                if (result) break;
                                capturedIncap|=mask;
                            }
                            unsigned desired=0;
                            if (!strcmp(policy,"loss")) desired=(b==2 || !core->busRead16(core,party+100+0x56));
                            else if ((!strcmp(policy,"defensive") && turn<(b==0?2:3))
                                     || (!strcmp(policy,"fortify") && turn<3)) desired=1;
                            else if (b==2 && !core->busRead8(core,mons+b*0x58+0x24)) desired=1;
                            unsigned cursor=core->busRead8(core,moveCursor+b);
                            // Fixed duo has exactly two actions; exhausted pairs use engine STRUGGLE.
                            key=cursor==desired?1:desired?16:32;
                            actor=b; menu=2; selection=desired; break;
                        }
                        if (callback==inputTarget) {
                            unsigned target=core->busRead8(core,targetCursor);
                            key=(!strcmp(policy,"loss") && b==0
                                 && core->busRead16(core,party+100+0x56) && target!=2)?16:1;
                            actor=b; menu=3; selection=target; break;
                        }
                    }
                    if (actor!=UINT_MAX)
                        printf("pilot frame=%u turn=%u actor=%u menu=%u selection=%u key=%u\n",total,turn,actor,menu,selection,key);
                }
                if (result) break;
                core->setKeys(core,key);
                core->runFrame(core);
                elapsed++;total++;
                if (turn!=lastTurn) {
                    printf("pilot turn=%u HP=%u,%u foeHP=%u,%u foeAtk=%u foeDef=%u CarlAtk=%u\n",turn,
                        core->busRead16(core,party+0x56),core->busRead16(core,party+100+0x56),
                        core->busRead16(core,mons+0x58+0x28),core->busRead16(core,mons+3*0x58+0x28),
                        core->busRead8(core,mons+0x58+0x19),core->busRead8(core,mons+0x58+0x1A),
                        core->busRead8(core,mons+0x19));
                    lastTurn=turn;
                }
            }
            if (result) break;
            core->setKeys(core,0);
            if (core->busRead8(core,mainstate+0x439)&2) {fprintf(stderr,"pilot exceeded frame budget\n");result=32;break;}
            printf("pilot completed policy=%s frames=%u outcome=%u incapacitation=%u\n",policy,elapsed,core->busRead8(core,outcome),lastPilotIncap);
            checks++;
            continue;
        }
        if (sscanf(line,"step %31s %31s %127s %c",ft,kt,name,&extra)==3) {
            if (!number(ft,36000,&frames) || !number(kt,1023,&keys) || !frames ||
                total>UINT_MAX-frames) {result=9;break;}
            core->setKeys(core,keys);
            for (unsigned i=0;i<frames;i++) core->runFrame(core);
            total+=frames;
            if (strcmp(name,"-")) {
                if (strspn(name,"abcdefghijklmnopqrstuvwxyz0123456789-.")!=strlen(name)) {result=10;break;}
                result=capture(name,pixels,width,height);
                if (result) break;
            }
        } else if (strncmp(line,"tile ",5) && strncmp(line,"expect ",7) && strncmp(line,"battle ",7) && strncmp(line,"roster ",7) && strncmp(line,"support ",8) && strncmp(line,"uses ",5) && strncmp(line,"pocket ",7) && strncmp(line,"policy ",7) && strncmp(line,"growth ",7) && strncmp(line,"stats ",6) && strncmp(line,"foes ",5) && strncmp(line,"item ",5) && strncmp(line,"flag ",5) && strncmp(line,"pattern ",8) && strncmp(line,"incap ",6) && strncmp(line,"color ",6) && strcmp(line,"duo healthy\n")) {result=13;break;}
        if (!strncmp(line,"incap ",6)) {
            char value[32]; unsigned wanted;
            if (sscanf(line,"incap %31s %c",value,&extra)!=1 || !number(value,7,&wanted)
                || wanted!=lastPilotIncap) {fprintf(stderr,"FAILED incapacitation=%u: %s",lastPilotIncap,line);result=33;break;}
            checks++;printf("PASS %s",line);
        }
        if (!strncmp(line,"tile ",5)) {
            char values[3][32]; unsigned tx,ty,wanted;
            if (!maplayout || sscanf(line,"tile %31s %31s %31s %c",values[0],values[1],values[2],&extra)!=3
                || !number(values[0],15,&tx) || !number(values[1],11,&ty) || !number(values[2],65535,&wanted)) {result=25;break;}
            unsigned width=core->busRead32(core,maplayout), height=core->busRead32(core,maplayout+4);
            unsigned data=core->busRead32(core,maplayout+8);
            if (tx+7>=width || ty+7>=height || !data) {result=25;break;}
            unsigned actual=core->busRead16(core,data+2*((ty+7)*width+tx+7));
            if (actual!=wanted) {fprintf(stderr,"FAILED: %sactual tile=%u\n",line,actual);result=25;break;}
            checks++; printf("PASS %s",line);
            continue;
        }
        if (!strncmp(line,"color ",6)) {
            char values[3][32]; unsigned slot, index, wanted;
            if (sscanf(line,"color %31s %31s %31s %c",values[0],values[1],values[2],&extra)!=3
                || !number(values[0],15,&slot) || !number(values[1],15,&index)
                || !number(values[2],32767,&wanted)) {result=30;break;}
            unsigned actual=core->busRead16(core,0x05000200 + slot*32 + index*2);
            if (actual!=wanted) {
                fprintf(stderr,"FAILED actual=%u: %s",actual,line); result=30;break;
            }
            checks++; printf("PASS %s",line);
        }
        unsigned sb=core->busRead32(core,saveptr);
        unsigned object=objects+core->busRead8(core,avatar+5)*0x24;
        int group=core->busRead8(core,sb+4),map=core->busRead8(core,sb+5);
        int x=(short)core->busRead16(core,object+0x10)-7;
        int y=(short)core->busRead16(core,object+0x12)-7;
        int flags=core->busRead8(core,sb+0x1274)&7;
        printf("frame=%u map=%d.%d pos=%d,%d flags=%d\n",total,group,map,x,y,flags);
        unsigned hp0=core->busRead16(core,party+0x56), max0=core->busRead16(core,party+0x58);
        unsigned hp1=core->busRead16(core,party+100+0x56), max1=core->busRead16(core,party+100+0x58);
        unsigned state[]={(core->busRead8(core,mainstate+0x439)>>1)&1,
            core->busRead8(core,battlers),core->busRead8(core,outcome),
            core->busRead8(core,mons+0x24),core->busRead8(core,mons+2*0x58+0x24),
            (core->busRead8(core,sb+0x1270+0x857/8)>>(0x857%8))&1,
            core->busRead8(core,mons+2*0x58+0x20)};
        printf("party=%u HP=%u/%u,%u/%u battle=%u battlers=%u outcome=%u PP=%u,%u trial=%u donut-ability=%u\n",
            core->busRead8(core,count),hp0,max0,hp1,max1,state[0],state[1],state[2],state[3],state[4],state[5],state[6]);
        unsigned roster[]={hp0,hp1,party_pp(core,party,0),party_pp(core,party+100,0),
            core->busRead32(core,party+0x50),core->busRead32(core,party+100+0x50)};
        printf("persistent PP=%u,%u status=%u,%u\n",roster[2],roster[3],roster[4],roster[5]);
        if (!strncmp(line,"roster ",7)) {
            char values[6][32]; unsigned wanted;
            if (sscanf(line,"roster %31s %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],values[5],&extra)!=6) result=19;
            for (unsigned i=0;i<6 && !result;i++)
                if (!number(values[i],UINT_MAX,&wanted) || wanted!=roster[i]) result=19;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        unsigned growth[]={core->busRead8(core,party+0x54),growth_word(core,party,1),growth_word(core,party,0)>>16,
            core->busRead8(core,party+100+0x54),growth_word(core,party+100,1),growth_word(core,party+100,0)>>16};
        unsigned stats[]={max0,core->busRead16(core,party+0x5A),max1,core->busRead16(core,party+100+0x60)};
        unsigned foes[]={core->busRead16(core,mons+0x58+0x28),core->busRead16(core,mons+3*0x58+0x28)};
        printf("growth level/xp/item=%u/%u/%u,%u/%u/%u stats maxHP/attack,maxHP/magic=%u/%u,%u/%u foesHP=%u,%u\n",
            growth[0],growth[1],growth[2],growth[3],growth[4],growth[5],stats[0],stats[1],stats[2],stats[3],foes[0],foes[1]);
        if (!strncmp(line,"growth ",7) || !strncmp(line,"stats ",6) || !strncmp(line,"foes ",5)) {
            unsigned *actual=growth,n=6,offset=7,wanted; char values[6][32]; int parsed;
            if (!strncmp(line,"stats ",6)) {actual=stats;n=4;offset=6;}
            if (!strncmp(line,"foes ",5)) {actual=foes;n=2;offset=5;}
            parsed=sscanf(line+offset,"%31s %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],values[5],&extra);
            if (parsed!=(int)n) result=23;
            for (unsigned i=0;i<n && !result;i++)
                if (!number(values[i],UINT_MAX,&wanted) || wanted!=actual[i]) result=23;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++;printf("PASS %s",line);
        }
        if (!strncmp(line,"item ",5) || !strncmp(line,"flag ",5)) {
            char idtext[32],wanttext[32]; unsigned id,wanted,actual=0;
            int is_item=!strncmp(line,"item ",5);
            if (sscanf(line+5,"%31s %31s %c",idtext,wanttext,&extra)!=2 ||
                !number(idtext,is_item?65535:0x8FF,&id) || !number(wanttext,65535,&wanted)) result=24;
            if (!result && is_item) {
                if (!pockets || !save2ptr) result=24;
                else {
                    unsigned key=core->busRead16(core,core->busRead32(core,save2ptr)+0xAC);
                    for (unsigned pocket=0;pocket<5;pocket++) {
                        unsigned slots=core->busRead32(core,pockets+8*pocket),capacity=core->busRead8(core,pockets+8*pocket+4);
                        for (unsigned i=0;i<capacity;i++)
                            if (core->busRead16(core,slots+4*i)==id)
                                actual+=core->busRead16(core,slots+4*i+2)^key;
                    }
                }
            } else if (!result) actual=(core->busRead8(core,sb+0x1270+id/8)>>(id%8))&1;
            if (result || actual!=wanted) {fprintf(stderr,"FAILED actual=%u: %s",actual,line);result=24;break;}
            checks++;printf("PASS %s",line);
        }
        unsigned pattern[]={trainer?core->busRead16(core,trainer):0,
            results?core->busRead8(core,results+0x13):0,
            core->busRead8(core,mons+0x58+0x24),core->busRead8(core,mons+0x58+0x25),
            core->busRead8(core,mons+0x58+0x19),core->busRead8(core,mons+0x58+0x1A),
            core->busRead8(core,mons+0x19),core->busRead8(core,mons+0x58+0x2A)};
        printf("pattern trainer=%u turn=%u foePP=%u,%u foeAtkDef=%u,%u CarlAtk=%u foeLevel=%u\n",
            pattern[0],pattern[1],pattern[2],pattern[3],pattern[4],pattern[5],pattern[6],pattern[7]);
        if (!strncmp(line,"pattern ",8)) {
            char values[8][32]; unsigned wanted;
            if (!trainer || !results || sscanf(line+8,"%31s %31s %31s %31s %31s %31s %31s %31s %c",
                values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],&extra)!=8) result=25;
            for (unsigned i=0;i<8 && !result;i++)
                if (!number(values[i],65535,&wanted) || wanted!=pattern[i]) result=25;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++;printf("PASS %s",line);
        }
        unsigned support[]={core->busRead8(core,mons+0x25),core->busRead8(core,mons+2*0x58+0x25),
            core->busRead8(core,mons+0x1A),core->busRead8(core,mons+0x58+0x19),
            core->busRead8(core,mons+3*0x58+0x19)};
        printf("support PP=%u,%u Carl-defense=%u enemy-attack=%u,%u\n",
            support[0],support[1],support[2],support[3],support[4]);
        if (!strncmp(line,"support ",8)) {
            char values[5][32]; unsigned wanted;
            if (sscanf(line,"support %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],&extra)!=5) result=20;
            for (unsigned i=0;i<5 && !result;i++)
                if (!number(values[i],255,&wanted) || wanted!=support[i]) result=20;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strncmp(line,"pocket ",7) || !strncmp(line,"policy ",7)) {
            char value[32]; unsigned wanted;
            unsigned address=!strncmp(line,"pocket ",7)?bag:probe;
            unsigned actual=address?(!strncmp(line,"pocket ",7)?core->busRead8(core,bag+5):core->busRead32(core,probe)):UINT_MAX;
            if (sscanf(line+7,"%31s %c",value,&extra)!=1 || !number(value,UINT_MAX,&wanted) || !address || wanted!=actual) {
                fprintf(stderr,"FAILED actual=%u: %s",actual,line); result=22;break;
            }
            checks++; printf("PASS %s",line);
        }
        unsigned uses[]={roster[2],party_pp(core,party,1),roster[3],party_pp(core,party+100,1)};
        printf("party action uses=%u,%u / %u,%u\n",uses[0],uses[1],uses[2],uses[3]);
        if (!strncmp(line,"uses ",5)) {
            char values[4][32]; unsigned wanted;
            if (sscanf(line,"uses %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],&extra)!=4) result=21;
            for (unsigned i=0;i<4 && !result;i++)
                if (!number(values[i],255,&wanted) || wanted!=uses[i]) result=21;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strcmp(line,"duo healthy\n")) {
            const unsigned char names[2][6]={{0xBD,0xBB,0xCC,0xC6,0xFF,0},{0xBE,0xC9,0xC8,0xCF,0xCE,0xFF}};
            if (core->busRead8(core,count)!=2 || !hp0 || hp0!=max0 || !hp1 || hp1!=max1) result=17;
            for (unsigned n=0;n<2;n++) for (unsigned i=0;i<(n?6:5);i++)
                if (core->busRead8(core,party+n*100+8+i)!=names[n][i]) result=17;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strncmp(line,"battle ",7)) {
            char values[7][32]; unsigned wanted;
            if (sscanf(line,"battle %31s %31s %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],values[5],values[6],&extra)!=7) result=18;
            for (unsigned i=0;i<7 && !result;i++)
                if (!number(values[i],255,&wanted) || wanted!=state[i]) result=18;
            if (result) {fprintf(stderr,"FAILED: %s",line);break;}
            checks++; printf("PASS %s",line);
        }
        if (!strncmp(line,"expect ",7)) {
            char values[5][32];
            unsigned eg,em,ex,ey,ef;
            if (sscanf(line,"expect %31s %31s %31s %31s %31s %c",values[0],values[1],values[2],values[3],values[4],&extra)!=5 ||
                !number(values[0],255,&eg) || !number(values[1],255,&em) ||
                !number(values[2],2047,&ex) || !number(values[3],2047,&ey) || !number(values[4],7,&ef) ||
                (int)eg!=group || (int)em!=map || (int)ex!=x || (int)ey!=y || (int)ef!=flags) {
                fprintf(stderr,"FAILED: %s",line);result=14;break;
            }
            checks++;
            printf("PASS %s",line);
        }
        fflush(stdout);
    }
    if (ferror(stdin)) result=15;
    if (!result && !checks) result=16;
    mCoreConfigDeinit(&core->config);
    core->deinit(core);
    mLogSetDefaultLogger(NULL);
    free(pixels);
    printf("result=%d assertions=%u\n",result,checks);
    return result;
}
