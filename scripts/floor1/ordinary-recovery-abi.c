/* Compile-only native header layout and bitfield checks for ordinary recovery. */
#include "global.h"
#include "battle.h"
#include "main.h"
#include "palette.h"
#include "task.h"
#include "constants/vars.h"
#define O_OFFSET(type, field) ((unsigned)&(((type *)0)->field))
const u32 ordinaryLayout[] = {
 sizeof(struct Pokemon), sizeof(struct BoxPokemon), sizeof(struct BattlePokemon),
 O_OFFSET(struct BattlePokemon, hp), sizeof(struct SaveBlock1), sizeof(struct SaveBlock2),
 O_OFFSET(struct SaveBlock1, flags), sizeof(((struct SaveBlock1 *)0)->flags),
 O_OFFSET(struct SaveBlock1, money), O_OFFSET(struct SaveBlock1, seen1),
 O_OFFSET(struct SaveBlock1, playerPartyCount), O_OFFSET(struct SaveBlock1, playerParty),
 O_OFFSET(struct SaveBlock1, vars) + 2*(VAR_FRIENDSHIP_STEP_COUNTER-0x4000),
 O_OFFSET(struct SaveBlock2, encryptionKey), sizeof(struct ObjectEvent),
 O_OFFSET(struct ObjectEvent, currentCoords), O_OFFSET(struct PlayerAvatar, objectEventId),
 O_OFFSET(struct Main, callback1), O_OFFSET(struct Main, callback2),
 O_OFFSET(struct Main, vblankCallback), sizeof(struct Task), O_OFFSET(struct Task, isActive)
};
const struct ObjectEvent ordinaryFacing = {.facingDirection = 1};
const struct Main ordinaryBattle = {.inBattle = TRUE};
const struct PaletteFadeControl ordinaryFade = {.active = TRUE};
