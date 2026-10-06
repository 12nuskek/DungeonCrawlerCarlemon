# Live backlog

Handoff: 2026-10-06. Full acceptance criteria: [development loop](development-loop.md).

| Task | Depends on | State |
| --- | --- | --- |
| F01 | None | Complete: implemented, compiled, runtime verified and merged in PR #2 |
| F02 | F01 | Complete: implemented, compiled, runtime verified and merged in PR #3 |
| E01 | F01 | Complete: implemented, compiled, runtime verified and merged in PR #5 |
| E02 | E01 | Complete: 55 assertions, merged PR #11; issue #10 closed |
| B01 | F01 | Complete: compiled/runtime verified, merged PR #6 (`8616025`) |
| B02 | B01 | Verified: 83 assertions; issue #12; integration pending |
| B03 | B02 | Pending: capture/storage/breeding removal and audit |
| R01 | B02, E02 | Pending: XP and equipment |
| R02 | R01 | Pending: persistent achievements/loot |
| D01 | E02, R02 | Pending: trap, secret and optional quest |
| D02 | R01, D01 | Pending: explosive recipe |
| S01 | B03, R02, D02 | Pending: connected slice, boss and stairs |
| S02 | S01 | Pending: original assets, dialogue/UI and placeholder review |
| S03 | S02 | Pending: full regression and review package |

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
