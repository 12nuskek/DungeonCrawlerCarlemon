[Draft PR #112](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/112) / existing [tracking #106](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/106), open/draft/unmerged. Initial evidence publication `4f497561e35508555d9463479f2f3ad539c330e4`; tested host/route/game identities below stay frozen.

Current environment-stage checkpoint — 9 October2026: integration accepted,
PR111 matrix/docs merged at54526744. First environment-only pilot now implemented,
compiled and bounded runtime verified; unmerged. Native assets only, no character/
reaction/action-bound battle changes. See [actual pilot](../evidence/floor1/v01/environment/README.md).
Parent visible-pilot review precedes any later stage. Historical entry plan below
retains its original checkpoint date/scope; no broad rollout or gate waiver.

## Historical integration entry plan

# V01 entry plan after reviewed integration

Status 9 October 2026: dependency-ready plan only. Integration through PR110 is
verified on main `a83777b94684919d121cabf4f6b2d45de23027c7`; parent review of the
integration checkpoint precedes separately scoped V01 implementation. No art
work, concept generation, new route or V01 runtime acceptance occurs in this increment.
[Integration evidence](../evidence/floor1/g01e/reviewed-integration/README.md) records
exact bases/heads/tested identities/merge checks and build identity.

## Scope and fixed baseline

Follow the complete [accepted plan](accepted-plan.md), its existing provenance,
and [G01e inventory](g01e-acceptance-inventory.md). Scope is the nine authored
Floor 1 districts, permanent Carl/Donut, accessible recovery, pinned Emerald/GBA,
Book 1 opening spoiler ceiling, and no catching/storage/breeding or later floors.
D1 pilot geometry, collision, anchors, approach tiles, widths, recovery travel,
save layout, controller policies and encounter balance stay fixed.

Live T 1449 = Field 982 + Quiet 115 + Workshop 116 + Warden 118 + Checkpoint 118.
Whole-floor 8–12T=11592–17388 walkable cells; working 10T14490. This spatial baseline
does not measure play duration. Preserve 25 source width probes and their native
camera evidence. Main routes 5–7, side 3–4, chosen junctions 8–12 usable metatiles;
short deliberate 1–2 doors remain brief thresholds.

Integrated engine tree 46e5f0f… equals 5084/23c77. Existing linked EWRAM 249704
(12440 static remaining), IWRAM 30892 (1876 remaining), SaveBlock1 15752/15872 and
SaveBlock2 3884/3968 are baselines, not heap/stack/VRAM peak claims.

## One staged pilot

1. Select the native junction, workshop/optional cue and safe doorway/Quiet
   contrast from the existing staged environment 91 PNGs, architecture and
   full-floor material references. Hold collision and navigation fixed; use
   native tileset/palette/export integration.
2. Reuse the authoritative nine Carl 16×32 masters and mirror right directions.
   Do not import the flawed right-facing reference into a left slot. Reuse
   three Donut 16×16 standing directions; clean the staged attention pose into
   one short native reaction. No follower or new creature system.
3. Reuse staged Carl STRIKE/BRACE, Donut SPARK/WEAKEN and five Warden keyposes/
   lift 8 variants. Bind the warning hold to the actual WIND UP action and SLAM
   contact/recovery to the actual action. Keep timings and battle input policy;
   idle playback is not proof of action binding.
4. Build one committed pilot with exact pinned tooling. Measure changed native
   scene and battle object/sprite allocation, palette/OBJ/BG/VRAM and runtime
   heap/stack budgets against equivalent current states. Existing diagnostic
   scene peaks are source-qualified comparison references, not current pilot
   measurements.
5. Capture equivalent 240×160 before/after states and ordinary-speed direction,
   reaction and battle clips. Add narrowly affected collision/approach/recovery/
   persistence checks only when the change warrants them. Review the pilot
   before any broader rollout.

Current staged packages: battle 250 native +180 package checks, full-floor 231,
environment 123 checksum/91 native PNG/721 static checks. Those verify candidates,
not game integration or visual quality. Genuine remaining work is native Donut
reaction cleanup and action-bound pose/tileset/export integration. Missing Donut
corrected source prevents complete regeneration but does not block verified native
WEAKEN PNG reuse; missing environment prop source/optional 4bpp does not block
existing verified PNG reuse. A generated district stitch remains concept only.

## Evidence and later dependencies

PR110's bounded corrected route/cold retains 164+18 assertions, six measured legs,
13 real captures and exact manual Save/cold from reconstructed ordinary inputs.
PR109 STOP71 and every earlier failure/controller record remain unchanged.
Prepared 270+132 and unprepared first-clear pairs keep their own source/input
identities. Neither integration nor the V01 pilot authorises their replay.

Original 16 legacy saves/raw logs/original patrol-complete input remain missing.
Keep historical evidence and the unavailable original-input gate explicit;
reconstructed files never substitute. Existing necessary new saves/raw evidence
stay in supported private Library backups. No ROM/save/raw context/key/denied
dataset enters Git or public release.

C01 uninterrupted prepared/unprepared opening, multiple timing trajectories,
human pacing/comprehension and later district/full-floor acceptance remain
separate later gates. Parent owns the sole continuation and existing progress
dashboard. No new task, schedule, writer or art increment is started here.
