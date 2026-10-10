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
 co.limit=100000;co.kind=CO_STABLE;
 FILE*f=fopen("fixture.bin","rb");assert(f&&fread(&co.last,1,sizeof co.last,f)==sizeof co.last&&!fclose(f));co.before=co.last;co.armed=1;
 memcpy(memory+0x1000,co.last.party,600);memory[0x60]=2;put32(0x50,0x4000);put32(0x54,0x8000);
 memory[0x4004]=35;memcpy(memory+0x5270,co.last.flags,300);memcpy(memory+0x4490,co.last.owned,1272);memcpy(memory+0x539c,co.last.vars,512);
 put32(0x2000,0x111);put32(0x2004,0x121);put32(0x200c,0x131);
 put32(0x3000+35*4,0x3100);put32(0x3100,0x3200);put16(0x2810,15);put16(0x2812,45);memory[0x2818]=1;
 put32(0x3300,80);put32(0x3304,60);put32(0x3308,0xa000);put16(0x92,858);
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
  if(mode==1)co.frames=100000;
  if(mode==2){co.kind=CO_BOSS;co.encounterFrames[3]=30000;memory[0x2439]=2;}
  if(mode==3)put32(0x2004,co.a.continueGame);
  if(mode==4){co.cold=1;put32(0x2004,co.a.newGame);}
  if(mode==5){co.kind=CO_BOSS;co.attempts=3;event=1;put16(0x92,859);}
  if(mode==6){co.kind=CO_BOSS;co.attempts=4;event=1;}
  if(mode==7){co.cold=1;co.kind=CO_COLD;event=1;}
  if(mode==8){co.kind=CO_BOSS;co.attempts=4;memory[0x2439]=2;put32(0x2004,co.a.battleMain);co.combatLoaded=1;}
  if(mode==9){co.kind=CO_GUARD;co.encounterFrames[1]=36000;memory[0x2439]=2;}
  if(mode==10){co.kind=CO_BOSS;co.attempts=3;co.encounterFrames[3]=29999;event=1;co_run(&mock,mockPixels,240,160);}
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
int main(int argc,char**argv){
 if(argc>1){
  setup();struct CoSnapshot before={0},after={0},actual={0};unsigned result;
  if(argc==3&&!strcmp(argv[1],"--snapshot")){
   readSnapshot(argv[2],&after);installSnapshot(&after);result=co_read(&mock,&actual);
   if(!result)assert(!memcmp(&actual,&after,sizeof after));
  }else{
   assert(argc==5&&!strcmp(argv[1],"--transition"));readSnapshot(argv[2],&before);readSnapshot(argv[3],&after);
   co.last=co.before=before;co.kind=(unsigned)strtoul(argv[4],NULL,10);co.armed=1;installSnapshot(&after);result=co_read(&mock,&actual);
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
 setup();co.motion=fopen("/dev/null","wb");co.kind=CO_BOSS;co.attempts=3;event=1;co_run(&mock,mockPixels,240,160);assert(co.attempts==4&&co.encounterFrames[3]==1);
 event=0;for(unsigned i=0;i<29998;i++){co.chunkFrames=0;co_run(&mock,mockPixels,240,160);}event=2;co_run(&mock,mockPixels,240,160);
 assert(co.encounterFrames[3]==30000&&advances==30000&&co.frames==30000);closeFiles();
 puts("PASS inert exact-host: source phase/pointer safety, full corruption negatives, walking/poison, Potion, terminal first-failure and30000 entry/interior/exit vector; zero emulators");return 0;
}
