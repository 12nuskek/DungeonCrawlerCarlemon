# DungeonCrawlerCarlemon

An in-development GBA adaptation using stock Pokémon Emerald's decompilation.
The approved target is an authored Book 1 opening slice with Carl and Donut duo
battles, original dialogue, no catching and accessible defeat recovery.

**Current state: connected prototype through boss and staircase, runtime verified. Approved protagonist art and the original visual/UI pass are merged; full slice regression passes 1,053 assertions. Requested opponent-art refinement is next.**
See [progress](docs/progress.md), [backlog](docs/backlog.md),
[build and testing](docs/testing.md), and [content ledger](docs/content-ledger.md).

Accepted plans copied in full at handoff **2026-10-06**:

- [Game design](docs/game-design.md)
- [Roadmap](docs/roadmap.md)
- [Development loop](docs/development-loop.md)

Stages 0–5 are authorized. Stage 6 awaits the user's slice playtest.
No ROMs or generated build products are distributed in this repository.

For the current custom game, run `bash scripts/setup-foundation.sh` then
`make -C engine -j2` with the dependencies documented in [testing](docs/testing.md).
Run the latest milestone replay listed there for real mGBA checks and screenshot
review. Matching-stock ROM comparison and `scripts/verify-container.sh` belong to
the Stage 0 revision `03353fb3f1287074102a5bc98df4f19b0d4c189f`, before gameplay
changes; see the [baseline evidence](docs/evidence/f02/README.md).

Play from a fresh save in a GBA emulator. Move with the D-pad, interact/confirm
with A, cancel with B; START opens the menu (Save outside battle). Read the entrance
note, reach the Quiet Landing guide/trial, then explore the Service Room. Its
southwest ladder leads to two gauntlet patrols and the gate warden. Win the trial
and patrols, beat the warden, then examine the northeast stairs. The guide restores
health/actions freely; defeat recovers locally. The quest, trap, equipment and
cache preparation are optional. See [S03 evidence](docs/evidence/s03/README.md) and the [playtest guide](docs/playtest.md).
