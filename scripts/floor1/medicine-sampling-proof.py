"""Static retained-binary and frame-return proof; never creates an emulator."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess
ROOT=Path(__file__).resolve().parents[2]
AUDIT=Path('/workspace/scratch/c01-medicine-sampling-audit-r1-20261010')
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def native_proof(out):
 runner=module('sampling_runner',ROOT/'scripts/test-f1-c01-guard-choice-r2.py')
 symbols=module('sampling_symbols',ROOT/'scripts/floor1/v01-battle-symbols.py')
 boundary=module('sampling_bytes',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
 elf=runner.ENGINE/'pokeemerald.elf';lib=runner.TOOL/'usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5'
 assert sha(elf)==runner.ELF_SHA and sha(runner.ENGINE/'pokeemerald.gba')==runner.ROM_SHA
 assert sha(lib)=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
 rows=symbols.elf_symbols(elf);functions={}
 scopes={n:'party_menu.o' for n in ('Task_DisplayHPRestoredMessage','DisplayPartyMenuMessage','Task_PrintAndWaitForText','Task_ClosePartyMenuAfterText','Task_ClosePartyMenu','Task_ClosePartyMenuAndSetCB2','UpdatePartyToFieldOrder','FreePartyPointers')}
 scopes['DisplayPartyMenuMessage']=None
 scopes.update({'RunTextPrinters':None,'SetMainCallback2':None,'memcpy':None,'DestroyTask':None,'BeginNormalPaletteFade':None,'ResetSpriteData':None,'AgbMain':None,'CallCallbacks':None})
 for name,scope in scopes.items():
  hits=[r for r in rows if r['name']==name and r['type']==2 and (scope is None or r['scope']==scope)];assert len(hits)==1,(name,hits)
  r=hits[0];start=r['value']&~1
  text=subprocess.check_output([str(runner.TOOL/'usr/bin/arm-none-eabi-objdump'),'-d','--start-address='+hex(start),'--stop-address='+hex(start+r['size']),str(elf)],text=True)
  (out/(name+'.asm')).write_text(text)
  functions[name]={**r,'address':start,'compiled_SHA256':hashlib.sha256(boundary.rom_bytes(elf,start,r['size'])).hexdigest(),'disassembly_SHA256':hashlib.sha256(text.encode()).hexdigest()}
 def instruction(name,offset,token):
  text=(out/(name+'.asm')).read_text();address=functions[name]['address']+offset
  line=next(x for x in text.splitlines() if x.lstrip().startswith(f'{address:x}:'))
  assert token in line,(name,offset,token,line)
 # These are actual retained instructions, not just textual source order.
 instruction('Task_DisplayHPRestoredMessage',0x2a,'<DisplayPartyMenuMessage>')
 instruction('Task_DisplayHPRestoredMessage',0x44,'str\tr1, [r0, #0]')
 instruction('RunTextPrinters',0x6e,'strb\tr0, [r5, #23]')
 instruction('Task_PrintAndWaitForText',0xa,'<RunTextPrintersRetIsActive>')
 instruction('Task_PrintAndWaitForText',0x2c,'<ClearStdWindowAndFrameToTransparent>')
 instruction('Task_PrintAndWaitForText',0x38,'<DestroyTask>')
 instruction('BeginNormalPaletteFade',0xb6,'strb\tr0, [r5, #7]')
 instruction('Task_ClosePartyMenu',0x16,'<BeginNormalPaletteFade>')
 instruction('Task_ClosePartyMenu',0x26,'str\tr1, [r0, #0]')
 instruction('Task_ClosePartyMenuAndSetCB2',0x1e,'<UpdatePartyToFieldOrder>')
 instruction('Task_ClosePartyMenuAndSetCB2',0x2c,'<SetMainCallback2>')
 instruction('Task_ClosePartyMenuAndSetCB2',0x46,'<ResetSpriteData>')
 instruction('Task_ClosePartyMenuAndSetCB2',0x4a,'<FreePartyPointers>')
 instruction('Task_ClosePartyMenuAndSetCB2',0x50,'<DestroyTask>')
 instruction('SetMainCallback2',2,'str\tr0, [r1, #4]')
 instruction('UpdatePartyToFieldOrder',0x12,'<memcpy>')
 instruction('UpdatePartyToFieldOrder',0x32,'<memcpy>')
 instruction('UpdatePartyToFieldOrder',0x3e,'bls.n')
 for offset in (0x1c,0x20,0x24,0x28,0x36):instruction('memcpy',offset,'stmia\tr1!, {r0}')
 layout=json.loads((AUDIT/'host-layout.json').read_text())
 assert layout=={'core_cpu':0,'core_board':8,'core_runFrame':5080,'gba_video':3216,'gba_timing':6496,'video_frameCounter':2120,'ARMCore_gprs':0,'ARMCore_cpsr':64,'ARMCore_spsr':68,'ARMCore_mode':292}
 raw=lib.read_bytes();h=struct.unpack_from('<16sHHIQQQIHHHHHH',raw)
 def bytes_at(address,size):
  for i in range(h[10]):
   ph=struct.unpack_from('<IIQQQQQQ',raw,h[5]+i*h[9])
   if ph[0]==1 and ph[3]<=address and address+size<=ph[3]+ph[5]:return raw[ph[2]+address-ph[3]:ph[2]+address-ph[3]+size]
  raise AssertionError('unmapped native library address')
 assert struct.unpack('<Q',bytes_at(0x1d17a8,8))[0]==0xf18b0
 for name,start,end in [('mgba-core-create',0xf31d0,0xf36c0),('mgba-run-frame',0xf18b0,0xf191d),('mgba-arm-run-loop',0xafe70,0xaff9e)]:
  text=subprocess.check_output(['objdump','-d','--start-address='+hex(start),'--stop-address='+hex(end),str(lib)],text=True)
  (out/(name+'.asm')).write_text(text)
 create=(out/'mgba-core-create.asm').read_text();run=(out/'mgba-run-frame.asm').read_text();arm=(out/'mgba-arm-run-loop.asm').read_text()
 assert '# 1d17a8' in create and 'movups %xmm0,0x13d8(%rdx)' in create
 assert '0x14d8(%rbx)' in run and '<ARMRunLoop@plt>' in run and '$0x44e0f' in run
 assert layout['gba_video']+layout['video_frameCounter']==0x14d8 and layout['gba_timing']==0x1960
 assert 'call   *(%rdx,%rax,8)' in arm and 'jmp    *%rax' in arm # instruction dispatch, then event hook
 sources=json.loads((AUDIT/'source-downloads.json').read_text())
 for name,row in sources.items():assert row['url'].startswith('https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/') and sha(AUDIT/name)==row['SHA256']
 core=(AUDIT/'core.c').read_text();video=(AUDIT/'video.c').read_text();armSource=(AUDIT/'arm.c').read_text()
 assert 'gba->video.frameCounter == frameCounter' in core and 'VIDEO_TOTAL_LENGTH + VIDEO_HORIZONTAL_LENGTH' in core
 assert 'case GBA_VIDEO_VERTICAL_PIXELS:' in video and '++video->frameCounter;' in video
 assert 'while (cpu->cycles < cpu->nextEvent)' in armSource and 'cpu->irqh.processEvents(cpu);' in armSource
 assert 'cpu->gprs[ARM_PC] += WORD_SIZE_THUMB;' in armSource
 host=module('sampling_host',ROOT/'scripts/floor1/guard-choice-r2-host.py');code,_=host.generate(runner.git)
 assert hashlib.sha256(code.encode()).hexdigest()=='56c5f71914f2ecccb96d56eae2da0ae2e54b2769a80383a26bbd4dcbe897b153'
 assert code.count('->runFrame(')==1 and 'result=gc_observe(core,pixels,width,height);' in code
 textRow=[r for r in rows if r['name']=='gText_PkmnHPRestoredByVar2' and r['type']==1];assert len(textRow)==1
 textBytes=boundary.rom_bytes(elf,textRow[0]['value'],textRow[0]['size']);assert textBytes.endswith(bytes([0xfc,9,255]))
 assert [textBytes[i+1] for i,x in enumerate(textBytes[:-1]) if x==0xfd]==[2,3]
 (out/'native-restored-text.bin').write_bytes(textBytes)
 result={'PASS':True,'class':'static actual-binary/API reasoning; no gameplay or cycle-phase execution proof','gameplay_processes':0,'ELF_SHA256':runner.ELF_SHA,'ROM_SHA256':runner.ROM_SHA,'libmgba_SHA256':sha(lib),'functions':functions,'restored_text_SHA256':hashlib.sha256(textBytes).hexdigest(),'restored_text_source_native_placeholders':[2,3],'source_downloads':sources,'host_layout':layout,'runFrame_pointer_offset':5080,'runFrame_actual_library_address':0xf18b0,'frame_counter_board_offset':0x14d8,'runFrame_time_fallback_cycles':282128,'callback_completion_barrier':False,'instruction_granularity':True,'all_five_boundaries_not_excluded_by_API':True,'actual_frozen_route_cut_occurrence_proven':False,'frame_interrupt_PC_and_task_context_not_in_current_medicine_predicate':True,'native_party_copy_word_size':4,'current_native_sampling_admitted':False,'do_not_skip_party_validation':True}
 (out/'native-observation-proof-private.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result
