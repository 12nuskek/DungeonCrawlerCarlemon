#!/usr/bin/env python3
"""Isolated GBA fixture: compare real base damage and exercise a full-inventory crate.
Never patch a production checkout; no debug grant or host RAM write ships in game.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "battle.h"\n#include "item.h"\n#include "constants/items.h"\n#include "constants/item.h"\n#include "constants/pokemon.h"\nEWRAM_DATA u32 gDccEquipmentProbe = 0;\nstatic void ProbeEquipment(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    ProbeEquipment();')
s+='''
static void ProbeEquipment(void)
{
    struct BattlePokemon attacker = {0};
    struct BattlePokemon defender = {0};
    u32 i, count = 0;
    s32 plain, wrapped;
    u16 savedMove = gCurrentMove, savedPower = gBattleMovePower;
    u8 savedCrit = gCritMultiplier;
    attacker.level = 8;
    attacker.attack = 20;
    defender.defense = 10;
    for (i = 0; i < NUM_BATTLE_STATS; i++)
    {
        attacker.statStages[i] = DEFAULT_STAT_STAGE;
        defender.statStages[i] = DEFAULT_STAT_STAGE;
    }
    gCurrentMove = MOVE_DCC_STRIKE;
    gCritMultiplier = 1;
    plain = CalculateBaseDamage(&attacker, &defender, MOVE_DCC_STRIKE, 0, 0, 0, 0, 1);
    attacker.item = ITEM_DCC_WRIST_WRAP;
    wrapped = CalculateBaseDamage(&attacker, &defender, MOVE_DCC_STRIKE, 0, 0, 0, 0, 1);
    if (plain == 10 && wrapped == 11)
        gDccEquipmentProbe |= 1;
    gCurrentMove = savedMove;
    gBattleMovePower = savedPower;
    gCritMultiplier = savedCrit;
    for (i = 1; i < ITEMS_COUNT && count < gBagPockets[ITEMS_POCKET].capacity; i++)
        if (i != ITEM_DCC_WRIST_WRAP && GetItemPocket(i) == POCKET_ITEMS && AddBagItem(i, 1))
            count++;
    if (count == gBagPockets[ITEMS_POCKET].capacity && !AddBagItem(ITEM_DCC_WRIST_WRAP, 1)
        && !CheckBagHasItem(ITEM_DCC_WRIST_WRAP, 1) && !FlagGet(FLAG_DCC_WRAP_TAKEN))
        gDccEquipmentProbe |= 2;
}
'''
p.write_text(s)
