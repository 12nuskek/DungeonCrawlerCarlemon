"""Independent source-event counterexample; synthetic bytes, no RNG or emulator."""
from pathlib import Path
import copy,hashlib,re,struct
ROOT=Path(__file__).resolve().parents[2]

def fixture(state,before):
    paths=('engine/src/pokemon.c','engine/src/battle_script_commands.c',
           'engine/src/battle_controller_player.c','engine/src/battle_util.c',
           'engine/src/battle_main.c','engine/data/battle_scripts_1.s',
           'engine/src/data/pokemon/experience_tables.h',
           'engine/src/data/pokemon/species_info.h','engine/src/data/battle_moves.h')
    sources={p:(ROOT/p).read_text() for p in paths}
    commands=sources[paths[1]];player=sources[paths[2]];util=sources[paths[3]]
    main=sources[paths[4]];scripts=sources[paths[5]]
    for token in ('damage = damage * gBattleMovePower;', 'damage *= (2 * attacker->level / 5 + 2);',
                  'damage = damage / damageHelper;', 'damage /= 50;', 'return damage + 2;',
                  'currentHP += newMaxHP - oldMaxHP;'):
        assert token in sources[paths[0]]
    for token in ('gBattleMoveDamage = gBattleMoveDamage * gCritMultiplier * gBattleScripting.dmgMultiplier;',
                  'u16 randPercent = 100 - (rand % 16);',
                  'calculatedExp = gSpeciesInfo[gBattleMons[gBattlerFainted].species].expYield * gBattleMons[gBattlerFainted].level / 7;',
                  '*exp = SAFE_DIV(calculatedExp, viaSentIn);',
                  'gBattleMoveDamage = (gBattleMoveDamage * 150) / 100;',
                  'gCurrentActionFuncId = B_ACTION_TRY_FINISH;',
                  'gBattleOutcome |= B_OUTCOME_WON;',
                  'gBattleMons[2].spAttack = GetMonData(&gPlayerParty[gBattleStruct->expGetterMonId], MON_DATA_SPATK);'):
        assert token in commands
    assert 'if (currExp + gainedExp >= nextLvlExp)' in player
    assert 'CalculateMonStats(mon);' in player
    assert 'if (!HandleFaintedMonActions())' in util
    assert 'BattleScriptExecute(BattleScript_GiveExp);' in util
    assert 'BattleScriptExecute(BattleScript_HandleFaintedMon);' in util
    assert 'if (gBattleOutcome != 0)\n        gCurrentActionFuncId = B_ACTION_FINISHED;' in main
    assert 'BattleScript_MoveEnd::\n\tmoveendall\n\tend' in scripts
    assert 'checkteamslost BattleScript_LinkHandleFaintedMonMultiple' in scripts
    growth=sources[paths[6]]
    assert '#define EXP_MEDIUM_FAST(n) (CUBE(n))' in growth
    assert '#define EXP_MEDIUM_SLOW(n) ((6 * CUBE(n)) / 5 - (15 * SQUARE(n)) + (100 * n) - 140)' in growth
    info=sources[paths[7]];moves=sources[paths[8]]
    powers={}
    for name in ('STRIKE','SPARK'):
        block=re.search(r'\[MOVE_DCC_'+name+r'\]\s*=\s*\{(.*?)\n    \}',moves,re.S)[1]
        powers[name]=int(re.search(r'\.power\s*=\s*(\d+)',block)[1])
    assert powers==dict(STRIKE=40,SPARK=50)
    rewards=[]
    for species in ('WHISMUR','ZIGZAGOON'):
        block=re.search(r'\[SPECIES_'+species+r'\]\s*=\s*\{(.*?)\n    \}',info,re.S)[1]
        xp=((int(re.search(r'\.expYield\s*=\s*(\d+)',block)[1])*9//7)//2)*150//100
        ev=[int(re.search(r'\.evYield_'+k+r'\s*=\s*(\d+)',block)[1]) for k in ('HP','Attack','Defense','Speed','SpAttack','SpDefense')]
        rewards.append((xp,ev))
    assert rewards==[(64,[1,0,0,0,0,0]),(57,[0,0,0,1,0,0])]
    current=copy.deepcopy(before);events=[]
    def member(i):return bytearray(state.fields.decode(current['party'][100*i:100*(i+1)])['canonical'])
    def install(i,c):
        raw=current['party'][100*i:100*(i+1)];party=bytearray(current['party'])
        party[100*i:100*(i+1)]=state.prior.encode(c,raw);current['party']=bytes(party)
    def spend(i):
        c=member(i);assert c[52]>0;c[52]-=1;install(i,c)
    def summary():
        return [dict(level=c[84],XP=struct.unpack_from('<I',c,36)[0],
                     HP=struct.unpack_from('<H',c,86)[0],maxHP=struct.unpack_from('<H',c,88)[0],
                     attack=struct.unpack_from('<H',c,90)[0],spatk=struct.unpack_from('<H',c,96)[0],
                     friendship=c[41],PP=list(c[52:56])) for c in (member(0),member(1))]
    def earned(index):
        xp_gain,ev=rewards[index]
        for i in range(2):
            c=member(i);xp=struct.unpack_from('<I',c,36)[0]+xp_gain;struct.pack_into('<I',c,36,xp)
            for j,v in enumerate(ev):c[56+j]+=v
            old_level=c[84];level=old_level
            # This fixture independently uses the source growth expressions;
            # it never calls the conservative outgoing audit/model.
            def threshold(l):return (6*l*l*l)//5-15*l*l+100*l-140 if i==0 else l*l*l
            while xp>=threshold(level+1):level+=1
            if level!=old_level:
                oldmax=struct.unpack_from('<H',c,88)[0];hp=struct.unpack_from('<H',c,86)[0]
                c[84]=level;stats=state.prior.level_stats(c,level)
                struct.pack_into('<7H',c,86,hp+stats[0]-oldmax,*stats)
                c[41]=state.friendship.level_ups(c[41],levels=level-old_level,met_location=c[69],section=current['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=struct.unpack_from('<H',c,34)[0],pokerus=c[68])
            install(i,c)
        events.append(dict(event='earned XP after faint',foe=index,XP_each=xp_gain,party=summary()))
    initial=summary();assert [(m['XP'],m['level'],m['attack'],m['spatk']) for m in initial]==[(627,10,25,12),(937,9,14,14)]
    # T0: 100% allowed rolls, critical spread SPARK. Direct native integer
    # expressions below are independent of audit.damage (no seed enumeration).
    spark=[max(1,14*powers['SPARK']*(2*9//5+2)//defense//50//2)+2 for defense in (9,12)]
    spark=[v*2 for v in spark];assert spark==[10,8];spend(1)
    foes=[30-spark[0],25-spark[1]]
    events.append(dict(turn=0,event='critical spread SPARK',damage=spark,foe_HP=foes.copy()))
    # Scuttler (speed16) acts before Carl (14), ordinary Tackle to Carl.
    tackle=(9*35*(2*9//5+2)//17//50+2)*15//10;assert tackle==4
    c=member(0);struct.pack_into('<H',c,86,struct.unpack_from('<H',c,86)[0]-tackle);install(0,c)
    events.append(dict(turn=0,event='ordinary Scuttler Tackle to Carl',damage=tackle))
    strike=(25*powers['STRIKE']*(2*10//5+2)//9//50+2)*2;assert strike==30
    spend(0);foes[0]=max(0,foes[0]-strike);assert foes==[0,17]
    events.append(dict(turn=0,event='critical STRIKE faints Howler',damage=strike,foe_HP=foes.copy()))
    earned(0);mixed=copy.deepcopy(current);middle=summary()
    assert [(m['XP'],m['level'],m['maxHP']) for m in middle]==[(691,10,36),(1001,10,30)]
    assert middle[0]['attack']==25 and middle[1]['spatk']==15
    # T1: faster Donut uses its last SPARK, single live target (no spread).
    spark_final=(middle[1]['spatk']*powers['SPARK']*(2*middle[1]['level']//5+2)//12//50+2)*2
    assert spark_final==18 and spark_final>=foes[1];spend(1);foes[1]=0
    events.append(dict(turn=1,event='critical single-target SPARK faints Scuttler',damage=spark_final,foe_HP=foes.copy()))
    earned(1)
    # Cmd_end -> TRY_FINISH -> faint XP/checkteamslost -> WON -> FINISHED:
    # no later Scuttler/Carl/Howler move or PP cost occurs on turn1.
    final=summary();assert [m['PP'] for m in final]==[[7,40,0,0],[0,40,0,0]]
    assert [(m['XP'],m['level'],m['maxHP']) for m in final]==[(748,11,38),(1058,10,30)]
    flags=bytearray(current['flags']);flags[2137//8]|=1<<(2137%8);current['flags']=bytes(flags)
    logical=bytearray(current['logical']);struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+360);current['logical']=bytes(logical)
    variables=bytearray(current['vars']);struct.pack_into('<H',variables,0x56,0);current['vars']=bytes(variables)
    assert current['saved']==mixed['saved']==before['saved'] and current['saved_count']==2
    return mixed,current,dict(PASS=True,synthetic_offline_only=True,RNG_search=False,
        conservative_planning_uses_criticals=False,source_SHA256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        initial=initial,events=events,mixed=middle,terminal=final,
        Carl_STRIKE_uses=1,Carl_PP=7,Donut_SPARK_uses=2,Carl_turn1_action=False,
        turn_termination='Cmd_end -> TRY_FINISH -> HandleFaintedMonActions -> checkteamslost WON -> RunTurnActionsFunctions FINISHED')
