/* Bounded module instructions on synthetic RAM/bus timings. Never loads a ROM.
 * Native calls are counted stubs; BIOS copy/queue/side/position/memset cost is
 * excluded. These are control-path measurements, not game cycle predictions. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <mgba/core/core.h>
#include <mgba/gba/core.h>
#include <mgba/internal/arm/isa-inlines.h>
#include <mgba/internal/gba/gba.h>
enum { UPDATE, APPLY, NOTIFY, FLAGS, TRAINER, ATTACKER, ANIM, COUNT, ABSENT,
    IDS, MONS, SPRITES, GFX, BITS, STATES, ACTIVE, PENDING, SIDE, POSITION,
    CPUSET, QUEUE, ZERO, PICTURES, MONSIZE, HPOFFSET, SYMBOL_COUNT };
static uint32_t a[SYMBOL_COUNT], *code;
static uint32_t (*nativeLoad32)(struct ARMCore *, uint32_t, int *);
static void region(struct ARMCore *c, uint32_t address)
{
    (void)address; c->memory.activeRegion = code; c->memory.activeMask = 0xffffff;
    c->memory.activeSeqCycles32 = c->memory.activeSeqCycles16 = 1;
    c->memory.activeNonseqCycles32 = c->memory.activeNonseqCycles16 = 1;
}
static uint32_t literal(struct ARMCore *c, uint32_t address, int *cycles)
{
    if (address >> 24 == 8) { if (cycles) *cycles += 1; return code[(address & 0xffffff) / 4]; }
    return nativeLoad32(c, address, cycles);
}
static uint8_t *ram(struct GBA *g, unsigned address, unsigned n)
{
    assert(address >= 0x02000000 && address + n <= 0x02040000);
    return (uint8_t *)g->memory.wram + address - 0x02000000;
}
static void put(struct GBA *g, unsigned address, unsigned value, unsigned n)
{ memcpy(ram(g, address, n), &value, n); }
static void ret(struct ARMCore *c)
{
    assert(c->gprs[ARM_LR] & 1);
    c->executionMode = MODE_THUMB; c->cpsr.t = 1;
    c->gprs[ARM_PC] = c->gprs[ARM_LR] & ~1; ThumbWritePC(c);
}
int main(int argc, char **argv)
{
    unsigned segments, address, bytes, i, test;
    FILE *f;
    assert(argc == 2); code = calloc(1, 0x1000000); assert(code);
    f = fopen(argv[1], "rb"); assert(f);
    assert(fread(a, sizeof *a, SYMBOL_COUNT, f) == SYMBOL_COUNT);
    assert(fread(&segments, 4, 1, f) == 1);
    for (i = 0; i < segments; i++)
    {
        assert(fread(&address, 4, 1, f) == 1 && fread(&bytes, 4, 1, f) == 1);
        assert(address >= 0x08000000 && address + bytes <= 0x09000000);
        assert(fread((uint8_t *)code + (address & 0xffffff), 1, bytes, f) == bytes);
    }
    assert(fgetc(f) == EOF); fclose(f);
    for (test = 0; test < 28; test++)
    {
        struct mCore *core = GBACoreCreate(); struct GBA *g; struct ARMCore *c;
        unsigned entry, action = 0, age = 0, applied = 0, active = 0;
        unsigned steps, sides = 0, positions = 0, copies = 0, requests = 0, clears = 0;
        assert(core && core->init(core)); g = core->board; c = core->cpu;
        mTimingClear(&g->timing); memset(g->memory.wram, 0, 0x40000);
        put(g, a[FLAGS], 8, 4); put(g, a[TRAINER], 858, 2);
        put(g, a[COUNT], 4, 1); put(g, a[ANIM], 1, 1);
        put(g, a[GFX], 0x02030000, 4);
        for (i = 0; i < 4; i++)
        {
            put(g, a[IDS] + i, i, 1);
            put(g, a[MONS] + a[MONSIZE] * i, i == 0 ? 66 : i == 1 ? 294 : i == 2 ? 52 : 100, 2);
            put(g, a[MONS] + a[MONSIZE] * i + a[HPOFFSET], 30, 2);
            put(g, a[SPRITES] + 68 * i + 0x3e, 1, 1);
            put(g, a[SPRITES] + 68 * i + 12, 0x02030074 + 32 * i, 4);
            put(g, 0x02030004 + 4 * i, 0x02031000 + i * 8192, 4);
        }
        /* 0 fresh REST, 1 synthetic frame8536-like all REST, 2/3 held warning/slam,
         * 4 contact hold, 5 warning threshold, 6 contact threshold, 7 recovery,
         * 8 final REST, 9 HP-zero pending, 10 held failed guard, 11 pending
         * held native end, 12 nonpilot notification, 13 pilot notification,
         * 14..20 seven direct Apply guards, 21..27 seven cached guards. */
        entry = a[UPDATE];
        if (test == 1) { applied = 1; put(g, a[STATES] + 7, 13, 1); put(g, a[STATES] + 11, 7, 1); }
        if (test == 2) { action = 5; age = 18; applied = 15; }
        if (test == 3) { action = 6; age = 1; applied = 16; }
        if (test == 4) { action = 1; age = 8; applied = 3; }
        if (test == 5) { action = 5; age = 17; applied = 15; active = 1; }
        if (test == 6) { action = 1; age = 7; applied = 2; active = 1; }
        if (test == 7) { action = 1; applied = 3; active = 1; put(g, a[STATES] + 2, 1, 1); }
        if (test == 8) { applied = 4; active = 1; }
        if (test == 9) { action = 5; age = 18; applied = 15; active = 1; put(g, a[MONS] + a[HPOFFSET], 0, 2); }
        if (test == 10) { action = 1; age = 12; active = 1; put(g, a[SPRITES] + 12, 0, 4); }
        if (test == 11) { action = 1; age = 8; applied = 3; put(g, a[ANIM], 0, 1); if (a[PENDING]) put(g, a[PENDING], 15, 1); }
        if (test == 12 || test == 13) { entry = a[NOTIFY]; if (test == 12) put(g, a[FLAGS], 0, 4); }
        put(g, a[STATES], action, 1); put(g, a[STATES] + 1, age, 1); put(g, a[STATES] + 3, applied, 1);
        if (a[ACTIVE]) put(g, a[ACTIVE], active, 1);
        if (test >= 14)
        {
            unsigned guard = test <= 20 ? test - 14 : test - 21;
            entry = a[APPLY]; put(g, a[STATES] + 3, test >= 21 ? 1 : 0, 1);
            if (guard == 1) put(g, a[GFX], 0, 4);
            if (guard == 2) put(g, a[IDS], 64, 1);
            if (guard == 4) put(g, a[SPRITES] + 0x3e, 0, 1);
            if (guard == 5) put(g, a[SPRITES] + 12, 0, 4);
            if (guard == 6) put(g, 0x02030004, 0, 4);
            c->gprs[1] = guard == 3 ? 17 : 0;
        }
        c->memory.setActiveRegion = region; region(c, entry);
        nativeLoad32 = c->memory.load32; c->memory.load32 = literal;
        ARMSetPrivilegeMode(c, MODE_SYSTEM); c->executionMode = MODE_THUMB; c->cpsr.packed = 0x3f;
        c->gprs[ARM_SP] = 0x03007c00; c->gprs[ARM_LR] = 0x08000081;
        c->gprs[0] = 0; c->gprs[ARM_PC] = entry; ThumbWritePC(c);
        c->cycles = 0; c->nextEvent = INT_MAX;
        for (steps = 0; steps < 5000; steps++)
        {
            unsigned pc = (unsigned)c->gprs[ARM_PC] - (c->executionMode == MODE_THUMB ? 2 : 4);
            if (pc == 0x08000080) break;
            if (pc == a[SIDE]) { c->gprs[0] &= 1; sides++; ret(c); }
            else if (pc == a[POSITION]) { positions++; ret(c); }
            else if (pc == a[CPUSET])
            {
                unsigned n = ((unsigned)c->gprs[2] & 0x1fffff) * 4;
                assert(n == 2048 && copies < 4);
                assert((unsigned)c->gprs[1] == 0x02031000 + copies * 2048);
                memcpy(ram(g, c->gprs[1], n), (uint8_t *)code + (c->gprs[0] & 0xffffff), n);
                copies++; ret(c);
            }
            else if (pc == a[QUEUE])
            { assert(c->gprs[0] == 0x02031000 && c->gprs[1] == 0x06010000 && c->gprs[2] == 2048); requests++; ret(c); }
            else if (pc == a[ZERO])
            { memset(ram(g, c->gprs[0], c->gprs[2]), c->gprs[1], c->gprs[2]); clears++; ret(c); }
            else ARMRun(c);
        }
        if (steps == 5000) fprintf(stderr, "cost fixture limit: test=%u pc=%08x\n", test, c->gprs[ARM_PC]);
        assert(steps < 5000);
        if (test >= 14)
        {
            unsigned changed = test == 14;
            assert(copies == 4 * changed && requests == changed);
            for (i = 0; i < 8192; i++)
            {
                unsigned poseAddress = code[(a[PICTURES] & 0xffffff) / 4];
                unsigned expected = changed ? ((uint8_t *)code)[(poseAddress & 0xffffff) + i % 2048] : 0;
                assert(*ram(g, 0x02031000 + i, 1) == expected);
            }
        }
        printf("{\"case\":%u,\"stepsIncludingStubs\":%u,\"syntheticCyclesExcludingNativeStubs\":%u,\"sideCalls\":%u,\"positionCalls\":%u,\"copies\":%u,\"requests\":%u,\"clears\":%u,\"action\":%u,\"age\":%u,\"recovering\":%u,\"applied\":%u,\"PASS\":true}\n",
            test, steps, (unsigned)mTimingCurrentTime(&g->timing), sides, positions, copies, requests, clears,
            *ram(g, a[STATES], 1), *ram(g, a[STATES] + 1, 1), *ram(g, a[STATES] + 2, 1), *ram(g, a[STATES] + 3, 1));
        core->deinit(core);
    }
    free(code); return 0;
}
