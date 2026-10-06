# Dungeon design audit — overnight refinement

Handoff 2026-10-06; read-only reviewer observations against main
bf27e2692025eb4291ffbf992a3b6412340d32cd and existing emulator captures. This
is a design review, not a new runtime claim. Implementation writer reconciles
recommendations against current source and validates each bounded change.

## Concrete defects and priorities

- Entrance rocks at (7,6)/(7,7) use BREAKABLE_ROCK/NPC1. DCC loads Donut's
  palette into NPC1; inherited rocks become teal/yellow. Replace with authored
  rubble on the existing shared prop palette; preserve both footprints and
  approved Donut colors. Check menus, battle return, map return and cold reload.
- Warning, route-tag storage, workbench, cache and supplies share MOVING_BOX.
  Give sign, tools, reinforced cache and medical supplies distinct silhouettes,
  preserving interaction centers/approaches for the first visual increment.
- Trap/cache/secret and cleared patrols retain unresolved visuals. Use existing
  flags for burned wire, opened cache, disturbed panel and inactive patrol token.
  Keep repeat interactions and prove reentry/save reload/no duplicate awards.
  State-script work belongs in a separate increment from static materials.
- N00 fixed the stale trial objective, contradictory ending and ladder directions.
  N00b selects remaining patrols; repeat recovery/Journal verbosity remains to
  assess. Preserve first-use advice, HP/PP/status rules and every retimed assertion.
- Before spending CHARGE, identify the cache as gate supplies. Existing optional
  boss advantage should be intelligible before the irreversible expenditure.
  Link supply and gate machinery visually; preserve quantities/capacity/flags.

## Room intentions and review viewpoints

| Room | Composition and story | Actual capture viewpoints |
|---|---|---|
| Entrance | Collapsed threshold, repaired floor, clustered rubble, distinguish note/medicine and frame northeast ladder; quiet main path | Arrival4,8; note4,6; medicine10,8; ladder12,4 |
| Landing | Warm guide nook at4,8, bedding/cups/shelf; practice zone around9,6; Donut perch; direct ladder route | Center8,8; guide4,9; trial9,7 |
| Service | Damaged workshop; bench6,8, conduit to trap8,6, clear bypasses, readable warning7,5; loose secret panel12,2 | Center8,8; sign7,6; tag11,5; secret12,3; bench6,9; cache13,9 |
| Gauntlet | Two patrol bays: braced Guard5,6 and alarm-grille Howler10,6, direct backtracking lane | Center8,8; each patrol from south; exit12,4; both orders/cleared states |
| Gate | Frame Warden8,6 with machinery, quiet central emblem; sealed interactable northeast threshold distinct from return ladder | Locked/unlocked12,5; prepared/unprepared boss; defeated/cleared states |
| Exit | Lighter earned threshold, worn rest patch distinct from Landing; concise earned duo exchange, no next-floor construction | Arrival4,6; center8,8; Donut6,8; return2,4; cold save |

Do not enlarge all rooms or force zigzags to manufacture duration. Geometry may
introduce shallow alcoves/intentional room outlines in a separate bounded change.
Map diagrams must be labeled diagrams. Capture native240×160 no-dialogue views,
matched before/after position/facing/state, as well as interaction evidence.

## Native integration contract

Each16×12 map cell has10-bit metatile,2-bit collision and4-bit elevation. Preserve
upper bits and effective metatile behavior cell-by-cell during visual-only work.
There are512 secondary8×8 tiles and512 secondary metatiles available; secondary
palette banks6–12. Secondary tile0 remains transparent for overlays. Existing
metatile table has416 entries. Floor/rug/stripe/debris/trap attributes0x0008;
stairs0x0061; wall base/side/lamp0x0000. Blocking bits remain independent.

The current checker hardcodes old atlas bounds/bank6 and a small variant map.
Expand explicit bounds/bank/behavior assertions when importing the native kit;
do not remove validation. Establish one exporter owner so slice_art.py cannot
overwrite imported native materials. Keep all49 approved character/opponent
asset hashes (normalize palette text line endings only) and the shared OBJ palette.
NPC_SPECIAL is the existing safe shared prop slot. MAP_OFFSET7 exposes border at
room edges; improve border composition rather than beginning a camera project.

No new floors, platform, systems or later-book story. Original adaptation
scenes/art require source/author/replacement entries in the content ledger.
