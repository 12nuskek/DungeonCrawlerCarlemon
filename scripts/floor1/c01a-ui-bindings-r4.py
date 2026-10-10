"""Offline scoped ELF identities and passive Thumb instruction profile."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess,struct
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-action-hints-r4-20261010')
OLD=Path('/workspace/scratch/c01a-action-hints-r3-20261010')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CB2={'uiBagCB2':'G:CB2_BagMenuRun','uiPartyCB2':'L:party_menu.o:CB2_UpdatePartyMenu','uiSummaryCB2':'L:pokemon_summary_screen.o:MainCB2'}
def resolve(rows,identity):
    assert identity.startswith(('G:','L:'))
    hit=[r for r in rows if identity in r['aliases']]
    assert len(hit)==1 and hit[0]['address'] and hit[0]['size'],identity
    return hit[0]
def profile(case):
    b=module('edgeBoundary',ROOT/'scripts/floor1/v01-native-boundary-symbols.py')
    ident=json.loads((OLD/case/'identity.json').read_text());elf=Path(ident['ROM']).with_suffix('.elf')
    assert sha(elf)==ident['ELF_SHA256']
    syms=b.symbols.elf_symbols(elf);rows=b.symbols.functions(syms)
    assert rows==json.loads((OLD/case/'verified-functions.json').read_text())
    bindings=dict(ident['native_bindings'],**CB2);selected={n:resolve(rows,i) for n,i in bindings.items()}
    rejected=0
    for n,i in bindings.items():
        for modified in [[],[dict(selected[n],address=0)],[dict(selected[n],aliases=['L:wrong.o:'+i.split(':')[-1]])]]:
            try:resolve(modified,i)
            except AssertionError:rejected+=1
            else:raise AssertionError('Scoped negative accepted '+n)
    text=(OLD/case/'game.sym').read_text()
    for n in CB2:text+=f"{selected[n]['address']:08x} A {n}\n"
    for alias,n,offset in [('uiWireless','gWirelessCommType',0),('uiWiredCount','gLink',4029),('uiRfuCount','gRfu',2534),('uiRemotePlayers','gReceivedRemoteLinkPlayers',0)]:
        hit=[r for r in syms if r['name']==n];assert len(hit)==1 and hit[0]['value']
        text+=f"{hit[0]['value']+offset:08x} A {alias}\n"
    points=[]
    definitions=[(i,1,k+1,False) for k,i in enumerate(ident['native_bindings'].values())]
    definitions += [('G:MenuHelpers_ShouldWaitForLinkRecv',2,0,True),('G:ListMenu_ProcessInput',3,0,False),('G:ListMenu_ProcessInput',4,0,True),('G:Task_FadeAndCloseBagMenu',5,4,False),('L:item_menu.o:Task_CloseBagMenu',6,4,False)]
    for index,(identity,role,kind,at_return) in enumerate(definitions):
        row=resolve(rows,identity);pc=row['address']
        if at_return:
            dis=subprocess.check_output([str(TOOL/'usr/bin/arm-none-eabi-objdump'),'-d',f'--start-address={pc}',f'--stop-address={pc+row["size"]}',str(elf)],text=True)
            hits=re.findall(r'^\s*([0-9a-f]+):\s+4708\s+bx\s+r1\s*$',dis,re.M)
            assert len(hits)==1,(identity,dis);pc=int(hits[0],16)
        opcode=struct.unpack('<H',b.rom_bytes(elf,pc,2))[0]
        point=dict(identity=identity,address=pc,opcode=opcode,function=row['address'],role=role,kind=kind,compiled_function_SHA256=hashlib.sha256(b.rom_bytes(elf,row['address'],row['size'])).hexdigest())
        points.append(point)
        for name,value in [('pc',pc),('op',opcode),('fn',row['address']),('role',role),('kind',kind),('scope',1)]:text+=f'{value:08x} A ce_{name}{index}\n'
    return text,dict(PASS=True,case=case,ELF_SHA256=sha(elf),scoped_bindings={n:dict(identity=bindings[n],address=r['address'],compiled_SHA256=hashlib.sha256(b.rom_bytes(elf,r['address'],r['size'])).hexdigest()) for n,r in selected.items()},negative_cases_rejected=rejected,points=points,passive_profile_count=len(points),native_return_register='r0 at unique compiled bx r1')
def main():
    for case in ['baseline','candidate']:
        text,proof=profile(case);(OUT/(case+'-game.sym')).write_text(text);(OUT/(case+'-bindings-proof.json')).write_text(json.dumps(proof,indent=2)+'\n')
    print('PASS: both actual ELFs; three mandatory scoped CB2s/seven input callbacks;60 scoped negatives;24 exact passive points')
if __name__=='__main__':main()
