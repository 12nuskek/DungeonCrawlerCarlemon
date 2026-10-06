#include "global.h"
#include "crawler.h"
#include "pokemon.h"
#include "event_data.h"
#include "constants/flags.h"
#include "constants/species.h"
#include "constants/moves.h"
#include "constants/battle.h"

// Reuse Emerald records. Species/art are temporary, not collectible pets.
void InitCrawlerParty(void)
{
    static const u8 sCarlName[POKEMON_NAME_LENGTH + 1] = _("CARL");
    static const u8 sDonutName[POKEMON_NAME_LENGTH + 1] = _("DONUT");
    u8 noAbilitySlot = 1;
    u32 experience;
    CreateMon(&gPlayerParty[0], SPECIES_MACHOP, 8, 20, TRUE, 128, OT_ID_PLAYER_ID, 0);
    SetMonData(&gPlayerParty[0], MON_DATA_NICKNAME, sCarlName);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_DCC_STRIKE, 0);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_DCC_BRACE, 1);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_NONE, 2);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_NONE, 3);
    CreateMon(&gPlayerParty[1], SPECIES_MEOWTH, 8, 20, TRUE, 0, OT_ID_PLAYER_ID, 0);
    SetMonData(&gPlayerParty[1], MON_DATA_NICKNAME, sDonutName);
    // Meowth's unused second slot is ABILITY_NONE: no accidental random Pickup loot.
    SetMonData(&gPlayerParty[1], MON_DATA_ABILITY_NUM, &noAbilitySlot);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_DCC_SPARK, 0);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_DCC_WEAKEN, 1);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_NONE, 2);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_NONE, 3);
    // Compressed tutorial: earned trial XP demonstrates the next level.
    // Keep the existing species growth curves and stat calculation.
    experience = gExperienceTables[gSpeciesInfo[SPECIES_MACHOP].growthRate][9] - 20;
    SetMonData(&gPlayerParty[0], MON_DATA_EXP, &experience);
    experience = gExperienceTables[gSpeciesInfo[SPECIES_MEOWTH].growthRate][9] - 20;
    SetMonData(&gPlayerParty[1], MON_DATA_EXP, &experience);
    gPlayerPartyCount = 2;
    FlagSet(FLAG_SYS_POKEMON_GET);
}

// Scripted field hazard: cannot knock out a crawler or cause poison-step damage.
void DccApplyServiceTrap(void)
{
    u16 hp = GetMonData(&gPlayerParty[0], MON_DATA_HP);
    u32 status = STATUS1_PARALYSIS;
    if (hp == 0)
        return;
    hp = hp > 4 ? hp - 4 : 1;
    SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
    if (GetMonData(&gPlayerParty[0], MON_DATA_STATUS) == 0)
        SetMonData(&gPlayerParty[0], MON_DATA_STATUS, &status);
}
