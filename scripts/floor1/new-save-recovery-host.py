"""Separate parent-authorised fresh-input contract; preserve historical hosts."""
import importlib.util
import hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def generate(git):
    spec=importlib.util.spec_from_file_location('preserved_recovery_host', ROOT/'scripts/floor1/recovery-host.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    code, base=prior.generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='743ee603601c131046a1c270fe8240e84bd8f9d9aeda99d86d51d3781544163f'
    replace=prior.replace_once
    code=replace(code, 'int main(int argc, char **argv)',
        (ROOT/'scripts/floor1/new-save-potion-state.h').read_text()+'\nint main(int argc, char **argv)')
    code=replace(code, 'unsigned potionStage=0,',
        'unsigned potionHp=0, potionExpected=0, potionDonut=0, potionUses[4]={0}, moneyAnchor=0, haveMoney=0;\n    unsigned potionStage=0,')
    code=replace(code, '    FILE *symbols=fopen(argv[3], "r");',
        '    unsigned attacker=0, defender=0, currentMove=0, critical=0, moveDamage=0;\n    FILE *symbols=fopen(argv[3], "r");')
    anchor='        if (!strcmp(symbol,"gTasks")) tasks=addr;'
    code=replace(code, anchor, r'''
        if (!strcmp(symbol,"gBattlerAttacker")) attacker=addr;
        if (!strcmp(symbol,"gBattlerTarget")) defender=addr;
        if (!strcmp(symbol,"gCurrentMove")) currentMove=addr;
        if (!strcmp(symbol,"gCritMultiplier")) critical=addr;
        if (!strcmp(symbol,"gBattleMoveDamage")) moveDamage=addr;
'''+anchor)
    start=code.index('                        if (core->busRead16(core,trainer)!=856 || chp!=3 || dhp!=30')
    end=code.index('                        potionStage=1;', start)
    code=code[:start]+r'''
                        if (!new_save_potion_decision(core->busRead16(core,trainer),turn,actor,
                                chp,core->busRead16(core,party+0x58),dhp,owned_potions(core,pockets,save2ptr))
                            || core->busRead16(core,party+0x58)!=36 || core->busRead16(core,party+100+0x58)!=30
                            || party_pp(core,party,0)!=4 || party_pp(core,party,1)!=40
                            || party_pp(core,party+100,0)!=0 || party_pp(core,party+100,1)!=38
                            || core->busRead16(core,mons+0x58+0x28)!=0 || !core->busRead16(core,mons+3*0x58+0x28)
                            || core->busRead8(core,actionCursor)!=0) {
                            result=44;fprintf(stderr,"Fresh-save Potion decision preconditions failed; STOP\n");break;
                        }
                        potionHp=chp;potionDonut=dhp;
                        potionExpected=new_save_potion_hp(chp,core->busRead16(core,party+0x58));
                        potionUses[0]=party_pp(core,party,0);potionUses[1]=party_pp(core,party,1);
                        potionUses[2]=party_pp(core,party+100,0);potionUses[3]=party_pp(core,party+100,1);
                        result=capture("decision-before.ppm",pixels,width,height);if (result) break;
                        checks++;printf("PASS fresh Potion decision trainer=856 actor=0 turn=4 HP=%u expected=%u gain=%u DonutHP=%u owned=1 PP=4,40,0,38\n",
                            potionHp,potionExpected,potionExpected-potionHp,potionDonut);
''' + code[end:]
    code=replace(code, 'core->busRead16(core,party+0x56)!=23 || core->busRead16(core,mons+0x28)!=23',
        'core->busRead16(core,party+0x56)!=potionExpected || core->busRead16(core,mons+0x28)!=potionExpected')
    code=replace(code, 'checks++;printf("PASS Potion battle return HP=23 quantity=0 PP=4,40,0,38\\n");',
        'checks++;printf("PASS Potion battle return HP=%u quantity=0 PP=4,40,0,38\\n",potionExpected);')
    code=replace(code, 'if (chp!=23 || dhp!=30 || owned_potions(core,pockets,save2ptr)!=0',
        'if (chp!=potionExpected || dhp!=potionDonut || owned_potions(core,pockets,save2ptr)!=0')
    # PP expectations are observed at the decision; their exact 4/40/0/38 gate stays.
    for old,new in [('party_pp(core,party,0)!=4','party_pp(core,party,0)!=potionUses[0]'),
                    ('party_pp(core,party,1)!=40','party_pp(core,party,1)!=potionUses[1]'),
                    ('party_pp(core,party+100,0)!=0','party_pp(core,party+100,0)!=potionUses[2]'),
                    ('party_pp(core,party+100,1)!=38','party_pp(core,party+100,1)!=potionUses[3]')]:
        at=code.index('if (rescue && potionStage>0')
        code=code[:at]+code[at:].replace(old,new)
    code=replace(code, 'Potion did not heal20HP/consume exactly one/preserve PP', 'Potion did not heal min(20, missingHP)/consume exactly one/preserve PP')
    code=replace(code, 'checks++;printf("PASS Potion healed20HP Carl=3->23 inventory=1->0 PP unchanged\\n");',
        'checks++;printf("PASS Potion actual gain=%u Carl=%u->%u inventory=1->0 DonutHP=%u PP unchanged\\n",potionExpected-potionHp,potionHp,chp,dhp);')
    # Observe money values only; encryption material is neither logged nor exported.
    point='        if (!strcmp(line,"xp remember\\n") || !strcmp(line,"xp same\\n")) {'
    code=replace(code,point,r'''
        if (!strcmp(line,"money remember\n") || !strcmp(line,"money same\n") || !strncmp(line,"money gain ",11)) {
            unsigned now=core->busRead32(core,core->busRead32(core,saveptr)+0x490)
                ^core->busRead32(core,core->busRead32(core,save2ptr)+0xAC), gain=0;
            if (!strcmp(line,"money remember\n")) {moneyAnchor=now;haveMoney=1;printf("MONEY anchor=%u\n",now);continue;}
            if (!haveMoney || (strncmp(line,"money gain ",11)==0 && sscanf(line,"money gain %u %c",&gain,&extra)!=1)
                || now!=moneyAnchor+gain) {result=45;fprintf(stderr,"Money reward/idempotence mismatch\n");break;}
            checks++;printf("PASS money reward delta=%u actual=%u\n",gain,now);continue;
        }
''' +point)
    # Read-only per-frame HP transitions clarify damage/target/critical context without any input change.
    code=replace(code,'unsigned elapsed=0, lastTurn=UINT_MAX, capturedIncap=0;',
        'unsigned elapsed=0, lastTurn=UINT_MAX, capturedIncap=0, observedHp[4]={0};\n            if (!attacker || !defender || !currentMove || !critical || !moveDamage) {result=44;break;}\n            for (unsigned b=0;b<4;b++) observedHp[b]=core->busRead16(core,mons+b*0x58+0x28);')
    point='                unsigned chp=core->busRead16(core,party+0x56), dhp=core->busRead16(core,party+100+0x56);'
    code=replace(code,point,r'''
                for (unsigned b=0;b<4;b++) {
                    unsigned hp=core->busRead16(core,mons+b*0x58+0x28);
                    if (hp!=observedHp[b]) printf("HP transition frame=%u battler=%u from=%u to=%u attacker=%u target=%u move=%u criticalMultiplier=%u pendingDamage=%d\n",
                        total,b,observedHp[b],hp,core->busRead8(core,attacker),core->busRead8(core,defender),
                        core->busRead16(core,currentMove),core->busRead8(core,critical),(int)core->busRead32(core,moveDamage));
                    observedHp[b]=hp;
                }
''' +point)
    # Victory/no-incapacity remains required, now explicitly for each patrol.
    code=replace(code,'            checks++;\n            continue;\n        }\n        if (sscanf(line,"step',
        '            if (core->busRead8(core,outcome)!=1 || lastPilotIncap) {result=44;fprintf(stderr,"Patrol victory/no-incapacity assertion failed\\n");break;}\n            checks++;\n            continue;\n        }\n        if (sscanf(line,"step')
    assert not any(x in code for x in ['snapshot','STATE {','encryption_key','busWrite'])
    return code,base
