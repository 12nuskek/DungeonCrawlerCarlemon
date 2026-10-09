/* Compile-only ABI checks against actual pinned ARM native headers. */
#include "global.h"
#include "battle.h"
#include "sprite.h"
#include "main.h"
#include "palette.h"
#include "task.h"
#define BV_OFFSET(type, field) ((unsigned)&(((type *)0)->field))
STATIC_ASSERT(sizeof(struct MonSpritesGfx) == 384, MonSpritesGfxABI)
STATIC_ASSERT(BV_OFFSET(struct MonSpritesGfx, sprites) == 4, PictureBuffers)
STATIC_ASSERT(BV_OFFSET(struct MonSpritesGfx, frameImages) == 116, FrameOwnership)
STATIC_ASSERT(sizeof(struct SpriteFrameImage) == 8, FrameStride)
STATIC_ASSERT(sizeof(struct Sprite) == 68, SpriteStride)
STATIC_ASSERT(BV_OFFSET(struct Sprite, images) == 12, SpriteOwnership)
STATIC_ASSERT(BV_OFFSET(struct Sprite, data) == 46, NativeBattlerOwnership)
STATIC_ASSERT(BV_OFFSET(struct Main, callback1) == 0, FieldCallback1)
STATIC_ASSERT(BV_OFFSET(struct Main, callback2) == 4, FieldCallback2)
STATIC_ASSERT(BV_OFFSET(struct Main, savedCallback) == 8, SavedTrainerReturn)
STATIC_ASSERT(BV_OFFSET(struct Main, state) == 0x438, NativeFieldLoadState)
STATIC_ASSERT(sizeof(struct Task) == 40, FieldTaskStride)
STATIC_ASSERT(BV_OFFSET(struct Task, isActive) == 4, FieldTaskActive)
/* The native compiler output verifies the bitfield accessor used by the host. */
unsigned BvNativeFadeActive(void) { return gPaletteFade.active; }
