#!/usr/bin/env python3
"""Labeled GBA boundary probes; no synthetic trainer is instantiated or flagged."""
from pathlib import Path
import subprocess,sys

root=Path(sys.argv[1]);extended=len(sys.argv)>2 and sys.argv[2]=='extended'
subprocess.run(['python3',str(Path(__file__).with_name('membership-fixture.py')),str(root),'extended' if extended else ''],check=True)
p=root/'engine/src/crawler.c';s=p.read_text()
s=s.replace('static void ProbeMembership(void);', 'static void ProbeMembership(void);\nextern bool8 DccProbePaletteBoundary(void);\nextern bool8 DccProbeCacheBoundary(void);\nextern bool8 DccProbeObjectBoundary(void);\nextern bool8 DccProbeBattleBoundary(void);')
s=s.replace('    sDccProbeFinished = TRUE;', '''    if (DccProbePaletteBoundary()) gDccMembershipProbe |= 16;
    if (DccProbeCacheBoundary()) gDccMembershipProbe |= 32;
    if (DccProbeObjectBoundary()) gDccMembershipProbe |= 64;
    if (DccProbeBattleBoundary()) gDccMembershipProbe |= 128;
    sDccProbeFinished = TRUE;''')
p.write_text(s)
additions={
'event_object_movement.c': '''
// TEST FIXTURE ONLY: actual palette-tag dispatch, not a stock-map playthrough.
bool8 DccProbePaletteBoundary(void)
{
    static const u16 ids[] = {0x2200, 0x2206, 0x0000, 0x2302};
    struct WarpData location = gSaveBlock1Ptr->location;
    u8 reflection = sCurrentReflectionType;
    u32 i;
    bool8 ok = TRUE;
    sCurrentReflectionType = 0;
    for (i = 0; i < ARRAY_COUNT(ids); i++)
    {
        bool8 member = i == 0 || (EXTENDED && i == 3);
        u16 expected = member ? OBJ_EVENT_PAL_TAG_DCC_DONUT : sObjectPaletteTagSets[0][PALSLOT_NPC_1];
        gSaveBlock1Ptr->location.mapGroup = ids[i] >> 8;
        gSaveBlock1Ptr->location.mapNum = ids[i] & 0xFF;
        if (GetObjectPaletteTag(PALSLOT_NPC_1) != expected)
            ok = FALSE;
    }
    sCurrentReflectionType = reflection;
    gSaveBlock1Ptr->location = location;
    return ok;
}
''',
'fieldmap.c': '''
// TEST FIXTURE ONLY: snapshot the current entrance buffer, then dispatch the
// actual cache loader under member/nonmember identities. All bytes restored.
EWRAM_DATA static u16 sDccProbeCacheMap[31 * 26] = {0};
bool8 DccProbeCacheBoundary(void)
{
    static const u16 ids[] = {0x2200, 0x2206, 0x0000, 0x2302};
    u16 previousView[ARRAY_COUNT(gSaveBlock1Ptr->mapView)];
    struct WarpData location = gSaveBlock1Ptr->location;
    u32 i, j;
    bool8 ok = TRUE;
    if (gBackupMapLayout.width != 31 || gBackupMapLayout.height != 26)
        return FALSE;
    memcpy(sDccProbeCacheMap, sBackupMapData, sizeof(sDccProbeCacheMap));
    memcpy(previousView, gSaveBlock1Ptr->mapView, sizeof(previousView));
    for (i = 0; i < ARRAY_COUNT(ids); i++)
    {
        bool8 member = i == 0 || (EXTENDED && i == 3);
        memcpy(sBackupMapData, sDccProbeCacheMap, sizeof(sDccProbeCacheMap));
        for (j = 0; j < ARRAY_COUNT(gSaveBlock1Ptr->mapView); j++)
            gSaveBlock1Ptr->mapView[j] = 0x3222;
        gSaveBlock1Ptr->location.mapGroup = ids[i] >> 8;
        gSaveBlock1Ptr->location.mapNum = ids[i] & 0xFF;
        LoadSavedMapView();
        if ((memcmp(sBackupMapData, sDccProbeCacheMap, sizeof(sDccProbeCacheMap)) == 0) != member)
            ok = FALSE;
        for (j = 0; j < ARRAY_COUNT(gSaveBlock1Ptr->mapView); j++)
            if (gSaveBlock1Ptr->mapView[j] != 0) ok = FALSE;
    }
    memcpy(sBackupMapData, sDccProbeCacheMap, sizeof(sDccProbeCacheMap));
    memcpy(gSaveBlock1Ptr->mapView, previousView, sizeof(previousView));
    gSaveBlock1Ptr->location = location;
    return ok;
}
''',
'overworld.c': '''
#include "constants/event_objects.h"
// TEST FIXTURE ONLY: 64 valid source templates avoid out-of-bounds fixture reads
// in the stock loader. Current map/events/templates/objects are fully restored.
EWRAM_DATA static struct ObjectEventTemplate sDccProbeSourceTemplates[OBJECT_EVENT_TEMPLATES_COUNT] = {0};
EWRAM_DATA static struct ObjectEventTemplate sDccProbeSavedTemplates[OBJECT_EVENT_TEMPLATES_COUNT] = {0};
EWRAM_DATA static struct ObjectEvent sDccProbeObjects[OBJECT_EVENTS_COUNT] = {0};
EWRAM_DATA static struct ObjectEvent sDccProbeSavedObjects[OBJECT_EVENTS_COUNT] = {0};
bool8 DccProbeObjectBoundary(void)
{
    static const u16 ids[] = {0x2200, 0x2206, 0x0000, 0x2302};
    static const u8 scripts[] = {2, 2};
    struct MapEvents events = *gMapHeader.events;
    const struct MapEvents *originalEvents = gMapHeader.events;
    struct WarpData location = gSaveBlock1Ptr->location;
    u32 i, j;
    bool8 ok = TRUE;
    memcpy(sDccProbeSavedTemplates, gSaveBlock1Ptr->objectEventTemplates, sizeof(sDccProbeSavedTemplates));
    memcpy(sDccProbeObjects, gObjectEvents, sizeof(sDccProbeObjects));
    memcpy(sDccProbeSavedObjects, gSaveBlock1Ptr->objectEvents, sizeof(sDccProbeSavedObjects));
    for (j = 0; j < OBJECT_EVENT_TEMPLATES_COUNT; j++)
    {
        sDccProbeSourceTemplates[j].localId = j + 1;
        sDccProbeSourceTemplates[j].graphicsId = OBJ_EVENT_GFX_MAN_2;
        sDccProbeSourceTemplates[j].script = &scripts[1];
    }
    events.objectEventCount = 2;
    events.objectEvents = sDccProbeSourceTemplates;
    gMapHeader.events = &events;
    for (i = 0; i < ARRAY_COUNT(ids); i++)
    {
        bool8 member = i == 0 || (EXTENDED && i == 3);
        for (j = 0; j < OBJECT_EVENT_TEMPLATES_COUNT; j++)
        {
            gSaveBlock1Ptr->objectEventTemplates[j].localId = j + 1;
            gSaveBlock1Ptr->objectEventTemplates[j].graphicsId = OBJ_EVENT_GFX_HIKER;
            gSaveBlock1Ptr->objectEventTemplates[j].script = &scripts[0];
        }
        memset(gObjectEvents, 0, sizeof(gObjectEvents));
        gSaveBlock1Ptr->location.mapGroup = ids[i] >> 8;
        gSaveBlock1Ptr->location.mapNum = ids[i] & 0xFF;
        gObjectEvents[1].active = TRUE;
        gObjectEvents[1].localId = 1;
        gObjectEvents[1].mapGroup = ids[i] >> 8;
        gObjectEvents[1].mapNum = ids[i] & 0xFF;
        gObjectEvents[1].graphicsId = OBJ_EVENT_GFX_HIKER;
        gSaveBlock1Ptr->objectEvents[1] = gObjectEvents[1];
        LoadSaveblockObjEventScripts();
        for (j = 0; j < OBJECT_EVENT_TEMPLATES_COUNT; j++)
        {
            struct ObjectEventTemplate *object = &gSaveBlock1Ptr->objectEventTemplates[j];
            if (object->script != (member && j >= 2 ? &scripts[0] : &scripts[1])) ok = FALSE;
            if (object->graphicsId != (member && j < 2 ? OBJ_EVENT_GFX_MAN_2 : OBJ_EVENT_GFX_HIKER)) ok = FALSE;
        }
        if (gObjectEvents[1].graphicsId != (member ? OBJ_EVENT_GFX_MAN_2 : OBJ_EVENT_GFX_HIKER)) ok = FALSE;
        if (gSaveBlock1Ptr->objectEvents[1].graphicsId != (member ? OBJ_EVENT_GFX_MAN_2 : OBJ_EVENT_GFX_HIKER)) ok = FALSE;
    }
    memcpy(gSaveBlock1Ptr->objectEventTemplates, sDccProbeSavedTemplates, sizeof(sDccProbeSavedTemplates));
    memcpy(gObjectEvents, sDccProbeObjects, sizeof(sDccProbeObjects));
    memcpy(gSaveBlock1Ptr->objectEvents, sDccProbeSavedObjects, sizeof(sDccProbeSavedObjects));
    gMapHeader.events = originalEvents;
    gSaveBlock1Ptr->location = location;
    return ok;
}
''',
'battle_setup.c': '''
// TEST FIXTURE ONLY: invoke the actual callback synchronously with valid crawler
// IDs, last stock trainer854 and the stock secret-base exception. Never901.
EWRAM_DATA static struct Pokemon sDccProbeParty[PARTY_SIZE] = {0};
bool8 DccProbeBattleBoundary(void)
{
    static const u16 trainers[] = {TRAINER_DCC_TRIAL, TRAINER_DCC_GUARD, TRAINER_DCC_HOWLER,
        TRAINER_DCC_BOSS, TRAINER_DCC_BOSS_PREPARED, 854, TRAINER_SECRET_BASE};
    MainCallback callback = gMain.callback2;
    u8 state = gMain.state;
    u16 opponent = gTrainerBattleOpponent_A;
    u8 outcome = gBattleOutcome;
    u16 hp = 1;
    u32 i;
    bool8 ok = TRUE;
    memcpy(sDccProbeParty, gPlayerParty, sizeof(sDccProbeParty));
    for (i = 0; i < ARRAY_COUNT(trainers); i++)
    {
        memcpy(gPlayerParty, sDccProbeParty, sizeof(sDccProbeParty));
        SetMonData(&gPlayerParty[0], MON_DATA_HP, &hp);
        gTrainerBattleOpponent_A = trainers[i];
        gBattleOutcome = B_OUTCOME_LOST;
        CB2_EndTrainerBattle();
        if (gMain.callback2 != (i == 5 ? CB2_WhiteOut : CB2_ReturnToFieldContinueScriptPlayMapMusic)) ok = FALSE;
        if (GetMonData(&gPlayerParty[0], MON_DATA_HP) != (i < 5 ? GetMonData(&gPlayerParty[0], MON_DATA_MAX_HP) : 1)) ok = FALSE;
    }
    memcpy(gPlayerParty, sDccProbeParty, sizeof(sDccProbeParty));
    gMain.callback2 = callback;
    gMain.state = state;
    gTrainerBattleOpponent_A = opponent;
    gBattleOutcome = outcome;
    return ok;
}
'''}
for name,code in additions.items():
    p=root/'engine/src'/name
    p.write_text(p.read_text()+code.replace('EXTENDED','TRUE' if extended else 'FALSE'))
