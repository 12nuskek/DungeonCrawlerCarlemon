#!/usr/bin/env python3
"""Probe actual GBA identity/presentation APIs in a labeled isolated test ROM.

The extended variant adds two synthetic map IDs in another group and one
nonadjacent trainer ID to this fixture only. It never warps to these IDs or starts
a nonexistent trainer battle. Harness inputs stay normal/read-only.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1])
extended=len(sys.argv)>2 and sys.argv[2]=='extended'
identity=root/'engine/src/crawler_identity.c'
original=identity.read_text()
if extended:
    original=original.replace('    case MAP_DCC_ENTRANCE:', '    case (35 << 8) | 2:\n    case (35 << 8) | 4:\n    case MAP_DCC_ENTRANCE:')
    original=original.replace('    case TRAINER_DCC_TRIAL:', '    case 901:\n    case TRAINER_DCC_TRIAL:')
identity.write_text(original)
p=root/'engine/src/crawler.c'
s=p.read_text().replace('#include "crawler.h"', '#include "crawler.h"\nEWRAM_DATA u32 gDccMembershipProbe = 0;\nstatic void ProbeMembership(void);\nstatic void ProbePresentationIdentity(void);')
assert s.count('    FlagSet(FLAG_SYS_POKEMON_GET);')==1
s=s.replace('    FlagSet(FLAG_SYS_POKEMON_GET);', '    FlagSet(FLAG_SYS_POKEMON_GET);\n    ProbeMembership();')
assert s.count('void DccRestoreMapPresentation(void)\n{\n    u32 i;')==1
s=s.replace('void DccRestoreMapPresentation(void)\n{\n    u32 i;', 'void DccRestoreMapPresentation(void)\n{\n    u32 i;\n    ProbePresentationIdentity();')
s+='''
// TEST FIXTURE ONLY: exhaustive 16-bit identity space against frozen baseline IDs.
static void ProbeMembership(void)
{
    u32 id;
    bool8 mapsOk = TRUE;
    bool8 trainersOk = TRUE;
    for (id = 0; id <= 0xFFFF; id++)
    {
        bool8 mapExpected = id == 0x2200 || id == 0x2201 || id == 0x2202
            || id == 0x2203 || id == 0x2204 || id == 0x2205;
        bool8 trainerExpected = id == 855 || id == 856 || id == 857
            || id == 858 || id == 859;
        if (EXTENDED && (id == 0x2302 || id == 0x2304))
            mapExpected = TRUE;
        if (EXTENDED && id == 901)
            trainerExpected = TRUE;
        if (DccIsMap(id >> 8, id & 0xFF) != mapExpected)
            mapsOk = FALSE;
        if (DccIsEncounter(id) != trainerExpected)
            trainersOk = FALSE;
    }
    if (mapsOk) gDccMembershipProbe |= 1;
    if (trainersOk) gDccMembershipProbe |= 2;
}

static u32 ProbeMapHash(void)
{
    u32 i;
    u32 hash = 2166136261u;
    for (i = 0; i < gBackupMapLayout.width * gBackupMapLayout.height; i++)
        hash = (hash ^ gBackupMapLayout.map[i]) * 16777619u;
    return hash;
}

static void ProbePresentationIdentity(void)
{
    static bool8 running = FALSE;
    static bool8 finished = FALSE;
    static const u16 aliases[] = {0x0002, 0x0004, 0x2206, 0x2302, 0x2304};
    u16 previousTiles[ARRAY_COUNT(sDccPresentationTiles)];
    bool8 previousFlags[ARRAY_COUNT(sDccPresentationTiles)];
    struct WarpData location;
    u32 i;
    u32 hash;
    bool8 aliasesOk = TRUE;
    bool8 registeredOk = TRUE;
    if (running || finished || gBackupMapLayout.map == NULL)
        return;
    running = TRUE;
    location = gSaveBlock1Ptr->location;
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
    {
        const struct DccPresentationTile *tile = &sDccPresentationTiles[i];
        previousTiles[i] = gBackupMapLayout.map[(tile->y + MAP_OFFSET) * gBackupMapLayout.width + tile->x + MAP_OFFSET];
        previousFlags[i] = FlagGet(tile->flag);
    }
    // Set all outcomes in the fixture, so an erroneous alias would visibly write
    // resolved tiles or mark unrelated stock objects as dungeon remains.
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
        FlagSet(sDccPresentationTiles[i].flag);
    hash = ProbeMapHash();
    for (i = 0; i < ARRAY_COUNT(aliases); i++)
    {
        gSaveBlock1Ptr->location.mapGroup = aliases[i] >> 8;
        gSaveBlock1Ptr->location.mapNum = aliases[i] & 0xFF;
        DccRestoreMapPresentation();
        if (ProbeMapHash() != hash
            || DccObjectIsResolved(OBJ_EVENT_GFX_DCC_CACHE_SEALED)
            || DccObjectIsResolved(OBJ_EVENT_GFX_HIKER))
            aliasesOk = FALSE;
    }
    gSaveBlock1Ptr->location.mapGroup = MAP_GROUP(MAP_DCC_BOSS);
    gSaveBlock1Ptr->location.mapNum = MAP_NUM(MAP_DCC_BOSS);
    DccRestoreMapPresentation();
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
    {
        const struct DccPresentationTile *tile = &sDccPresentationTiles[i];
        u16 actual = gBackupMapLayout.map[(tile->y + MAP_OFFSET) * gBackupMapLayout.width + tile->x + MAP_OFFSET];
        if (actual != (tile->mapId == MAP_DCC_BOSS ? tile->resolved : previousTiles[i]))
            registeredOk = FALSE;
    }
    if (!DccObjectIsResolved(OBJ_EVENT_GFX_HIKER))
        registeredOk = FALSE;
    // Restore every temporary tile/flag/location value; no fixture progress is
    // carried into the normal intro or saved as a production state.
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
    {
        const struct DccPresentationTile *tile = &sDccPresentationTiles[i];
        MapGridSetMetatileEntryAt(tile->x + MAP_OFFSET, tile->y + MAP_OFFSET, previousTiles[i]);
    }
    for (i = 0; i < ARRAY_COUNT(sDccPresentationTiles); i++)
        if (!previousFlags[i]) FlagClear(sDccPresentationTiles[i].flag);
    gSaveBlock1Ptr->location = location;
    if (aliasesOk) gDccMembershipProbe |= 4;
    if (registeredOk) gDccMembershipProbe |= 8;
    finished = TRUE;
    running = FALSE;
}
'''.replace('EXTENDED', 'TRUE' if extended else 'FALSE')
p.write_text(s)
p=root/'engine/data/maps/DCC_Entrance/scripts.inc'
s=p.read_text();assert s.count('DCC_Entrance_Intro:\n')==1
p.write_text(s.replace('DCC_Entrance_Intro:\n', 'DCC_Entrance_Intro:\n\tspecial DccRestoreMapPresentation\n'))
