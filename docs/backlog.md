# Live backlog

Handoff: 2026-10-06. Full acceptance criteria: [development loop](development-loop.md).

| Task | Depends on | State |
| --- | --- | --- |
| F01 | None | Complete: implemented, compiled, runtime verified and merged in PR #2 |
| F02 | F01 | Complete: implemented, compiled, runtime verified and merged in PR #3 |
| E01 | F01 | Complete: implemented, compiled, runtime verified and merged in PR #5 |
| E02 | E01 | Complete: 55 assertions, merged PR #11; issue #10 closed |
| B01 | F01 | Complete: compiled/runtime verified, merged PR #6 (`8616025`) |
| B02 | B01 | Complete: 83 assertions; merged PR #13 (`4c76d69`); issue #12 closed |
| B03 | B02 | Complete: 110 assertions; merged PR #15 (`4a27fc4`); issue #14 closed |
| R01 | B02, E02 | Complete: 174 assertions; merged PR #17 (`5a0fd8e`); issue #16 closed |
| R02 | R01 | Complete: 169 assertions; merged PR #19 (`ae4679e`); issue #18 closed |
| D01 | E02, R02 | Complete: 114 assertions; merged PR #21 (`c42d444`); issue #20 closed |
| D02 | R01, D01 | Complete: 111 assertions; merged PR #23 (`369a9ea`); issue #22 closed |
| S01 | B03, R02, D02 | Complete:357 assertions; merged PR #25 (`abf9875`); issue #24 closed |
| S02 | S01 | Complete:199 checks/11 sessions; merged PR #27 (`d8f8ae6`); issue #26 closed |
| S03 | S02 | Complete:1053 checks/62 sessions; merged PR #30 (`eb73f72`); issue #29 closed |

F01 objective: exact source pin, matching baseline ROM, real boot evidence.
Allowed: source import, setup/build/runtime harness, provenance and handoff docs.
Excluded: gameplay changes, scheduler, binary distribution, platform changes.
Exit: clean build matches upstream identity and observed emulator boot; record
integration separately. Next task only after reconciling this gate and PR state.

F02 objective: provision a fresh isolated build/emulator environment and prove
the documented setup/build/boot from committed source. Base:
`1af617261881fcc26c6bb0fbd924d4c8a3c56d9a` (F01 merged). Allowed: reproducible
environment definition, scripts, docs and validation evidence. Excluded: engine
or gameplay changes, new scheduler, binary publication. Acceptance: fresh image
installs recorded dependencies, exact-pin setup/build passes comparison, real
mGBA boot route passes, image/tool versions and tested commit recorded.

E01 base: `fbc28d44529347e5f4f24108c1f9b7a518729b6a`. Scope: fixed Carl identity,
original walking sprite, authored entrance and returnable landing, original text,
existing persistent flag bits and normal saves. Excludes battle/party changes and
save-layout changes. Acceptance: fresh-game entry, four directions, collisions,
crate first/repeat dialogue, both ladder transitions, actual save and cold reload.

Validation follow-up (nonblocking): replace F01 harness scanf unsigned parsing
with checked conversion and add overflow tests (4294967416 frames, 4294967296 keys).
Parent independently confirmed valid F01/F02 evidence; this does not invalidate it.

B01 base `91afb3deb6f856b4565e00bb65e81f0f1497a05f`. Scope: two fixed protagonist
records, deterministic duo trial, both actors choose/execute actions, victory and
safe loss return. Preserve save layout and list temporary species/art. Acceptance:
four battlers, both actions/PP, victory/map return and saved roster; deliberately
lose through ordinary inputs and retry. No broader combat rewrite, capture/storage
audit (B03), full recovery hub (E02) or reward systems. Fresh B01 save required;
E01 zero-party saves are not migrated.

## Next task contract: E02

Dependency E01 is merged. Start from reconciled main after B01 PR #6 and the
integration checkpoint. Add an original guide interaction and safe-room recovery
service; explain objective, saving and retry clearly. Keep the existing save
layout and authored rooms. Validate injured/depleted duo restoration through
ordinary inputs, dialogue bounds, repeat use, return route and cold save reload.
If trial victory recovery is adjusted to make the guide meaningful, update its
promised behavior and new regression routes together; preserve accessible local
trial defeat recovery. Do not claim the historical B01 route applies unchanged to
new recovery behavior. No quest/reward/crafting, capture audit, final battle art or
new floor work in this focused task. Record placeholders and adaptation departures.
Embed actual tested emulator screenshots on its gameplay PR/issue with logs.

