#include "global.h"
#include "crawler.h"
#include "pokemon.h"
#include "constants/species.h"
#include "constants/moves.h"

// Reuse Emerald records. Species/art are temporary, not collectible pets.
void InitCrawlerParty(void)
{
    static const u8 sCarlName[POKEMON_NAME_LENGTH + 1] = _("CARL");
    static const u8 sDonutName[POKEMON_NAME_LENGTH + 1] = _("DONUT");
    CreateMon(&gPlayerParty[0], SPECIES_MACHOP, 8, 20, TRUE, 128, OT_ID_PLAYER_ID, 0);
    SetMonData(&gPlayerParty[0], MON_DATA_NICKNAME, sCarlName);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_TACKLE, 0);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_FOCUS_ENERGY, 1);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_NONE, 2);
    SetMonMoveSlot(&gPlayerParty[0], MOVE_NONE, 3);
    CreateMon(&gPlayerParty[1], SPECIES_MEOWTH, 8, 20, TRUE, 0, OT_ID_PLAYER_ID, 0);
    SetMonData(&gPlayerParty[1], MON_DATA_NICKNAME, sDonutName);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_SWIFT, 0);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_GROWL, 1);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_NONE, 2);
    SetMonMoveSlot(&gPlayerParty[1], MOVE_NONE, 3);
    gPlayerPartyCount = 2;
}
