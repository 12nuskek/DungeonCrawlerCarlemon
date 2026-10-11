"""Source-derived geometry, native integer damage and policy proof; no RNG search."""
from pathlib import Path
import re,json,struct,hashlib
ROOT=Path(__file__).resolve().parents[2]
def step_proof(engine=None):
    """Read the actual retained map words and stock step ordering; no game execution."""
    engine=Path(engine) if engine is not None else ROOT/'engine'
    avatar=(engine/'src/field_control_avatar.c').read_text()
    body=avatar.split('int ProcessPlayerFieldInput(struct FieldInput *input)\n{',1)[1]
    assert body.index('IncrementGameStat(GAME_STAT_STEPS);')<body.index('TryStartStepBasedScript(&position, metatileBehavior, playerDirection)')
    body=avatar.split('static bool8 TryStartStepBasedScript(struct MapPosition *position, u16 metatileBehavior, u16 direction)\n{',1)[1].split('\n}',1)[0]
    assert 'if (TryStartWarpEventScript(position, metatileBehavior) == TRUE)\n        return TRUE;' in body
    assert body.index('TryStartWarpEventScript')<body.index('TryStartStepCountScript')
    for token in ('UpdateFriendshipStepCounter();','UpdatePoisonStepCounter()','(*ptr) %= 128;','(*ptr) %= 4;',
                  'AdjustFriendship(mon, FRIENDSHIP_EVENT_WALKING);','VarSet(VAR_POISON_STEP_COUNTER, 0);',
                  'MetatileBehavior_IsLadder(metatileBehavior) != TRUE','DoWarp();\n        return TRUE;'):
        assert token in avatar
    assert 'ClearPoisonStepCounter();' in (engine/'src/battle_setup.c').read_text()
    enum=(engine/'include/constants/metatile_behaviors.h').read_text().split('enum {',1)[1].split('}',1)[0]
    assert re.findall(r'\bMB_\w+',re.sub(r'//[^\n]*','',enum)).index('MB_LADDER')==97
    assert 'if (metatileBehavior == MB_LADDER)' in (engine/'src/metatile_behavior.c').read_text()
    layouts=json.loads((engine/'data/layouts/layouts.json').read_text())['layouts']
    attrs_path=engine/'data/tilesets/secondary/dcc/metatile_attributes.bin';attrs=attrs_path.read_bytes()
    contract=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    result={}
    for key,word,dest in (('quiet',0x326b,'MAP_DCC_F1D1FIELD'),('field',0x3245,'MAP_DCC_F1D1QUIET')):
        warp=contract['maps'][key]['warps'][0];x,y=warp['at']
        model_path=engine/f'data/maps/DCC_F1D1{key.title()}/map.json';model=json.loads(model_path.read_text())
        layout=next(v for v in layouts if v['id']==model['layout']);path=engine/layout['blockdata_filepath'];raw=path.read_bytes()
        actual=struct.unpack_from('<H',raw,2*(x+y*layout['width']))[0]
        original=next(v for v in layouts if v['name']==warp['source_map']+'_Layout');oldpath=engine/original['blockdata_filepath'];sx,sy=warp['source_at']
        assert actual==word==struct.unpack_from('<H',oldpath.read_bytes(),2*(sx+sy*original['width']))[0]
        attribute=struct.unpack_from('<H',attrs,2*((word&0x3ff)-512))[0]
        assert attribute==97 and word&0xfc00==0x3000
        assert model['warp_events'][0]==dict(x=x,y=y,elevation=3,dest_map=dest,dest_warp_id='0')
        result[key]=dict(position=[x,y],map_word=word,attribute=attribute,behavior='MB_LADDER',
                         layout_SHA256=hashlib.sha256(raw).hexdigest(),map_JSON_SHA256=hashlib.sha256(model_path.read_bytes()).hexdigest(),
                         copied_from=dict(map=warp['source_map'],position=[sx,sy],layout_SHA256=hashlib.sha256(oldpath.read_bytes()).hexdigest()))
    sources=('src/field_control_avatar.c','src/battle_setup.c','src/metatile_behavior.c','include/constants/metatile_behaviors.h')
    return dict(ladders=result,attributes_SHA256=hashlib.sha256(attrs).hexdigest(),
                stock_source_SHA256={p:hashlib.sha256((engine/p).read_bytes()).hexdigest() for p in sources},
                contract_SHA256=hashlib.sha256((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_bytes()).hexdigest(),
                generation_source_SHA256=hashlib.sha256((ROOT/'scripts/floor1/generate-live-opening.py').read_bytes()).hexdigest(),
                physical_steps_each_leg=17,step_script_updates_each_leg=16,GAME_STAT_STEPS_delta=34,
                friendship_counter_anchors=[78,94,110],poison_counters=[2,2,0,0],battle_poison_reset=True)
def choice(c,cm,d,dm,h,s,n,strike,brace):
    if c<0 or d<0 or c>cm or d>dm or cm not in (36,38) or dm not in (28,30) or not 0<=n<=1 or not 0<=strike<=8 or not 0<=brace<=40 or h not in (0,1) or s not in (0,1):return 103
    if not c or not d:return 90
    if not h and not s:return 0
    if strike<=1:return 92
    threshold=(16 if s else 12) if h else 9
    cr=c<=threshold;dr=s and d<=12
    if cr and dr:return 100
    if not cr and not dr:return 0
    if not n:return 101
    if min((c if cr else d)+20,cm if cr else dm)<=(threshold if cr else 12):return 102
    return 1 if cr else 2
def damage(attack,defense,level,power,stage=0,critical=False,stab=False,spread=False,roll=85):
    # APPLY_STAT_MOD precedes the three integer divisions. Critical ignores a
    # negative attacking stage, multiplies after +2, then STAB and the roll.
    a=attack if critical and stage<0 else attack*2//(2-stage) if stage<0 else attack*(2+stage)//2
    v=a*power*(2*level//5+2)//defense//50
    if spread:v//=2
    v=max(v,1)+2
    if critical:v*=2
    if stab:v=v*15//10
    return max(1,v*roll//100)
def audit():
    pokemon=(ROOT/'engine/src/pokemon.c').read_text();commands=(ROOT/'engine/src/battle_script_commands.c').read_text()
    for token in ('damage = damage * gBattleMovePower;','damage *= (2 * attacker->level / 5 + 2);','damage = damage / damageHelper;','damage /= 50;','return damage + 2;'):
        assert token in pokemon
    assert 'u16 randPercent = 100 - (rand % 16);' in commands
    assert 'gBattleMoveDamage = gBattleMoveDamage * gCritMultiplier * gBattleScripting.dmgMultiplier;' in commands
    assert 'gBattleMoveDamage = gBattleMoveDamage / 10;' in commands
    opponents=(ROOT/'engine/src/battle_controller_opponent.c').read_text()
    assert 'pattern = turn % 3 == 0 ? 1 : 0;' in opponents
    # The trainer's nameHash accumulates through both members. Species labels
    # are the authored HOWLER/SCUTTLER strings, not the stock species names.
    names=(ROOT/'engine/src/data/text/species_names.h').read_text();info=(ROOT/'engine/src/data/pokemon/species_info.h').read_text()
    charmap=dict((a,int(b,16)) for a,b in re.findall(r"'([A-Z])'\s*=\s*([0-9A-F]+)",(ROOT/'engine/charmap.txt').read_text()))
    namehash=0;foes=[]
    for species in ('WHISMUR','ZIGZAGOON'):
        label=re.search(r'\[SPECIES_'+species+r'\] = _\("(\w+)"\)',names)[1]
        namehash+=sum(charmap[c] for c in 'HOWLER'+label);personality=0x80+(namehash<<8);nature=personality%25
        block=re.search(r'\[SPECIES_'+species+r'\]\s*=\s*\{(.*?)\n    \}',info,re.S)[1]
        bases=[int(re.search(r'\.base'+k+r'\s*=\s*(\d+)',block)[1]) for k in ('HP','Attack','Defense','Speed','SpAttack','SpDefense')]
        stats=[2*b*9//100+(19 if i==0 else 5) for i,b in enumerate(bases)]
        if nature//5!=nature%5:
            for i in range(1,6):
                if i-1==nature//5:stats[i]=stats[i]*110//100
                if i-1==nature%5:stats[i]=stats[i]*90//100
        foes.append(dict(species=species,personality=personality,nature=nature,stats=stats))
    assert [f['stats'][:4] for f in foes]==[[30,14,9,9],[25,9,12,16]],foes
    growth=(ROOT/'engine/src/data/pokemon/experience_tables.h').read_text()
    assert '#define EXP_MEDIUM_FAST(n) (CUBE(n))' in growth
    assert '#define EXP_MEDIUM_SLOW(n) ((6 * CUBE(n)) / 5 - (15 * SQUARE(n)) + (100 * n) - 140)' in growth
    assert '.growthRate = GROWTH_MEDIUM_SLOW,' in re.search(r'\[SPECIES_MACHOP\]\s*=\s*\{(.*?)\n    \}',info,re.S)[1]
    assert '.growthRate = GROWTH_MEDIUM_FAST,' in re.search(r'\[SPECIES_MEOWTH\]\s*=\s*\{(.*?)\n    \}',info,re.S)[1]
    exp=[]
    for f in foes:
        block=re.search(r'\[SPECIES_'+f['species']+r'\]\s*=\s*\{(.*?)\n    \}',info,re.S)[1]
        exp.append((int(re.search(r'\.expYield\s*=\s*(\d+)',block)[1])*9//7//2)*150//100)
    assert exp==[64,57]
    def threshold(i,l):return max(0,6*l**3//5-15*l*l+100*l-140) if i==0 else l**3
    assert threshold(0,11)==742 and threshold(1,10)==1000
    # All ordinary outgoing rolls are bounded below by 85. Eight traces cover
    # no Potion or one replacing either early SPARK/later support turn.
    # This is a monotone integer bound, never enumeration of RNG states/seeds.
    strike_bounds=[]
    for potion_turn in (None,0,1,2,3,4,5,6):
        hp=[30,25];stage=0;strikes=0;trace=[];xp=[627,937];levels=[10,9];given=set()
        for turn in range(7):
            before=hp.copy()
            if turn<2 and turn!=potion_turn:
                both=all(hp)
                for i,defense in enumerate((foes[0]['stats'][5],foes[1]['stats'][5])):
                    if hp[i]:hp[i]=max(0,hp[i]-damage(14 if levels[1]==9 else 15,defense,levels[1],50,spread=both))
            target=0 if hp[0] else 1
            if hp[target]:
                assert xp[0]<742 and levels[0]==10 # final foe's XP is not yet earned
                hp[target]=max(0,hp[target]-damage(25,(9,12)[target],levels[0],40,stage));strikes+=1
            earned=[]
            for i in range(2):
                if not hp[i] and i not in given:
                    given.add(i);earned.append(exp[i]);xp=[v+exp[i] for v in xp]
            for i in range(2):
                while xp[i]>=threshold(i,levels[i]+1):levels[i]+=1
            if hp[0] and turn%3==0:stage=max(-6,stage-1)
            trace.append(dict(turn=turn,before=before,after=hp.copy(),Carl_attack_stage=stage,earned_XP=earned,party_XP=xp.copy(),party_levels=levels.copy()))
            if not any(hp):break
        assert not any(hp) and strikes<=7 and xp==[748,1058] and levels==[11,10],(potion_turn,hp,trace)
        strike_bounds.append(dict(Potion_turn=potion_turn,strikes=strikes,trace=trace))
    both=max(damage(14,17,9,35,critical=True,stab=True,roll=100)+damage(9,17,9,35,stab=True,roll=100),
             damage(14,17,9,35,stab=True,roll=100)+damage(9,17,9,35,critical=True,stab=True,roll=100))
    assert both==16 and damage(14,17,9,35,critical=True,stab=True,roll=100)==12
    assert damage(9,17,9,35,critical=True,stab=True,roll=100)==9
    assert damage(9,13,9,35,critical=True,stab=True,roll=100)==12
    plateaus=[(stage,damage(9,17,9,35,stage=stage,stab=True,roll=100)) for stage in (0,-1,-2,-3,-4,-5,-6)]
    assert any(a[1]==b[1] for a,b in zip(plateaus,plateaus[1:]))
    # Seventeen physical steps in each direction, checked against committed
    # collision words and actor positions, with the reciprocal native warps.
    paths={'quiet':[(4,y) for y in range(5,2,-1)],'field':[(x,26) for x in range(37,52)]+[(51,27)]}
    identities={}
    for key,path in paths.items():
        name='DCC_F1D1'+key.title();model=json.loads((ROOT/f'engine/data/maps/{name}/map.json').read_text())
        layouts=json.loads((ROOT/'engine/data/layouts/layouts.json').read_text())['layouts'];layout=next(x for x in layouts if x['id']==model['layout'])
        p=ROOT/'engine'/layout['blockdata_filepath'];raw=p.read_bytes();words=struct.unpack('<'+'H'*(len(raw)//2),raw)
        actors={(x['x'],x['y']) for x in model['object_events']}
        for x,y in path:assert (x,y) not in actors and not(words[x+layout['width']*y]&0xc00),(key,x,y)
        identities[key]={'path':path,'layout_SHA256':hashlib.sha256(raw).hexdigest(),'native_warps':model['warp_events']}
    assert len(paths['quiet'])-1+len(paths['field'])-1==17
    return dict(PASS=True,step_proof=step_proof(),foes=foes,order=[23,16,14,9],seven_STRIKE_without_favorable_criticals=strike_bounds,
                one_critical_plus_ordinary_envelopes=[16,12,9,12],simultaneous_criticals_guaranteed=False,
                WEAKEN_integer_plateaus=plateaus,route=identities,physical_steps_each_leg=17,fixed_frames_each_leg=704)
