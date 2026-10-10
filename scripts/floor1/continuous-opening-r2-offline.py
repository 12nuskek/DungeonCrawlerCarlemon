"""Source-derived offline native trajectory. No emulator, input or runtime acceptance."""
from pathlib import Path
import copy, hashlib, json, re, struct, subprocess

ROOT=Path(__file__).resolve().parents[2]
RETAINED=Path('/workspace/scratch/c01-uninterrupted-unprepared-r1-20261010/opening/first-invalid-or-partial-state.bin')

def source_rewards():
    species=(ROOT/'engine/src/data/pokemon/species_info.h').read_text()
    parties=(ROOT/'engine/src/data/trainer_parties.h').read_text()
    commands=(ROOT/'engine/src/battle_script_commands.c').read_text()
    main=(ROOT/'engine/src/battle_main.c').read_text()
    assert 'calculatedExp = gSpeciesInfo[gBattleMons[gBattlerFainted].species].expYield * gBattleMons[gBattlerFainted].level / 7;' in commands
    assert '*exp = SAFE_DIV(calculatedExp, viaSentIn);' in commands
    assert 'gBattleMoveDamage = (gBattleMoveDamage * 150) / 100;' in commands
    assert 'moneyReward = 4 * lastMonLevel * gBattleStruct->moneyMultiplier * 2 * gTrainerMoneyTable[i].value;' in commands
    fallback=int(re.search(r'\{0xFF,\s*(\d+)\}',main)[1])
    assert fallback==5 and 'TRAINER_CLASS_PKMN_TRAINER_1,' not in main
    result={}
    for phase,title in [('trial','Trial'),('guard','Guard'),('howler','Howler'),('boss','Boss')]:
        body=re.search(r'sParty_Dcc'+title+r'\[\] = \{(.*?)\n\};',parties,re.S)[1]
        enemies=re.findall(r'\.lvl = (\d+), \.species = (SPECIES_\w+)',body)
        xp=0;ev=[0]*6
        for level,name in enemies:
            entry=re.search(r'\['+name+r'\]\s*=\s*\{(.*?)\n    \}',species,re.S)[1]
            value=int(re.search(r'\.expYield\s*=\s*(\d+)',entry)[1])
            xp+=((value*int(level)//7)//2)*150//100
            for i,suffix in enumerate(('HP','Attack','Defense','Speed','SpAttack','SpDefense')):
                ev[i]+=int(re.search(r'\.evYield_'+suffix+r'\s*=\s*(\d+)',entry)[1])
        result[phase]={'XP':xp,'EV':ev,'money':4*int(enemies[-1][0])*2*fallback}
    assert result=={'trial':{'XP':96,'EV':[1,0,0,1,0,0],'money':320},'guard':{'XP':132,'EV':[0,0,0,1,1,0],'money':320},'howler':{'XP':121,'EV':[1,0,0,1,0,0],'money':360},'boss':{'XP':226,'EV':[3,0,0,0,0,0],'money':360}}
    return result

def pack(d):
    values=[d['context'],d['counter'],d['count'],d['saved_count'],*d['map'],d['section'],*d['position'],d['facing']]
    return d['party']+d['flags']+d['owned']+d['vars']+d['saved']+struct.pack('<10I',*values)

def run(model,directory,executable,env,names,kinds,route):
    rewards=source_rewards();counts={'retained_snapshot_both_validators':0,'unused_slot_mutation_cases_both_validators':0,'phase_chain_both_validators':0,'phase_corruptions':0,'walking_native_transitions':0,'map_temp_lifecycle':0,'key_independent_resource_cases':0,'save_disk_cold_cases':0,'unsupported_Pokerus_strict_rejections':0}
    flags_source=(ROOT/'engine/include/constants/flags.h').read_text()
    expected_flags={'FLAG_DCC_INTRO_SEEN':32,'FLAG_DCC_CRATE_READ':33,'FLAG_DCC_ACH_READER':36,'FLAG_DCC_GUIDE_MET':34,'FLAG_DCC_ACH_DUO':37,'FLAG_DCC_LOOT_SUPPLY':38,'FLAG_DCC_LOOT_SCRAP':39,'FLAG_DCC_BOSS_CLEARED':47,'FLAG_DCC_SLICE_COMPLETE':48}
    for name,value in expected_flags.items():assert int(re.search(r'#define '+name+r'\s+(0x[0-9A-Fa-f]+)',flags_source)[1],16)==value
    native=(ROOT/'engine/src/pokemon.c').read_text();assert 'arg = MAIL_NONE;' in native
    assert re.search(r'#define MAIL_NONE\s+0xFF', (ROOT/'engine/include/constants/items.h').read_text())
    assert 'RandomlyGivePartyPokerus(gPlayerParty);' in (ROOT/'engine/src/battle_main.c').read_text()
    assert 'PartySpreadPokerus(gPlayerParty);' in (ROOT/'engine/src/battle_main.c').read_text()
    assert 'if (CheckPartyHasHadPokerus(mon, 0))\n            multiplier = 2;' in native
    assert 'SetMonData(&gPlayerParty[1], MON_DATA_ABILITY_NUM, &noAbilitySlot);' in (ROOT/'engine/src/crawler.c').read_text()
    assert re.search(r'\.abilities\s*=\s*\{ABILITY_PICKUP, ABILITY_NONE\}',re.search(r'\[SPECIES_MEOWTH\]\s*=\s*\{(.*?)\n    \}',(ROOT/'engine/src/data/pokemon/species_info.h').read_text(),re.S)[1]) and 'noAbilitySlot = 1' in (ROOT/'engine/src/crawler.c').read_text()
    growth=(ROOT/'engine/src/data/pokemon/experience_tables.h').read_text();assert '#define EXP_MEDIUM_FAST(n) (CUBE(n))' in growth and '#define EXP_MEDIUM_SLOW(n) ((6 * CUBE(n)) / 5 - (15 * SQUARE(n)) + (100 * n) - 140)' in growth
    avatar=(ROOT/'engine/src/field_control_avatar.c').read_text();assert '(*ptr) %= 128;' in avatar and '(*ptr) %= 4;' in avatar and 'AdjustFriendship(mon, FRIENDSHIP_EVENT_WALKING);' in avatar
    assert 'if (Random() & 1)' in native
    assert 'setvar VAR_TEMP_1, 1' in (ROOT/'engine/data/maps/DCC_F1D1Field/scripts.inc').read_text()
    opponents=(ROOT/'engine/include/constants/opponents.h').read_text()
    for trainer,number in [('TRIAL',855),('GUARD',856),('HOWLER',857),('BOSS',858)]:assert int(re.search(r'#define TRAINER_DCC_'+trainer+r'\s+(\d+)',opponents)[1])==number
    assert 'special HealPlayerParty' in (ROOT/'engine/data/maps/DCC_Vestibule/scripts.inc').read_text()
    healing=(ROOT/'engine/src/script_pokemon_util.c').read_text()
    for token in ('SetMonData(&gPlayerParty[i], MON_DATA_HP, arg);','CalculatePPWithBonus(GetMonData(&gPlayerParty[i], MON_DATA_MOVE1 + j), ppBonuses, j)','SetMonData(&gPlayerParty[i], MON_DATA_STATUS, arg);'):assert token in healing
    moves=(ROOT/'engine/src/data/battle_moves.h').read_text()
    for name,pp in [('STRIKE',8),('BRACE',40),('SPARK',2),('WEAKEN',40)]:assert int(re.search(r'\.pp\s*=\s*(\d+)',re.search(r'\[MOVE_DCC_'+name+r'\]\s*=\s*\{(.*?)\n    \}',moves,re.S)[1])[1])==pp
    assert 'memset(&gSaveBlock1Ptr->vars[TEMP_VARS_START - VARS_START], 0, TEMP_VARS_SIZE);' in (ROOT/'engine/src/event_data.c').read_text()


    def snapshot(raw,name='snapshot'):
        path=directory/(name+'.bin');path.write_bytes(raw);return model.snapshot(path)
    def c_snapshot(raw):
        path=directory/'native-read.bin';path.write_bytes(raw)
        return subprocess.run([str(executable),'--snapshot',str(path)],cwd=directory,env=env,capture_output=True,text=True).returncode
    def c_transition(before,after,kind):
        a=directory/'native-before.bin';b=directory/'native-after.bin';a.write_bytes(pack(before));b.write_bytes(pack(after))
        return subprocess.run([str(executable),'--transition',str(a),str(b),str(kind)],cwd=directory,env=env,capture_output=True,text=True).returncode
    def rejects(fn):
        try:fn()
        except AssertionError:return
        raise AssertionError('unexpected acceptance of offline corruption')
    def sync(d,key=None):
        if key is not None:d['context']=key
        d['owned']=model.prior.resources.canonical(d['logical'],struct.pack('<I',d['context']))
        # Every positive fixture passes through the actual Python snapshot path.
        return snapshot(pack(d))
    raw=RETAINED.read_bytes();state=snapshot(raw,'retained-STOP82-offline-only');assert c_snapshot(raw)==0
    assert state['saved_count']==0 and state['saved']==bytes(600);counts['retained_snapshot_both_validators']=1
    # Exhaustive arbitrary-byte mutation rejection in each unused native record.
    for slot in range(2,6):
        for offset in range(100):
            bad=bytearray(raw);bad[100*slot+offset]^=1
            rejects(lambda:snapshot(bad));assert c_snapshot(bad)==82;counts['unused_slot_mutation_cases_both_validators']+=1
        for mail in (0,1,254):
            bad=bytearray(raw);bad[100*slot+85]=mail
            rejects(lambda:snapshot(bad));assert c_snapshot(bad)==82;counts['unused_slot_mutation_cases_both_validators']+=1
    # All six member checksum damage cases, including occupied records.
    for slot in range(6):
        bad=bytearray(raw);bad[100*slot+28]^=1;rejects(lambda:snapshot(bad));assert c_snapshot(bad)==82
    assert len(model.EMPTY_POKEMON)==100 and model.EMPTY_POKEMON[85]==255

    def add_flags(d,values):
        f=bytearray(d['flags'])
        for v in values:f[v//8]|=1<<(v%8)
        d['flags']=bytes(f)
    def variables(d,offset,value):
        b=bytearray(d['vars']);struct.pack_into('<H',b,offset,value);d['vars']=bytes(b)
    def mutate_member(d,i,fn):
        raw=d['party'][100*i:100*i+100];c=bytearray(model.fields.decode(raw)['canonical']);fn(c)
        p=bytearray(d['party']);p[100*i:100*i+100]=model.prior.encode(c,raw);d['party']=bytes(p)
    def walk(d,event=True):
        after=copy.deepcopy(d);after['counter']=(d['counter']+1)%128;variables(after,0x54,after['counter']);variables(after,0x56,(struct.unpack_from('<H',d['vars'],0x56)[0]+1)%4)
        if after['counter']==0 and event:
            for i in range(2):
                def friendship(c):c[41]=model.friendship.target(c[41],event='WALKING',met_location=c[69],section=after['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15)
                mutate_member(after,i,friendship)
        after=sync(after);assert c_transition(d,after,1)==0;counts['walking_native_transitions']+=1;return after
    # Complete counter cycle, real source event and native random skip; no RNG read.
    walking=copy.deepcopy(state)
    for _ in range(128):walking=walk(walking)
    for _ in range(128):walking=walk(walking,event=False)
    bad=copy.deepcopy(walking);bad['counter']=3;variables(bad,0x54,3);assert c_transition(walking,sync(bad),1)==85
    bad=copy.deepcopy(walking);variables(bad,0x56,3);assert c_transition(walking,sync(bad),1)==86

    # Phase locations come from the unchanged authored route's actual expect records.
    anchors={};location=[35,0,8,38,1]
    for line in route.splitlines():
        if line.startswith('expect '):location=list(map(int,line.split()[1:]))
        if line.startswith('phase begin '):anchors[line[12:]]=location[:]
    sections=json.loads((ROOT/'engine/src/data/region_map/region_map_sections.json').read_text())
    rows=sections['map_sections'];section_ids={x['id']:i for i,x in enumerate(rows)}
    sections_by_map={i:section_ids[json.loads((ROOT/('engine/data/maps/'+n+'/map.json')).read_text())['region_map_section']] for i,n in [(0,'DCC_F1D1Field'),(1,'DCC_F1D1Quiet'),(3,'DCC_F1D1Warden'),(4,'DCC_F1D1Checkpoint')]}
    def relocate(d,location):
        d=walk(d);after=copy.deepcopy(d);after['map']=location[:2];after['position']=location[2:4];after['facing']=location[4];after['section']=sections_by_map[location[1]]
        if after['map']!=d['map']:variables(after,2,0)
        after=sync(after);assert c_transition(d,after,1)==0;counts['map_temp_lifecycle']+=1
        if after['map']==[35,0] and struct.unpack_from('<H',after['vars'],2)[0]==0:
            before=after;after=copy.deepcopy(before);variables(after,2,1);after=sync(after);assert c_transition(before,after,1)==0;counts['map_temp_lifecycle']+=1
        return after
    def battle(d,name):
        after=copy.deepcopy(d);reward=rewards[name]
        for i in range(2):
            def earned(c):
                xp=struct.unpack_from('<I',c,36)[0]+reward['XP'];struct.pack_into('<I',c,36,xp)
                for j,v in enumerate(reward['EV']):c[56+j]+=v
                oldlevel=level=c[84]
                threshold=lambda n:max(0,6*n**3//5-15*n*n+100*n-140) if i==0 else n**3
                while xp>=threshold(level+1):level+=1
                c[41]=model.friendship.level_ups(c[41],levels=level-oldlevel,met_location=c[69],section=after['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=0,pokerus=c[68]);c[84]=level
                stats=model.prior.level_stats(c,level);struct.pack_into('<7H',c,86,stats[0]-3,*stats);c[52]=max(0,c[52]-1)
            mutate_member(after,i,earned)
        logical=bytearray(after['logical']);struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+reward['money']);after['logical']=bytes(logical);variables(after,0x56,0)
        return after
    additions={'boot':[32],'note':[33,36],'supply':[38],'guide-initial':[34],'trial':[37,2135],'scrap':[39],'guard':[2136],'howler':[2137],'boss':[47,2138],'stairs-yes':[48]}
    for name,kind in zip(names,kinds):
        if name!='boot':state=relocate(state,anchors[name])
        before=state;after=copy.deepcopy(before);add_flags(after,additions.get(name,[]))
        if name=='boot':variables(after,2,1)
        elif name in rewards:
            after=battle(after,name)
        elif name in ('supply','scrap'):after['logical']=model.change_item(after['logical'],13 if name=='supply' else 378,2)
        elif name=='potion':
            def potion(c):
                hp,maxhp=struct.unpack_from('<HH',c,86);assert 0<hp<maxhp;struct.pack_into('<H',c,86,min(hp+20,maxhp))
            mutate_member(after,1,potion);after['logical']=model.change_item(after['logical'],13,-1)
        elif name.startswith('guide-'):
            for i in range(2):
                def heal(c):c[52:56]=bytes((8 if i==0 else 2,40,0,0));struct.pack_into('<I',c,80,0);c[86:88]=c[88:90]
                mutate_member(after,i,heal)
        elif name=='stairs-yes':after['map']=[35,4];after['position']=[4,4];after['section']=sections_by_map[4];variables(after,2,0)
        elif name=='save':after['saved']=after['party'];after['saved_count']=2
        after=sync(after);model.validate(name,before,after)
        numeric={'BOOT':0,'NOTE':2,'SUPPLY':3,'GUIDE':4,'TRIAL':5,'SCRAP':6,'POTION':7,'GUARD':8,'HOWLER':9,'BOSS':10,'STABLE':1,'STAIRS':11,'SAVE':12}[kind]
        assert c_transition(before,after,numeric)==0,(name,'C transition');counts['phase_chain_both_validators']+=1
        assert after['party'][200:]==state['party'][200:]==model.EMPTY_POKEMON*4
        if name!='save':assert after['saved']==bytes(600) and after['saved_count']==0
        for key,offset in [('party',20),('party',285),('flags',90),('vars',90),('logical',90),('saved',20)]:
            bad=copy.deepcopy(after);q=bytearray(bad[key]);q[offset]^=1;bad[key]=bytes(q)
            if key=='logical':bad['owned']=model.prior.resources.canonical(bad['logical'],struct.pack('<I',bad['context']))
            rejects(lambda:model.validate(name,before,bad))
            result=c_transition(before,bad,numeric)
            assert result==0 if name=='save' and key=='saved' else result!=0,(name,key,offset,result,'SAVE intermediate exemption is intentional')
            counts['phase_corruptions']+=1
        if name in rewards:
            pokerus=copy.deepcopy(after);mutate_member(pokerus,0,lambda c:c.__setitem__(68,0x11));pokerus=sync(pokerus)
            rejects(lambda:model.validate(name,before,pokerus));assert c_transition(before,pokerus,numeric)==85;counts['unsupported_Pokerus_strict_rejections']+=1
            doubled=copy.deepcopy(after)
            for i in range(2):
                def ev_double(c):
                    for j,v in enumerate(rewards[name]['EV']):c[56+j]+=v
                    stats=model.prior.level_stats(c,c[84]);struct.pack_into('<6H',c,88,*stats)
                mutate_member(doubled,i,ev_double)
            doubled=sync(doubled);rejects(lambda:model.validate(name,before,doubled));assert c_transition(before,doubled,numeric)==85;counts['unsupported_Pokerus_strict_rejections']+=1
        for key in (0,0xA15B3E4D,0xFFFFFFFF):
            rekey=sync(copy.deepcopy(after),key);assert rekey['logical']==after['logical'];assert c_transition(after,rekey,1)==0;counts['key_independent_resource_cases']+=1
        if name.startswith('guide-') and before['party']!=after['party']:
            partial=copy.deepcopy(after)
            member=next(i for i in range(2) if model.fields.decode(before['party'][100*i:100*i+100])['canonical'][86:88]!=model.fields.decode(after['party'][100*i:100*i+100])['canonical'][86:88])
            def incomplete_heal(c):c[86:88]=model.fields.decode(before['party'][100*member:100*member+100])['canonical'][86:88]
            mutate_member(partial,member,incomplete_heal);partial=sync(partial)
            rejects(lambda:model.validate(name,before,partial));assert c_transition(before,partial,numeric)==85
        state=after
    assert counts['phase_chain_both_validators']==18
    assert [model.fields.decode(state['party'][100*i:100*i+100])['fields']['experience'] for i in range(2)]==[974,1284]
    assert [model.fields.decode(state['party'][100*i:100*i+100])['fields']['level'] for i in range(2)]==[12,10]
    assert state['map']==[35,4] and state['position']==[8,6] and struct.unpack_from('<I',state['logical'])[0]==4360
    # CO_SAVE intermediate copied buffer is exempt in C, not continuously derived.
    intermediate=copy.deepcopy(before);intermediate['saved_count']=2;intermediate['saved']=state['party'][:100]+bytes(500)
    assert c_transition(before,intermediate,12)==0
    rejects(lambda:model.validate('save',before,intermediate));counts['save_disk_cold_cases']+=1
    save=native_save(state);path=directory/'chain-native-save.sav';path.write_bytes(save)
    assert model.disk_equivalence(path,snapshot(pack(state)))['PASS'];counts['save_disk_cold_cases']+=1
    for sector in range(14):
        bad=bytearray(save);bad[4096*sector]^=1;path.write_bytes(bad);rejects(lambda:model.disk_equivalence(path,state));counts['save_disk_cold_cases']+=1
    path.write_bytes(save)
    # Full native u32 persistence count, including upper bytes under valid CRCs.
    for value in (0,0x10002):
        badstate=copy.deepcopy(state);badstate['saved_count']=value;path.write_bytes(native_save(badstate))
        rejects(lambda:model.disk_equivalence(path,state));counts['save_disk_cold_cases']+=1
    path.write_bytes(save)
    cold=sync(copy.deepcopy(state),0xDEADBEEF)
    for key in ('party','count','counter','flags','vars','logical','saved','saved_count','map','position'):assert cold[key]==state[key]
    assert model.cold_equivalence(state,cold,path)['PASS'] and c_transition(state,cold,13)==0;counts['save_disk_cold_cases']+=1
    for key,offset in [('party',20),('saved',20),('flags',90),('vars',90),('logical',90)]:
        bad=copy.deepcopy(cold);q=bytearray(bad[key]);q[offset]^=1;bad[key]=bytes(q)
        rejects(lambda:model.cold_equivalence(state,bad,path));counts['save_disk_cold_cases']+=1
    for key in ('count','saved_count','counter'):
        bad=copy.deepcopy(cold);bad[key]+=1;rejects(lambda:model.cold_equivalence(state,bad,path));counts['save_disk_cold_cases']+=1
    for key in ('map','position'):
        bad=copy.deepcopy(cold);bad[key]=[0,0];rejects(lambda:model.cold_equivalence(state,bad,path));counts['save_disk_cold_cases']+=1
    # Exercise the very CLI used by the generated cold observer, on inert disk bytes.
    (directory/'game.sav').write_bytes(save);(directory/'expected-final-state.bin').write_bytes(pack(state));(directory/'current-state.bin').write_bytes(pack(cold))
    subprocess.run(['python3',str(ROOT/'scripts/floor1/continuous-opening-state.py'),'cold'],cwd=directory,env=env,check=True,stdout=subprocess.DEVNULL);counts['save_disk_cold_cases']+=1
    # No frame-boundary atomicity claim: partial native setter/heal states stay rejected.
    return dict(counts,source_rewards=rewards,retained_STOP82_SHA256=hashlib.sha256(raw).hexdigest(),old_runtime_success=False,gameplay_processes=0)

def native_save(d):
    sizes=[0xf2c]+[min(3968,0x3d88-i*3968) for i in range(4)]+[min(3968,0x83d0-i*3968) for i in range(9)]
    sb=bytearray(0x3d88);struct.pack_into('<hh',sb,0,*d['position']);sb[4:6]=bytes(d['map']);struct.pack_into('<I',sb,0x234,d['saved_count']);sb[0x238:0x490]=d['saved'];sb[0x490:0x988]=d['owned'];sb[0x1270:0x139c]=d['flags'];sb[0x139c:0x159c]=d['vars']
    sb2=bytearray(0xf2c);struct.pack_into('<I',sb2,0xac,d['context'])
    sectors=[bytes(sb2)]+[bytes(sb[i*3968:i*3968+sizes[i+1]]) for i in range(4)]+[bytes(sizes[i]) for i in range(5,14)]
    save=bytearray(b'\xff'*131072)
    for sid,data in enumerate(sectors):
        base=sid*4096;save[base:base+len(data)]=data;total=sum(struct.unpack('<'+str(len(data)//4)+'I',data))&0xffffffff;checksum=((total&65535)+(total>>16))&65535
        struct.pack_into('<HHII',save,base+0xff4,sid,checksum,0x08012025,1)
    return save
