# Stock foundation provenance

Handoff: 2026-10-06. Upstream: https://github.com/pret/pokeemerald
Revision: `731ad5bfd6e6f265508d0efcca0ba42f9dcf5881`, committed 2026-10-01.
Subject: Report SaveBlock1/SaveBlock2/PokemonStorage usage (#2364).
Imported from `git archive` into `engine/`; exact revision chosen before gameplay.
Source history is preserved at the upstream link; this is an attributed snapshot,
not a claim of authorship or of an independently licensed original game.

Exceptions to the snapshot: `.github/` omitted so upstream automation is not
enabled here (workflow text retained as `build.yml.txt`). The three upstream
`data/mb_*.gba` multiboot binary inputs are omitted from source commits and hydrated
by `scripts/setup-foundation.sh`, verified against exact upstream blob IDs.
An added `engine/data/.gitignore` keeps these inputs ignored despite upstream's
parent ignore exception. No gameplay or other engine source modifications in F01.

Matching C compiler: https://github.com/pret/agbcc at
`da598c1d918402c42c0c0d7128ba14567f3175e9`.
Use `bash build.sh` and `install.sh` as described in the pinned `engine/INSTALL.md`.
Upstream expected ROM SHA-1: `f3ae088181bf583e55daf962a92bb46f4f1d07b7`.
The SHA-256 and observed emulator route belong in the F01 evidence report.

All baseline artwork, text, maps and sound remain upstream technical placeholders
for this adaptation. No adaptation or originality claim is made for them.
