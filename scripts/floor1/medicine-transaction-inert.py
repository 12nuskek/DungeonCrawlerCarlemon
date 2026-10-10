"""Extend the retained inert harness; never initialise an emulator."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate(observer,fixture_header):
 s=(ROOT/'scripts/floor1/guard-choice-r2-inert.c').read_text().replace('OBSERVER',str(observer))
 def once(a,b):
  nonlocal s
  assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
 once('static unsigned char memory[65536];','static unsigned char memory[65536],txStack[0x8000];\nstatic struct ARMCore txCpu;\nstatic unsigned txLifecycleError(unsigned e){return e==107||e==GT_ERROR;}')
 once('(void)c;assert(a<sizeof memory);','(void)c;if(a>=0x03000000&&a<0x03008000)return txStack[a-0x03000000];assert(a<sizeof memory);')
 once('static void put32(unsigned a,unsigned v){put16(a,v);put16(a+2,v>>16);}','static void put32(unsigned a,unsigned v){if(a>=0x03000000&&a+4<=0x03008000){memcpy(txStack+a-0x03000000,&v,4);return;}put16(a,v);put16(a+2,v>>16);}')
 once('co.limit=72000;co.kind=CO_STABLE;', 'co.limit=72000;co.kind=CO_STABLE;memset(txStack,0,sizeof txStack);memset(&txCpu,0,sizeof txCpu);mock.cpu=&txCpu;txCpu.cpsr.packed=0x3f;txCpu.executionMode=MODE_THUMB;txCpu.privilegeMode=MODE_SYSTEM;txCpu.gprs[15]=GT_WAITVBLANK+0x1a+2;txCpu.gprs[13]=0x03007000;put32(0x03007000,0x080004bf);gtHeapBase=0x3800;gtHeapSize=sizeof memory-gtHeapBase;')
 once('put32(0x2004,0x191);medicineTask(0x1a0);','put32(0x2004,0x191);medicineTask(0x1a0);put32(gc.a.internal,0x3900);put16(0x38f0,1);put16(0x38f2,0xa3a3);put32(0x38f4,568);')
 once('put32(gc.a.internal,0);nativeState=5;', 'put16(0x38f0,0);nativeState=5;')
 once('memory[0x342c]=1;put16(0x3430,0);','memory[0x342c]=1;memory[0x342f]=1;put16(0x3430,0);')
 once('static void lifecycleFinish(', '#include "'+str(fixture_header)+'"\nstatic void lifecycleFinish(')
 once('nativeMessageSetup();assert(!gc_observe', 'transactionCuts();nativeMessageSetup();assert(!gc_observe')
 s=s.replace('assert(gc_observe(&mock,mockPixels,240,160)==107)', 'assert(txLifecycleError(gc_observe(&mock,mockPixels,240,160)))')
 return s
