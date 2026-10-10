/* Actual generated production readers and Save handoff, synthetic native bus. */
static void howlerSetup(unsigned h,unsigned s,unsigned c,unsigned d,unsigned n) {
 setup();gcf=(struct GcFoeAddresses){0xc0,0xc4,0xc8};memory[gcf.count]=4;
 const unsigned species[]={66,370,52,288};
 for(unsigned i=0;i<4;i++){memory[gcf.positions+i]=i;put16(co.a.mons+88*i,species[i]);}
 put16(co.a.mons+40,c);put16(co.a.mons+44,36);put16(co.a.mons+2*88+40,d);put16(co.a.mons+2*88+44,28);
 put16(co.a.mons+88+40,h?30:0);put16(co.a.mons+88+44,30);put16(co.a.mons+3*88+40,s?25:0);put16(co.a.mons+3*88+44,25);
 gc.a.indexes=0x2c00;put16(gc.a.indexes,0);put16(gc.a.indexes+4,1);
 memory[co.a.mons+36]=8;memory[co.a.mons+37]=40;
 memset(gc.owned,0,1272);
  if(n){walk_put16(gc.owned+0xd0,13);walk_put16(gc.owned+0xd2,n);}
}
static void howlerIntegration(void) {
 unsigned checks=0;
 const unsigned vectors[][6]={{1,1,16,18,1,1},{1,1,17,18,1,0},{1,0,12,12,1,1},{1,0,13,12,0,0},
 {0,1,9,18,1,1},{0,1,10,18,0,0},{1,1,17,12,1,2},{0,1,10,12,1,2},
 {1,1,16,12,1,100},{1,1,16,18,0,101},{0,0,1,1,0,0},{1,1,0,18,1,90},{0,0,0,1,0,90}};
 for(unsigned h=0;h<2;h++)for(unsigned s=0;s<2;s++)for(unsigned absence=0;absence<2;absence++) {
  howlerSetup(h,s,17,18,1);memory[gcf.absent]=absence?(!h?2:0)|(!s?8:0):0;unsigned a,b;
  assert(!gc_decision(&mock,&a,&b)&&a==h&&b==s);checks++;closeFiles();
 }
 for(unsigned i=0;i<sizeof vectors/sizeof *vectors;i++) {
  const unsigned*v=vectors[i];howlerSetup(v[0],v[1],v[2],v[3],v[4]);unsigned h,s;
  assert(gc_decision(&mock,&h,&s)==v[5]);checks++;closeFiles();
 }
 for(unsigned i=0;i<13;i++) {
  howlerSetup(1,1,17,18,1);
  if(i==0)memory[gcf.count]=3;
  if(i==1)memory[gcf.positions+1]=3;
  if(i==2)put16(co.a.mons+88,308);
  if(i==3)put16(gc.a.indexes+4,0);
  if(i==4)put16(co.a.mons+88+40,31);
  if(i==5)put16(co.a.mons+3*88+40,26);
  if(i==6)put16(co.a.mons+88+44,29);
  if(i==7)put16(co.a.mons+3*88+44,24);
  if(i==8)memory[gcf.absent]=2;
  if(i==9)memory[gcf.absent]=8;
  if(i==10)memory[gcf.absent]=1;
  if(i==11)put16(co.a.mons+44,33);
  if(i==12)walk_put16(gc.owned+0xd2,2);
  unsigned h,s;assert(gc_decision(&mock,&h,&s)==103);checks++;closeFiles();
 }
 printf("PASS Howler actual native reader checks=%u four presence combinations\n",checks);
}
static void howlerSaveIntegration(void) {
 setup();memset(&hc,0,sizeof hc);hc.overwrite=0x170;hc.different=0xd2;
 const unsigned callback=0xd4,confirm=0x160,success=0x180,done=0x190,fade=0xe0,printer=0x300,menu=0x400;
 unsigned checks=0;
 for(unsigned stage=0;stage<3;stage++) {
  assert(!hc_save_key(1,1));checks++;
  assert(hc_save_key(1,1)==95);checks++;assert(!hc_save_key(0,1));
  put32(callback,0x999);assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu)==1);checks++;
  unsigned want=stage==0?confirm:stage==1?hc.overwrite:success;put32(callback,want|1);
  memory[printer+27]=1;assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu)==1);checks++;memory[printer+27]=0;
  memory[fade+7]=128;assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu)==1);checks++;memory[fade+7]=0;
  memory[hc.different]=1;assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu)==95);checks++;memory[hc.different]=0;
  if(stage<2){memory[menu+2]=1;assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu)==95);checks++;memory[menu+2]=0;}
  assert(!hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printer,menu));checks++;
  hc.saveStage++;
 }
 assert(hc.presses==3&&hc.saveStage==3&&hc_save_key(1,1)==95);checks++;
 memset(&hc,0,sizeof hc);assert(hc_save_key(1,2)==95&&hc_save_key(3,1)==95);checks+=2;
 memcpy(memory+0x600,"resolved\xff",9);memcpy(memory+0x700,"resolved\xff",9);
 assert(hc_text_exact(&mock,0x600,0x700));checks++;
 for(unsigned i=0;i<9;i++){memory[0x600+i]^=1;assert(!hc_text_exact(&mock,0x600,0x700));memory[0x600+i]^=1;checks++;}
 closeFiles();printf("PASS native same-file Save stateful readiness/edge handoffs checks=%u two confirmations plus menu entry\n",checks);
}
static void howlerTerminalIntegration(void) {
 const unsigned reasons[]={87,87,88,89,89,89,89,89,87};
 const unsigned expectedAdvances[]={0,0,0,1,1,0,1,1,0};
 for(unsigned mode=0;mode<9;mode++) {
  int pipefd[2];assert(!pipe(pipefd));fflush(NULL);pid_t child=fork();assert(child>=0);
  if(!child){close(pipefd[0]);report_fd=pipefd[1];assert(!atexit(report_advances));setup();
   if(mode==0)co.frames=co.limit;
   if(mode==1){co.cold=1;co.limit=co.frames=6000;}
   if(mode==2)put32(co.a.main+4,co.a.newGame);
   if(mode==3){co.kind=CO_HOWLER;event=1;put16(co.a.trainer,856);}
   if(mode==4){co.kind=CO_HOWLER;event=1;co.attempts=1;put16(co.a.trainer,857);}
   if(mode==5){co.kind=CO_GUARD;memory[co.a.main+0x439]=2;}
   if(mode==6){co.kind=CO_STABLE;event=1;put16(co.a.trainer,857);}
   if(mode==7){co.cold=1;co.kind=CO_COLD;event=1;put16(co.a.trainer,857);}
   if(mode==8){co.kind=CO_HOWLER;co.encounterFrames[2]=36000;memory[co.a.main+0x439]=2;}
   co_run(&mock,mockPixels,240,160);_exit(250);
  }
  close(pipefd[1]);unsigned observed[2];assert(read(pipefd[0],observed,sizeof observed)==sizeof observed);close(pipefd[0]);
  int status;assert(waitpid(child,&status,0)==child&&WIFEXITED(status)&&WEXITSTATUS(status)==(int)reasons[mode]);
  assert(observed[0]==expectedAdvances[mode]);
 }
 puts("PASS Howler native first-failure terminal cases=9 zero extra advances");
}
