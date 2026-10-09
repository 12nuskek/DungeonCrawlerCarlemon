"""Verified ELF32 function identities; no compiler labels or guessed callbacks."""
from pathlib import Path
import hashlib,json,struct

# Routing addresses come from scoped ELF STT_FUNC identities, not nm names.
LIFECYCLE_FUNCTIONS={
    'firstTurn':'L:battle_main.o:HandleTurnActionSelectionState',
    'freeReset':'L:battle_main.o:FreeResetData_ReturnToOvOrDoEvolutions',
    'tryEvolve':'L:battle_main.o:TryEvolvePokemon',
    'returnBattle':'L:battle_main.o:ReturnFromBattleToOverworld',
    'endTrainer':'L:battle_setup.o:CB2_EndTrainerBattle',
    'continueScript':'G:CB2_ReturnToFieldContinueScriptPlayMapMusic',
    'returnLocal':'L:overworld.o:CB2_ReturnToFieldLocal',
    'fieldCB1':'G:CB1_Overworld','fieldCB2':'G:CB2_Overworld',
    'battleCB2':'G:BattleMainCB2',
    'waitFade':'L:field_screen_effect.o:Task_WaitForFadeAndEnableScriptCtx',
}

def lifecycle_symbols(rows):
    result=''
    for field,identity in LIFECYCLE_FUNCTIONS.items():
        matches=[r for r in rows if identity in r['aliases']]
        assert len(matches)==1, 'Missing/ambiguous source-pinned lifecycle function: '+identity
        result+=f"{matches[0]['address']:08x} V bv_{field}\n"
    return result

def elf_symbols(path):
    data=Path(path).read_bytes()
    header=struct.unpack_from('<16sHHIIIIIHHHHHH',data)
    assert header[0][:7]==b'\x7fELF\x01\x01\x01' and header[2]==40, 'Expected pinned ARM ELF32'
    sections=[struct.unpack_from('<10I',data,header[6]+i*header[11]) for i in range(header[12])]
    rows=[]
    for section in sections:
        if section[1]!=2:continue
        strings=sections[section[6]];table=data[strings[4]:strings[4]+strings[5]];scope=''
        assert section[9]==16
        for offset in range(section[4],section[4]+section[5],16):
            name,value,size,info,other,index=struct.unpack_from('<IIIBBH',data,offset)
            name=table[name:table.index(b'\0',name)].decode()
            if info&15==4:scope=name
            rows.append(dict(name=name,value=value,size=size,type=info&15,bind=info>>4,index=index,scope=scope))
    return rows

def functions(rows):
    groups={}
    for row in rows:
        # STT_FUNC is authority. NOTYPE .gcc2_compiled., mapping/data labels and
        # observer routing aliases are never admitted, even at a function address.
        if row['type']!=2 or not row['index'] or row['name'].startswith('.') or not row['name']:continue
        address=row['value']&~1
        assert 0x08000000<=address<0x0a000000, 'Function outside pinned executable ROM'
        assert row['bind'] in (0,1,2)
        if row['bind']==0:assert row['scope'], 'Unresolved local function scope'
        label=('L:'+row['scope']+':' if row['bind']==0 else 'G:')+row['name']
        groups.setdefault(address,[]).append((label,row['size']))
    result=[];identities={};hashes={}
    for address,aliases in sorted(groups.items()):
        labels=sorted({name for name,size in aliases});sizes={size for name,size in aliases if size}
        assert len(sizes)<=1, 'Ambiguous alias extents'
        identity='|'.join(labels)
        assert identity not in identities or identities[identity]==address, 'Ambiguous function identity/address'
        identities[identity]=address
        token='fn_'+hashlib.sha256(identity.encode()).hexdigest()
        hash32=2166136261
        for byte in token.encode():hash32=((hash32^byte)*16777619)&0xffffffff
        assert hash32 and (hash32 not in hashes or hashes[hash32]==identity), 'Callback ID collision'
        hashes[hash32]=identity
        result.append(dict(address=address,token=token,identity=identity,aliases=labels,size=next(iter(sizes),0),hash32=hash32))
    return result

def export(elf,output):
    rows=functions(elf_symbols(elf))
    Path(output).write_text(json.dumps(rows,indent=2)+'\n')
    return ''.join(f"{r['address']:08x} F {r['token']}\n" for r in rows)+lifecycle_symbols(rows)
