#!/usr/bin/env python3
"""Fill an isolated test ROM's item pocket to exercise atomic two-Potion rewards.
No fixture/debug path is present in the production source.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "item.h"\n#include "constants/items.h"\n#include "constants/item.h"\nEWRAM_DATA u32 gDccRewardProbe = 0;\nstatic void PrepareRewardFixture(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    PrepareRewardFixture();')
s+='''
static void PrepareRewardFixture(void)
{
    u32 item, count = 0;
    for (item = 1; item < ITEMS_COUNT && count < gBagPockets[ITEMS_POCKET].capacity; item++)
        if (GetItemPocket(item) == POCKET_ITEMS && AddBagItem(item, 1))
            count++;
    // Existing Potion stack98, every slot occupied: a two-item reward cannot fit.
    if (count == gBagPockets[ITEMS_POCKET].capacity && AddBagItem(ITEM_POTION, 97)
        && CountTotalItemQuantityInBag(ITEM_POTION) == 98
        && !AddBagItem(ITEM_POTION, 2)
        && CountTotalItemQuantityInBag(ITEM_POTION) == 98
        && !FlagGet(FLAG_DCC_LOOT_SUPPLY))
        gDccRewardProbe = 1;
}
'''
p.write_text(s)
