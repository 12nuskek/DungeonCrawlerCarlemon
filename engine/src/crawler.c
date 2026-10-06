#include "global.h"
#include "crawler.h"
#include "pokemon.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "fieldmap.h"
#include "field_camera.h"
#include "sprite.h"
#include "constants/flags.h"
#include "constants/maps.h"
#include "constants/event_objects.h"
#include "constants/opponents.h"
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

struct DccPresentationTile
{
    u8 mapNum, x, y;
    u16 flag, unresolved, resolved;
};

#include "data/dcc_presentation.h"

// Reconstruct presentation from existing persistent outcomes. No new save fields,
// reward writes, collision changes or inventory effects belong in this layer.
void DccRestoreMapPresentation(void)
{
    u32 i;
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_DCC_ENTRANCE))
        return;
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
    {
        const struct DccPresentationTile *tile = &sDccPresentationTiles[i];
        if (gSaveBlock1Ptr->location.mapNum == tile->mapNum)
            MapGridSetMetatileEntryAt(tile->x + MAP_OFFSET, tile->y + MAP_OFFSET,
                FlagGet(tile->flag) ? tile->resolved : tile->unresolved);
    }
}

bool8 DccObjectIsResolved(u8 graphicsId)
{
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_DCC_ENTRANCE))
        return FALSE;
    switch (gSaveBlock1Ptr->location.mapNum)
    {
    case MAP_NUM(MAP_DCC_ENTRANCE):
        return graphicsId == OBJ_EVENT_GFX_MOVING_BOX && FlagGet(FLAG_DCC_LOOT_SUPPLY);
    case MAP_NUM(MAP_DCC_VESTIBULE):
        return (graphicsId == OBJ_EVENT_GFX_MOVING_BOX && FlagGet(FLAG_DCC_WRAP_TAKEN))
            || (graphicsId == OBJ_EVENT_GFX_MAN_1 && FlagGet(TRAINER_FLAGS_START + TRAINER_DCC_TRIAL));
    case MAP_NUM(MAP_DCC_SERVICE):
        return graphicsId == OBJ_EVENT_GFX_DCC_CACHE_SEALED && FlagGet(FLAG_DCC_CACHE_BLASTED);
    case MAP_NUM(MAP_DCC_CORRIDOR):
        return (graphicsId == OBJ_EVENT_GFX_NINJA_BOY && FlagGet(TRAINER_FLAGS_START + TRAINER_DCC_GUARD))
            || (graphicsId == OBJ_EVENT_GFX_MAN_3 && FlagGet(TRAINER_FLAGS_START + TRAINER_DCC_HOWLER));
    case MAP_NUM(MAP_DCC_BOSS):
        return graphicsId == OBJ_EVENT_GFX_HIKER && FlagGet(FLAG_DCC_BOSS_CLEARED);
    }
    return FALSE;
}

void DccRefreshMapPresentation(void)
{
    u32 i;
    if (gSaveBlock1Ptr->location.mapGroup != MAP_GROUP(MAP_DCC_ENTRANCE))
        return;
    DccRestoreMapPresentation();
    DrawWholeMapView();
    for (i = 0; i < OBJECT_EVENTS_COUNT; i++)
    {
        struct ObjectEvent *object = &gObjectEvents[i];
        if (object->active && !object->isPlayer
            && object->mapGroup == gSaveBlock1Ptr->location.mapGroup
            && object->mapNum == gSaveBlock1Ptr->location.mapNum
            && DccObjectIsResolved(object->graphicsId))
        {
            ObjectEventSetGraphicsId(object, object->graphicsId);
            StartSpriteAnim(&gSprites[object->spriteId], 0);
        }
    }
}