## B02 contract

Base `471a9c183752ed27f8bfa51b5a451f6722d1e69b`. Use stock effects to author STRIKE,
BRACE, SPARK and WEAKEN as distinct move records; preserve enemy move definitions.
Provisional use budgets 8/40/2/40. Validate both offensive/support roles, actual stat
changes, zero-use rejection with alternate action, one actor incapacitated then
both defeated and recovered, guide HP/PP recovery and cold reload. Original action
names and stock animation placeholders go in ledger. No capture/storage/evolution
UI audit (B03), reward systems, new battle framework or save-layout changes.

## B03 contract

Base `4c76d692b37a2fa934e89e4b057e0b83568e64f0`; branch task/b03-no-collection.
Issue #14. Block collection at both UI and engine entry points, keep two fixed
protagonists and authored skills, expose roster/equipment access without reorder.
Audit accessible maps, gifts, tutorials, storage and breeding. Preserve save layout.
Acceptance: isolated build, real menu/pocket/roster and combat/recovery replay,
separate test-fixture defensive-rule checks, full logs and screenshots. Excludes
new encounters/rewards, original S02 battle art, expanded campaign or scheduling.

S03 retained edge coverage: either crawler incapacitated while the other acts;
all actions exhausted; save/reload while depleted or immediately after defeat;
cure a genuinely inflicted nonzero status once such encounters exist. These are
coverage edges, not demonstrated B02 failures. B03 adds Donut-down/Carl-acting.

## R01 contract

Base `4a27fc4b082b8d8b6dfa1840eb6d5f01ce554363`. Existing XP/level/stat machinery
and one held-item effect; unique optional equipment grant. Demonstrate normal
acquisition, equip/take, combat effect, earned level growth, save/cold reload and
repeat interaction without duplicate gear. Win without equipment; preserve defeat
recovery. No new save schema, combat model, maps, achievements/loot or expansion.

## R02 contract

Base `5a0fd8eaef6b4746c745e128bd9923f00afeeee0`. Two one-time achievement flags
(note reading/trial win), two boxes (Potions/Scrap), exact contents, locked/opened/
full states. Existing flag and atomic inventory APIs only. Test repeated triggers,
map re-entry/cold saves, item use/persistence, no partial capacity grant and retry.
No new maps/save schema/randomizer; original notices, explicit placeholder props.

## D01 contract

Base `ae4679e2e19a94fd60ac879c9dd18e89f7de2c41`, issue #20. One authored service
room, marked avoidable nonlethal trap, optional secret and two original crawler
NPCs with a retrieval quest. Preserve decline/accept/complete, tag/reward quantities,
trap state and recovery across cold saves and backtracking. Prove actual paralysis
and guide cure. No new battle model/save schema/crafting/boss/scheduler. Fresh save
required for new map objects. Exact input routes/logs/screenshots required before merge.

## D02 contract

Base `c42d444b8c2ae1b665105baad133094859bf8fa5`, issue #22. Scrap2→Charge1
workbench with empty-material/cancel/capacity/success/repeat states. Optional cache
consumes charge only after reward capacity succeeds, awards SuperPotion1 once and
persists. Test cold crafting/use, medicine effect, both atomic failure paths and
R02 workshop Scrap full-capacity branch. No main-route gate, save schema, new battle
model or scheduler. Original item/prop art remains S02.

## S01 contract

Base `369a9ea0dbe8aa61d7f091da533d18c6efafd5fb`, issue #24. Connected second
zone, durable/disruptive patrols, boss with readable cadence/preparation advantage,
confirmed staircase/review ending. Prove fresh progression, win/defeat/retry,
prepared/unprepared strategies, cleared fights no duplicate XP, cold saves and
return routes. Keep optional quest/trap/rewards independent of main progression.
No Stage6 expansion, save schema, parallel writer or scheduler. User explicitly
kept original S01→S02→S03 order after asking about visuals.

