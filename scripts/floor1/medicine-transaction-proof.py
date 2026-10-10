"""Exact retained-instruction/host-layout binding; no emulator or game build."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01-medicine-transaction-offline-r3-20261010')
ELF=Path('/workspace/scratch/c01a-journal-art-r2-20261010/candidate-build/source/engine/pokeemerald.elf')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
LIB=TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
NAMES={'restored':'Task_DisplayHPRestoredMessage','display':'DisplayPartyMenuMessage','create':'CreateTask','printWait':'Task_PrintAndWaitForText','text':'RunTextPrinters','textRet':'RunTextPrintersRetIsActive','closeText':'Task_ClosePartyMenuAfterText','close':'Task_ClosePartyMenu','fade':'BeginNormalPaletteFade','closeFade':'Task_ClosePartyMenuAndSetCB2','update':'UpdatePartyToFieldOrder','copy':'memcpy','runTasks':'RunTasks','party':'CB2_UpdatePartyMenu','freePointers':'FreePartyPointers','destroy':'DestroyTask','setCB':'SetMainCallback2','free':'Free','getSlot':'GetPartyIdFromBattleSlot','waitVBlank':'WaitForVBlank','main':'AgbMain'}
def copy_steps():
 # Symbolic microstates of the exact aligned 100-byte Thumb memcpy. Values:
 # ANY0, DEST1, SOURCE2, WORD3, CONST4, BUFFER5, RECORD6, SOURCE|DEST8.
 regs=[(1,0),(2,0),(4,100),(0,0),(6,0),(5,0),(4,100)];copied=0;pushed=0;steps=[]
 def at(pc):
  flags=0
  if pc in (0xa,0xc):flags=0x20000000
  elif pc==0x14:flags=0x40000000
  elif pc in (0x16,0x18,0x3a,0x48,0x5a):flags=0x60000000
  elif pc in (0x1a,0x1c,0x1e,0x20,0x22,0x24,0x26,0x28,0x2a):flags=0 if copied<16 or (copied==16 and pc==0x2a) else 0x20000000
  elif pc==0x2c:flags=0x20000000
  elif pc==0x2e:flags=0x20000000 if regs[2][1]>15 else 0x80000000
  elif pc in (0x30,0x3c,0x3e,0x42,0x46):flags=0x80000000
  elif pc in (0x32,0x34,0x36,0x38):flags=0x20000000
  steps.append({'pc':pc,'copied':copied,'pushed':pushed,'flags':flags,'registers':[list(x) for x in regs]})
 at(0);pushed=1;at(2);regs[5]=(1,0);at(4);regs[4]=(1,0);at(6);regs[3]=(2,0);at(8);at(10);at(12);regs[0]=regs[3];at(14);regs[0]=(8,0);at(16);regs[1]=(4,3);at(18);regs[0]=(4,0);at(20);at(22);at(24);regs[1]=(1,0)
 remaining=100;source=0
 while remaining>15:
  for load,store in ((0x1a,0x1c),(0x1e,0x20),(0x22,0x24),(0x26,0x28)):
   at(load);regs[0]=(3,source);source+=4;regs[3]=(2,source);at(store);copied+=4;regs[1]=(1,copied)
  at(0x2a);remaining-=16;regs[2]=(4,remaining);at(0x2c);at(0x2e)
 at(0x30);at(0x32)
 while remaining>3:
  at(0x34);regs[0]=(3,source);source+=4;regs[3]=(2,source);at(0x36);copied+=4;regs[1]=(1,copied);at(0x38);remaining-=4;regs[2]=(4,remaining);at(0x3a);at(0x3c)
 at(0x3e);regs[4]=regs[1];at(0x40);regs[2]=(4,0xffffffff);at(0x42);regs[0]=(4,1);at(0x44);regs[0]=(4,0xffffffff);at(0x46);at(0x48);at(0x5a);regs[0]=(1,0);at(0x5c)
 assert copied==100 and source==100 and len({(x['pc'],x['copied']) for x in steps})==len(steps)
 return steps
def prove(out=OUT):
 assert sha(ELF)=='7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d'
 assert sha(LIB)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
 sym=module('tx_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py');bound=module('tx_bytes',ROOT/'scripts/floor1/v01-native-boundary-symbols.py');rows=sym.elf_symbols(ELF);functions={};instructions=[]
 for alias,name in NAMES.items():
  hits=[r for r in rows if r['name']==name and r['type']==2]
  if len(hits)>1:hits=[r for r in hits if r['scope']=='party_menu.o']
  assert len(hits)==1,(name,hits);r=hits[0];address=r['value']&~1
  dis=subprocess.check_output([str(TOOL/'usr/bin/arm-none-eabi-objdump'),'-d','--start-address='+hex(address),'--stop-address='+hex(address+r['size']),str(ELF)],text=True);(out/(name+'.asm')).write_text(dis)
  for line in dis.splitlines():
   match=re.match(r'\s*([0-9a-f]+):\s+[0-9a-f ]+\t(.*)',line)
   if match and not match[2].startswith('.'):
    instructions.append(int(match[1],16))
  functions[alias]={'name':name,'address':address,'size':r['size'],'scope':r['scope'],'compiled_SHA256':hashlib.sha256(bound.rom_bytes(ELF,address,r['size'])).hexdigest()}
 assert re.search(r'80004ba:.*bl\s+80008ac', (out/'AgbMain.asm').read_text())
 # CRT IRQ stack comes from the pinned ARM startup literal, not a host guess.
 init=[r for r in rows if r['name']=='Init'];irq_sp=[r for r in rows if r['name']=='sp_irq'];assert len(init)==len(irq_sp)==1
 assert int.from_bytes(bound.rom_bytes(ELF,irq_sp[0]['value'],4),'little')==0x03007fa0
 startup=subprocess.check_output([str(TOOL/'usr/bin/arm-none-eabi-objdump'),'-d','--start-address='+hex(init[0]['value']),'--stop-address='+hex(irq_sp[0]['value']+4),str(ELF)],text=True)
 (out/'startup.asm').write_text(startup);assert re.search(r'ldr\s+sp,.*<sp_irq>',startup)
 source=(ELF.parent/'src/party_menu.c').read_text();a=source.index('struct PartyMenuInternal\n');b=source.index('\n};',a)+3
 abi='#include "global.h"\n#include "task.h"\n#include "main.h"\n#include "palette.h"\n'+source[a:b]+'\nconst unsigned txInternalABI[]={sizeof(struct PartyMenuInternal),offsetof(struct PartyMenuInternal,exitCallback)};\n'
 (out/'party-internal-ABI.c').write_text(abi)
 pp=subprocess.check_output(['gcc','-E','-iquote','include','-iquote','src','-DMODERN=0','-I','tools/agbcc/include','-I','tools/agbcc','-nostdinc','-undef','-std=gnu89',str(out/'party-internal-ABI.c')],cwd=ELF.parent)
 assembly=subprocess.check_output([str(TOOL/'tools/agbcc/bin/agbcc'),'-mthumb-interwork','-Wimplicit','-Wparentheses','-Werror','-O2','-fhex-asm','-o','-','-'],input=pp,cwd=ELF.parent)
 (out/'party-internal-ABI.s').write_bytes(assembly+b'\n.text\n\t.align\t2, 0\n')
 subprocess.run([str(TOOL/'usr/bin/arm-none-eabi-as'),'-mcpu=arm7tdmi','--defsym','MODERN=0','-o',str(out/'party-internal-ABI.o'),str(out/'party-internal-ABI.s')],check=True)
 abi_data=subprocess.check_output([str(TOOL/'usr/bin/arm-none-eabi-objdump'),'-s','-j','.rodata',str(out/'party-internal-ABI.o')],text=True)
 assert '38020000 04000000' in abi_data,abi_data
 # Native source call sites and task stores remain exactly the audited binary.
 expected=json.loads(Path('/workspace/scratch/c01-medicine-sampling-audit-r1-20261010/native-observation-proof-private.json').read_text())
 for alias in ('restored','display','printWait','text','closeText','close','fade','closeFade','update','copy','freePointers','destroy','setCB'):
  assert functions[alias]['compiled_SHA256']==expected['functions'][NAMES[alias]]['compiled_SHA256']
 objects={}
 for alias,name in (('heap','gHeap'),('printers','sTextPrinters')):
  hits=[r for r in rows if r['name']==name and r['type']==1];assert len(hits)==1;objects[alias]={'address':hits[0]['value'],'size':hits[0]['size']}
 layout='''#include <stddef.h>
#include <stdio.h>
#include <mgba/core/core.h>
#include <mgba/internal/arm/arm.h>
int main(void){printf("%zu %zu %zu %zu %zu %zu %zu %zu\\n",offsetof(struct mCore,cpu),offsetof(struct ARMCore,gprs),offsetof(struct ARMCore,cpsr),offsetof(struct ARMCore,spsr),offsetof(struct ARMCore,bankedRegisters),offsetof(struct ARMCore,bankedSPSRs),offsetof(struct ARMCore,executionMode),offsetof(struct ARMCore,privilegeMode));}
'''
 (out/'cpu-layout.c').write_text(layout);subprocess.run(['cc','-Wall','-Wextra','-Werror','-I'+str(TOOL/'usr/include'),str(out/'cpu-layout.c'),'-o',str(out/'cpu-layout')],check=True)
 values=list(map(int,subprocess.check_output([str(out/'cpu-layout')],text=True).split()));assert values==[0,0,64,68,84,252,292,296],values
 for name,start,end in (('ARMRaiseIRQ',0xafa80,0xafb91),('ARMSetPrivilegeMode',0xaf6f0,0xaf820)):
  dis=subprocess.check_output(['objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(LIB)],text=True);(out/(name+'.asm')).write_text(dis)
 irq=(out/'ARMRaiseIRQ.asm').read_text();switch=(out/'ARMSetPrivilegeMode.asm').read_text()
 assert '$0x800000001c' in irq and '0x44(%rbx)' in irq and '$0x2,%r12d' in irq and '0x38(%rbx)' in irq
 assert 'mov    %r8,0x54(%rax,%rdi,4)' in switch and 'mov    0x54(%rax,%rdi,4),%rdi' in switch and 'mov    %rdi,0x34(%rax)' in switch # paired 64-bit SP/LR bank transfer
 header='#include <mgba/internal/arm/arm.h>\n'
 for name,value in zip(('CORE_CPU','CPU_GPRS','CPU_CPSR','CPU_SPSR','CPU_BANKS','CPU_BANKED_SPSR','CPU_MODE','CPU_PRIV'),values):header+='_Static_assert(offsetof('+('struct mCore,cpu' if name=='CORE_CPU' else 'struct ARMCore,'+{'CPU_GPRS':'gprs','CPU_CPSR':'cpsr','CPU_SPSR':'spsr','CPU_BANKS':'bankedRegisters','CPU_BANKED_SPSR':'bankedSPSRs','CPU_MODE':'executionMode','CPU_PRIV':'privilegeMode'}[name])+')=='+str(value)+',"exact retained CPU ABI");\n'
 for alias,r in functions.items():header+='#define GT_'+alias.upper()+' '+hex(r['address'])+'u\n'
 header+='static unsigned gtHeapBase='+hex(objects['heap']['address'])+'u,gtHeapSize='+str(objects['heap']['size'])+'u;\n'
 header+='static const unsigned gtInstructionPoints[]={'+','.join(hex(x)+'u' for x in sorted(set(instructions)))+'};\n'
 header+='struct GtCopyStep {unsigned pc,copied,pushed,flags;unsigned kind[7],value[7];};\nstatic const struct GtCopyStep gtCopySteps[]={\n'
 for st in copy_steps():header+='{'+','.join(map(str,(st['pc'],st['copied'],st['pushed'],str(st['flags'])+'u')))+',{'+','.join(str(x[0]) for x in st['registers'])+'},{'+','.join(str(x[1])+'u' for x in st['registers'])+'}},\n'
 header+='};\n';(out/'transaction-bindings.h').write_text(header)
 proof={'PASS':True,'class':'static retained binary/context proof plus symbolic aligned-copy microstates; no gameplay','ELF_SHA256':sha(ELF),'libmgba_SHA256':sha(LIB),'functions':functions,'objects':objects,'CPU_ABI':values,'IRQ_supported':'only fresh ARMRaiseIRQ entry at raw ARM PC0x1c, IRQ mode0x12/ARM, original SPSR system Thumb, untouched r0-r12 and BANK_NONE SP/LR; other interrupt contexts fail closed','IRQ_SP_required':0x03007fa0,'IRQ_interrupted_next_PC':'LR_irq-4','normal_next_PC':'raw Thumb PC-2','compiled_instruction_points':sorted(set(instructions)),'copy_steps':copy_steps(),'native_internal_ABI':[568,4],'native_internal_ABI_SHA256':sha(out/'party-internal-ABI.o'),'startup_SHA256':sha(out/'startup.asm'),'bindings_SHA256':sha(out/'transaction-bindings.h'),'copy_instruction_bytes':bound.rom_bytes(ELF,functions['copy']['address'],functions['copy']['size']).hex(),'runtime_frames':0}
 (out/'transaction-proof-private.json').write_text(json.dumps(proof,sort_keys=True,indent=2)+'\n');return proof
if __name__=='__main__':print(json.dumps({'PASS':prove()['PASS'],'gameplay_processes':0}))
