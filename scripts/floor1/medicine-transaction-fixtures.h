/* Inert, independent instruction execution of the retained Thumb memcpy.
 * No mGBA core is initialised. Actual compiled opcodes come from the pinned ELF. */
static unsigned char txSavedMemory[65536],txSavedStack[0x8000];
static struct GcMedicine txSavedGc;
static struct GtTransaction txSavedGt;
static struct ARMCore txSavedCpu;
static unsigned txSavedFrame,txPositive,txNegative,txEquivalent,txSnapshotBytes,txPrefixes[26];
static void txSave(void){memcpy(txSavedMemory,memory,sizeof memory);memcpy(txSavedStack,txStack,sizeof txStack);txSavedGc=gc;txSavedGt=gtx;txSavedCpu=txCpu;txSavedFrame=co.frames;}
static void txRestore(void){memcpy(memory,txSavedMemory,sizeof memory);memcpy(txStack,txSavedStack,sizeof txStack);gc=txSavedGc;gtx=txSavedGt;txCpu=txSavedCpu;co.frames=txSavedFrame;}
static void txTaskFrame(unsigned sp,unsigned bytes,unsigned id){put32(sp,gc.a.tasks+40*id);put32(sp+4,gc.a.tasks);put32(sp+bytes-4,(GT_RUNTASKS+0x1e)|1);put32(sp+bytes+8,(GT_PARTY+6)|1);}
static void txCpuAt(unsigned pc,unsigned sp){memset(&txCpu,0,sizeof txCpu);txCpu.cpsr.packed=0x3f;txCpu.executionMode=MODE_THUMB;txCpu.privilegeMode=MODE_SYSTEM;txCpu.gprs[15]=pc+2;txCpu.gprs[13]=sp;}
static unsigned txCheck(void){unsigned positions[6];assert(gc_order(gc.order,positions));return gc_lifecycle(&mock,r32(&mock,co.a.main+4)&~1u,positions);}
static void txAcceptBoth(void){struct GcMedicine a=gc;struct GtTransaction b=gtx;struct ARMCore cpu=txCpu;unsigned before=advances;
 unsigned error=txCheck();if(error)fprintf(stderr,"transaction cut rejected pc=%08x sp=%08x err=%u\n",cpu.gprs[15]-2,cpu.gprs[13],error);assert(!error);txPositive++;gc=a;gtx=b;
 txCpu.bankedRegisters[BANK_NONE][0]=cpu.gprs[13];txCpu.bankedRegisters[BANK_NONE][1]=cpu.gprs[14];txCpu.spsr=cpu.cpsr;
 txCpu.gprs[14]=cpu.gprs[15]-2+4;txCpu.gprs[15]=0x1c;txCpu.gprs[13]=0x03007fa0;
 txCpu.cpsr.packed=(cpu.cpsr.packed&~255u)|0x92;txCpu.executionMode=MODE_ARM;txCpu.privilegeMode=MODE_IRQ;
 assert(!txCheck());txPositive++;assert(advances==before);gc=a;gtx=b;txCpu=cpu;
}
static void txReject(void){struct GcMedicine a=gc;struct GtTransaction b=gtx;unsigned before=advances;assert(txCheck()!=0);assert(advances==before);gc=a;gtx=b;txNegative++;}
static void txContextNegatives(unsigned sp){
 unsigned value=txCpu.gprs[15];txCpu.gprs[15]=GT_COPY+2;txReject();txCpu.gprs[15]=value;
 value=txCpu.executionMode;txCpu.executionMode=MODE_ARM;txReject();txCpu.executionMode=value;
 value=txCpu.privilegeMode;txCpu.privilegeMode=MODE_IRQ;txReject();txCpu.privilegeMode=value;
 value=txCpu.cpsr.packed;txCpu.cpsr.packed=0x33;txReject();txCpu.cpsr.packed=value;
 value=r32(&mock,sp);put32(sp,value^4);txReject();put32(sp,value);
 value=memory[gc.a.tasks+40*gtx.owner+8];memory[gc.a.tasks+40*gtx.owner+8]^=1;txReject();memory[gc.a.tasks+40*gtx.owner+8]=value;
 value=memory[gc.a.owner];memory[gc.a.owner]=0;txReject();memory[gc.a.owner]=value;
 value=memory[gtx.internal-16];memory[gtx.internal-16]=0;txReject();memory[gtx.internal-16]=value;
 struct ARMCore original=txCpu;
 txCpu.bankedRegisters[BANK_NONE][0]=original.gprs[13];txCpu.bankedRegisters[BANK_NONE][1]=original.gprs[14];txCpu.spsr=original.cpsr;
 txCpu.gprs[14]=original.gprs[15]+2;txCpu.gprs[15]=0x1c;txCpu.gprs[13]=0x03007fa0;txCpu.cpsr.packed=(original.cpsr.packed&~255u)|0x92;txCpu.executionMode=MODE_ARM;txCpu.privilegeMode=MODE_IRQ;
 value=txCpu.gprs[15];txCpu.gprs[15]=0x20;txReject();txCpu.gprs[15]=value;
 value=txCpu.gprs[13];txCpu.gprs[13]-=4;txReject();txCpu.gprs[13]=value;
 value=txCpu.spsr.packed;txCpu.spsr.packed=0x1f;txReject();txCpu.spsr.packed=value;
 value=txCpu.bankedRegisters[BANK_NONE][0];txCpu.bankedRegisters[BANK_NONE][0]+=4;txReject();txCpu.bankedRegisters[BANK_NONE][0]=value;
 txCpu=original;
}
static void txAcknowledged(void){gc.ack=gc.released=gc.printerFinished=gc.taskDestroyed=gc.fadeSeen=1;gc.ackFrame=co.frames-1;gc.keys=0;memory[gc_message(&mock)+27]=0;memory[0x342c]=0;}
static void txCreation(void){txRestore();nativeMessageSetup();put32(0x3400,gc.a.restored|1);txCpuAt(GT_RESTORED+0x2e,0x03006000);txCpu.gprs[5]=gtx.owner;txTaskFrame(0x03006000,12,gtx.owner);txAcceptBoth();txContextNegatives(0x03006000);
 for(unsigned off=0x12;off<=0x22;off+=2){txCpuAt(GT_DISPLAY+off,0x03005ff8);txCpu.gprs[4]=0;put32(0x03005ffc,(GT_RESTORED+0x2e)|1);txAcceptBoth();}
 const unsigned offsets[]={0x36,0x38,0x4c};
 for(unsigned i=0;i<3;i++){txCpuAt(GT_CREATE+offsets[i],0x03005fe4);txCpu.gprs[4]=gc.a.tasks+40;txCpu.gprs[5]=40;txCpu.gprs[6]=1;txCpu.gprs[7]=gc.a.tasks;put32(0x03005ff4,(GT_DISPLAY+0x12)|1);put32(0x03005ff8,0);put32(0x03005ffc,(GT_RESTORED+0x2e)|1);txAcceptBoth();}
}
static void txPrinting(void){txRestore();nativeMessageSetup();gc.ack=gc.released=1;gc.ackFrame=co.frames-1;memory[gc_message(&mock)+27]=0;gtx.wait=1;txCpuAt(GT_PRINTWAIT+0xe,0x03006000);txCpu.gprs[4]=txCpu.gprs[5]=1;txTaskFrame(0x03006000,12,1);txAcceptBoth();txContextNegatives(0x03006000);
 struct GcMedicine a=gc;assert(!txCheck()&&gc.printerFinished&&!gc.taskDestroyed&&!gc.exitSeen);gc=a;
 txTaskFrame(0x03006000,12,1);put32(0x03005ff8,1);put32(0x03005ffc,(GT_PRINTWAIT+0xe)|1);put32(0x03005ff4,(GT_TEXTRET+0xc)|1);put32(0x03005fe4,6);put32(0x03005fe8,1);
 for(unsigned off=0x70;off<=0x7c;off+=2){txCpuAt(GT_TEXT+off,0x03005fe0);txCpu.gprs[4]=1;txCpu.gprs[6]=216+(off>=0x72?36:0);txCpu.gprs[5]=gc_message(&mock)+4+(off>=0x74?36:0);txCpu.gprs[8]=gc_message(&mock)+(off>=0x78?36:0);txCpu.gprs[7]=25-(off>=0x7a?1:0);txAcceptBoth();unsigned old=txCpu.gprs[6];txCpu.gprs[6]+=36;txReject();txCpu.gprs[6]=old;}
}
static void txFading(void){txRestore();nativeMessageSetup();txAcknowledged();gc.fadeSeen=0;memory[gc.a.fade+7]=128;txCpuAt(GT_CLOSE+0x1a,0x03006000);txCpu.gprs[4]=gtx.owner;put32(0x03006000,0);put32(0x03006004,gtx.owner);put32(0x03006008,(GT_CLOSETEXT+0x26)|1);put32(0x0300600c,gc.a.tasks+40*gtx.owner);put32(0x03006010,(GT_RUNTASKS+0x1e)|1);put32(0x0300601c,(GT_PARTY+6)|1);txAcceptBoth();txContextNegatives(0x03006000);
 for(unsigned offset=0xb8;offset<=0x12c;offset+=2){unsigned valid=0;for(unsigned i=0;i<sizeof gtInstructionPoints/sizeof *gtInstructionPoints;i++)if(gtInstructionPoints[i]==GT_FADE+offset)valid=1;if(!valid)continue;
  txCpuAt(GT_FADE+offset,0x03005fe8);put32(0x03005fec,gtx.owner);put32(0x03005ffc,(GT_CLOSE+0x1a)|1);txAcceptBoth();}
}
static void txSnapshotNegatives(void){const unsigned bases[]={0x1000,0x5270,0x4490,0x539c,0x4238,0x4234};const unsigned lengths[]={600,300,1272,512,600,4};
 for(unsigned i=0;i<6;i++)for(unsigned j=0;j<lengths[i];j++){memory[bases[i]+j]^=1;txReject();memory[bases[i]+j]^=1;txSnapshotBytes++;}
 const unsigned metadata[]={0x60,0x4004,0x4005,0x53f0,0x80ac,0x2810,0x2812,0x2818,0x3214};
 for(unsigned i=0;i<sizeof metadata/sizeof *metadata;i++){memory[metadata[i]]^=1;txReject();memory[metadata[i]]^=1;txSnapshotBytes++;}
}
/* This small interpreter derives registers and writes directly from compiled
 * instruction encoding, rather than consuming the validator's microstate table. */
