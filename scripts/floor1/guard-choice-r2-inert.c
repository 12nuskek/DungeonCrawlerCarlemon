/* Offline mock of exact generated host; no emulator core is initialised. */
#include "OBSERVER"
#include <assert.h>
#include <sys/wait.h>
#include <unistd.h>
static unsigned char memory[65536];
static unsigned advances,saveReads,event;
static int report_fd=-1;
static void report_advances(void){unsigned values[2]={advances,co.frames};if(report_fd>=0)assert(write(report_fd,values,sizeof values)==sizeof values);}
static color_t mockPixels[240*160];
static uint32_t r8(struct mCore*c,uint32_t a){(void)c;assert(a<sizeof memory);if(a==0x50||a==0x54)saveReads++;return memory[a];}
static uint32_t r16(struct mCore*c,uint32_t a){return r8(c,a)|((unsigned)r8(c,a+1)<<8);}
static uint32_t r32(struct mCore*c,uint32_t a){return r16(c,a)|((unsigned)r16(c,a+2)<<16);}
static void put16(unsigned a,unsigned v){memory[a]=v;memory[a+1]=v>>8;}
static void put32(unsigned a,unsigned v){put16(a,v);put16(a+2,v>>16);}
static void advance(struct mCore*c){(void)c;advances++;if(event==1)memory[0x2439]=2;if(event==2){memory[0x2439]=0;memory[0x90]=1;}if(event==3)put16(0x92,859);}
static bool mock_register(const struct mCore*c,const char*n,void*out){(void)c;unsigned v=0xA0000000u;if(n[0]=='r')v+=(unsigned)strtoul(n+1,NULL,10);else if(!strcmp(n,"cpsr"))v+=16;else if(!strcmp(n,"spsr"))v+=17;else return false;memcpy(out,&v,4);return true;}
static struct mCore mock={.readRegister=mock_register,.busRead8=r8,.busRead16=r16,.busRead32=r32,.runFrame=advance};
static void setup(void){
 memset(memory,0,sizeof memory);memset(&co,0,sizeof co);advances=saveReads=event=0;
 co.a=(struct CoAddresses){.party=0x1000,.count=0x60,.save1=0x50,.save2=0x54,.main=0x2000,.cb1=0x110,.cb2=0x120,.vblank=0x130,.objects=0x2800,.avatar=0x2900,.maps=0x3000,.trainer=0x92,.outcome=0x90,.newGame=0x140,.continueGame=0x150,.grid=0x3300,.mons=0x1800,.turn=0x99,.move=0x9a,.power=0x9c,.crit=0x9e,.attacker=0x9f,.target=0xa0,.controls=0x2700,.chosen=0x2a00,.moveResults=0x2a10,.damage=0x2a14,.battleMain=0x180};
 co.limit=72000;co.kind=CO_STABLE;
 FILE*f=fopen("fixture.bin","rb");assert(f&&fread(&co.last,1,sizeof co.last,f)==sizeof co.last&&!fclose(f));co.before=co.last;co.armed=1;resource_canonical(gc.owned,co.before.owned,co.before.context);
 memcpy(memory+0x1000,co.last.party,600);memory[0x60]=2;put32(0x50,0x4000);put32(0x54,0x8000);
 memory[0x4004]=35;memcpy(memory+0x5270,co.last.flags,300);memcpy(memory+0x4490,co.last.owned,1272);memcpy(memory+0x539c,co.last.vars,512);
 put32(0x2000,0x111);put32(0x2004,0x121);put32(0x200c,0x131);
 put32(0x3000+35*4,0x3100);put32(0x3100,0x3200);put16(0x2810,15);put16(0x2812,45);memory[0x2818]=1;
 put32(0x3300,80);put32(0x3304,60);put32(0x3308,0xa000);put16(0x92,856);
 co.trace=tmpfile();co.index=tmpfile();co.battleTrace=tmpfile();assert(co.trace&&co.index&&co.battleTrace);
}
static void installSnapshot(const struct CoSnapshot*s){
 memcpy(memory+0x1000,s->party,600);memory[0x60]=s->count;put32(0x4234,s->savedCount);memcpy(memory+0x4238,s->saved,600);
 memory[0x4004]=s->group;memory[0x4005]=s->map;put16(0x53f0,s->counter);
 memcpy(memory+0x5270,s->flags,300);memcpy(memory+0x4490,s->owned,1272);memcpy(memory+0x539c,s->vars,512);put32(0x80ac,s->context);
 put32(0x3100+4*s->map,0x3200);memory[0x3214]=s->section;put16(0x2810,s->x+7);put16(0x2812,s->y+7);memory[0x2818]=s->facing;
}
static void readSnapshot(const char*path,struct CoSnapshot*s){FILE*f=fopen(path,"rb");assert(f&&fread(s,1,sizeof *s,f)==sizeof *s&&fgetc(f)==EOF&&!fclose(f));}
static void closeFiles(void){if(co.motion)assert(!fclose(co.motion));assert(!fclose(co.trace)&&!fclose(co.index)&&!fclose(co.battleTrace));}
static void mustStop(unsigned reason,unsigned mode){
 int pipefd[2];assert(!pipe(pipefd));fflush(NULL);pid_t child=fork();assert(child>=0);
 if(!child){close(pipefd[0]);report_fd=pipefd[1];assert(!atexit(report_advances));setup();
  if(mode==1)co.frames=72000;
  if(mode==2){co.kind=CO_GUARD;co.encounterFrames[1]=36000;memory[0x2439]=2;}
  if(mode==3)put32(0x2004,co.a.continueGame);
  if(mode==4){co.cold=1;put32(0x2004,co.a.newGame);}
  if(mode==5){co.kind=CO_GUARD;co.attempts=1;event=1;put16(0x92,859);}
  if(mode==6){co.kind=CO_GUARD;co.attempts=2;event=1;}
  if(mode==7){co.cold=1;co.kind=CO_COLD;event=1;}
  if(mode==8){co.kind=CO_GUARD;co.attempts=2;memory[0x2439]=2;put32(0x2004,co.a.battleMain);co.combatLoaded=1;}
  if(mode==9){co.kind=CO_GUARD;co.encounterFrames[1]=36000;memory[0x2439]=2;}
  if(mode==10){co.kind=CO_GUARD;co.attempts=1;co.encounterFrames[1]=35999;event=1;co_run(&mock,mockPixels,240,160);}
  if(mode==11){co.cold=1;co.limit=co.frames=6000;}
  co_run(&mock,mockPixels,240,160);_exit(250);
 }
 close(pipefd[1]);unsigned observed[2];assert(read(pipefd[0],observed,sizeof observed)==sizeof observed);close(pipefd[0]);
 assert(observed[0]==(mode==5||mode==6||mode==7||mode==8||mode==10?1u:0u));
 int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==(int)reason);
 FILE*cpu=fopen("first-failure-CPU-context-private.bin","rb");unsigned regs[24];assert(cpu&&fread(regs,1,sizeof regs,cpu)==sizeof regs&&fgetc(cpu)==EOF&&!fclose(cpu));
 assert(regs[0]==observed[1]&&regs[1]==reason&&regs[2]==65535&&regs[20]==1&&regs[21]==1);
 for(unsigned i=0;i<16;i++){assert(regs[4+i]==0xA0000000u+i);}assert(regs[22]==0xA0000010u&&regs[23]==0xA0000011u);
}

