# F1-G01b recovery travel — continuation brief

Issue63. Branch `task/floor1-g01b-recovery-travel`.
Base `535b0809703f53a86dfd9e2cea1f751c4e6585f1`, mergedG01a PR62.
Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`; parent owns continuation.
This checkpoint adds no new Cloud task, scheduler or implementation writer.

## Problem and narrow outcome

The tested candidate supports64×48 field/camera/buffer/save operation, but is
rejected for live adoption. Field-only Guard/Howler waypoint→hub-door lengths
are24/37steps versus14/19steps in verified old encounter→guide outbound routes.
The field numbers exclude the unfinished interior and therefore already fail.
Co-design shorter hub/bay geography and compact-interior arrival/guide anchors;
keep all original D1 beats, both patrol orders, free recovery and optional branches.

Start by recording ordinary same-starting-encounter roundtrips and walking time
on retained production; old guard-rest/boss-rest routes return to a different
next encounter, so their outbound measurements do not prove that roundtrip.
The guide approach in the old interior is five walking steps from its west warp.
A compact-interior redesign may move the guide nearer the arrival, but must keep
safety, Donut staging and the trial alcove clear and explicitly migrate old saves.
Shorten the geometry before tuning resources, HP, encounters or balance.

## Ready inputs and exact next action

Retained production: `artifacts/floor1/a01/run-I7PJq0/production.gba`, SHA256
`5c4f865a95c0b9e4c65f13d86c8ba44c9082599432b387f6fc350c0bd99b7230`.
Its ordinary `howler-pending.sav` was copied after Guard victory and before guide
recovery. `boss-loss.sav` was copied after Howler clear/recovery and before boss
loss; ordinary navigation back through the boss doorway can seed a cleared
Howler starting point. Inspect positions/flags from actual cold loads before
using either; never mutate save bytes/RAM or infer a fixture state from a name.
Keep all failed inputs/logs. Use copied saves, not the preserved originals.

Read `docs/evidence/floor1/g01/travel-review.json`, old `guard-rest`/`boss-rest`
routes and logs first. Capture ordinary return to the same starting encounter,
separate active walking from menus/dialogue/idle/warp transitions, and freeze
comparison ceilings. Then make one coordinated geometry/interior revision,
review clear widths and shortest paths statically, and run ordinary emulator
approaches/returns before committing live relocation. Existing preview driver
uses explicit accepted counts and must be reconciled deliberately for revised
routes; do not silently overwrite the archived4718908 candidate or its logs.

Two travel layouts were examined during G01a: initial boss/hub doors were far
apart; the revised tested candidate shortened that pair but still fails patrol
recovery. Preserve this history and do not restart retry accounting. Avoid more
isolated door guesses. If the coordinated next design fails materially, stop
dependent live migration/art and continue a concrete independent audit/content
item rather than repeating the same layout or claiming the gate passed.

## Acceptance before live adoption

- Main paths5–7clear metatiles, side paths3–4, junctions8–12, after actors/props;
  brief thresholds allowed, no hidden long narrow connector.
- Both patrol orders, retreat, cleared re-entry and return-loop traversal work;
  no new patrol lock and no loop traversal grants trial/patrol completion.
- Actual same-encounter hub roundtrips/recovery ceilings pass; preserve existing
  local defeat retry (zero walking). Capture native camera and continuous motion.
- Include compact interior arrival/guide/trial/exit anchors and measurable trips.
- FinalT remains null until reviewed final field+interiors; then count unique
  reachable collision-valid cells consistently, including interiors once.

After geometry passes, allocate explicit full map IDs and loop/layout-version
state using numeric audits. Save migration must precede old-layout lookup and
handle layoutID, position, object templates/localIDs/scripts/graphics, active
objects, every warp and idempotent second save/cold. Old completion remains the
opening milestone, separate from newD9 completion. Use all I01/corner/state
fixtures and full relevant regression; no save ABI expansion in this increment.

No production/gameplay change has started on this continuation branch. No PR
for G01b yet. Full G01 and the nine-district Floor1 remain incomplete; V01 art
rollout is dependency blocked by recovery travel. Continue autonomously within
this scope; parent can request a quota checkpoint pause under the soft safeguard.

Before resuming issue63, integrate issue64 fresh-source provenance repair and
fast-forward this branch to current main. Whole-engine DCC_G01_CACHE is forbidden;
use fresh committed snapshots and separately pinned DCC_CACHE only.
