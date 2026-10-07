#include "global.h"
#include "crawler.h"
#include "constants/maps.h"
#include "constants/opponents.h"

// Register each authored map here, regardless of its map group. Other Emerald
// maps must retain their own palette, saved viewport and object reload behavior.
bool8 DccIsMap(u8 mapGroup, u8 mapNum)
{
    switch ((mapGroup << 8) | mapNum)
    {
    case MAP_DCC_ENTRANCE:
    case MAP_DCC_VESTIBULE:
    case MAP_DCC_SERVICE:
    case MAP_DCC_CORRIDOR:
    case MAP_DCC_BOSS:
    case MAP_DCC_EXIT:
    case MAP_DCC_F1D1FIELD:
    case MAP_DCC_F1D1QUIET:
    case MAP_DCC_F1D1WORKSHOP:
    case MAP_DCC_F1D1WARDEN:
    case MAP_DCC_F1D1CHECKPOINT:
        return TRUE;
    }
    return FALSE;
}

// New encounters must opt into local crawler recovery explicitly. Never infer
// membership from adjacency in the stock trainer table.
bool8 DccIsEncounter(u16 trainerId)
{
    switch (trainerId)
    {
    case TRAINER_DCC_TRIAL:
    case TRAINER_DCC_GUARD:
    case TRAINER_DCC_HOWLER:
    case TRAINER_DCC_BOSS:
    case TRAINER_DCC_BOSS_PREPARED:
        return TRUE;
    }
    return FALSE;
}
