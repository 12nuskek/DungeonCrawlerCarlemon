# Native battle-art integration candidates

These are genuine indexed, native-dimension technical conversion candidates for the approved Carl/Donut art direction. They are not game screenshots. They have not been compiled into the ROM or emulator-tested. The enlarged native sprites were visually reviewed on 2026-10-06; final in-game acceptance remains pending.

## What is included

| Character | File | Dimensions | Contents |
|---|---|---:|---|
| Carl | assets/carl/front.png | 64×64 | Full-body three-quarter front, facing left |
| Carl | assets/carl/back.png | 64×64 | Full-body three-quarter rear, looking right |
| Carl | assets/carl/anim_front.png | 64×128 | Two identical front frames; existing static timing retained |
| Carl | assets/carl/trainer_back.png | 64×256 | Four identical rear frames; no newly authored intro motion |
| Donut | assets/donut/front.png | 64×64 | Three-quarter face view, angled right |
| Donut | assets/donut/back.png | 64×64 | Three-quarter rear view, angled right |
| Donut | assets/donut/anim_front.png | 64×128 | Two identical front frames; existing static timing retained |
| Each | normal.pal / shiny.pal | 16 entries | Identical normal/shiny palettes for this adaptation |

All PNGs are indexed P mode, encoded at 4 bits/pixel, transparent palette index 0, binary transparency, and at most 15 opaque colors. Palette RGB888 values are multiples of 8 and therefore represent the intended GBA RGB555 values without additional channel truncation. Carl's art occupies 39×56 / 38×56 within the 64×64 cells; Donut 46×44 / 42×44. Ground contact is at y=61 with a transparent bottom margin.

## Palette integration is important

Carl and Donut intentionally have SEPARATE palettes. Each character's front, back and packed variants share that character's exact 16-entry palette. Use assets/carl/normal.pal for Carl, assets/donut/normal.pal for Donut. Never load both with Carl's palette, never treat the indices as a shared global palette, and do not replace graphics/dcc/shared.pal.

Existing S02 species front/back files already have individual normal.pal/shiny.pal paths, but the sole writer must inspect actual palette references before replacing them. In particular, check Carl's trainer_back loader: if it currently uses a shared palette, bind it to Carl's matching palette or omit that packed candidate until this is safely addressed. This package does not alter code, table bindings, IDs or palette banks.

No icon.png candidates are approved here. Existing 32×64 icons may use a shared icon palette, so do not regenerate icons using these new palette indices without auditing and testing their palette-table entry. Likewise, do not alter the overworld palette from this package. Keep normal/shiny files identical unless a later design explicitly requires a separate appearance.

## Reproduce the conversion

Requirements: Python 3, Pillow, NumPy. Run from the package directory:

    python3 convert_native.py
    python3 validate_native.py

The source is ../carl-donut-proposed-replacement-reference-v2.png, committed unchanged beside this candidate directory. It is the approved generated reference with SHA-256 4c713bb73c041af17a4daf9568087fc911f63daba617c184b68e0744b51619aa. The converter verifies this hash before working.

Conversion steps are explicit and deterministic:

1. Extract independently measured source components. Do not split the generated sheet into equal quadrants.
2. Convert alpha to a binary silhouette at 128. Most source body pixels had alpha 253, so requiring 255 would erase them.
3. Area-sample the irregular high-resolution source grid to the measured native occupied size; map the result immediately to the chosen 15 opaque colors without dithering. Final assets contain only hard indexed pixels, no smooth alpha or gradients.
4. Preserve source-derived small-color masks for the boxer heart prints, Donut's teal collar jewel, amber irises and dark pupils. These masks retain existing details that plain average-color shrinking washed out; they do not invent new anatomy or accessories. Source rectangles and changed pixels are logged in manifest.json.
5. Repair only an isolated transparent pinhole wholly surrounded by the same palette color, if present. No such repairs were needed for the selected images.
6. Pack the documented static duplicates and export PNG/JASC palettes.

These are technical conversions with source-detail preservation, not a claim of painstaking hand-drawn native sprite animation. The human-readable script and manifest make every conversion decision inspectable. Do not run the old geometric protagonist generator over these results; adapt the existing pipeline to consume approved native masters or this reproducible conversion step, while preserving unrelated assets.

## Visual review and acceptance

Running the converter generates previews/battle-native-1x.png, which shows actual native pixels on a neutral gray field. previews/battle-native-6x.png is exact nearest-neighbor enlargement. Both are asset review images, not emulator screenshots. The silhouettes, natural anatomy, shorts, paws, fur patches and eye colors remain recognizable at 1×; they are materially more coherent than the previous geometric placeholders. The heart pattern is necessarily tiny, and some fine fur/hand detail is simplified.

The sole writer still needs to compile and inspect actual duo battle, summaries/front presentation and trainer intro. Verify no palette corruption, clipping, incorrect offsets, sprite overlap, species binding mistakes or unexpected palette-bank use. Retain actual 240×160 captures with tested commit and route. Run relevant art checks and gameplay regression. The new art must not change combat rules, event/collision behavior, IDs, frame counts, save layout or timing.

## Native overworld remains unfinished

A separate technical normalization experiment confirmed that direct conversion of the generated exploration sheet is insufficient. At 16×32, eyes/facial contrast and tiny heart marks are weak, the side-contact poses do not clearly establish a valid alternating walk cycle, and the source has different body proportions by view. Donut loses important 16×16 face detail. The reference's last side view also required mirroring for direction, and the rear cat touched the source boundary.

Therefore this deliverable approves only battle candidates. Diagnostic overworld images are not in assets/ and must not be integrated as finished work. A native overworld redraw/cleanup and actual cadence review remain necessary. Do not tell the user the outside-combat work is complete because battle assets are prepared.

## Provenance and rights

Reference: OpenAI built-in image generation from the user's character/adaptation brief, followed by one pixel-density revision. No third-party image was supplied or traced. Native candidates: deterministic local format conversion and source-mask/color-preservation pass on 2026-10-06. Preserve the original reference-generation prompts and the distinction between generated reference, native conversion and runtime-tested game art. This is not a claim of clearance of underlying character IP.

This package is staged only under docs/art-references/native-candidates. The S02 integrator owns game changes and final runtime evidence.

## Package checks

Run `sha256sum -c SHA256SUMS` before regenerating. `validation-report.json` records the bundled validator result. `clean-reproduction-report.json` also records an independent regeneration in a fresh directory, matching all 11 asset/palette files plus the manifest byte-for-byte. Source/format checks do not prove runtime acceptance. Generated preview files are intentionally excluded from this package.
