# Dungeon environment kit: native candidates

Prepared against `bf27e2692025eb4291ffbf992a3b6412340d32cd` on 2026-10-06. Asset/design preparation only. This package is staged as reference documentation. No engine, map, event, collision, save, palette binding or deployment was changed.

## Partial publication

All 91 native PNGs, palettes, manifests, scripts and previews are present. Two files are absent pending publication: the optional `native/background-tiles.4bpp` and original `source/environment-props-reference.png`. Their identities are recorded in `package-status.json`. The native PNG kit can be evaluated and integrated independently, but complete source-sheet reproduction is unavailable from this tree. The historical 109-output clean reproduction used the complete local delivery before publication.

## Ready to evaluate

- 56 original, code-authored 16×16 architecture tiles: quiet floors, sparse broken joints, repair/drain/wear, dark opaque cutaway, north/south caps, wall faces/side returns, inside/outside corners, door framing, thresholds, small wall lights, conduit and a small seam-continuous mat.
- 14 generated-and-mechanically-converted 16×16 shared-palette prop candidates. **Use 12; exclude `trap_armed` and `trap_spent` pressure-plate alternatives.** `wire_live` and `wire_spent` preserve the actual narrated trap concept.
- 20 environment-palette prop/architecture variants, 16×16 to 32×32. Again exclude the two pressure-plate alternatives. The 32×16 bench and 32×32 gates/stairs retain useful shape at native scale.
- Deduplicated BG staging atlas: 230 unique 8×8 tiles (including transparent tile0), 240 allocated tiles in a 128×120 PNG, and a documented 7,360-byte tightly packed 4bpp representation (not included). The 74 recommended BG source images form 93 16×16 chunks. This fits the engine's 512-secondary-tile budget; it is **not a drop-in replacement** for existing tile IDs.
- Static validation: 721 checks pass. Palette/index/alpha/bounds, required seam continuity, fully opaque floor tiles, fixed prop margins, atlas reconstruction and GBA nibble packing are checked. No emulator or gameplay acceptance is claimed.

## Review files

- `previews/world_shared-enlarged.png`: every one-cell prop at nearest-neighbor zoom
- `previews/background_env6-enlarged.png`: larger environment variants
- `previews/architecture-enlarged.png`: exact native architecture kit at 4×
- `previews/architecture-room-native-diagram.png`: 256×192 illustrative assembly
- `previews/architecture-room-neutral-enlarged-diagram.png`: 4× assembly with optional neutral BG palette

The room diagram is an **asset-assembly illustration, not an emulator capture, final room layout, or collision map**. Its rectangular perimeter exists only to check joining and visual scale. The six final rooms should use different compositions described in `INTEGRATION_HANDOFF.md`. Revised floors are opaque, predominantly one quiet body tone and use only a few broken seams; there is no alpha-checker or alternating floor fill. Do not repeat joints on every tile.

## Validate this partial tree

Python 3.12.14 and Pillow 12.3.0 are the reference environment. Run:

1. `sha256sum -c SHA256SUMS`
2. `python3 verify_staged.py`

The verifier checks all staged hashes and 91 decoded native PNG identities, then
runs the 721 static packing checks in a temporary directory from the native PNGs.
It publishes nothing. No game checkout or network is needed.

`convert_native.py`, `author_architecture.py` and `pack_validate.py` retain the
original generation logic. Complete source reproduction would run them in that
order, but **do not claim that workflow passes from this tree**: the first script
requires the absent main reference PNG. The historical clean-run reports describe
the complete local delivery before this partial publication. The preserved state
source PNG and exact generation prompts remain available under `source/`.

## Palette safety

`native/world_shared/` exactly matches the current `graphics/dcc/shared.pal`; leave that palette unchanged. It must not be redirected to Donut's OBJ palette. `native/architecture/` and `native/background_env6/` exactly match the current dungeon BG bank6 palette. Optional neutral/warm/cold/gate BG palettes are separate in `native/optional_bg_palettes/`; evaluate them deliberately, without touching OBJ palettes or approved Carl/Donut/opponent pixels.

## Provenance

Architecture: original native geometry in `author_architecture.py`, no external art source. Props/gate/stairs: two original OpenAI image-generation outputs, with exact prompts and the smaller state source PNG under `source/`; the larger original source reference is absent pending publication; no stock or copied third-party artwork. Native conversion records source crop bounds, output dimensions, hashes and limitations in `manifest.json`. Full high-resolution sheets are references, **not engine-ready sprite sheets**.

The new images do not contain or replace Carl, Donut or opponents. Existing palette values and engine facts were verified in the user's repository. `INTEGRATION_HANDOFF.md` links the authoritative implementation and source evidence.