## S02 contract

Base `abf9875af2ffead2a342b8a5835c1e3dff157ec0`, issue26, branch
`task/s02-original-presentation`. Original Carl/Donut battle/icons/exploration,
reachable enemies, dungeon tiles/palettes/props and room treatment; crawler-facing
UI/dialogue review and planned flag-based Journal. Preserve combat rules, collisions
and save schema. Build, real same-route before/after screenshots, menu/field/battle
checks and provenance ledger. S03 final regression follows; no Stage6 expansion.


## S03 contract

Base d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530; issue29; sole writer branch
`task/s03-slice-validation`. Revalidate complete fresh-save routes with current
art/UI, optional branches, both boss approaches, defeat/incapacitation, empty
resources, rewards/crafting/capacity and reload. Separate production and explicit
GBA diagnostic fixtures; record actual captures, commands and tested commit.
Fix verified defects, avoid unrelated features. No Stage6, save schema or release.

## I01 requested opponent presentation improvement — issue31

Depends on verified S03. User requested enemy quality matching protagonist upgrade.
Five existing original adaptation enemies only: Scuttler, Grub, Guard, Howler,
Warden. Integrate parent-staged asset-only package; preserve roles, maps/collisions,
combat and save state. Native64×64 fronts/backs,64×128 animation atlases,32×64
icons and existing four32×32 map tokens; index0 transparent/max15 opaque colors.
Battle palettes may differ; icons and map tokens must respect shared palettes.
Prevent slice_art.py from overwriting masters; address inherited Spinda spots for
Guard. Prove reproducibility/build, actual before/after five battle appearances,
four map tokens and affected runtime regression. No new enemies/features/Stage6.

I01 acceptance: tested81b232ae41647b5e456e45ed73d51a170f17fb58. Clean build,
1053 runtime assertions/62 sessions and9 exact rendered-pixel checks PASS.
All62 emulator error logs empty. Evidence docs/evidence/i01; PR32 merged052979d38ff9800780fac66cb052896767c4f1c8.
No further substantive defect identified; stop after cycle1 and await user playtest.
Do not start Stage6 or manufacture improvement cycles to keep automation active.

## Completion boundary

Stages0–5 and requested improvement1 are implemented, compiled, runtime verified
and merged. Private production review ZIP saved to the user's Library.
**Next action: await the user's playtest.** No active implementation task, no
remaining acceptance blocker, no Stage6 authorisation. Human pacing and feedback
are pending, not established by automated tests. Parent owns the sole continuation
mechanism and should stop/disable automatic implementation at this boundary.

## Overnight work reopened

User request2026-10-06 13:19:10UTC authorises existing-slice refinement through
approximately21:19UTC. Previous playtest pause superseded for this window.
N01 issue35 active; see overnight-plan.md for audited priorities and boundaries.
No new scheduler, Stage6, platform or major system. Preserve approved art.

N00 issue36 is active ahead of N01 while the environment kit is prepared: fix
contradictory ending text, stale Journal objective and ambiguous ladder guidance.
N01 remains the next visual foundation task. One implementation writer.

N00 verified at f3514ca: 373 core +7 supplementary assertions, actual text reviewed;
PR37 awaiting integration. N01 next after the external native environment kit.

N00 merged PR37 a9491f1. N00b issue38 /PR39 verified8e9d0d0:23 sessions/416
assertions, both patrol orders and cold remaining-objective pages. N01 next.

N00b merged d36f3af via PR39. N01 native candidate kit ready externally; integration
pending asset-only staging handoff. Invariants and before-room route committed;
source staging must finish/relinquish writes before implementation resumes.

N01 complete: PR41 props and PR42 room materials/save-cache compatibility merged.
N02 issue43 now active: explicit30-cell outlines/supports; full regression and
old-save escape proof required. Persistent visual state feedback follows after
verified geometry, then final full playthrough/private updated review package.

N02 verified atdec2c5e: final26-cell contract,73 processes/1210 assertions,
17 exact rendered-art checks; all original/newer/legacy routes retained. PR44
awaits merge. N03 next: existing-state environment feedback and accurate matching
dialogue, with N02 geometry invariant. Final private review package still pending.