static unsigned txNz(unsigned flags,unsigned value){return (flags&0x30000000)|(value&0x80000000)|(value?0u:0x40000000);}
static unsigned txArithmetic(unsigned a,unsigned b,unsigned result,unsigned subtract){unsigned carry=subtract?a>=b:(unsigned long long)a+b>UINT_MAX;unsigned overflow=subtract?((a^b)&(a^result))>>31:((~(a^b))&(a^result))>>31;return txNz(0,result)|(carry<<29)|(overflow<<28);}
static void txRecord(unsigned record,const unsigned*positions){
 txRestore();nativeMessageSetup();txAcknowledged();medicineTask(gc.a.closeFade);gtx.wait=1;
 unsigned buffer=0xd000,sp=0x03006000;put16(buffer-16,1);put16(buffer-14,0xa3a3);put32(buffer-12,600);memcpy(memory+buffer,gc.healed.party,600);
 for(unsigned i=0;i<record;i++)memcpy(memory+co.a.party+100*positions[i],gc.healed.party+100*i,100);
 unsigned regs[16]={0};regs[0]=co.a.party+100*positions[record];regs[1]=buffer+100*record;regs[2]=100;regs[4]=record;regs[5]=buffer;regs[6]=100;regs[13]=sp;regs[14]=(GT_UPDATE+0x36)|1;
 put32(sp,gc.a.partyMenu);put32(sp+4,gtx.owner);put32(sp+12,(GT_CLOSEFADE+0x22)|1);txTaskFrame(sp+16,12,gtx.owner);
 unsigned pc=0,copied=0,left=0,right=0,flags=0;
 for(unsigned iteration=0;iteration<200;iteration++){
  txCpuAt(GT_COPY+pc,regs[13]);memcpy(txCpu.gprs,regs,sizeof regs);txCpu.gprs[15]=GT_COPY+pc+2;txCpu.cpsr.packed=flags|0x3f;
  txAcceptBoth();assert(!txCheck());txPositive++;
  txPrefixes[copied/4]++;
  unsigned old=memory[co.a.party+100*positions[record]];memory[co.a.party+100*positions[record]]^=1;txReject();memory[co.a.party+100*positions[record]]=old;
  old=memory[buffer+599];memory[buffer+599]^=1;txReject();memory[buffer+599]=old;
  old=txCpu.gprs[14];txCpu.gprs[14]^=4;txReject();txCpu.gprs[14]=old;
  old=txCpu.gprs[3];txCpu.gprs[3]+=4;if(pc>=0x8){txReject();}txCpu.gprs[3]=old;
  old=txCpu.cpsr.packed;for(unsigned bit=28;bit<32;bit++){txCpu.cpsr.packed=old^(1u<<bit);txReject();}txCpu.cpsr.packed=old;
  old=txCpu.gprs[0];txCpu.gprs[0]^=4;txReject();txCpu.gprs[0]=old;
  old=txCpu.gprs[2];txCpu.gprs[2]^=1;txReject();txCpu.gprs[2]=old;
  old=memory[buffer-16];memory[buffer-16]=0;txReject();memory[buffer-16]=old;
  unsigned prior=gtx.copyProgress;gtx.copyProgress=copied+100*record+4;txReject();gtx.copyProgress=prior;
  prior=gtx.copyBuffer;gtx.copyBuffer=buffer+4;txReject();gtx.copyBuffer=prior;
  if(pc==0x1c||pc==0x20||pc==0x24||pc==0x28||pc==0x36){
   /* Premature/skipped or duplicate previous writes must not match the exact
    * compiled image. Identical source/old words carry no observable history. */
   unsigned address=regs[1],word=r32(&mock,address),newWord=regs[0];put32(address,newWord);
   if(newWord!=word)txReject();else txEquivalent++;
   put32(address,word);
   if(copied){address=co.a.party+100*positions[record]+copied-4;word=r32(&mock,address);newWord=r32(&mock,buffer+100*record+copied);put32(address,newWord);if(newWord!=word)txReject();else txEquivalent++;put32(address,word);}
  }
  if(record==0&&pc==0x24&&copied==8){txSnapshotNegatives();txContextNegatives(regs[13]);}
  unsigned ins=txMemcpyOpcodes[pc/2],next=pc+2;
  if(ins==0xb530){regs[13]-=12;put32(regs[13],regs[4]);put32(regs[13]+4,regs[5]);put32(regs[13]+8,regs[14]);}
  else if(ins==0xbd30){assert(copied==100);return;}
  else if((ins&0xff00)==0x1c00){unsigned dst=ins&7,src=(ins>>3)&7;unsigned lhs=regs[src],rhs=(ins>>6)&7;regs[dst]=lhs+rhs;flags=txArithmetic(lhs,rhs,regs[dst],0);}
  else if((ins&0xf800)==0x2000){regs[(ins>>8)&7]=ins&255;flags=txNz(flags,ins&255);}
  else if((ins&0xf800)==0x3800){unsigned reg=(ins>>8)&7,lhs=regs[reg],rhs=ins&255;regs[reg]-=rhs;flags=txArithmetic(lhs,rhs,regs[reg],1);}
  else if((ins&0xffc0)==0x4300){regs[ins&7]|=regs[(ins>>3)&7];flags=txNz(flags,regs[ins&7]);}
  else if((ins&0xffc0)==0x4000){regs[ins&7]&=regs[(ins>>3)&7];flags=txNz(flags,regs[ins&7]);}
  else if((ins&0xffc0)==0x4240){unsigned rhs=regs[(ins>>3)&7];regs[ins&7]=0u-rhs;flags=txArithmetic(0,rhs,regs[ins&7],1);}
  else if((ins&0xf800)==0x2800){left=regs[(ins>>8)&7];right=ins&255;flags=txArithmetic(left,right,left-right,1);}
  else if((ins&0xffc0)==0x4280){left=regs[ins&7];right=regs[(ins>>3)&7];flags=txArithmetic(left,right,left-right,1);}
  else if((ins&0xff00)==0xcb00){assert((ins&255)==1);regs[0]=r32(&mock,regs[3]);regs[3]+=4;}
  else if((ins&0xff00)==0xc100){assert((ins&255)==1);put32(regs[1],regs[0]);regs[1]+=4;copied+=4;}
  else if((ins&0xf000)==0xd000){unsigned condition=(ins>>8)&15,take=condition==0?left==right:condition==1?left!=right:condition==8?left>right:condition==9?left<=right:0;assert(condition==0||condition==1||condition==8||condition==9);if(take)next=pc+4+2*(signed char)(ins&255);}
  else {fprintf(stderr,"unknown fixture opcode %04x at %x\n",ins,pc);assert(0);}
  pc=next;
 }
 assert(0);
}
static void txCleanup(void){const unsigned points[]={0x30,0x46,0x4a,0x4e,0x50,0x54};unsigned positions[6];assert(gc_order(gc.order,positions));
 for(unsigned i=0;i<6;i++){txRestore();nativeMessageSetup();txAcknowledged();medicineTask(gc.a.closeFade);unsigned char party[600];gc_permute(gc.healed.party,party,positions,1);memcpy(memory+co.a.party,party,600);put32(co.a.main+4,gc.a.exitBattle|1);if(i>=3)put16(gtx.internal-16,0);if(i==5)memory[0x3404]=0;txCpuAt(GT_CLOSEFADE+points[i],0x03006000);txCpu.gprs[4]=gc.a.partyMenu;txCpu.gprs[5]=gtx.owner;txTaskFrame(0x03006000,12,gtx.owner);txAcceptBoth();assert(!txCheck());assert(gc.exitSeen==(i==5));txPositive++;
  if(i>=3){/* A stale payload may be poisoned; it must never be followed. */unsigned old=r32(&mock,gtx.internal+4);put32(gtx.internal+4,0xffffffff);txAcceptBoth();put32(gtx.internal+4,old);put16(gtx.internal-16,1);txReject();put16(gtx.internal-16,0);}
  unsigned old=r32(&mock,0x03006008);put32(0x03006008,old^4);txReject();put32(0x03006008,old);
  old=memory[co.a.party+599];memory[co.a.party+599]^=1;txReject();memory[co.a.party+599]=old;
 }
 for(unsigned kind=0;kind<2;kind++)for(unsigned off=kind?0x1a:0xe;off<=(kind?0x6a:0x36);off+=2){unsigned fn=kind?GT_DESTROY:GT_FREEPOINTERS,valid=0;for(unsigned j=0;j<sizeof gtInstructionPoints/sizeof *gtInstructionPoints;j++)if(gtInstructionPoints[j]==fn+off)valid=1;if(!valid)continue;
  txRestore();nativeMessageSetup();txAcknowledged();medicineTask(gc.a.closeFade);unsigned char party[600];gc_permute(gc.healed.party,party,positions,1);memcpy(memory+co.a.party,party,600);put32(co.a.main+4,gc.a.exitBattle|1);put16(gtx.internal-16,0);if(kind)memory[0x3404]=0;
  unsigned sp=0x03006000-(kind?8:4);txCpuAt(fn+off,sp);txCpu.gprs[4]=kind?gc.a.tasks:gc.a.partyMenu;txCpu.gprs[5]=gtx.owner;txCpu.gprs[2]=gc.a.tasks+40*gtx.owner;
  if(kind){put32(sp,gc.a.partyMenu);}
  put32(sp+(kind?4:0),(GT_CLOSEFADE+(kind?0x54:0x4e))|1);txTaskFrame(0x03006000,12,gtx.owner);txAcceptBoth();assert(!gc.exitSeen);
 }
 txRestore();nativeMessageSetup();txAcknowledged();medicineTask(gc.a.closeFade);put32(co.a.main+4,gc.a.exitBattle|1);txCpuAt(GT_CLOSEFADE+0x54,0x03006000);txCpu.gprs[5]=gtx.owner;txTaskFrame(0x03006000,12,gtx.owner);txReject(); /* live owner/allocation: premature completion */
}
static void transactionCuts(void){unsigned initialAdvances=advances;txSave();txCreation();txPrinting();txFading();unsigned positions[6];assert(gc_order(txSavedGc.order,positions));for(unsigned i=0;i<6;i++)txRecord(i,positions);txCleanup();txRestore();assert(advances==initialAdvances);for(unsigned i=0;i<26;i++)assert(txPrefixes[i]);printf("PASS passive compiled transaction cuts use=%u positive=%u negative=%u snapshot_byte_negatives=%u legal_prefixes=26 unobservable_identical_words=%u\n",gc.uses+1,txPositive,txNegative,txSnapshotBytes,txEquivalent);}
