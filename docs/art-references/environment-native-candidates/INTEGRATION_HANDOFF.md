# Environment integration handoff

## Publication status

This partial tree contains all native PNG candidates. The optional packed `native/background-tiles.4bpp` and original `source/environment-props-reference.png` are absent pending publication. Use PNG candidates directly; do not assume either absent file is available. Full source-sheet reproduction is blocked by the missing main source image. `package-status.json` records their exact identities.

## Scope and native contract

This is an unintegrated candidate kit. The integrator must select useful images, establish mapping, collisions and state bindings, then verify a clean build and real emulator acceptance. Do not blindly replace the generated atlas.

Verified baseline: [`bf27e269`](https://github.com/12nuskek/DungeonCrawlerCarlemon/tree/bf27e2692025eb4291ffbf992a3b6412340d32cd).

- [`fieldmap.h`](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/bf27e2692025eb4291ffbf992a3b6412340d32cd/engine/include/fieldmap.h): 512 primary + 512 secondary 8×8 tiles; 512 + 512 metatiles; secondary palette banks6–12; MAP_OFFSET7.
- [`global.fieldmap.h`](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/bf27e2692025eb4291ffbf992a3b6412340d32cd/engine/include/global.fieldmap.h): map block packs 10-bit metatile ID, two collision bits and four elevation bits. A metatile stores four base + four upper-layer 8×8 entries, not eight independent map cells.
- [`slice_art.py`](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/bf27e2692025eb4291ffbf992a3b6412340d32cd/scripts/content/slice_art.py): current dungeon has only nine native designs, 37 used tiles, bank6 everywhere, and a blank transparent overlay tile. Generated PNG's original embedded palette differs from external BG palette; index identity is what matters at runtime. This kit embeds the actual target colors to prevent that preview confusion.
- [`check-slice-art.py`](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/bf27e2692025eb4291ffbf992a3b6412340d32cd/scripts/check-slice-art.py): existing `<550` subtile restriction and bank6-only assertion are present-content contracts, not hardware ceilings. Expand bounded validation explicitly for new IDs/banks; retain behavior/layer equivalence.
- All six DCC maps are16×12. Current ordinary floor is0x3201; wall0x0611; boss interact stair0x3605. A visual-only replacement preserves the upper six map-block bits, metatile behavior/layer, all event/warp centers and approach cells.

## Recommended adoption order

1. Use the correct shared-palette rubble for Entrance's inherited BREAKABLE_ROCK at(7,6)/(7,7). Current rock selects NPC_1, which DCC globally substitutes with Donut's palette; do not recolor Donut to fix rocks.
2. Assign distinct native graphics to warning, workbench, quest tag, supplies/cache and state feedback. Keep the existing one-cell event footprint and suitable approach cells. The 16×16 bench is readable as a table but loses fine tools; prefer the32×16 BG bench with an obvious existing interaction anchor if placement permits.
3. Replace the brick-filled off-room border with the opaque `void`, deliberate wall tops/faces and corner modules. Keep two-row north wall depth and one narrow side/bottom cutaway. Inspect actual arrival camera views because MAP_OFFSET7 exposes much of the border.
4. Use `floor_plain` for most walkable cells, with only a few broken joints/scuffs/drains/repairs. `floor_slab_*` are sparse joint patches, **not an alternating whole-room grid**. Damage belongs by collapse; drain/conduit by workshop; warm mat only in actual rest nook.
5. Place one meaningful focal arrangement per room. Only then adjust room outlines/alcoves if needed, treating those as collision/layout changes with separate route regression.
6. Apply existing flags to live/spent wire, sealed/open cache, cracked/disturbed secret and resolved encounter feedback. These require state-script integration and reload tests; assets alone do not implement persistence.

## Room direction and suggested placements

These suggestions are art composition, not new collision instructions. Preserve existing event centers unless the integrator deliberately undertakes and tests a layout change.

- **Entrance: collapsed threshold.** Earth/stone rubble at(7,6)/(7,7), isolated fracture/wear nearby, note distinct from medicine, strong northeast exit frame at(12,4). Keep quiet bypasses around both obstacles and clear initial view from(4,8). Avoid scattering debris uniformly around every wall.
- **Quiet Landing: occupied refuge plus separate voluntary trial.** A small warm mat/bedroll/cup/rack grouping near guide(4,8); keep guide and healing approachable from(4,9). The existing trial(9,6) gets its own restrained practice boundary, away from the recovery mat. Preserve Donut(7,5), both upper exits and short clear connection between them. No cushion is implied by the bedroll.
- **Service: coherent damaged workshop.** Bench(6,8), warning(7,5), readable live wire(8,6), quest tag(11,4), cache(13,8). Group storage and conduit around existing functions; do not add random props into approaches. Route a subdued service/supply motif toward cache and repeat it in gate room so the optional preparation benefit has visible context. Secret wall(12,2) gets one displaced joint; after claim use disturbed/breached art without accidentally implying a new traversable room. Mara(4,7), Lev(11,8), return(2,4), onward(2,9) stay readable.
- **Supply Gauntlet: two compact patrol bays.** Braced/storage motif around Guard(5,6), grille/alarm motif around Howler(10,6), uninterrupted floor spine between exits(2,4)/(12,4), clear rules interaction(8,8). Retain encounter order choice and free return. Resolved marker must not imply the repeat interaction disappeared if scripts still use it.
- **Gate Chamber: weight and a sealed destination.** Frame Warden(8,6) with broad architectural supports; replace uninterrupted yellow racing stripes with a few actual threshold markings. Northeast A-interact stairs(12,4) need a visible sealed/open arch, different from west ordinary ladder(2,4). A32px-wide BG arch requires thoughtful alignment: center its opening over the interaction cell, possibly inside a48px/three-metatile wrapper with8px side padding. Do not move collision merely to center art. Prepared/unprepared gate machinery can share the Service cache motif.
- **Exit: stair overlook and relief.** A higher-value stairwell/threshold silhouette, small worn rest patch and fewer props; no reused6×4 Landing rug. Keep guide(8,6), Donut(6,7), return(2,4). Treat any onward stair art as end-of-slice scenery, not an unimplemented new floor or misleading usable warp.

## Packing and binding cautions

`tile-pack.json` describes 230 deduplicated8×8 images; tile0 is blank. Each16×16 chunk names local tile IDs in TL,TR,BL,BR order and optional bank6 entry values. `native/background-tiles-8x8.png` has240 slots (128×120); the omitted raw `.4bpp` representation would contain only230 used tiles. Every recommended native BG source reconstructs exactly from the staged PNG atlas. Its230 used and240 allocated tiles remain below512. This packing is a convenience for the integrator, not a demand to replace the existing exporter strategy.

Do not import pressure-plate `trap_armed`/`trap_spent`: the story's hazard is wire. They are excluded from the recommended BG pack and retained only to document the generation source. World sources include them for provenance but they are not recommended.

Architecture tiles are opaque. Isolated prop art has transparent index0 and must be combined with a floor underlay in metatiles; do not let transparent corners expose the wrong BG layer. Gates/stairs are multiple chunks; a single event footprint does not become2×2 merely because its artwork does. Authoritative behavior/layer mappings must be selected explicitly from existing working equivalents.

No metatile IDs, object graphics constants, palette slots, source generator edits or state scripts are supplied as an automatic patch. Incorporate selected masters into the repository's authoritative export pipeline so regeneration cannot erase them. Leave the Carl/Donut/opponent export ownership and palette bindings intact.

## Honest quality limits and acceptance

- Generated source sheets are high-resolution references. Native conversions are technically formatted candidates with readable overall silhouettes, not hand-polished animation assets. The wire pair was mechanically normalized to14×8 content with alpha threshold48 to preserve the thin cable; all remaining output alpha is binary, and each16×16 OBJ has at least one pixel margin.
- Fine text/tool detail was intentionally sacrificed. Warning/tag/cache are identified by silhouette; no tiny generated lettering is relied upon. The optional neutral BG palette is a candidate, not a required replacement; independently validate bank6–12 usage and never touch OBJ palette colors.
- The architecture room diagram is not a final room redesign and cannot prove collision, warp, layering, animation, state or persistence correctness.
- For visual-only work, compare map upper bits/event coordinates/warp coordinates/behaviors before and after. For layout/state changes, test every route, interaction approach, both wire bypasses, active/spent state, optional skip paths, both patrol orders, free healing/retry, prepared/unprepared boss, stair cancel/confirm and cold reload.
- Capture clean native240×160 arrival and center frames for all six rooms, then same-position/facing before/after cache/wire/secret/cleared markers. Verify palettes after menus, battles, transitions and cold reload. Keep whole-map art diagrams labeled separately from emulator evidence.
