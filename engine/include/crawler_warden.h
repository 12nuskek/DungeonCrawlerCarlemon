#ifndef GUARD_CRAWLER_WARDEN_H
#define GUARD_CRAWLER_WARDEN_H
#include "constants/battle.h"
#include "constants/moves.h"
#include "constants/opponents.h"
#include "constants/species.h"

// Pure encounter guards: shared moves and stock battles retain their rules.
static inline bool8 DccWardenEncounter(u16 trainer, u32 flags)
{
    return (trainer == TRAINER_DCC_BOSS || trainer == TRAINER_DCC_BOSS_PREPARED)
        && (flags & BATTLE_TYPE_TRAINER)
        && !(flags & ~(BATTLE_TYPE_TRAINER | BATTLE_TYPE_DOUBLE | BATTLE_TYPE_IS_MASTER));
}

static inline bool8 DccWardenSlam(u16 trainer, u32 flags, u16 species, u8 side, u16 move)
{
    return DccWardenEncounter(trainer, flags) && side == B_SIDE_OPPONENT
        && species == SPECIES_LOUDRED && move == MOVE_DCC_SLAM;
}

static inline bool8 DccWardenHelper(u16 trainer, u32 flags, u16 species, u8 side)
{
    return DccWardenEncounter(trainer, flags) && side == B_SIDE_OPPONENT
        && species == SPECIES_WHISMUR;
}

static inline bool8 DccWardenHelperAttacks(u8 turn)
{
    // Opening WIND UP, then every second WIND UP: 0, 4, 8, ...
    return turn % 4 == 0;
}
#endif