static void medicineTask(unsigned cb){memset(memory+0x3400,0,16*40);put32(0x3400,cb|1);memory[0x3404]=1;}
static void medicineSetup(unsigned swapped,unsigned recipient,unsigned quantity){
 setup();memset(&gc,0,sizeof gc);co.kind=CO_GUARD;
 gc.a=(struct GcAddresses){.tasks=0x3400,.fade=0x3800,.bagMain=0x160,.bagInput=0x170,.context=0x180,
  .partyMain=0x190,.partyInput=0x1a0,.partyMenu=0x3840,.bagPosition=0x3880,.menu=0x38c0,
  .selected=0xb0,.owner=0xb2,.order=0xb4,.indexes=0xb8,.actions=0xc0,.itemCB=0xc4,
  .medicine=0x1b0,.useExit=0xc8,.internal=0xcc,.exitBattle=0x1c0,.completeItem=0x1d0,
  .bufferRun=0x1e0,.hpTask=0x1f0,.restored=0x210,.closeText=0x220,.returnBag=0x230,
  .messagePrinters=0xb000,.printWait=0x240,.closeFade=0x250,.setupReshow=0x260,.reshowEntry=0x270,.reshow=0x280,
  .textFlags=0xd0,.disablePrinters=0xd1,.string4=0xc000};
 put16(0x1000+86,recipient?30:22);put16(0x1000+100+86,recipient?9:20);
 put16(0x4490+0xd0,13);put16(0x4490+0xd2,quantity);put16(0x4490+0xd4,378);put16(0x4490+0xd6,2);
 assert(!gc_read(&mock,&gc.before));co.before=gc.before;resource_canonical(gc.owned,gc.before.owned,gc.before.context);
 memory[0xb2]=2;memory[0xb4]=swapped?0x10:0x01;memory[0xb5]=0x23;memory[0xb6]=0x45;
 put16(0xb8,0);put16(0xbc,1);memory[0xc0]=0;memory[0xc2]=1;put16(co.a.chosen,355);put32(co.a.controls+8,0x1d1);
 put16(co.a.mons+40,recipient?30:22);put16(co.a.mons+44,walk_u16(gc.before.party+88));
 put16(co.a.mons+2*88+40,recipient?9:20);put16(co.a.mons+2*88+44,walk_u16(gc.before.party+188));
 gc.stage=1;gc.recipient=recipient;gc.start=co.frames=100;gc.turn=2;
 memory[0x3884]=1;put32(0x2004,0x161);medicineTask(0x170);
}
/* Source-ordered, key-driven printer/task/fade/reorder/reshow lifecycle.
 * This synthetic mock never initialises an emulator, loads state, or writes game RAM. */
