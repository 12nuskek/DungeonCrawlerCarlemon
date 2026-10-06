# E01 exploration evidence — 2026-10-06

Implemented, compiled and runtime verified: **PASS**. Merge state is recorded in
[progress](../../progress.md). Base `fbc28d44529347e5f4f24108c1f9b7a518729b6a`;
tested implementation `b28143b56f9413ff211473a70ca8429414335412`.
Subsequent E01 commits add only documentation/evidence.

Custom ROM SHA-256: `f025dec94c66033c9ff49b9cac3096e11f2f8672407dd86a4027b0ca6aa75640`.
This is no longer the stock ROM. No claim that stock `make compare` passes.
Build uses the recorded F01 agbcc/binutils environment. Actual command:

```sh
PATH=/workspace/toolchain/root/usr/bin:$PATH \
PKG_CONFIG_SYSROOT_DIR=/workspace/toolchain/root \
PKG_CONFIG_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu/pkgconfig \
LIBRARY_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu \
DCC_TEST_CFLAGS=-I/workspace/toolchain/root/usr/include \
DCC_TEST_LDFLAGS='-L/workspace/toolchain/root/usr/lib/x86_64-linux-gnu -Wl,-rpath,/workspace/toolchain/root/usr/lib/x86_64-linux-gnu' \
bash scripts/test-e01.sh
```

Exit 0. The runner checks a clean tracked tree, records the commit, builds, records
ROM identity and symbols, then runs two independent mGBA 0.10.5 processes using
an actual flash-save file. It never patches RAM or uses an emulator savestate.
RAM reads identify map, player coordinates and the two existing flag bits.
No save structure or battle system changed. Map group 34 appends the new rooms;
old map IDs remain intact. These are source map `.bin` assets, not compiled ROMs.

| Check | Route result / evidence |
| --- | --- |
| Fresh game | Fixed CARL identity, direct entrance at (4,8), four original tutorial pages. [Intro](intro.png), [AI](ai.png), [controls](controls.png) |
| Four directions | Exact position assertions after north/west/south/east inputs. [North](north.png), [west](west.png), [south](south.png), [east](east.png) |
| Collision | Held west stops at x=2; two rock approaches stop at (6,6)/(6,7); route around remains clear. [Wall](wall.png), [rock](rock-block.png) |
| Interaction | Crate first text explains saving/ladder; repeated text selected after flag 0x21 is set |
| Exits | Entrance ladder → quiet landing → entrance → landing, with no forced intro replay. [Landing](landing.png), [return](returned.png) |
| Manual save | START → SAVE → YES through normal game UI. [Prompt](save-prompt.png) |
| Cold reload | New emulator process loads flash file; CONTINUE restores landing (11,4) and both flags. [Continue](continue.png), [reloaded](reloaded.png) |
| Persistent interaction | After cold reload, return to entrance and inspect crate from above; resolved text remains. [Reloaded crate](reloaded-crate.png) |

Fresh route: [inputs](new-game.route), [16 passing assertions](new-game.log).
Cold route: [inputs](reload.route), [3 passing assertions](reload.log).
Both emulator error logs were empty. All listed screenshots were visually
inspected for visible sprites and dialogue bounds. [Build log](build.log) and
[checksums](evidence.sha256) accompany the routes. Full local review outputs,
executable and private test save remain ignored in `artifacts/e01/run-BkGu7n`.
No ROM, executable, symbols or save is committed.

## Review and limits

Original sprite provenance, scene purposes and deliberate chronology compression
are in [content-ledger](../../content-ledger.md). Art is an initial original
walking sketch; tiles, props, music, title/logo, menus and badges remain upstream
placeholders. Donut is described on Carl's shoulder, not yet drawn. No battles,
party model, healing service, rewards or campaign-completion claim in E01.

E01 saves use the existing engine format. Start fresh for the crawler opening;
baseline Emerald saves are not supported campaign starts. Existing unused flag
bits 0x20 and 0x21 are reserved in the ledger. Only save bits, maps, fields and
new-game presentation change; save structures and battle files have empty diffs.

Resolved issues: text macro syntax required a static named string; exploratory
dialogue inputs were too early and were spaced for readable pages; emulator
compiler include flags initially leaked through CFLAGS into agbcc, then were
isolated as DCC_TEST_CFLAGS/DCC_TEST_LDFLAGS. Final recorded replay passes.

The new gameplay harness uses checked numeric conversion, rejects routes without
assertions, and creates a new output directory/save for each replay. The separate
old stock harness's overflow hardening is tracked as a nonblocking follow-up.
