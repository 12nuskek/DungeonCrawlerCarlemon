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

#include "pokemon.h"
struct SpriteCopyRequest
{
    const u8 *src;
    u8 *dest;
    u16 size;
};
struct MemBlock {
    // Whether this block is currently allocated.
    bool16 flag;

    // Magic number used for error checking. Should equal MALLOC_SYSTEM_ID.
    u16 magic;

    // Size of the block (not including this header struct).
    u32 size;

    // Previous block pointer. Equals sHeapStart if this is the first block.
    struct MemBlock *prev;

    // Next block pointer. Equals sHeapStart if this is the last block.
    struct MemBlock *next;

    // Data in the memory block. (Arrays of length 0 are a GNU extension.)
    u8 data[0];
};
const u32 observerLayout[] = {sizeof(struct Pokemon),sizeof(struct BoxPokemon),sizeof(struct BattlePokemon),BV_OFFSET(struct BattlePokemon, hp),sizeof(struct SaveBlock1),sizeof(struct SaveBlock2),BV_OFFSET(struct SaveBlock1, flags),sizeof(((struct SaveBlock1 *)0)->flags),BV_OFFSET(struct SaveBlock1, money),BV_OFFSET(struct SaveBlock1, seen1),BV_OFFSET(struct BattleResults, battleTurnCounter),sizeof(struct SpriteCopyRequest),BV_OFFSET(struct SpriteCopyRequest, dest),BV_OFFSET(struct SpriteCopyRequest, size),sizeof(struct MemBlock),BV_OFFSET(struct MemBlock, magic),BV_OFFSET(struct MemBlock, size),BV_OFFSET(struct MemBlock, next)};
const struct Sprite observerInUse = {.inUse = TRUE};
const struct Sprite observerInvisible = {.invisible = TRUE};
const struct Sprite observerAnimBeginning = {.animBeginning = TRUE};
const struct Sprite observerUsingSheet = {.usingSheet = TRUE};
const struct Main observerInBattle = {.inBattle = TRUE};
const struct PaletteFadeControl observerFadeActive = {.active = TRUE};
