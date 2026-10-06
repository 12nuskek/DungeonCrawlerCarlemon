# S02 replacement art handoff — 2026-10-06

**Visual acceptance FAILED by user review. Do not merge/finalize the present
character artwork.** Sole implementation writer remains on
`task/s02-original-presentation`; parent coordinates a separate asset-only task
outside this repository. No overlapping repository writer is authorized.
Current source `a242983b6f6d061dd2c5bd4916c34f8b1fd10266` compiles and passes128
runtime assertions, but that does not override the user's art rejection.

Target: readable, appealing Emerald-scale pixel art with stronger silhouettes,
natural poses, deliberate shading and expressive faces. Carl: human, bare torso/
feet, heart-patterned shorts; Donut: long-haired cat, distinctive face/ruff/tail.
No later-book costumes/classes implied. Existing chunky geometric art is a failed
prototype, not a quality reference. Keep original artwork, not traced stock sprites.

## Engine-ready dimensions

| Asset | Exact canvas / frame layout | Pose and use | Current destination |
| --- | --- | --- | --- |
| Carl front |64x64, one frame| Three-quarter/front portrait; summary and future front presentation | `engine/graphics/dcc/carl/front.png` |
| Carl animated front |64x128, two64x64 frames vertically| Same base pose, subtle second frame; duplicate acceptable initially | `engine/graphics/dcc/carl/anim_front.png` |
| Carl back |64x64, one frame| Back/three-quarter facing upper-right, natural ready stance; normal duo battle | `engine/graphics/dcc/carl/back.png` |
| Donut front/animated/back | Same64x64 /64x128 /64x64 contracts | Expressive long-haired cat; back faces upper-right in duo battle | corresponding files under `engine/graphics/dcc/donut/` |
| Party icons, each |32x64, two32x32 frames vertically| Simplified recognizable silhouette, subtle idle | `engine/graphics/dcc/{carl,donut}/icon.png` |
| Carl trainer back |64x256, four64x64 frames vertically| Battle intro ready/gesture sequence; same palette as Carl | `engine/graphics/dcc/carl/trainer_back.png` |
| Carl overworld |144x32, nine16x32 frames horizontally| down, up, left; down-step1/2, up-step1/2, left-step1/2. Right is mirrored left. Feet near bottom, consistent anchor | `engine/graphics/object_events/pics/people/carl/walking.png` |
| Donut overworld |48x16, three16x16 frames horizontally| down, up, left standing; currently stationary exploration scenes, not follower | `engine/graphics/dcc/donut/overworld.png` |

Battle front/back coordinate tables currently use64x64 and y_offset0. Keep the
full figure inside the canvas (e.g. feet near y60–61), with clear padding and a
consistent bottom-center anchor. No automatic cropping, extra frames, variable
frame size or smoothing. Current enemy sprites also use64x64 and can be a later
focused replacement; do not delay the requested protagonist improvement for them.

## Color and transparency

Runtime PNGs must be indexed (P mode), at most16 entries: index0 transparent,
indices1–15 visible. No partial alpha/antialiasing. Front/back/animated frames for
a given character must use identical palette-index meanings. Provide matching
16-color `normal.pal` (JASC-PAL,0100,16); `shiny.pal` may be the same palette.
The engine supports separate Carl and Donut battle palettes. Current assets share
one palette only as a prototype convenience, not a creative constraint.

Party icons currently share palette slot0 via `graphics/dcc/shared.pal`; Carl's
trainer palette also points there. The integrator will wire separate appropriate
palettes if the replacements require them. Please provide the intended palette
for icons and trainer frames explicitly; do not assume changing a PNG's embedded
palette alone changes the runtime palette. Current Donut overworld uses Carl's
palette tag/player slot; independent Donut colors likewise need an integration
change. This is ordinary asset wiring, not a platform/save-format change.

RGBA working references are welcome, but must be labelled references rather than
engine-ready assets. Supply unscaled native pixels when possible, plus optional
nearest-neighbor previews. Keep a provenance/author note and frame/palette manifest.
Do not produce fake emulator screenshots. The sole integrator will compile, run
actual emulator captures and present replacements for visual review.

## Current code/art wiring

- `scripts/content/slice_art.py`: failed prototype generator; will overwrite its
  generated destinations if rerun. Stop generating those paths when replacing
  them with authored assets; preserve unrelated item/tile generation deliberately.
- `scripts/content/carl_sprite.py`: earlier Carl walking generator, same caution.
- `engine/src/data/graphics/pokemon.h`, `engine/src/anim_mon_front_pics.c`:
  front/back/icon/palette assets; internal MACHOP/MEOWTH slots stay engine details.
- `engine/src/data/graphics/trainers.h`: Carl battle intro.
- `engine/src/graphics.c`, `engine/src/pokemon_icon.c`: icon palette selection.
- `engine/src/data/object_events/*`: walking/Donut scene geometry and palette tags.
- `scripts/check-slice-art.py`: dimensions/4bpp/tile budget checks.
- `scripts/test-s02.sh`: isolated production build and128 relevant runtime checks.

Keep gameplay, event/collision semantics and save layout unchanged. Title/menu
correctness can continue independently. Final S02 integration waits for acceptable
replacement art and actual before/after emulator review. S03 remains dependent.
