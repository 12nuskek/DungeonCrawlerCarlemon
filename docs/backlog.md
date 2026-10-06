# Live backlog

Handoff: 2026-10-06. Full acceptance criteria: [development loop](development-loop.md).

| Task | Depends on | State |
| --- | --- | --- |
| F01 | None | Complete: implemented, compiled, runtime verified and merged in PR #2 |
| F02 | F01 | Complete: implemented, compiled, runtime verified and merged in PR #3 |
| E01 | F01 | Implemented, compiled and runtime verified; integration pending |
| E02 | E01 | Pending: safe room, guide and recovery |
| B01 | F01 | Pending: Carl/Donut duo prototype |
| B02 | B01 | Pending: actions and defeat recovery |
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
