"""Scratch-only pinned compile/guard/cost experiment. No game build or gameplay."""
from pathlib import Path
import argparse,subprocess,hashlib,json,importlib.util,struct
root=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
base=root/'artifacts/floor1/v01-battle/build-headers/source/engine';out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256((base/'pokeemerald.elf').read_bytes()).hexdigest()=='0bbce8cce6485cf6860ac19ce3b75b580ca8b2d5735909b40906f64c056eb98f'
assert hashlib.sha256(Path('/usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5').read_bytes()).hexdigest()=='a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63'
spec=importlib.util.spec_from_file_location('auditelf',root/'scripts/floor1/v01-native-boundary-symbols.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
src=(base/'src/dcc_battle_pose.c').read_text();assert src==(root/'engine/src/dcc_battle_pose.c').read_text()
assert hashlib.sha256(src.encode()).hexdigest()=='ac641475290d4814b7b8211bfe7b1eed64dcb24a37af14ae27685e4c18858b12'
variant=src.replace('    sprite = &gSprites[id];','    if (state->applied == pose + 1) return;\n    sprite = &gSprites[id];').replace(' || state->applied == pose + 1','')
assert variant!=src
commands=[]
def run(cmd,**kw):commands.append(cmd);return subprocess.run(cmd,check=True,capture_output=True,**kw).stdout
for name,text in [('retained',src),('counterfactual',variant)]:
 (out/(name+'.c')).write_text(text)
 pp=run(['gcc','-E','-iquote','include','-iquote','src','-Wno-trigraphs','-DMODERN=0','-I','tools/agbcc/include','-I','tools/agbcc','-nostdinc','-undef','-std=gnu89',str(out/(name+'.c'))],cwd=base)
 p=run(['tools/preproc/preproc','-i','-g','build/assets',str(out/(name+'.c')),'charmap.txt'],input=pp,cwd=base)
 asm=run(['tools/agbcc/bin/agbcc','-mthumb-interwork','-Wimplicit','-Wparentheses','-Werror','-O2','-fhex-asm','-g','-o','-','-'],input=p,cwd=base)
 (out/(name+'.s')).write_bytes(asm+b'\n.text\n\t.align\t2, 0\n')
 run(['arm-none-eabi-as','-mcpu=arm7tdmi','--defsym','MODERN=0','-o',str(out/(name+'.o')),str(out/(name+'.s'))],cwd=base)
# Section bytes compare independent of debug paths.
def section(path,want):
 d=path.read_bytes();h=struct.unpack_from('<16sHHIIIIIHHHHHH',d);s=[struct.unpack_from('<10I',d,h[6]+i*h[11]) for i in range(h[12])];sh=s[h[13]];strings=d[sh[4]:sh[4]+sh[5]]
 for r in s:
  n=strings[r[0]:strings.index(0,r[0])].decode()
  if n==want:return d[r[4]:r[4]+r[5]]
 raise ValueError(want)
ret=section(base/'build/emerald/src/dcc_battle_pose.o','.text');assert ret==section(out/'retained.o','.text')
syms=m.symbols.elf_symbols(base/'pokeemerald.elf');defs={r['name']:r['value'] for r in syms if r['bind']==1}
# nm -u is narrowly bounded to one object, never an ELF-wide symbol listing.
undefined=run(['arm-none-eabi-nm','-u',str(out/'counterfactual.o')],text=True).splitlines();names=[r.split()[-1] for r in undefined]
(out/'audit.ld').write_text('SECTIONS { .text 0x08e3dae4 : { *(.text) } .rodata 0x08e3e3c4 : { *(.rodata) } ewram_data 0x0203cf68 : { *(ewram_data) } }\n')
posfn=[r for r in m.symbols.functions(syms) if 'G:GetBattlerPosition' in r['aliases']][0]
(out/'position.bin').write_bytes(m.rom_bytes(base/'pokeemerald.elf',posfn['address'],posfn['size']))
(out/'native-stubs.s').write_text('.syntax unified\n.thumb\n.section .native_position,"ax"\n.global GetBattlerPosition\n.type GetBattlerPosition,%function\n.thumb_func\nGetBattlerPosition:\n.incbin "'+str(out/'position.bin')+'"\n.section .native_cpuset,"ax"\n.global CpuSet\n.type CpuSet,%function\n.thumb_func\nCpuSet:\nbx lr\n.section .native_queue,"ax"\n.global RequestSpriteCopy\n.type RequestSpriteCopy,%function\n.thumb_func\nRequestSpriteCopy:\nbx lr\n')
run(['arm-none-eabi-as','-mcpu=arm7tdmi','-o',str(out/'native-stubs.o'),str(out/'native-stubs.s')])
ldtext=(out/'audit.ld').read_text().replace('SECTIONS {','SECTIONS { .native_position 0x080a6670 : { *(.native_position) } .native_cpuset 0x082ea928 : { *(.native_cpuset) } .native_queue 0x080074ec : { *(.native_queue) }')
(out/'audit.ld').write_text(ldtext)
for name in ['retained','counterfactual','native']:
 if name!='native':run(['arm-none-eabi-ld','-T',str(out/'audit.ld'),'-o',str(out/(name+'.elf')),str(out/(name+'.o')),str(out/'native-stubs.o')]+['--defsym='+n+'='+hex(defs[n]) for n in names if n not in ['GetBattlerPosition','CpuSet','RequestSpriteCopy']])
 elf=base/'pokeemerald.elf' if name=='native' else out/(name+'.elf')
 funcs=m.symbols.functions(m.symbols.elf_symbols(elf));rows=[r for r in funcs if any(a.endswith(':Apply') for a in r['aliases'])];assert len(rows)==1;r=rows[0]
 (out/(name+'-Apply.asm')).write_bytes(run(['arm-none-eabi-objdump','-d','--start-address='+hex(r['address']),'--stop-address='+hex(r['address']+r['size']),str(elf)]))
 # Bounded Apply/veneers/position and authored pose data only, never a loaded game.
 segments=[(r['address'],m.rom_bytes(elf,r['address'],r['size']))]
 targets=[]
 for i in range(0,r['size']-3,2):
  target=m.thumb_bl(r['address']+i,segments[0][1][i:i+4])
  if target:targets.append(target)
 pos=m.symbols.functions(syms);p=[x for x in pos if 'G:GetBattlerPosition' in x['aliases']][0]
 # Three compiled call veneers; no unbounded symbol or code export.
 for target in set(targets):
  b=m.rom_bytes(elf,target,16)
  segments.append((target,b))
 segments.append((p['address'],m.rom_bytes(base/'pokeemerald.elf',p['address'],p['size'])))
 segments.append((0x08e3e3c4,m.rom_bytes(base/'pokeemerald.elf',0x08e3e3c4,34884) if name=='native' else section(elf,'.rodata')))
 with (out/(name+'-segments.bin')).open('wb') as f:
  f.write(struct.pack('<II',r['address'],len(segments)))
  for address,b in segments:f.write(struct.pack('<II',address,len(b)));f.write(b)
 info={'Apply_address':r['address'],'Apply_bytes':r['size'],'Apply_SHA256':hashlib.sha256(segments[0][1]).hexdigest(),'segments':[{'address':a,'size':len(b)} for a,b in segments]}
 (out/(name+'-identity.json')).write_text(json.dumps(info,indent=2)+'\n')
result={'engine_unchanged':True,'retained_object_text_byte_match':True,'retained_text_SHA256':hashlib.sha256(ret).hexdigest(),'counterfactual_text_SHA256':hashlib.sha256(section(out/'counterfactual.o','.text')).hexdigest(),'native_source_SHA256':hashlib.sha256(src.encode()).hexdigest(),'counterfactual_source_SHA256':hashlib.sha256(variant.encode()).hexdigest(),'agbcc_SHA256':hashlib.sha256((base/'tools/agbcc/bin/agbcc').read_bytes()).hexdigest(),'commands':commands,'scope':'Scratch-only cost experiment; no game build, implementation or execution'}
(out/'compile-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='commands'}))

run(['gcc','-std=gnu11','-O2','-Wall','-Wextra','-Werror',str(root/'scripts/floor1/v01-pose-cost-fixture.c'),'-lmgba','-o',str(out/'fixture')])
traces={}
for name in ['native','retained','counterfactual']:
 r=subprocess.run([str(out/'fixture'),str(out/(name+'-segments.bin'))],capture_output=True,text=True)
 (out/(name+'-trace.jsonl')).write_text(r.stdout);(out/(name+'-stderr.txt')).write_text(r.stderr);r.check_returncode()
 traces[name]=[json.loads(x) for x in r.stdout.splitlines()];assert len(traces[name])==14 and all(x['PASS'] for x in traces[name])
assert traces['native']==traces['retained']
for a,b in zip(traces['native'],traces['counterfactual']):
 for key in ['samePose','guard','CpuSetCalls','copiedBytes','requested2048ByteTransfers','applied','PASS']:assert a[key]==b[key]
result.update({'cases':42,'native_retained_identical':True,'all_write_time_guards_preserved':True,'synthetic_bus_cost_only':True,'unchanged_pose':{name:next(x for x in rows if x['samePose']==1 and x['guard']==0) for name,rows in traces.items()}})
(out/'cost-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'PASS':True,'cases':42,'native_retained_identical':True,'unchanged_pose':result['unchanged_pose'],'scope':result['scope']}))
