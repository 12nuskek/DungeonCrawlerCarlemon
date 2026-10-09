#ifndef GUARD_DCC_OVERWORLD_H
#define GUARD_DCC_OVERWORLD_H

struct ObjectEvent;
struct Sprite;

#define ANIM_DCC_DONUT_ATTENTION_WEST 20
#define ANIM_DCC_DONUT_ATTENTION_EAST 21

void DccDonutAttentionTryStart(const u8 *afterFacePlayer);
void DccDonutAttentionUpdate(struct ObjectEvent *objectEvent, struct Sprite *sprite);

#endif
