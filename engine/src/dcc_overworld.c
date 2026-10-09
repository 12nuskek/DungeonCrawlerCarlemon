#include "global.h"
#include "dcc_overworld.h"
#include "event_object_movement.h"
#include "field_player_avatar.h"
#include "script.h"
#include "sprite.h"
#include "constants/event_objects.h"

extern const u8 DCC_Donut_Talk[];

// Visual state only. No task/object allocation, movement, script wait or save data.
static EWRAM_DATA struct
{
    struct ObjectEvent *object;
    u8 pending;
    u8 frames;
    u8 paused;
    u8 direction;
} sDonutAttention = {0};

void DccDonutAttentionTryStart(const u8 *afterFacePlayer)
{
    struct ObjectEvent *objectEvent;
    u8 direction;

    // The existing Talk script is lock, faceplayer, msgbox. Its bytes stay fixed.
    if (afterFacePlayer != DCC_Donut_Talk + 2 || gSelectedObjectEvent >= OBJECT_EVENTS_COUNT)
        return;
    objectEvent = &gObjectEvents[gSelectedObjectEvent];
    direction = GetOppositeDirection(GetPlayerFacingDirection());
    if (!objectEvent->active || objectEvent->graphicsId != OBJ_EVENT_GFX_SKITTY
        || objectEvent->mapGroup != 35 || objectEvent->mapNum != 1 || objectEvent->localId != 5
        || (direction != DIR_WEST && direction != DIR_EAST))
        return;
    sDonutAttention.object = objectEvent;
    sDonutAttention.pending = TRUE;
    sDonutAttention.frames = 24;
    sDonutAttention.direction = direction;
}

void DccDonutAttentionUpdate(struct ObjectEvent *objectEvent, struct Sprite *sprite)
{
    if (objectEvent != sDonutAttention.object)
        return;
    if (!objectEvent->active || objectEvent->graphicsId != OBJ_EVENT_GFX_SKITTY
        || objectEvent->mapGroup != 35 || objectEvent->mapNum != 1 || objectEvent->localId != 5)
    {
        sDonutAttention.object = NULL;
        return;
    }
    if (sDonutAttention.pending)
    {
        if (!ScriptContext_IsEnabled())
        {
            sDonutAttention.object = NULL;
            return;
        }
        // Let the original held face movement finish before displaying the pose.
        if (!objectEvent->heldMovementFinished)
            return;
        if (objectEvent->facingDirection != sDonutAttention.direction)
        {
            sDonutAttention.object = NULL;
            return;
        }
        sDonutAttention.pending = FALSE;
        sDonutAttention.paused = sprite->animPaused;
        StartSpriteAnim(sprite, sDonutAttention.direction == DIR_WEST
            ? ANIM_DCC_DONUT_ATTENTION_WEST : ANIM_DCC_DONUT_ATTENTION_EAST);
    }
    if (!sDonutAttention.frames || !ScriptContext_IsEnabled()
        || objectEvent->facingDirection != sDonutAttention.direction)
    {
        StartSpriteAnim(sprite, GetFaceDirectionAnimNum(objectEvent->facingDirection));
        sprite->animPaused = objectEvent->frozen
            ? sDonutAttention.paused : objectEvent->spriteAnimPausedBackup;
        sDonutAttention.object = NULL;
        return;
    }
    sprite->animPaused = FALSE;
    sDonutAttention.frames--;
}
