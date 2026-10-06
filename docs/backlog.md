# Live backlog

Handoff: 2026-10-06. Full acceptance criteria: [development loop](development-loop.md).

| Task | Depends on | State |
| --- | --- | --- |
| F01 | None | Implemented, compiled, runtime verified; PR #2 integration pending |
| F02 | F01 | Pending: fresh-environment provisioning; clean-checkout reproduction already passed in F01 |
| E01 | F01 | Pending: Carl avatar, tutorial map and exploration runtime |
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
