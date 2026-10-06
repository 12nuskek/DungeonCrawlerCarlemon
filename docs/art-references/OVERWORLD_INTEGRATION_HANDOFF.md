# Carl and Donut exploration reference handoff

Status: proposed replacement exploration art/reference, 2026-10-06. Two built-in image-generation attempts completed: original overworld translation of the approved battle reference, then a targeted alternate-walking-foot correction. NOT an emulator screenshot, NOT engine-ready sprites, NOT a validated animation cycle. Asset-only work; no repository edits.

## Selected image

- Filename: carl-donut-overworld-proposed-reference-v2.png
- SHA-256: dd41385d4d2bb64fbccd0c83d1aef188505d04ea567914c166831a6f4a3d4b80
- Size: 968151 bytes; 1086×1448 RGBA.
- Approved battle identity reference: carl-donut-proposed-replacement-reference-v2.png.
- Provenance: generated with the built-in OpenAI image generator, using the earlier generated and user-approved battle sheet as an identity/style reference. No external illustration was supplied or traced. Character adaptation direction remains derived from the user's game. Do not call these hand-authored native sprites or imply rights clearance of underlying characters.

## Useful design direction

Carl is the same broad-shouldered, short dark-haired adult, with warm skin, bare torso and feet, and white/cream red-heart boxers. Overworld arms are relaxed for walking instead of a battle stance. Down, up and side views are clear. Donut retains the Persian face, tortoiseshell warm-dark/cream/russet coat, large ruff and plumed tail, with the approved small gold/teal collar and no tiara or later-story costume.

The first pass duplicated both walking columns. The selected revision successfully alternates visible lead feet in down/up rows, but introduced a right-facing final side pose. This reference is useful for coherent appearance; it is not a complete correct animation.

## Remaining defects to correct in native art

1. Row 3 column 3 faces RIGHT, contrary to the requested all-left row. Mirror/redraw this pose into a left-facing opposite contact; do not import it into the left-walk slot unchanged. Verify near/far leg shading and arm counter-swing after mirroring. The engine supplies right-facing through mirroring.
2. Donut's back reference touches the bottom image boundary at y=1448. Restore tail/paw margin in the native redraw. Restore the missing margin deliberately rather than assuming the clipped reference is a complete native frame.
3. Per-pose proportions are not mechanically consistent. A proportional fit into 14×28 gives Carl front/back about 20–22 pixels tall but side views 24–28. Do not independently fit each frame and create height pumping. Normalize one shared head/body/ground baseline and width before authoring the cycle.
4. Native-density diagnostic confirms that shrinking alone loses clean eye/heart/fur clusters. Rebuild the key pixels on the 16×32 and 16×16 grids; do not present a high-resolution resize as finished pixel art.
5. Source is not palette-constrained: 132461 distinct RGBA values. Alpha: 975252 fully transparent pixels, 594329 partial, only 2947 fully opaque. Most apparently solid pixels have alpha 253. Never mask with alpha==255; use a visually reviewed binary threshold, with alpha>=128 as a starting point.
6. Donut reference size relative to Carl is exaggerated on the sheet for visibility. In-game she must occupy a 16×16 frame, roughly half Carl's frame height, without giant-cat scale.

## Verified current export contract

Read from task/s02-original-presentation/scripts/content/carl_sprite.py:
- Carl walking PNG is engine/graphics/object_events/pics/people/carl/walking.png.
- Final atlas 144×32: nine horizontal 16×32 indexed frames.
- Index 0 transparent, 16-color palette.
- Exact frame order:
  0 down idle
  1 up idle
  2 left idle
  3 down walk A
  4 down walk B
  5 up walk A
  6 up walk B
  7 left walk A
  8 left walk B
