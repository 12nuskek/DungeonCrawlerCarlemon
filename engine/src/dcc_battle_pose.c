#include "global.h"
#include "battle.h"
#include "battle_anim.h"
#include "battle_setup.h"
#include "battle_util.h"
#include "dcc_battle_pose.h"
#include "sprite.h"
#include "util.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "constants/trainers.h"

// Verified native PNGs, not animated front-picture replacement stacks.
#include "data/dcc_battle_pose_graphics.h"

enum { REST, STRIKE, BRACE, SPARK, WEAKEN, WINDUP, SLAM, RECOVER };
struct DccPoseState { u8 action, age, recovering, applied; };
static EWRAM_DATA struct DccPoseState sDccBattlePoses[MAX_BATTLERS_COUNT] = {0};

static bool8 IsPilot(void)
{
    return (gBattleTypeFlags & BATTLE_TYPE_TRAINER)
        && (gTrainerBattleOpponent_A == TRAINER_DCC_BOSS
            || gTrainerBattleOpponent_A == TRAINER_DCC_BOSS_PREPARED);
}

static u8 Character(u8 battler)
{
    u8 side = GetBattlerSide(battler);
    u16 species = gBattleMons[battler].species;
    if (side == B_SIDE_PLAYER && species == SPECIES_MACHOP) return 0;
    if (side == B_SIDE_PLAYER && species == SPECIES_MEOWTH) return 1;
    if (side == B_SIDE_OPPONENT && species == SPECIES_LOUDRED) return 2;
    return 3;
}

static void Apply(u8 battler, u8 pose)
{
    struct Sprite *sprite;
    u8 position, i, id = gBattlerSpriteIds[battler];
    struct DccPoseState *state = &sDccBattlePoses[battler];
    if (!gMonSpritesGfxPtr || id >= MAX_SPRITES || pose >= ARRAY_COUNT(sDccPosePictures)) return;
    if (state->applied == pose + 1) return;
    sprite = &gSprites[id];
    position = GetBattlerPosition(battler);
    // Do not touch reused trainer/effect slots or a replaced sprite buffer.
    if (!sprite->inUse || sprite->images != gMonSpritesGfxPtr->frameImages[position]
        || !gMonSpritesGfxPtr->sprites.ptr[position]) return;
    for (i = 0; i < MAX_MON_PIC_FRAMES; i++)
        CpuCopy32(sDccPosePictures[pose], gMonSpritesGfxPtr->sprites.byte[position] + MON_PIC_SIZE * i, MON_PIC_SIZE);
    RequestSpriteCopy(gMonSpritesGfxPtr->sprites.ptr[position],
        (u8 *)OBJ_VRAM0 + sprite->oam.tileNum * TILE_SIZE_4BPP, MON_PIC_SIZE);
    state->applied = pose + 1;
}

void DccBattlePoseReset(void)
{
    memset(sDccBattlePoses, 0, sizeof(sDccBattlePoses));
}

void DccBattlePoseStart(u16 move)
{
    u8 battler = gBattleAnimAttacker, character, action = REST;
    struct DccPoseState *state;
    if (!IsPilot() || battler >= gBattlersCount || !gBattleMons[battler].hp) return;
    character = Character(battler);
    if (character == 0) action = move == MOVE_DCC_STRIKE ? STRIKE : move == MOVE_DCC_BRACE ? BRACE : REST;
    if (character == 1) action = move == MOVE_DCC_SPARK ? SPARK : move == MOVE_DCC_WEAKEN ? WEAKEN : REST;
    if (character == 2) action = move == MOVE_DCC_WINDUP ? WINDUP : move == MOVE_DCC_SLAM ? SLAM : REST;
    if (character == 3) return;
    state = &sDccBattlePoses[battler];
    state->action = action;
    state->age = state->recovering = 0;
}

void DccBattlePoseImpact(void)
{
    // Existing HP-update command is the real action resolution, not a timer.
    if (IsPilot() && gBattlerAttacker < gBattlersCount && gCurrentMove == MOVE_DCC_SLAM
        && Character(gBattlerAttacker) == 2 && sDccBattlePoses[gBattlerAttacker].action == SLAM)
    {
        sDccBattlePoses[gBattlerAttacker].action = RECOVER;
        sDccBattlePoses[gBattlerAttacker].age = 0;
    }
}

void DccBattlePoseFaint(u8 battler)
{
    if (IsPilot() && battler < MAX_BATTLERS_COUNT)
        memset(&sDccBattlePoses[battler], 0, sizeof(sDccBattlePoses[battler]));
}

void DccBattlePoseUpdate(void)
{
    u8 battler;
    if (!IsPilot() || !gMonSpritesGfxPtr) return;
    for (battler = 0; battler < gBattlersCount; battler++)
    {
        u8 character = Character(battler), pose;
        struct DccPoseState *state = &sDccBattlePoses[battler];
        if (character == 3 || (gAbsentBattlerFlags & gBitTable[battler]) || !gBattleMons[battler].hp)
        {
            memset(state, 0, sizeof(*state));
            continue;
        }
        // No graphics writes before a real move has started in this encounter.
        if (!state->action && !state->applied) continue;
        if (state->action >= STRIKE && state->action <= WEAKEN
            && (!gAnimScriptActive || gBattleAnimAttacker != battler) && !state->recovering)
        {
            state->recovering = TRUE;
            state->age = 0;
        }
        pose = character == 0 ? 0 : character == 1 ? 6 : 12;
        switch (state->action)
        {
        case STRIKE: pose = state->recovering ? 3 : state->age < 7 ? 1 : 2; break;
        case BRACE: pose = state->recovering ? 4 : state->age < 8 ? 4 : 5; break;
        case SPARK: pose = state->recovering ? 9 : state->age < 8 ? 7 : 8; break;
        case WEAKEN: pose = state->recovering ? 9 : state->age < 8 ? 10 : 11; break;
        case WINDUP: pose = state->age < 6 ? 12 : state->age < 16 ? 13 : 14; break;
        case SLAM: pose = 15; break;
        case RECOVER: pose = 16; break;
        }
        Apply(battler, pose);
        if (state->age < 255) state->age++;
        if ((state->recovering && state->age >= (state->action == SPARK ? 12 : state->action == BRACE ? 6 : 10))
            || (state->action == RECOVER && state->age >= 12))
        {
            state->action = REST;
            state->recovering = FALSE;
            state->age = 0;
        }
    }
}
