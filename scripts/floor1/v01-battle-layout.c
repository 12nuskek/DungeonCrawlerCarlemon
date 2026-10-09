/* Compile-only ABI checks against actual pinned ARM native headers. */
#include "global.h"
#include "battle.h"
#include "sprite.h"
#define BV_OFFSET(type, field) ((unsigned)&(((type *)0)->field))
STATIC_ASSERT(sizeof(struct MonSpritesGfx) == 384, MonSpritesGfxABI)
STATIC_ASSERT(BV_OFFSET(struct MonSpritesGfx, sprites) == 4, PictureBuffers)
STATIC_ASSERT(BV_OFFSET(struct MonSpritesGfx, frameImages) == 116, FrameOwnership)
STATIC_ASSERT(sizeof(struct SpriteFrameImage) == 8, FrameStride)
STATIC_ASSERT(sizeof(struct Sprite) == 68, SpriteStride)
STATIC_ASSERT(BV_OFFSET(struct Sprite, images) == 12, SpriteOwnership)
STATIC_ASSERT(BV_OFFSET(struct Sprite, data) == 46, NativeBattlerOwnership)
