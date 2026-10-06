#include "global.h"
#include "crawler.h"
#include "pokemon.h"
#include "event_data.h"
#include "constants/flags.h"
#include "constants/species.h"
#include "constants/moves.h"

// Reuse Emerald records. Species/art are temporary, not collectible pets.
void InitCrawlerParty(void)
{
    static const u8 sCarlName[POKEMON_NAME_LENGTH + 1] = _("CARL");
    static const u8 sDonutName[POKEMON_NAME_LENGTH + 1] = _("DONUT");
    u8 noAbilitySlot = 1;
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
    gPlayerPartyCount = 2;
    FlagSet(FLAG_SYS_POKEMON_GET);
}
