# N03 persistent environment feedback

Base: `96f651d828dd380eb836c49493417913f390d15e` (verified N02).
Tested source: `b530fa661254c2c4b5ef1d75ce4010c2d5d741ec`.
Production ROM SHA256:
`dc321def80b7b3d60d0dd5103c73a77d8104135b0ff055a02456656bb76a0891`.

The live wire has an amber core and pale sparks; it becomes a quiet broken cable
when spent. The secret panel stays breached after collection, caches visibly open,
the gate stays barred until victory, and four cleared encounters become remains.
The gate supply line reflects optional cache preparation. All presentation reads
existing flags; no new save fields, rewards, combat rules or geometry changes.
The tag-bag directions and cache dialogue now match the art and explain the
preparation benefit before spending a CHARGE. Existing dialogue page counts remain.

Map load reconstructs state; successful interactions refresh it immediately.
Capacity failure and cancellation leave sealed art intact. Resolved opponents keep
their original 32x32 / 512-byte sprite allocation. The native 16x16 marker is padded
at (8,16), preserving its exact visible pixels and floor position. This avoids the
allocation mismatch found during review of ObjectEventSetGraphicsId/DestroySprite.
No stock sprite allocator modification was needed.

Use the pinned toolchain/environment in docs/testing.md:

```sh
DCC_LEGACY_RUN=/path/to/completed/I01/run \
DCC_CORNER_SAVE=/path/to/ordinary/N01-corner.sav bash scripts/test-n03.sh
```

Both old-save inputs were supplied. Their ordinary-input origins and hashes are
recorded in N02 evidence; no save editing or game RAM writes. The tile command
reads actual map words, including collision/elevation, from mGBA.

- 76 emulator processes / 1,303 assertions: 63 production processes / 1,110 checks,
  and 13 explicitly labeled diagnostic-fixture processes / 193 checks.
- All 76 emulator error logs empty. Original 1,210 checks retained, plus 53 actual
  map-word checks and 40 ordinary-input wire setup/pair/cold checks.
- 38 exact rendered comparisons: nine approved opponent views, 18 object/frame
  cases, and 11 background state cases at fixed world/camera coordinates. One
  object case is the labeled capacity fixture; the other 37 use production ROM.
- Four individual cleared enemy markers, cancelled/full/sealed cache, successful
  and cold-reloaded open cache, and opened supply/equipment rewards verified.
- Same-position wire before/after, repeat traversal without second damage, and
  cold saved spent state. Both gate/preparation states and secret states verified.
- All 1,176 map/border values match N02's declared geometry; six event contracts
  and 49 approved art files preserved. State pairs have identical collision and
  behavior. 180 used 8x8 tiles / 192 allocated, 180 metatiles, BG banks 6–9.
- Two complete isolated exports reproduce 8,818 tracked asset files; palette line
  endings normalized only. Native PNG masters remain authoritative.

The first candidate `210e734` passed 1,263 main assertions plus the separate
40-check wire probe. Actual review prompted the live-cable contrast refinement.
The `a8e6ee4` rerun was deliberately stopped (exit 143) after source review found
the sprite allocation mismatch; it is not a completed acceptance run. The final
source above fixes it and passes the complete suite. Initial evidence remains
separately labelled in ../initial; no failed/stopped run was relabelled as final.

All stills are actual 240x160 mGBA output. Full raw build/replay logs are retained;
selected captures show the state comparisons and final room views. The raw build
hash was recorded before labeled fixture builds replaced the isolated engine
output; the unchanged `production.gba` copy is the reviewed deliverable. No ROM,
save, executable or fixture binary is committed here.

Source-kit omissions remain untouched; complete reference-sheet reproduction is
not claimed. Added wire highlights are code-authored palette derivatives of the
accepted silhouette; marker padding changes no opaque native pixels. Static poses,
stationary Donut, inherited audio/interface elements and compressed chronology
remain documented placeholders/departures.

Recovery/pacing limits are unchanged by this increment: six retry routes prove
re-entry, with wins checked separately. Prepared uninterrupted completion passes;
unprepared wins are segmented. Fixed waits are not human reading/decision time
and do not establish the 20–30-minute playtime target. Further recovery evidence
is the next focused task; Stage 6 remains blocked on the user's playtest.

After this runtime run, a runner-only review fix makes both legacy inputs mandatory
and enforces exact totals before the full-success message (N02: 73/1,210;
N03: 76/1,303; 193 fixture assertions each). Missing variables/files fail before
any build. Syntax checks and both accepted summaries pass the new contract;
runner-contract-validation.json records it. Engine/assets are identical to tested
b530fa6. This does not claim an unnecessary second runtime build.
