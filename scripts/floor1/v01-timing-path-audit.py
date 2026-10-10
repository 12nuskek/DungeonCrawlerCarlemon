"""Bounded read-only ELF/source timing identities, with local disassembly only."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
def module(n,p):s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=module('timingelf',root/'scripts/floor1/v01-native-boundary-symbols.py');selected_names=['AgbMain','UpdateLinkAndCallCallbacks','ReadKeys','CallCallbacks','PlayTimeCounter_Update','MapMusicMain','WaitForVBlank','VBlankIntr','IntrMain','BattleMainCB2','DccBattlePoseUpdate','IsPilot','Apply','Character','GetBattlerPosition','GetBattlerSide','AnimateSprites','AnimateSprite','RequestSpriteCopy','ProcessSpriteCopyRequests','VBlankCB_Battle','m4aSoundMain']
results={}
expected={'before':'2fb481bdb041772fef7aa0ed15deb6a30b7a24c54f9f6d487c2b733fe26fb066','after':'0bbce8cce6485cf6860ac19ce3b75b580ca8b2d5735909b40906f64c056eb98f'}
for case,path in [('before','artifacts/floor1/v01-overworld/build-registered/source/engine'),('after','artifacts/floor1/v01-battle/build-headers/source/engine')]:
 elf=root/path/'pokeemerald.elf';assert hashlib.sha256(elf.read_bytes()).hexdigest()==expected[case];symbols=m.symbols.elf_symbols(elf);functions=m.symbols.functions(symbols);d=out/case;d.mkdir(exist_ok=True);selected=[]
 for name in selected_names:
  rows=[r for r in functions if any(a.split(':')[-1]==name for a in r['aliases'])]
  if name in ['IsPilot','Apply','Character']:rows=[r for r in rows if any('dcc_battle_pose.o' in a for a in r['aliases'])]
  if not rows:continue
  assert len(rows)==1,(case,name);r=rows[0];r={**r,'compiled_SHA256':hashlib.sha256(m.rom_bytes(elf,r['address'],r['size'])).hexdigest()}
  # IntrMain is assembler NOTYPE and handled separately below.
  code=subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(r['address']),'--stop-address='+hex(r['address']+r['size']),str(elf)],text=True)
  (d/(name+'.asm')).write_text(code);selected.append(r)
 irq=[r for r in symbols if r['name']=='IntrMain'];assert len(irq)==1
 # Bound to copied native IRQ dispatcher length0x800; native code itself terminates earlier at literal pool.
 r=irq[0];address=r['value'];(d/'IntrMain.asm').write_text(subprocess.check_output(['arm-none-eabi-objdump','-d','--start-address='+hex(address),'--stop-address='+hex(address+0x15c),str(elf)],text=True))
 data_symbols=[]
 for name in ['gMain','gSprites','gMonSpritesGfxPtr','sDccBattlePoses','gBattlerSpriteIds','gBattlersCount','gBattleMons','gBattleTypeFlags','gTrainerBattleOpponent_A','gIntrTable','gSTWIStatus','gBattlerPositions','gAbsentBattlerFlags','gAnimScriptActive','gBattleAnimAttacker','IntrMain_Buffer','sSpriteCopyRequests','sSpriteCopyRequestCount','sShouldProcessSpriteCopyRequests']:
  rows=[r for r in symbols if r['name']==name]
  if rows:assert len(rows)==1;data_symbols.append({k:rows[0][k] for k in ['name','value','size','scope']})
 results[case]={'ELF_SHA256':hashlib.sha256(elf.read_bytes()).hexdigest(),'selected_functions':selected,'IntrMain':{'address':address,'native_source':'src/crt0.s','copied_to_IWRAM':'IntrMain_Buffer; original0x800 InitIntrHandlers transfer','dispatcher_excerpt_bytes':0x15c,'compiled_excerpt_SHA256':hashlib.sha256(m.rom_bytes(elf,address,0x15c)).hexdigest()},'synthetic_data_addresses':data_symbols,'source_SHA256':{p:hashlib.sha256((root/path/p).read_bytes()).hexdigest() for p in ['src/main.c','src/crt0.s','src/play_time.c','src/sound.c','src/battle_main.c','src/sprite.c']}}
(out/'elf-path-identities.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({case:{'ELF_SHA256':r['ELF_SHA256'],'selected_function_count':len(r['selected_functions']),'selected_functions':[{k:x[k] for k in ['aliases','address','size']} for x in r['selected_functions'] if any(a.split(':')[-1] in ['AgbMain','WaitForVBlank','DccBattlePoseUpdate','Apply','PlayTimeCounter_Update','MapMusicMain'] for a in x['aliases'])]} for case,r in results.items()}))
