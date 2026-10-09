# DungeonCrawlerCarlemon

**Full Floor1 implementation resumed on2026-10-07.** See the [accepted plan and
execution authority](docs/floor1/README.md) and [active backlog](docs/floor1/backlog.md).
The delivered six-room slice below remains the preserved regression baseline.
The current live-opening branches are draft/unmerged: PR75 migration, PR77 pickup
feedback and [PR79 navigation/Journal](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/79) (issue78). The latter passes 17 emulator
sessions /236 assertions; [scoped evidence](docs/evidence/floor1/g01e/navigation/README.md).
Optional loop/trap/crafting/cache checks now pass 8 ordinary sessions /15,701
assertions on the same exact game; [evidence](docs/evidence/floor1/g01e/optional/README.md).
Full live gameplay/finalT and native-art rollout remain gated by the recorded combat
stop. The Stage0–5 delivery claims below describe the preserved baseline.

On the draft live opening: the warm door leads to Quiet Landing; its guide restores
you and the east alcove holds the trial. Both Quiet Landing and the southeast
workshop exit north to Field. Patrols wait south/east of the warm door. Mara's tag
is outside east of the workshop; the warden door is north of it. The warden's
southeast stairs lead to an opening checkpoint. The rest of Floor1 is in progress.


An in-development GBA adaptation using stock Pokémon Emerald's decompilation.
The approved target is an authored Book 1 opening slice with Carl and Donut duo
battles, original dialogue, no catching and accessible defeat recovery.

**Current state: Stages 0–5 implemented and runtime verified. Overnight refinement has added distinct dungeon rooms and persistent visual feedback; all six recovered-save victories are verified. The final build passes 90 emulator sessions / 1,531 checks; the updated private review package is delivered and ready for your playtest.**
See [progress](docs/progress.md), [backlog](docs/backlog.md),
[build and testing](docs/testing.md), and [content ledger](docs/content-ledger.md).

Accepted plans copied in full at handoff **2026-10-06**:

- [Game design](docs/game-design.md)
- [Roadmap](docs/roadmap.md)
- [Development loop](docs/development-loop.md)

Stages 0–5 are complete. The authorised overnight refinement stays within this
slice; Stage 6 awaits the user's playtest. A private review ZIP has been saved to the user's Library; there
is no public ROM release.
No ROMs or generated build products are distributed in this repository.

For the current custom game, run `bash scripts/setup-foundation.sh` then
`make -C engine -j2` with the dependencies documented in [testing](docs/testing.md).
Run the latest milestone replay listed there for real mGBA checks and screenshot
review. Matching-stock ROM comparison and `scripts/verify-container.sh` belong to
the Stage 0 revision `03353fb3f1287074102a5bc98df4f19b0d4c189f`, before gameplay
changes; see the [baseline evidence](docs/evidence/f02/README.md).

For the preserved six-room baseline, play from a fresh save in a GBA emulator. Move with the D-pad, interact/confirm
with A, cancel with B; START opens the menu (Save outside battle). Read the entrance
note, reach the Quiet Landing guide/trial, then explore the Service Room. Its
southwest ladder leads to two gauntlet patrols and the gate warden. Win the trial
and patrols, beat the warden, then examine the northeast stairs. The guide restores
health/actions freely; defeat recovers locally. The quest, trap, equipment and
cache preparation are optional. See the [visual comparison review](docs/review/README.md), [final runtime evidence](docs/evidence/n05/final/README.md), and [playtest guide](docs/playtest.md).
