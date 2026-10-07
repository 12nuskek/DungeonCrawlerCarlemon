#include "global.h"
#include "crawler.h"
#include "event_data.h"
#include "event_object_movement.h"
#include "overworld.h"
#include "constants/maps.h"
#include "constants/flags.h"

// Bounds generated from the complete group register, not inferred membership.
#include "data/dcc_map_counts.h"

static bool8 IsLegacy(const struct WarpData *warp)
{
    switch (((u8)warp->mapGroup << 8) | (u8)warp->mapNum)
    {
    case MAP_DCC_ENTRANCE: case MAP_DCC_VESTIBULE: case MAP_DCC_SERVICE:
    case MAP_DCC_CORRIDOR: case MAP_DCC_BOSS: case MAP_DCC_EXIT:
        return TRUE;
    }
    return FALSE;
}

static bool8 IsLive(const struct WarpData *warp)
{
    switch (((u8)warp->mapGroup << 8) | (u8)warp->mapNum)
    {
    case MAP_DCC_F1D1FIELD: case MAP_DCC_F1D1QUIET: case MAP_DCC_F1D1WORKSHOP:
    case MAP_DCC_F1D1WARDEN: case MAP_DCC_F1D1CHECKPOINT:
        return TRUE;
    }
    return FALSE;
}

static bool8 ValidIdentity(const struct WarpData *warp)
{
    return warp->mapGroup >= 0 && warp->mapGroup < ARRAY_COUNT(sDccMapCounts)
        && warp->mapNum >= 0 && warp->mapNum < sDccMapCounts[(u8)warp->mapGroup];
}

static bool8 ValidSchema(const struct WarpData *warp, u16 version)
{
    if (!ValidIdentity(warp))
        return FALSE;
    if (IsLegacy(warp))
        return version == 0;
    if (IsLive(warp))
        return version == 1;
    return TRUE; // Preserve stock Continue semantics and its unowned var slot.
}

bool8 DccContinueSupported(void)
{
    u16 version = VarGet(VAR_DCC_LAYOUT_VERSION);
    if (!ValidSchema(&gSaveBlock1Ptr->location, version))
        return FALSE;
    if (UseContinueGameWarp() && !ValidSchema(&gSaveBlock1Ptr->continueGameWarp, version))
        return FALSE;
    // Crawler layout identity is repaired before lookup. Stock alternate layouts
    // are preserved, but no invalid saved index may dereference gMapLayouts.
    if (!DccIsMap(gSaveBlock1Ptr->location.mapGroup, gSaveBlock1Ptr->location.mapNum)
        && (gSaveBlock1Ptr->mapLayoutId == 0 || gSaveBlock1Ptr->mapLayoutId > 447))
        return FALSE;
    return TRUE;
}

// Normalize valid legacy warp indices before semantic relocation. Current pos
// is authoritative for an ordinary Continue; a remembered return uses its index.
static void RemapLegacy(struct WarpData *warp)
{
    const struct MapHeader *header;
    u16 id, dest;
    s16 x, y;
    if (!IsLegacy(warp))
        return; // Dummy sentinel and every stock record stay byte-identical.
    id = ((u8)warp->mapGroup << 8) | (u8)warp->mapNum;
    header = Overworld_GetMapHeaderByGroupAndId(warp->mapGroup, warp->mapNum);
    if (warp->warpId >= 0 && warp->warpId < header->events->warpCount)
    {
        warp->x = header->events->warps[warp->warpId].x;
        warp->y = header->events->warps[warp->warpId].y;
    }
    dest = MAP_DCC_F1D1FIELD; x = 8; y = 38;
    switch (id)
    {
    case MAP_DCC_VESTIBULE: dest = MAP_DCC_F1D1QUIET; x = 4; y = 5; break;
    case MAP_DCC_SERVICE: dest = MAP_DCC_F1D1WORKSHOP; x = 4; y = 4; break;
    case MAP_DCC_CORRIDOR:
        x = 37; y = 31;
        if (warp->x >= 8 && warp->x < header->mapLayout->width
            && warp->y >= 0 && warp->y < header->mapLayout->height)
        { x = 51; y = 27; }
        break;
    case MAP_DCC_BOSS: dest = MAP_DCC_F1D1WARDEN; x = 8; y = 7; break;
    case MAP_DCC_EXIT: dest = MAP_DCC_F1D1CHECKPOINT; x = 4; y = 4; break;
    }
    warp->mapGroup = MAP_GROUP(dest);
    warp->mapNum = MAP_NUM(dest);
    warp->warpId = WARP_ID_NONE;
    warp->x = x; warp->y = y;
}

bool8 DccMigrateContinue(void)
{
    const struct MapHeader *header;
    bool8 legacy = IsLegacy(&gSaveBlock1Ptr->location);
    if (!legacy)
    {
        if (IsLive(&gSaveBlock1Ptr->location))
        {
            header = Overworld_GetMapHeaderByGroupAndId(gSaveBlock1Ptr->location.mapGroup, gSaveBlock1Ptr->location.mapNum);
            gSaveBlock1Ptr->mapLayoutId = header->mapLayoutId;
        }
        return FALSE;
    }
    // The caller has already rejected unknown schemas/identities. No gameplay
    // outcome, party, inventory, money or trainer flag is touched here.
    gSaveBlock1Ptr->location.warpId = WARP_ID_NONE;
    gSaveBlock1Ptr->location.x = gSaveBlock1Ptr->pos.x;
    gSaveBlock1Ptr->location.y = gSaveBlock1Ptr->pos.y;
    RemapLegacy(&gSaveBlock1Ptr->location);
    RemapLegacy(&gSaveBlock1Ptr->continueGameWarp);
    RemapLegacy(&gSaveBlock1Ptr->dynamicWarp);
    RemapLegacy(&gSaveBlock1Ptr->lastHealLocation);
    RemapLegacy(&gSaveBlock1Ptr->escapeWarp);
    if (UseContinueGameWarp())
        gSaveBlock1Ptr->location = gSaveBlock1Ptr->continueGameWarp;
    gSaveBlock1Ptr->pos.x = gSaveBlock1Ptr->location.x;
    gSaveBlock1Ptr->pos.y = gSaveBlock1Ptr->location.y;
    header = Overworld_GetMapHeaderByGroupAndId(gSaveBlock1Ptr->location.mapGroup, gSaveBlock1Ptr->location.mapNum);
    gSaveBlock1Ptr->mapLayoutId = header->mapLayoutId;
    memset(gSaveBlock1Ptr->mapView, 0, sizeof(gSaveBlock1Ptr->mapView));
    memset(gSaveBlock1Ptr->objectEvents, 0, sizeof(gSaveBlock1Ptr->objectEvents));
    memset(gSaveBlock1Ptr->objectEventTemplates, 0, sizeof(gSaveBlock1Ptr->objectEventTemplates));
    memset(gObjectEvents, 0, sizeof(gObjectEvents));
    FlagClear(FLAG_DCC_D1_LOOP_OPEN);
    VarSet(VAR_DCC_LAYOUT_VERSION, 1);
    return TRUE; // Requires local map load/spawn, never active-only ReturnToField.
}
