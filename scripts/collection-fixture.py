#!/usr/bin/env python3
"""Patch an isolated B03 snapshot for GBA-side defensive API probes, never production.
The harness still only sends inputs/reads memory. Test ROM/source diff stays local.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])
p=root/'engine/src/battle_script_commands.c'
p.write_text(p.read_text()+'''
// TEST FIXTURE ONLY: invoke the unchanged production capture opcode with each mode.
bool8 DccProbeCapturePolicy(void)
{
    const u8 *saved = gBattlescriptCurrInstr;
    u32 flags = gBattleTypeFlags;
    u32 busy = gBattleControllerExecFlags;
    u8 outcome = gBattleOutcome;
    const u32 modes[] = {0, BATTLE_TYPE_TRAINER, BATTLE_TYPE_WALLY_TUTORIAL, BATTLE_TYPE_SAFARI};
    u32 i;
    bool8 ok = TRUE;
    for (i = 0; i < ARRAY_COUNT(modes); i++)
    {
        gBattleTypeFlags = modes[i];
        gBattleControllerExecFlags = 0;
        gBattlescriptCurrInstr = saved;
        Cmd_handleballthrow();
        if (gBattlescriptCurrInstr != BattleScript_DccCaptureBlocked || gBattleOutcome != outcome)
            ok = FALSE;
        gBattleControllerExecFlags = 1;
        gBattlescriptCurrInstr = saved;
        Cmd_handleballthrow();
        if (gBattlescriptCurrInstr != saved || gBattleOutcome != outcome)
            ok = FALSE;
    }
    gBattlescriptCurrInstr = saved;
    gBattleTypeFlags = flags;
    gBattleControllerExecFlags = busy;
    return ok;
}
''')
p=root/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"','#include "crawler.h"\n#include "item.h"\n#include "daycare.h"\n#include "script_pokemon_util.h"\n#include "constants/items.h"\n#include "constants/pokemon.h"\nextern bool8 DccProbeCapturePolicy(void);\nEWRAM_DATA u32 gDccCollectionProbe = 0;\nstatic void ProbeCollectionPolicy(void);')
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);','    FlagSet(FLAG_SYS_POKEMON_GET);\n    ProbeCollectionPolicy();')
s+='''
static void ProbeCollectionPolicy(void)
{
    u32 i;
    struct Pokemon gift = gPlayerParty[0];
    struct Pokemon before[2];
    bool8 noBalls = TRUE;
    u8 level;
    memcpy(before, gPlayerParty, sizeof(before));
    for (i = ITEM_MASTER_BALL; i <= ITEM_PREMIER_BALL; i++)
        if (AddBagItem(i, 1) || CheckBagHasItem(i, 1))
            noBalls = FALSE;
    if (noBalls) gDccCollectionProbe |= 1;
    if (GiveMonToPlayer(&gift) == MON_CANT_GIVE) gDccCollectionProbe |= 2;
    if (ScriptGiveEgg(SPECIES_PICHU) == MON_CANT_GIVE) gDccCollectionProbe |= 4;
    StoreSelectedPokemonInDaycare();
    GiveEggFromDaycare();
    if (gPlayerPartyCount == 2 && memcmp(before, gPlayerParty, sizeof(before)) == 0)
        gDccCollectionProbe |= 8;
    level = 28;
    SetMonData(&gift, MON_DATA_LEVEL, &level);
    if (GetEvolutionTargetSpecies(&gift, EVO_MODE_NORMAL, ITEM_NONE) == SPECIES_NONE)
    {
        level = 13;
        SetMonData(&gift, MON_DATA_LEVEL, &level);
        if (MonTryLearningNewMove(&gift, TRUE) == MOVE_NONE)
            gDccCollectionProbe |= 16;
    }
    if (DccProbeCapturePolicy()) gDccCollectionProbe |= 32;
    // Ordinary inventory remains usable: required by R01 and later crafting.
    if (AddBagItem(ITEM_POTION, 1) && CheckBagHasItem(ITEM_POTION, 1)
        && RemoveBagItem(ITEM_POTION, 1) && !CheckBagHasItem(ITEM_POTION, 1))
        gDccCollectionProbe |= 64;
}
'''
p.write_text(s)
