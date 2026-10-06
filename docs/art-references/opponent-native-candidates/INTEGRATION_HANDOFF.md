# Opponent-art integration candidates

Prepared 2026-10-06 against repository contract inspection base
`d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530`.
This package stages source references and native candidates only. No engine
integration, compilation, emulator runs or game screenshots are provided.
Technical format validity and neutral-background visual review do not establish
runtime correctness or user acceptance.

## Existing roster only

1. Scuttler, internal ZIGZAGOON slot: rusty chitin arthropod. Trial melee foe and
   patrol partner.
2. Grub, WURMPLE: teal segmented larva. Trial melee foe.
3. Guard, SPINDA: compact gray/teal armored sentry with red visor. Existing durable
   BRACE/TACKLE patrol.
4. Howler, WHISMUR: crimson wing-armed screamer with large dark mouth and golden
   eyes. Existing WEAKEN patrol and boss helper.
5. Warden, LOUDRED: broad armored automaton with amber visor and red core.
   Existing WIND UP/SLAM gate boss.

Names, roles and basic silhouettes derive from the existing content ledger,
species names, trainer parties and `scripts/content/slice_art.py`. These are
original tutorial adaptations, not identification of canonical Book 1 enemies.
Do not introduce new enemies, equipment with gameplay meaning, abilities,
encounters, movement, story or later-book material through this art change.

## Exact native file contracts

Each `assets/{scuttler,grub,guard,howler,warden}/` directory contains:

| File | Contract |
| --- | --- |
| `front.png` | 64x64, one front/three-quarter battle sprite |
| `back.png` | Identical to front; preserves the non-playable opponent contract, not a newly authored rear view |
| `anim_front.png` | 64x128, two identical front frames; no authored motion |
| `normal.pal`, `shiny.pal` | Identical JASC-PAL 0100 16-entry palettes, separate per opponent |
| `icon.png` | 32x64, two identical 32x32 frames using the existing shared palette |
| `overworld.png` | One stationary 32x32 token for Scuttler, Guard, Howler and Warden only |

No Grub token is created: none was mapped in the inspected game. The Grub cell
in the small-asset preview is its icon only. Tokens are static, not directional
walk cycles, and their existence does not establish completed world integration.

All 24 PNGs are indexed P mode at 4bpp, with transparent index 0 and at most
15 opaque indices. No smooth alpha, extra frames or variable canvas sizes.
Battle palettes are snapped to RGB555 precision. Occupied sizes are Scuttler
52x39, Grub 42x33, Guard 47x50, Howler 56x46 and Warden 60x48; all bottom-align
to y=61 inside 64x64. Warden is broader rather than stretched taller.

The five small icons and four tokens are source-derived conversion candidates.
Fine detail is reduced at 32x32; actual room and interface readability still
requires review in the game with surrounding actors and tiles.

## Palette wiring

Battle front/back/animation PNGs share each opponent's own exact battle indices
and matching `normal.pal`. The inspected `engine/src/data/graphics/pokemon.h`
already points each relevant species at its own `graphics/dcc/{name}/normal.pal`
and `shiny.pal`. Replace each complete set coherently. Do not remap the battle
fronts through the old shared battle palette.

Icons and stationary tokens intentionally retain the exact existing
`graphics/dcc/shared.pal` indices. `source/existing-shared.pal` is the verified
185-byte repository palette, Git blob `a53187e0f6ff720864149e69d6855dbce4db2c91`.
Its input copy had one extra trailing blank line, removed during independent
staging review. Palette colors and all native output bytes are unchanged.
Mapping distance used the RGB555-truncated runtime colors.

Keep the existing shared icon slot 0 / prop palette binding. Do not attach these
small assets to their new battle palettes. Do not replace the runtime shared
palette, reserve new banks, recolor other NPCs, or touch Carl and Donut's existing
independent palettes. Guard and Warden happen to share battle palette definitions;
that coincidence does not change the shared-small-asset contract.

## Generator ownership

The inspected `scripts/content/slice_art.py` still generates and overwrites all
five opponent sets, their icons and four tokens with geometric placeholders.
The sole integrator must replace only that opponent export path with deliberate
native-master ownership. Preserve unrelated tiles, items, NPCs, title, battle
arena and both protagonist exporters. Do not invoke this standalone converter
from the game's generation loop without intentionally adapting its source/output
paths and dependency assumptions.

