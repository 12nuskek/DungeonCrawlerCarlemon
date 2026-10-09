/* Fixed synthetic event schedules. No Save, ROM, input replay or game process. */
#include "global.h"
#include <stdio.h>
#include "module.c"
#ifdef BASELINE
void DccBattlePoseNotify(void) {}
#endif
struct BattleMon gBattleMons[4];
struct Sprite gSprites[64];
struct MonSpritesGfx gfx, *gMonSpritesGfxPtr = &gfx;
u8 gBattleAnimAttacker, gBattlerAttacker, gBattlersCount = 4;
u8 gAbsentBattlerFlags, gAnimScriptActive, gBattlerSpriteIds[4] = {0, 1, 2, 3};
u16 gTrainerBattleOpponent_A = 858, gCurrentMove;
u32 gBattleTypeFlags = 8;
const u32 gBitTable[4] = {1, 2, 4, 8};
static u8 buffers[4][8192];
static unsigned writes[32][4], queues[8][3], copies, requests, sides, positions;
static unsigned tick, scenario;

void CpuCopy32(const void *src, void *dst, unsigned n)
{
    unsigned b, offset, pose;
    for (b = 0; b < 4; b++)
        if ((uintptr_t)dst >= (uintptr_t)buffers[b] && (uintptr_t)dst < (uintptr_t)(buffers[b] + 8192)) break;
    assert(b < 4 && n == 2048 && copies < 32);
    offset = (u8 *)dst - buffers[b];
    assert(offset % 2048 == 0 && offset <= 6144);
    for (pose = 0; pose < 17 && src != sDccPosePictures[pose]; pose++) {}
    assert(pose < 17);
    writes[copies][0] = b; writes[copies][1] = offset;
    writes[copies][2] = pose; writes[copies++][3] = n;
    memcpy(dst, src, n);
}
void RequestSpriteCopy(const u8 *src, u8 *dst, u16 n)
{
    unsigned b;
    for (b = 0; b < 4 && src != buffers[b]; b++) {}
    assert(b < 4 && n == 2048 && requests < 8);
    queues[requests][0] = b; queues[requests][1] = (uintptr_t)dst - OBJ_VRAM0;
    queues[requests++][2] = n;
}
u8 GetBattlerSide(u8 b) { sides++; return b & 1; }
u8 GetBattlerPosition(u8 b) { positions++; return b; }
static unsigned hash(void)
{
    unsigned h = 2166136261u, i;
    const u8 *bytes = buffers[0];
    for (i = 0; i < sizeof buffers; i++) h = (h ^ bytes[i]) * 16777619u;
    return h;
}
static void setup(unsigned trainer)
{
    unsigned b;
    DccBattlePoseReset();
    memset(gBattleMons, 0, sizeof gBattleMons);
    memset(gSprites, 0, sizeof gSprites);
    memset(&gfx, 0, sizeof gfx); memset(buffers, 0, sizeof buffers);
    gMonSpritesGfxPtr = &gfx; gBattleTypeFlags = 8;
    gTrainerBattleOpponent_A = trainer; gBattlersCount = 4;
    gAbsentBattlerFlags = 0; gAnimScriptActive = 1;
    copies = requests = sides = positions = 0;
    scenario++;
    for (b = 0; b < 4; b++)
    {
        gBattleMons[b].hp = 30; gBattlerSpriteIds[b] = b;
        gSprites[b].inUse = 1; gSprites[b].oam.tileNum = 64 * b;
        gSprites[b].images = gfx.frameImages[b]; gfx.sprites.ptr[b] = buffers[b];
    }
    gBattleMons[0].species = SPECIES_MACHOP;
    gBattleMons[1].species = SPECIES_LOUDRED;
    gBattleMons[2].species = SPECIES_MEOWTH;
    gBattleMons[3].species = SPECIES_VOLTORB;
}
static void start(unsigned b, unsigned move)
{
    assert(!copies && !requests);
    gBattleAnimAttacker = gBattlerAttacker = b;
    gCurrentMove = move; gAnimScriptActive = 1;
    DccBattlePoseNotify(); DccBattlePoseStart(move);
    assert(!copies && !requests);
}
static void step(unsigned count)
{
    while (count--)
    {
        unsigned b, i;
        struct BattleMon before[4];
        memcpy(before, gBattleMons, sizeof before);
        sides = positions = 0; DccBattlePoseUpdate();
        assert(!memcmp(before, gBattleMons, sizeof before));
        printf("%u %u %u", scenario, ++tick, hash());
        for (b = 0; b < 4; b++)
        {
            struct DccPoseState *s = &sDccBattlePoses[b];
            printf(" %u,%u,%u,%u", s->action, s->recovering, s->applied,
                s->action == WINDUP && s->age >= 18);
        }
        printf(" W%u", copies);
        for (i = 0; i < copies; i++) printf(" %u,%u,%u,%u", writes[i][0], writes[i][1], writes[i][2], writes[i][3]);
        printf(" Q%u", requests);
        for (i = 0; i < requests; i++) printf(" %u,%u,%u", queues[i][0], queues[i][1], queues[i][2]);
        printf(" COST %u %u\n", sides, positions);
        copies = requests = 0;
    }
}
static void end(void) { gAnimScriptActive = 0; DccBattlePoseNotify(); }
static void guard(unsigned kind, unsigned on, unsigned b)
{
    switch (kind)
    {
    case 0: gMonSpritesGfxPtr = on ? NULL : &gfx; break;
    case 1: gBattlerSpriteIds[b] = on ? 64 : b; break;
    case 2: gSprites[b].inUse = !on; break;
    case 3: gSprites[b].images = on ? NULL : gfx.frameImages[b]; break;
    case 4: gfx.sprites.ptr[b] = on ? NULL : buffers[b]; break;
    }
    // Sprite guards require no notification while a failed transition is active.
}
int main(void)
{
    unsigned trainer, move, kind;
    const unsigned actors[6] = {0, 0, 2, 2, 1, 1};
    assert(sizeof(struct DccPoseState) == 4 && sizeof sDccBattlePoses == 16);
    for (trainer = TRAINER_DCC_BOSS; trainer <= TRAINER_DCC_BOSS_PREPARED; trainer++)
    {
        for (move = 355; move <= 360; move++)
        {
            setup(trainer); start(actors[move - 355], move);
            step(1); step(5); step(1); step(1); step(1); step(7); step(1); step(1); step(300);
            if (move == 359) assert(sDccBattlePoses[1].age >= 18);
            if (move == 360) DccBattlePoseImpact(); else end();
            step(14); step(300);
        }
        setup(trainer); start(0, 355); step(30);
        end(); gAnimScriptActive = 1; DccBattlePoseNotify(); step(1);
        assert(!sDccBattlePoses[0].recovering); // final native state, no early recovery
        gBattleAnimAttacker = 2; DccBattlePoseNotify(); step(12);
        setup(trainer); start(0, 355); step(30);
        gBattleAnimAttacker = 2; DccBattlePoseNotify();
        gBattleAnimAttacker = 0; DccBattlePoseNotify();
        gAbsentBattlerFlags = 1; DccBattlePoseNotify();
        gAbsentBattlerFlags = 0; DccBattlePoseNotify();
        gBattleMons[0].hp = 0; DccBattlePoseNotify();
        gBattleMons[0].hp = 30; DccBattlePoseNotify(); step(1);
        assert(!sDccBattlePoses[0].recovering && sDccBattlePoses[0].action == STRIKE);
        setup(trainer); start(1, 359); step(30); start(0, 356); step(25);
        start(2, 357); step(2); start(0, 355); step(2); start(0, 356); step(30); end(); step(20);
        setup(trainer); start(1, 359); step(30);
        gBattleMons[1].hp = 0; DccBattlePoseNotify(); step(1);
        assert(!sDccBattlePoses[1].action && !sDccBattlePoses[1].applied);
        step(3); DccBattlePoseFaint(1); step(1);
        gBattleMons[1].hp = 30; DccBattlePoseNotify(); step(5);
        setup(trainer); start(1, 359); step(30);
        DccBattlePoseFaint(1); step(3); start(1, 359); step(20);
        setup(trainer); start(0, 355); step(30);
        gAbsentBattlerFlags = 1; DccBattlePoseNotify(); step(1);
        gAbsentBattlerFlags = 0; DccBattlePoseNotify(); step(3); start(0, 355); step(30);
        gBattleMons[0].species = SPECIES_MEOWTH; DccBattlePoseNotify(); step(1);
        gBattleMons[0].species = SPECIES_VOLTORB; DccBattlePoseNotify(); step(1);
        gBattleMons[0].species = SPECIES_MACHOP; DccBattlePoseNotify(); step(2);
        setup(trainer); start(1, 359); step(30); DccBattlePoseReset(); step(5);
        for (move = 355; move <= 360; move++)
        for (kind = 0; kind < 5; kind++)
        {
            unsigned b = actors[move - 355];
            unsigned recovery = move == 356 ? 6 : move == 357 ? 12 : 10;
            setup(trainer); guard(kind, 1, b); start(b, move); step(19);
            assert(sDccBattlePoses[b].age == (kind == 0 ? 0 : 19));
            guard(kind, 0, b); step(3);
            if (move == 359)
            {
                end(); step(30); // native end alone cannot erase a held warning
                start(b, 360); step(1);
            }
            if (move >= 359) { DccBattlePoseImpact(); recovery = 12; }
            else end();
            step(recovery);
            // Final REST copy may fail after recovery; it must remain retryable.
            guard(kind, 1, b); step(4); guard(kind, 0, b); step(4);
            assert(sDccBattlePoses[b].applied == (b == 0 ? 1 : b == 2 ? 7 : 13));
        }
    }
    setup(856); start(0, 355); step(30);
    setup(858); gBattleTypeFlags = 0; start(0, 355); step(30);
    setup(858); start(3, 355); step(30);
    setup(858); start(0, 1); step(30); // unsupported action returns to REST
    setup(858); // Synthetic all-REST pattern; not recovered visual-frame-8536 bytes.
    sDccBattlePoses[0].applied = 1; sDccBattlePoses[1].applied = 13;
    sDccBattlePoses[2].applied = 7; step(10);
    return 0;
}
