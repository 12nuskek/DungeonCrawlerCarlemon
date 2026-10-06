# DungeonCrawlerCarlemon

An in-development GBA adaptation using stock Pokémon Emerald's decompilation.
The approved target is an authored Book 1 opening slice with Carl and Donut duo
battles, original dialogue, no catching and accessible defeat recovery.

**Current state: verified tutorial exploration prototype; the full slice is incomplete.**
See [progress](docs/progress.md), [backlog](docs/backlog.md),
[build and testing](docs/testing.md), and [content ledger](docs/content-ledger.md).

Accepted plans copied in full at handoff **2026-10-06**:

- [Game design](docs/game-design.md)
- [Roadmap](docs/roadmap.md)
- [Development loop](docs/development-loop.md)

Stages 0–5 are authorized. Stage 6 awaits the user's slice playtest.
No ROMs or generated build products are distributed in this repository.

Build the matching baseline with `bash scripts/setup-foundation.sh` followed by
`bash scripts/build-baseline.sh` after installing the dependencies in
[testing](docs/testing.md). To reproduce setup/build/boot in a fresh Docker
container, run `bash scripts/verify-container.sh` from a committed checkout.
The test route includes real mGBA emulation and requires manual screenshot review.