static unsigned nativeKeys,nativeOldKeys,nativeEdges,nativeState,nativeReshowFrames;
static void nativeSetKeys(struct mCore*c,uint32_t keys){(void)c;nativeKeys=keys;}
static void nativeAdvance(struct mCore*c) {
    (void)c;advances++;unsigned printer=gc_message(&mock);
    if(nativeState==0) { /* Ordinary glyph printing; no acknowledgement yet. */
        assert(!nativeKeys);memory[printer+28]=1;nativeState=1;
    }else if(nativeState==1) {
        if((nativeKeys&1)&&!(nativeOldKeys&1)) {
            assert(gc_ack_ready(&mock));nativeEdges++;memory[printer+28]=0;nativeState=2;
        }
    }else if(nativeState==2) { /* Native RENDER_FINISH and DestroyTask occur together. */
        assert(!nativeKeys);memory[printer+27]=0;memory[0x342c]=0;nativeState=3;
    }else if(nativeState==3) {
        assert(!nativeKeys&&!memory[0x342c]);medicineTask(gc.a.closeFade);memory[0x3807]=128;nativeState=4;
    }else if(nativeState==4&&memory[0x3807]) {
        assert(!nativeKeys);memory[0x3807]=0; /* UpdatePaletteFade after RunTasks; party CB persists this frame. */
    }else if(nativeState==4) {
        assert(!nativeKeys);unsigned positions[6];unsigned char party[600];
        assert(gc_order(gc.order,positions));gc_permute(memory+0x1000,party,positions,1);memcpy(memory+0x1000,party,600);
        memory[0x3404]=0;put32(0x2004,gc.a.exitBattle|1);put32(gc.a.internal,0);nativeState=5;
    }else if(nativeState==5) {put32(0x2004,gc.a.setupReshow|1);nativeState=6;
    }else if(nativeState==6) {put32(0x2004,gc.a.reshowEntry|1);nativeState=7;
    }else if(nativeState==7) {put32(0x2004,gc.a.reshow|1);nativeState=8;nativeReshowFrames=0;
    }else if(nativeState==8) {
        if(++nativeReshowFrames==20){put32(0x2004,co.a.battleMain|1);memory[0x3807]=128;nativeState=9;}
    }else if(nativeState==9) {assert(!nativeKeys);memory[0x3807]=0;nativeState=10;
    }else assert(0);
    nativeOldKeys=nativeKeys;
}
static void nativeMessageSetup(void) {
    unsigned printer=gc_message(&mock);medicineTask(gc.a.closeText);
    put32(0x3428,gc.a.printWait|1);memory[0x342c]=1;put16(0x3430,0);
    put32(printer,gc.a.string4+2);memory[gc.a.string4]=0xfc;memory[gc.a.string4+1]=9;memory[gc.a.string4+2]=255;
    memory[printer+4]=6;memory[printer+5]=1;put32(printer+16,0);memory[printer+27]=1;memory[printer+28]=0;
    nativeKeys=nativeOldKeys=nativeEdges=nativeState=nativeReshowFrames=0;
    mock.setKeys=nativeSetKeys;mock.runFrame=nativeAdvance;
}
static void lifecycleBadByte(unsigned address,unsigned value) {
    unsigned old=memory[address];struct GcMedicine original=gc;memory[address]=value;
    assert(gc_observe(&mock,mockPixels,240,160)!=0);unsigned key=77;gc=original;
    assert(gc_buttons(&mock,&key,mockPixels,240,160)!=0&&!key&&!gc.ack);memory[address]=old;gc=original;
}
static void lifecycleFinish(unsigned swapped,unsigned recipient,unsigned quantity) {
    (void)swapped;(void)recipient;(void)quantity;unsigned key=77,printer=gc_message(&mock),oldUses=gc.uses;
    nativeMessageSetup();assert(!gc_observe(&mock,mockPixels,240,160));
    assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&!key&&!gc.ack); /* Printing must never emit A. */
    nativeSetKeys(&mock,0);nativeAdvance(&mock);co.frames++; /* Source reaches WAIT. */
    assert(gc_ack_ready(&mock));
    lifecycleBadByte(printer+4,5);lifecycleBadByte(printer+5,0);lifecycleBadByte(printer+27,0);
    lifecycleBadByte(printer+28,2);lifecycleBadByte(0x342c,0);lifecycleBadByte(0x3404,0);
    lifecycleBadByte(0x3430,1);lifecycleBadByte(gc.a.owner,0);lifecycleBadByte(gc.a.fade+7,128);
    lifecycleBadByte(gc.a.textFlags,4);lifecycleBadByte(gc.a.disablePrinters,1);
    lifecycleBadByte(gc.a.string4+2,0);lifecycleBadByte(gc.a.useExit,0);
    put32(0x3450,gc.a.printWait|1);memory[0x3454]=1;
    assert(gc_observe(&mock,mockPixels,240,160)==107);memory[0x3454]=0;
    gc.keys=1;assert(gc_buttons(&mock,&key,mockPixels,240,160)==107&&!key&&!gc.ack);gc.keys=0;
    unsigned cb=r32(&mock,0x2004);put32(0x2004,co.a.battleMain|1);
    assert(gc_observe(&mock,mockPixels,240,160)!=0);put32(0x2004,cb); /* Unobserved direct return rejected. */
    const unsigned bases[]={0x1000,0x5270,0x4490,0x539c,0x4238,0x4234};
    const unsigned lengths[]={600,300,1272,512,600,4};
    for(unsigned region=0;region<6;region++)for(unsigned off=0;off<lengths[region];off++){
        memory[bases[region]+off]^=1;assert(gc_observe(&mock,mockPixels,240,160)!=0);memory[bases[region]+off]^=1;
    }
    assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&key==1&&gc.ack);
    unsigned duplicate=77;assert(!gc_buttons(&mock,&duplicate,mockPixels,240,160)&&!duplicate);
    gc.keys=key;nativeSetKeys(&mock,key);nativeAdvance(&mock);co.frames++;
    assert(nativeEdges==1&&!gc.released&&!gc.printerFinished);
    struct GcMedicine original=gc;unsigned oldFrame=co.frames;gc.keys=1;co.frames=gc.ackFrame+2;
    assert(gc_observe(&mock,mockPixels,240,160)==107);gc=original;co.frames=oldFrame;
    assert(!gc_observe(&mock,mockPixels,240,160));
    original=gc;unsigned owner=memory[gc.a.owner];memory[gc.a.owner]=0;
    assert(gc_observe(&mock,mockPixels,240,160)==105);memory[gc.a.owner]=owner;gc=original;
    memory[printer+27]=0;assert(gc_observe(&mock,mockPixels,240,160)==107);memory[printer+27]=1;gc=original;
    memory[0x3807]=128;assert(gc_observe(&mock,mockPixels,240,160)==107);memory[0x3807]=0;gc=original;
    cb=r32(&mock,0x2004);put32(0x2004,co.a.battleMain|1);
    assert(gc_observe(&mock,mockPixels,240,160)!=0);put32(0x2004,cb);gc=original;
    for(unsigned i=0;gc.stage&&i<40;i++) {
        assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&!key);
        gc.keys=key;nativeSetKeys(&mock,key);nativeAdvance(&mock);co.frames++;
        assert(!gc_observe(&mock,mockPixels,240,160));
    }
    assert(!gc.stage&&gc.uses==oldUses+1&&nativeState==10&&nativeEdges==1);
    assert(gc.released&&gc.printerFinished&&gc.taskDestroyed&&gc.fadeSeen&&gc.exitSeen&&gc.setupSeen&&gc.reshowEntrySeen&&gc.reshowSeen);
    mock.runFrame=advance;mock.setKeys=NULL;
}
static void medicineUse(unsigned swapped,unsigned recipient,unsigned quantity){
 unsigned key=999;
 memory[0xb2]=0;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0xb2]=2;
 memory[0x3884]=0;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0x3884]=1;
 put16(co.a.chosen,356);assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);put16(co.a.chosen,355);
 memory[0xc2]=0;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0xc2]=1;
 memory[0x3807]=128;assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&!key&&gc.stage==1);memory[0x3807]=0;
 memory[0x3404]=0;assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&!key&&gc.stage==1);memory[0x3404]=1;
 put32(0x2004,0x251);assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&!key&&gc.stage==1);put32(0x2004,0x161);
 assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&key==1&&gc.stage==2);
 medicineTask(0x180);put16(0xb0,378);assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);put16(0xb0,13);
 memory[0x38c2]=1;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0x38c2]=0;
 assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&key==1&&gc.stage==3);
 unsigned positions[6];assert(gc_order(memory+0xb4,positions));unsigned char reordered[600];gc_permute(gc.before.party,reordered,positions,0);memcpy(memory+0x1000,reordered,600);
 put32(0x2004,0x191);medicineTask(0x1a0);memory[0x3848]=0x11;memory[0x384b]=3;put32(0xc4,0x1b1);
 memory[0x384b]=0;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0x384b]=3;
 memory[0x3848]=0x10;assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);memory[0x3848]=0x11;
 put32(0xc4,0x251);assert(gc_buttons(&mock,&key,mockPixels,240,160)==105);put32(0xc4,0x1b1);
 if(swapped!=recipient){assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&key==128&&gc.stage==3);memory[0x3849]=1;}
 assert(!gc_buttons(&mock,&key,mockPixels,240,160)&&key==1&&gc.stage==4&&!gc.ack&&!gc.released&&!gc.printerFinished&&!gc.taskDestroyed&&!gc.fadeSeen&&!gc.reshowSeen);
 unsigned cap=gc.hp+20;if(cap>gc.max)cap=gc.max;
 put16(co.a.mons+(recipient?2:0)*88+40,cap);put16(0x1000+100*gc.slot+86,cap);put16(0x4490+0xd2,quantity-1);if(quantity==1)put16(0x4490+0xd0,0);
 medicineTask(0x1f0);put16(0x3408,gc.hp);put16(0x340a,gc.max);put16(0x340c,1);put16(0x340e,cap-gc.hp);put16(0x3410,gc.slot);put16(0x3412,gc.hp);
 assert(!gc_observe(&mock,mockPixels,240,160)&&gc.heals==1&&gc.stage==4);
 for(unsigned hp=gc.hp+1;hp<cap;hp++){put16(0x3408,hp);put16(0x340e,cap-hp);put16(0x1000+100*gc.slot+86,hp);assert(!gc_observe(&mock,mockPixels,240,160));}
 /* Complete native snapshot corruption, including all unused/Bag-hole bytes. */
 const unsigned bases[]={0x1000,0x5270,0x4490,0x539c,0x4238,0x4234};
 const unsigned lengths[]={600,300,1272,512,600,4};
 for(unsigned region=0;region<6;region++)for(unsigned off=0;off<lengths[region];off++){
  memory[bases[region]+off]^=1;assert(gc_observe(&mock,mockPixels,240,160)!=0);memory[bases[region]+off]^=1;
 }
 memory[0x5270+90]^=1;assert(gc_observe(&mock,mockPixels,240,160)==106);memory[0x5270+90]^=1;
 put16(0x340e,99);assert(gc_observe(&mock,mockPixels,240,160)==106);put16(0x340e,1);
 put16(0x1000+100*gc.slot+86,cap);medicineTask(0x210);memory[0xc8]=1;put32(0xcc,0x3900);put32(0x3904,0x1c1);memory[co.a.turn-16]=gc.healingCount+1;
 put16(0x4490+0xd2,99);assert(gc_observe(&mock,mockPixels,240,160)==106);put16(0x4490+0xd2,quantity-1);if(quantity==1)put16(0x4490+0xd0,0);
 put32(0x3904,0x231);assert(gc_observe(&mock,mockPixels,240,160)==105);put32(0x3904,0x1c1);
 assert(!gc_observe(&mock,mockPixels,240,160)&&gc.stage==5);
 lifecycleFinish(swapped,recipient,quantity);
}
static void twoSuccessive(void) {
 medicineSetup(1,0,2);medicineUse(1,0,2);assert(gc.uses==1&&gc.ack&&gc_quantity(gc.owned)==1);
 unsigned priorAck=gc.ackFrame;
 /* Synthetic ordinary enemy damage between turns; no latch/struct/core reset. */
 put16(0x1000+86,22);put16(co.a.mons+40,22);assert(!gc_read(&mock,&gc.before));co.before=gc.before;
 gc.stage=1;gc.start=co.frames;gc.turn++;put32(0x2004,gc.a.bagMain|1);medicineTask(gc.a.bagInput);
 memory[0x3849]=0;memory[0x3807]=0;assert(gc.ack&&gc.ackFrame==priorAck);
 medicineUse(1,0,1);assert(gc.uses==2&&gc.ackFrame>priorAck&&!gc_quantity(gc.owned));
 assert(walk_u16(gc.owned+0xd0)==0&&walk_u16(gc.owned+0xd2)==0&&walk_u16(gc.owned+0xd4)==378&&walk_u16(gc.owned+0xd6)==2);
 closeFiles();puts("PASS two successive Potion uses: per-use fresh edge reset, native closure, exact 2->1->0 hole and retained Scrap");

}
int main(int argc,char**argv){
 if(argc==2&&!strcmp(argv[1],"--medicine")){for(unsigned swapped=0;swapped<2;swapped++)for(unsigned recipient=0;recipient<2;recipient++)for(unsigned quantity=1;quantity<=2;quantity++){medicineSetup(swapped,recipient,quantity);medicineUse(swapped,recipient,quantity);closeFiles();}twoSuccessive();puts("PASS medicine native UI/animation/WAIT lifecycle mocks: 8 cases + 2 successive uses, all stages observed");return 0;}
 if(argc==3&&!strcmp(argv[1],"--choices")) {
  FILE*f=fopen(argv[2],"r");assert(f);unsigned c,cm,d,dm,g,n,s,b;
  while(fscanf(f,"%u %u %u %u %u %u %u %u",&c,&cm,&d,&dm,&g,&n,&s,&b)==8){printf("%u\n",gc_choice(c,cm,d,dm,g,n,s,b));}
  assert(!fclose(f));return 0;
 }
 if(argc==4&&(!strcmp(argv[1],"--remove")||!strcmp(argv[1],"--compact"))) {
  unsigned char raw[1272];FILE*f=fopen(argv[2],"rb");assert(f&&fread(raw,1,1272,f)==1272&&fgetc(f)==EOF&&!fclose(f));
  if(!strcmp(argv[1],"--remove"))assert(gc_remove(raw,0));else gc_compact(raw);
  f=fopen(argv[3],"wb");assert(f&&fwrite(raw,1,1272,f)==1272&&!fclose(f));return 0;
 }
 if(argc>1){
  setup();struct CoSnapshot before={0},after={0},actual={0};unsigned result;
  if(argc==3&&!strcmp(argv[1],"--snapshot")){
   readSnapshot(argv[2],&after);installSnapshot(&after);result=co_read(&mock,&actual);
   if(!result)assert(!memcmp(&actual,&after,sizeof after));
  }else{
   assert(argc==5&&!strcmp(argv[1],"--transition"));readSnapshot(argv[2],&before);readSnapshot(argv[3],&after);
   co.last=co.before=before;resource_canonical(gc.owned,before.owned,before.context);co.kind=(unsigned)strtoul(argv[4],NULL,10);co.armed=1;installSnapshot(&after);result=co_read(&mock,&actual);
   if(!result){assert(!memcmp(&actual,&after,sizeof after));result=co_field_validate(&actual);}
  }
  closeFiles();printf("INERT_VALIDATOR reason=%u\n",result);return result;
 }
 setup();struct CoSnapshot s={0};assert(!co_read(&mock,&s)&&!memcmp(&s,&co.last,sizeof s));

 put32(0x2600,0x171);memory[0x2604]=1;put16(0x260c,4);assert(!co_task_state(&mock,0x2600,0x170,2,5,65535));put16(0x260c,5);assert(co_task_state(&mock,0x2600,0x170,2,5,65535));
 put16(0x2608,0);assert(!co_task_state(&mock,0x2600,0x170,0,1,1));put16(0x2608,1);assert(co_task_state(&mock,0x2600,0x170,0,1,1));
 put32(0x2628,0x171);memory[0x262c]=1;assert(!co_task_state(&mock,0x2600,0x170,0,1,1));memory[0x262c]=0;
 put32(0x2004,0x181);assert(!recovery_field_ready(&mock,0x2000,0x160,0x2600,0x2680,0x170));
 put32(0x2004,0x161);memory[0x2687]=128;assert(!recovery_field_ready(&mock,0x2000,0x160,0x2600,0x2680,0x170));memory[0x2687]=0;
 assert(recovery_field_ready(&mock,0x2000,0x160,0x2600,0x2680,0x170));assert(!recovery_field_ready(&mock,0x2000,0x160,0x2600,0x2680,0x190));memory[0x2604]=0;
 put32(0x2004,0x121);
 saveReads=0;put32(0x200c,0);assert(!co_phase(&mock)&&co_read(&mock,&s)==80&&saveReads==0);put32(0x200c,0x131);
 memory[0x1000+33]^=1;assert(co_read(&mock,&s)==82);memory[0x1000+33]^=1;
 memory[0x1000+201]=1;assert(co_read(&mock,&s)==82);memory[0x1000+201]=0;
 put16(0xa000+2*(15+80*45),0xc00);assert(co_read(&mock,&s)==81);put16(0xa000+2*(15+80*45),0);
 assert(!co_read(&mock,&s));s.flags[83]^=1;assert(co_field_validate(&s)==83);s=co.last;s.owned[88]^=1;assert(co_field_validate(&s)==86);
 s=co.last;s.saved[201]=1;assert(co_field_validate(&s)==86);s=co.last;s.vars[90]=1;assert(co_field_validate(&s)==86);
 s=co.last;s.counter=1;walk_put16(s.vars+0x54,1);walk_put16(s.vars+0x56,1);assert(!co_field_validate(&s));
 s=co.last;s.counter=2;walk_put16(s.vars+0x54,2);walk_put16(s.vars+0x56,3);assert(co_field_validate(&s)==86);
 s=co.last;s.counter=4;walk_put16(s.vars+0x54,4);assert(co_field_validate(&s)==85);
 // Normal Potion changes only the unencrypted HP tail; the C guard accepts exactly
 // native checksum-derived encoding and capped healing on Donut.
 co.kind=CO_POTION;co.before=co.last;unsigned char a[100],b[100],plain[48];memcpy(a,co.last.party+100,100);walk_put16(a+86,walk_u16(a+88)-5);memcpy(b,a,100);walk_put16(b+86,walk_u16(b+88));
 memcpy(co.before.party+100,a,100);assert(co_mutable_member(1,a,b));b[20]^=1;assert(!co_mutable_member(1,a,b));b[20]^=1;
 (void)plain;closeFiles();
 mustStop(87,1);mustStop(87,2);mustStop(88,3);mustStop(88,4);mustStop(89,5);mustStop(89,6);mustStop(89,7);mustStop(90,8);mustStop(87,9);mustStop(87,10);mustStop(87,11);
 setup();co.motion=fopen("/dev/null","wb");co.kind=CO_GUARD;co.attempts=1;event=1;co_run(&mock,mockPixels,240,160);assert(co.attempts==2&&co.encounterFrames[1]==1);
 event=0;for(unsigned i=0;i<35998;i++){co.chunkFrames=0;co_run(&mock,mockPixels,240,160);}event=2;co_run(&mock,mockPixels,240,160);
 assert(co.encounterFrames[1]==36000&&advances==36000&&co.frames==36000);closeFiles();
 puts("PASS inert exact-host: source phase/pointer safety, full corruption negatives, walking/poison, Potion, terminal first-failure and36000 entry/interior/exit vector; zero emulators");return 0;
}
