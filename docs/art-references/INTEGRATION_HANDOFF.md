# Carl and Donut proposed replacement art

Status: proposed visual reference only, generated 2026-10-06. This is NOT an emulator screenshot, NOT a 64×64 native sprite atlas, NOT indexed GBA-ready art, and NOT integrated or runtime-tested. No repository files were changed by the asset artist.

## Selected deliverable

- File: carl-donut-proposed-replacement-reference-v2.png
- SHA-256: 4c713bb73c041af17a4daf9568087fc911f63daba617c184b68e0744b51619aa
- 1254×1254 RGBA PNG, 947,534 bytes.
- Built-in OpenAI image generation, original prompted composition; second targeted pixel-density simplification of first generated sheet. No third-party image was traced, recolored, or supplied as an image reference. Character names/design brief derive from the user's adaptation project. Do not assert clearance of underlying character IP or call this hand-drawn source.

## Visual intent and review

Carl: adult stocky, broad muscular human with short dark hair, white/cream boxer shorts with red hearts, bare torso and bare feet. Natural asymmetric ready pose. Separate front and three-quarter back views. Donut: fluffy tortoiseshell Persian with proud expression, short broad muzzle, layered ruff and sweeping tail; small gold collar and teal pendant. No tiara, armor, weapons, later-book costumes or forms. The small collar follows the current content ledger; it is an adaptation choice, not a newly verified canon statement.

The second pass is visibly coarser and clearer than the first, with stronger silhouettes and more usable cluster suggestions. However the generator still did not obey an exact logical pixel grid or color budget. It must not be described as hardware-ready. The sheet is not evenly packed into four 64×64 or equal-sized source cells: Carl occupies taller source regions. Front Donut faces somewhat rightward, unlike Carl's leftward front pose; decide orientation deliberately during the actual sprite pass.

## Verified current engine contract

Read from branch task/s02-original-presentation on 2026-10-06:
- scripts/check-slice-art.py: every engine/graphics/dcc PNG must be indexed P mode, all pixel indices <16, width/height aligned to 8.
- engine/graphics/dcc/{carl,donut}/front.png: 64×64.
- back.png: 64×64.
- anim_front.png: 64×128, two vertically stacked 64×64 frames. Current pipeline duplicates the front frame; preserve timing and document duplicates unless deliberately authoring/tested animation.
- icon.png: 32×64, two vertically stacked 32×32 icons.
- Carl trainer_back.png: 64×256, four 64×64 frames in the current authoring script.
- Palette index 0 is transparent. PNG saved with transparency=0, bits=4. Palette exports use JASC-PAL, version 0100, 16 entries. Current normal.pal and shiny.pal are identical for the protagonists.
- Current source of these assets is scripts/content/slice_art.py. Changes made only to generated PNGs would be overwritten on regeneration. Preserve any approved pixel masters and make generation consume them reproducibly.
- Original Carl exploration uses nine 16×32 walking frames in scripts/content/carl_sprite.py, right direction mirrored from left. Donut currently has a 48×16 three-frame standing exploration strip using Carl's separate overworld palette. Battle reference conversion does not complete these overworld deliverables.

Shared current battle palette, indices 0–15 RGB:
0: 0,0,0 (transparent)
1: 25,29,39
2: 62,46,43
3: 115,72,51
4: 189,120,82
5: 244,183,132
6: 255,220,172
7: 241,232,202
8: 177,163,142
9: 191,53,67
10: 111,34,53
11: 231,182,65
12: 69,151,145
13: 35,80,91
14: 110,118,136
15: 190,204,211

The existing shared palette has enough related warm tones for a first conversion. If changing palettes, audit all shared battle/icon/overworld references first; do not silently recolor unrelated sprites.

## Conversion needed by sole integration writer

1. Read the selected PNG committed alongside this handoff and verify its SHA-256 before conversion. Preserve these reference bytes unchanged; author native masters separately.
2. Do not split the source into equal quadrants. Alpha>=128 connected-component bounds (left, top, right exclusive, bottom exclusive) are:
   - Carl front: (78,46,540,706), 462×660.
   - Carl back: (745,46,1206,725), 461×679.
   - Donut front: (108,725,627,1225), 519×500.
   - Donut back: (676,735,1157,1235), 481×500.
   Add a little transparent extraction margin without crossing neighboring subjects, or select each connected component.
3. Resolve alpha to index-0 transparency. Important: most apparently solid body pixels have alpha 253, not 255. Thresholding for alpha==255 would destroy the image. Alpha>=128 is a reasonable first silhouette mask; visually inspect thin fur and toes. This source has 128,413 distinct RGBA values, 670,088 partially transparent pixels, 2,955 fully opaque pixels and 899,473 fully transparent pixels. GBA output must be binary transparency, not the source's partial alpha.
4. Reduce each extracted sprite proportionally into its own 64×64 canvas. Suggested occupied height: Carl about 56–58 pixels, Donut about 43–46 pixels; center horizontally with paws/feet near row 60. Preserve adult anatomy and cat silhouette instead of stretching both to fill the square. Do not claim a resize alone is authored native pixel art.
5. Quantize/map to an explicitly chosen 15 opaque colors plus transparent index 0; remove alpha halos. Rework native 1× clusters and key face/hand/heart/fur pixels. No smooth resampling in the final pixel output. Judge against the actual 240×160 game scene, since an attractive enlarged sheet can still fail in-game.
6. Review native-size front/back, enlarged nearest-neighbor previews, and silhouettes. Hearts must remain readable tiny accents; ensure feet, hands, cat paws and tail are unbroken. Keep fur in large coherent patches rather than isolated noise. Native cleanup is the key remaining art work.
7. Produce the required packed variants and palette files, with documented duplicate frames if retained. Run scripts/check-slice-art.py, compile, then actual emulator captures for duo battle, summary/front views and exploration if changed. Record exact tested commit and route. Keep reference previews clearly separate from gameplay evidence.
8. Update provenance/content ledger: generated reference, conversion steps, any hand-authored cleanup, scope still pending. S02 visual acceptance remains pending until the actual sprites are rendered and reviewed.

## Sources

- https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/26
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/scripts/check-slice-art.py
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/scripts/content/slice_art.py
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/scripts/content/carl_sprite.py
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/docs/content-ledger.md

Generation prompts are saved beside this handoff for reproducibility of intent; image generation itself is not deterministic.

