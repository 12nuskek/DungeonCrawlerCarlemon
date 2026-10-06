#!/usr/bin/env python3
"""Explicit isolated inventory limits fixture, never production gameplay.
Start with Scrap98, Charge99, SuperPotion99, all item slots occupied and the R02
workshop achievement unlocked. Normal input tests each actual refusal/retry script.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "item.h"\n#include "constants/items.h"\n#include "constants/item.h"\nEWRAM_DATA u32 gDccRewardProbe = 0;\nstatic void PrepareCraftingFixture(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    PrepareCraftingFixture();')
s+='''
static void PrepareCraftingFixture(void)
{
    u32 item, count = 3;
    AddBagItem(ITEM_DCC_SCRAP, 98);
    AddBagItem(ITEM_DCC_CHARGE, 99);
    AddBagItem(ITEM_SUPER_POTION, 99);
    for (item = 1; item < ITEMS_COUNT && count < gBagPockets[ITEMS_POCKET].capacity; item++)
        if (item != ITEM_DCC_SCRAP && item != ITEM_DCC_CHARGE && item != ITEM_SUPER_POTION
            && GetItemPocket(item) == POCKET_ITEMS && AddBagItem(item, 1))
            count++;
    FlagSet(FLAG_DCC_ACH_DUO);
    if (count == gBagPockets[ITEMS_POCKET].capacity
        && !AddBagItem(ITEM_DCC_SCRAP, 2)
        && !AddBagItem(ITEM_DCC_CHARGE, 1)
        && !AddBagItem(ITEM_SUPER_POTION, 1)
        && CountTotalItemQuantityInBag(ITEM_DCC_SCRAP) == 98
        && CountTotalItemQuantityInBag(ITEM_DCC_CHARGE) == 99
        && CountTotalItemQuantityInBag(ITEM_SUPER_POTION) == 99)
        gDccRewardProbe = 1;
}
'''
p.write_text(s)
