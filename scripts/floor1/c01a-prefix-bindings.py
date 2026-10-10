"""Exact retained ELF instruction/RAM bindings for diagnostic prefixes only."""
from pathlib import Path
import importlib.util,json,hashlib,re,struct,subprocess,os
ROOT=Path(__file__).resolve().parents[2]
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=module('prefixNativeSymbols',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def profile(identity):
    elf=Path(identity['ROM']).with_suffix('.elf');assert sha(elf)==identity['ELF_SHA256']
    raw=native.symbols.elf_symbols(elf);functions=native.symbols.functions(raw)
    def fun(n):
        hits=[f for f in functions if n in f['aliases']];assert len(hits)==1 and hits[0]['size'],n;return hits[0]
    points=[];compiled={};env=dict(os.environ,LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
    def instructions(n):
        f=fun(n);code=native.rom_bytes(elf,f['address'],f['size']);compiled[n]={'address':f['address'],'size':f['size'],'SHA256':hashlib.sha256(code).hexdigest()}
        text=subprocess.check_output([str(TOOL/'usr/bin/arm-none-eabi-objdump'),'-d',f'--start-address={f["address"]}',f'--stop-address={f["address"]+f["size"]}',str(elf)],env=env,text=True)
        return f,text
    def point(n,name,offset,role):
        f=fun(n);assert 0<=offset<f['size'];pc=f['address']+offset;op=struct.unpack('<H',native.rom_bytes(elf,pc,2))[0]
        points.append(dict(name=name,identity=f['identity'],function=f['address'],size=f['size'],hash32=f['hash32'],pc=pc,rom=pc,opcode=op,mode=1,role=role))
    f,dis=instructions('L:battle_main.o:BattleMainCB1')
    for offset,label in [(6,'state-call'),(36,'controller-call')]:
        assert native.thumb_bl(f['address']+offset,native.rom_bytes(elf,f['address']+offset,4))==fun('G:_call_via_r0')['address']
        point('L:battle_main.o:BattleMainCB1',label+'-entry',offset,1);point('L:battle_main.o:BattleMainCB1',label+'-return',offset+4,2)
    definitions=[('L:battle_controller_player.o:PlayerBufferRunCommand','player-dispatch',3),
      ('L:battle_controller_player.o:PlayerHandleChooseMove','player-choose-move',3),
      ('G:InitMoveSelectionsVarsAndStrings','move-init',3),
      ('L:battle_controller_player.o:MoveSelectionDisplayPPString','PP-USES-printer',3),
      ('L:battle_controller_player.o:MoveSelectionDisplayMoveType','TYPE-hint-printer',3),
      ('G:BattlePutTextOnWindow','battle-text',10),('G:AddTextPrinter','synchronous-text',11),
      ('L:battle_controller_player.o:HandleChooseMoveAfterDma3','DMA-wait',3),
      ('L:battle_controller_opponent.o:OpponentBufferRunCommand','opponent-dispatch',3),
      ('L:battle_controller_opponent.o:OpponentHandleChooseAction','opponent-action',3),
      ('L:battle_controller_opponent.o:OpponentHandleChooseMove','opponent-move',3),
      ('L:battle_controller_opponent.o:OpponentBufferExecCompleted','opponent-complete',3),
      ('G:RequestDma3Copy','DMA-copy-request',7),('G:RequestDma3Fill','DMA-fill-request',7),
      ('G:ClearDma3Requests','DMA-clear',3),('G:ProcessDma3Requests','DMA-process',3),
      ('G:IsDma3ManagerBusyWithBgCopy','BG-busy-check',3),
      ('L:main.o:VBlankIntr','VBlank-IRQ',3),('G:VBlankCB_Battle','battle-VBlank',3),
      ('L:pokemon.o:GetSubstruct','GetSubstruct',3)]
    for n,label,role in definitions:
        f,dis=instructions(n);point(n,label+'-entry',0,role)
        exits=[int(a,16)-f['address'] for a in re.findall(r'^\s*([0-9a-f]+):\s+[0-9a-f]+\s+bx\s+r\d+\s*$',dis,re.M)]
        assert len(exits)==1,(n,exits)
        point(n,label+'-return',exits[0],8 if role==7 else 4)
        if n=='L:battle_controller_opponent.o:OpponentBufferExecCompleted':
            # Source non-link exec clear compiled as one store; bracket it exactly.
            stores=re.findall(r'^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+str\s+r\d+,\s*\[r\d+,\s*#0\]\s*$',dis,re.M)
            assert len(stores)==2,(n,stores)
            at=int(stores[-1][0],16)-f['address'];point(n,'opponent-bit-clear-before',at,5);point(n,'opponent-bit-clear-after',at+2,6)
    # Original timeline keeps its independently bound copied ARM IRQ point.
    # IntrMain is STT_NOTYPE, not a scoped STT_FUNC: do not invent one here.
    # New sidecar captures IRQ state/PC at every point and the scoped VBlankIntr.
    data=lambda n:[s for s in raw if s['name']==n and s['index']]
    irq=data('IntrMain_Buffer');intr=data('IntrMain');assert len(irq)==len(intr)==1 and irq[0]['size']==2048 and intr[0]['type']==0
    assert native.rom_bytes(elf,intr[0]['value'],4)==struct.pack('<I',0xe3a03301)
    variables=[('gActiveBattler',1),('gBattlersCount',1),('gBattleBufferA',2048),('gBattleControllerExecFlags',4),('gBattlerControllerFuncs',16),('gBattleMainFunc',4),('gMain',1084),('sDma3Requests',2048),('sDma3ManagerLocked',1),('sDma3RequestCursor',1),('sDmaBusyBitfield',16)]
    ram=[]
    for n,size in variables:
        hits=data(n);assert len(hits)==1 and hits[0]['size']==size,(n,hits)
        ram.append(dict(name=n,address=hits[0]['value'],size=size,scope=hits[0].get('scope')))
    source=elf.parent;request=(source/'src/dma3_manager.c').read_text();assert 'u16 size;\n    u16 mode;\n    u32 value;' in request
    # The compiled queue stride and size/mode offsets additionally bind ARM ABI.
    _,requestdis=instructions('G:RequestDma3Copy')
    assert 'lsls\tr0, r2, #4' in requestdis and '[r1, #8]' in requestdis and '[r1, #10]' in requestdis
    assert len(points)<=96
    rows=[f'{len(points):08x} A dg_count\n']
    for i,p in enumerate(points):
        for alias,key in [('pc','pc'),('rom','rom'),('op','opcode'),('mode','mode'),('fn','function'),('id','hash32'),('role','role'),('size','size'),('scope',None)]:rows.append(f'{(p[key] if key else 1):08x} A dg_{alias}{i}\n')
    for i,p in enumerate(ram):rows.append(f'{p["address"]:08x} A dg_data{i}\n')
    return ''.join(rows),dict(ELF_SHA256=sha(elf),ROM_SHA256=identity['ROM_SHA256'],points=points,compiled=compiled,RAM=ram,original_timeline_IRQ_binding={'runtime_pc':irq[0]['value'],'ROM_source':intr[0]['value'],'opcode':0xe3a03301,'ELF_type':'STT_NOTYPE; not claimed as STT_FUNC'},
      layouts={'Dma3Request':{'size':16,'src':0,'dest':4,'size_field':8,'mode':10,'value':12,'count':128},'BattleBufferA_stride':512,'Main_CB1':0,'Main_CB2':4,'TextPrinterTemplate':{'size':16,'currentChar':0,'window':4,'font':5},'stack_slice_bytes':32},
      source_files_SHA256={n:sha(source/'src'/n) for n in ['battle_main.c','battle_controller_player.c','battle_controller_opponent.c','battle_message.c','text.c','dma3_manager.c','bg.c','main.c']})