Suggested runtime destinations are the corresponding
`engine/graphics/dcc/{name}/` files. Preserve source references, prompts and native
masters for provenance. Do not alter engine IDs, stats, moves, AI, event/collision
semantics, frame counts, save layouts or timings.

## Reproduction and independent verification

Requirements: Python 3, Pillow and NumPy. From this package:

```sh
sha256sum -c SHA256SUMS
python3 validate_native.py
python3 verify_reproduction.py
```

`convert_native.py` verifies the exact final reference SHA256 before operating.
Crops use individually measured alpha-component bounds, not equal grid cuts.
It thresholds source alpha at 128, area-samples to each occupied size, and maps
immediately to a selected 15-color palette without dithering. Source-only color
masks preserve eyes, visors and cores. Scuttler's eye mask is constrained to the
measured eye regions so shell highlights are not recolored red. `manifest.json`
records every limited source-detail correction. Small assets are independently
mapped to the original shared palette.

This is generated source art, deterministic technical conversion and limited
source-detail cleanup. It is not fully hand-drawn native animation. Generated
references can contain many colors and partial-alpha edges; only `assets/`
contains the indexed native candidates.

`validate_native.py` checks all 24 PNG dimensions, PNG 4bpp encoding, matching
palettes, transparent index 0, native margins, source hash, front/back identity,
packed duplicates and exact nearest-neighbor 6x previews. Independent review
additionally checks binary pixel alpha, 16-entry PNG palettes, absence of text/EXIF
metadata, packed front-frame equality and token/icon equality. Reproduction in
a clean temporary directory yields the same 41 output files in two successive
runs, even after restoring the exact repository palette bytes. Reports are
included. These checks do not prove runtime correctness.

## Required integration acceptance

Coordinate a separate scoped change through the repository's sole implementation
writer after the active baseline acceptance run is complete. Do not mix these
assets into an in-progress isolated run or create a competing implementation.

1. Inspect the actual pixels in the consuming environment, verify `SHA256SUMS`
   and recheck all destination, loader and palette bindings at the current commit.
2. Integrate complete sets and establish generator ownership. Ensure inherited
   Spinda spot rendering does not modify the Guard sprite in its SPINDA slot.
   Regenerate game
   content twice; verify art reproducibility and no unrelated changed files.
3. Run existing art contract checks and the relevant build/regression suite from
   an isolated committed snapshot. Record the exact tested commit, ROM hash,
   complete raw logs and assertion outcomes.
4. Capture actual trial battles with Scuttler/Grub, Guard, Howler and the Warden
   with its helper. Inspect colors, silhouettes, footprint, offsets, clipping,
   double-battle overlap, text/UI readability and unchanged combat behavior.
5. Capture the existing Scuttler/Guard/Howler/Warden map tokens beside Carl,
   Donut and NPCs. Test interaction, event/collision footprint, map/menu/battle
   return and cold reload. Static token candidates remain unaccepted until then.
6. Inspect shared icons where reachable and preserve palette-slot behavior.
   Do not expose a creature collection interface to reach inaccessible icons.
7. Link the scoped issue and draft PR with exact-commit before/after emulator
   captures as the working contract requires. Neutral-background previews and
   source references must never be labelled as emulator evidence.

For this docs/reference package: implemented = staged candidate files;
compiled = N/A; runtime verified = NO; runtime integration = PENDING;
emulator screenshots = N/A. No ROM, save or build product is included.

## Source provenance

OpenAI's built-in image generator produced `source/opponents-reference-v1.png`
from the existing roster descriptions and established protagonist art direction.
No third-party image was supplied or traced. One density-simplification edit
produced `source/opponents-reference-v2.png` using `source/revision-prompt.txt`.
Both generated PNGs are preserved byte-for-byte. The archived original prompt
has one conversation-relative phrase generalized without changing its requested
art direction; the revision prompt is unchanged.

Final generated reference SHA256:
`000068d6bdae0a60e93836438920f4f3b847cee6aca8335733d3f05c7ac4a279`.

The original draft, final source, provenance prompts and local conversion are
included. The shared palette derives from the repository as recorded above.
This provenance statement does not assert legal clearance of underlying adapted
character IP or acceptance of the native conversion as finished game art.
