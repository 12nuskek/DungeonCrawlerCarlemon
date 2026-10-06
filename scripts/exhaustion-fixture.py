#!/usr/bin/env python3
"""Isolated GBA diagnostic only: existing trap status/HP1 and both actions empty.
Never run against production checkout. Real menu input still drives Struggle,
saving and recovery. No host RAM patches or debugger commands.
"""
from pathlib import Path
import sys
p=Path(sys.argv[1])/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "script_pokemon_util.h"\nEWRAM_DATA u32 gDccRewardProbe = 0;\nstatic void PrepareExhaustionFixture(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    PrepareExhaustionFixture();')
s+='''
static void PrepareExhaustionFixture(void)
{
    u16 hp = 1;
    u32 status = STATUS1_POISON;
    u8 zero = 0, n, slot;
    SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
    SetMonData(&gPlayerParty[0], MON_DATA_STATUS, &status);
    DccApplyServiceTrap();
    if (GetMonData(&gPlayerParty[0], MON_DATA_HP) == 1
        && GetMonData(&gPlayerParty[0], MON_DATA_STATUS) == STATUS1_POISON)
        gDccRewardProbe |= 1;
    HealPlayerParty();
    for (n = 0; n < 2; n++)
        for (slot = 0; slot < MAX_MON_MOVES; slot++)
            SetMonData(&gPlayerParty[n], MON_DATA_PP1 + slot, &zero);
    if (GetMonData(&gPlayerParty[0], MON_DATA_PP1) == 0
        && GetMonData(&gPlayerParty[0], MON_DATA_PP2) == 0
        && GetMonData(&gPlayerParty[1], MON_DATA_PP1) == 0
        && GetMonData(&gPlayerParty[1], MON_DATA_PP2) == 0)
        gDccRewardProbe |= 2;
}
'''
p.write_text(s)
