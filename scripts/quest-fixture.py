#!/usr/bin/env python3
"""Explicit isolated GBA fixture: full Scrap stack/bag and trap HP boundary.
Never applied to production source; normal input tests quest refusal/retry.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "item.h"\n#include "script_pokemon_util.h"\n#include "constants/items.h"\n#include "constants/item.h"\nEWRAM_DATA u32 gDccRewardProbe = 0;\nstatic void PrepareQuestFixture(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    PrepareQuestFixture();')
s+='''
static void PrepareQuestFixture(void)
{
    u32 item, count = 1;
    u16 hp = 1;
    SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
    DccApplyServiceTrap();
    if (GetMonData(&gPlayerParty[0], MON_DATA_HP) == 1
        && GetMonData(&gPlayerParty[0], MON_DATA_STATUS) == STATUS1_PARALYSIS)
        gDccRewardProbe |= 1;
    HealPlayerParty();
    AddBagItem(ITEM_DCC_SCRAP, 98);
    for (item = 1; item < ITEMS_COUNT && count < gBagPockets[ITEMS_POCKET].capacity; item++)
        if (item != ITEM_DCC_SCRAP && GetItemPocket(item) == POCKET_ITEMS && AddBagItem(item, 1))
            count++;
    if (count == gBagPockets[ITEMS_POCKET].capacity
        && CountTotalItemQuantityInBag(ITEM_DCC_SCRAP) == 98
        && !AddBagItem(ITEM_DCC_SCRAP, 2)
        && CountTotalItemQuantityInBag(ITEM_DCC_SCRAP) == 98)
        gDccRewardProbe |= 2;
}
'''
p.write_text(s)