- Right-facing direction uses the engine's left-frame mirroring.
- Current generator places authored 24-pixel-tall art at y=5..28 with walk feet extending to y=29. Preserve ground contact/alignment unless the renderer offsets are deliberately reviewed.
- Donut currently exports engine/graphics/dcc/donut/overworld.png as a 48×16 strip, three 16×16 standing frames, sharing Carl's loaded overworld palette. Current script duplicates one front image. Confirm the object animation frame map before assigning distinct down/up/left views. Do not promise follower movement; this sheet does not implement following behavior.
- Source pipeline is scripts/content/carl_sprite.py for Carl and scripts/content/slice_art.py for Donut. Preserve approved native masters and make regeneration consume them. Editing generated PNGs alone will be overwritten.
- Keep fixed graphics IDs, event/collision behavior, frame count, palette-slot budget and save layout unchanged.

Current Carl overworld palette RGB, indices 0–15:
0 0,0,0 (transparent)
1 48,32,32
2 89,52,38
3 142,88,56
4 244,183,136
5 211,137,99
6 255,212,160
7 237,236,215
8 170,178,180
9 204,50,66
10 135,31,48
11 255,255,239
12 52,65,75
13 99,106,106
14 0,0,0
15 0,0,0

This differs from the battle shared palette. Do not reuse battle indices blindly. If using 14/15 for collar accents, first verify those slots are truly unused by every consumer of this overworld palette; do not change unrelated pixels or add a palette bank.

## Source extraction coordinates

Alpha>=128 component bounds, (left,top,right-exclusive,bottom-exclusive), in visual row-major order:
- Row1 down idle: (79,48,316,383)
- Row1 down A: (446,48,674,395)
- Row1 down B: (788,48,1018,396)
- Row2 up idle: (80,421,307,758)
- Row2 up A: (443,421,665,769)
- Row2 up B: (790,421,1017,769)
- Row3 left idle: (101,788,271,1141)
- Row3 left A: (445,788,647,1138)
- Row3 RIGHT contact needing correction: (809,789,993,1139)
- Row4 Donut down: (98,1160,310,1439)
- Row4 Donut up: (465,1191,677,1448), touches bottom edge
- Row4 Donut left: (782,1196,1042,1426)

Map visual sheet to final Carl engine frame order: [r1c1, r2c1, r3c1, r1c2, r1c3, r2c2, r2c3, r3c2, corrected r3c3].

## Native art and validation guidance

Use the reference to author coherent clusters at actual native resolution:
- Carl: outline and hair deep warm brown; 7–8-pixel readable head, single dark eye pixels, 2–3 skin tones, broad but tapered 12–14-pixel shoulder silhouette, waist narrower than shoulders; boxer white/cream and tiny red heart accents; distinctly separate feet.
- Keep his face/torso adult and stout without rectangular robot anatomy. Rebalance front and side proportions to the same height.
- Keep movement modest: one-pixel shifts, alternating feet and counter-swinging arms, invariant idle center. Establish a shared ground baseline and inspect a loop at the actual engine cadence, not only isolated frames.
- Donut: favor a clear Persian ruff/head and warm-dark/russet/cream silhouette over noisy fur strands. Collar may be a single accent pixel at 16×16. Preserve cat legs, ears and plume-tail readability.
- Review all directions at 1× and nearest-neighbor 4×/8×. Separate downscale diagnostics demonstrated this limitation; they are intentionally excluded from this source-reference package.
- Export binary transparency plus 15 opaque colors, correct indexed PNG mode, expected dimensions and exact frame packing. Regenerate, run art checks, compile.
- Capture real walking in at least down/up/left/right directions plus a standing Donut scene. Confirm no foot skating, height jitter, palette flash, direction mismatch, clipping or collision/event changes. Record exact tested commit and route. Generated references remain clearly separate from emulator evidence.
- Update provenance to distinguish generated reference, native conversion/redrawing, completed assets and pending work. Do not claim S02 accepted from this sheet.

## Source links

- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/scripts/content/carl_sprite.py
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/scripts/content/slice_art.py
- https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/task/s02-original-presentation/docs/content-ledger.md
- https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/26

