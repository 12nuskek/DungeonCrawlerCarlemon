#!/usr/bin/env python3
"""Labeled diagnostic ROM only: fill key-item pocket before ordinary tag pickup."""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c';s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "item.h"\n#include "constants/items.h"\n#include "constants/item.h"\nEWRAM_DATA u32 gDccRewardProbe = 0;\nstatic void FillKeyItems(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    FillKeyItems();')
s+='''
static void FillKeyItems(void)
{
    u32 item;
    for (item = 1; item < ITEMS_COUNT; item++)
        if (item != ITEM_DCC_ROUTE_TAG && GetItemPocket(item) == POCKET_KEY_ITEMS)
            AddBagItem(item, 1);
    if (!AddBagItem(ITEM_DCC_ROUTE_TAG, 1)
        && CountTotalItemQuantityInBag(ITEM_DCC_ROUTE_TAG) == 0)
        gDccRewardProbe = 1;
}
''';p.write_text(s)
