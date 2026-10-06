# B02 action/resource verification — 2026-10-06

Implemented YES; compiled PASS; runtime verified PASS. Integration is tracked in
[progress](../../progress.md) and [issue #12](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/12).

Base `471a9c183752ed27f8bfa51b5a451f6722d1e69b` (E02 merged).
Tested source `3bd031cb00439fdb4433930e5972fcce2bf01b84`.
ROM SHA256 `bb9fe023817947bb30f497e0ec65e9b7a3170580e40d487d6cc2bc7f3f369032`.
Real mGBA 0.10.5, 240×160 software framebuffer, controller inputs only.
Run directory `artifacts/b02/run-Mz2RRc`; no ROM/save/executable is distributed.

## Reproduce

With the [documented dependencies](../../testing.md), run `bash scripts/test-b02.sh`
from a committed checkout. Actual Cloud invocation:

```sh
PATH=/workspace/toolchain/root/usr/bin:$PATH \
PKG_CONFIG_SYSROOT_DIR=/workspace/toolchain/root \
PKG_CONFIG_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu/pkgconfig \
LIBRARY_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu \
DCC_CACHE=/workspace/dcc-toolchain-cache \
DCC_TEST_CFLAGS=-I/workspace/toolchain/root/usr/include \
DCC_TEST_LDFLAGS='-L/workspace/toolchain/root/usr/lib/x86_64-linux-gnu -Wl,-rpath,/workspace/toolchain/root/usr/lib/x86_64-linux-gnu' \
bash scripts/test-b02.sh
```

The runner exports the exact committed tree, rebuilds the pinned compiler from
clean cached source, hydrates verified upstream inputs and regenerates all game
products in the isolated snapshot. Full raw compiler/setup/emulator logs are
included; native trailing spaces are preserved. The host harness builds with
warnings as errors, never writes game RAM and uses real flash saves in separate
processes. Emulator error logs must be empty. Screenshots were visually inspected.

## Results

| Route | Checks / result |
| --- | --- |
| E01 new-game.route / setup.log | 16 PASS: fresh B02 game, exploration and real save |
| guide-before-trial.route | 10 PASS: guide dialogue/effects advice and all four party use counts |
| support-defeat.route | 19 PASS: BRACE defense 6→7, WEAKEN both enemy attacks 6→5; Carl then faints while Donut remains at 1 HP; Donut still acts (WEAKEN 30→29, Carl BRACE remains 30); both faint, recover locally with all uses restored and retry |
| depletion-victory.route | 28 PASS: both offensive actions; SPARK 2→1→0; attempted third cast rejected with HP/PP unchanged; alternate WEAKEN executes; victory then guide restoration of all four party use counts, return route and save |
| reload.route | 10 PASS: cold Continue retains trial/guide state and restored party HP/use counts, repeat guide and movement |

**83 assertions passed; five empty error logs.** Actual screenshots show menus,
zero-use refusal, the surviving actor's action menu, defeat recovery and guide
restoration. Routes/logs provide the behavioral proof beyond screenshots.

`support` reads battle move slots and stat stages. `roster`/`uses` read actual party
HP/status and locally decode the encrypted attack block for all four party PP
slots. After victory, party uses are 2/40/0/36; after the guide and cold reload they
are 8/40/2/40. After deliberate defeat they likewise reset to 8/40/2/40. Stale battle
PP is not used as evidence of guide healing. Normal status values are zero; curing
an inflicted nonzero status remains explicitly pending until such an encounter is
reachable. No RAM injection, savestate or debug command is used for these routes.

## Scope and remaining work

Four new records (IDs 355–358) reuse stock effects. STRIKE is a physical hit with
8 uses; BRACE raises Carl's defense and has 40 uses; SPARK is a magic attack hitting
both foes with 2 uses; WEAKEN reduces both foes' attack and has 40 uses. Budgets and
power are provisional balance. Separate move records preserve upstream enemy moves.
Move names/descriptions are authored adaptation choices, not canon skill claims.
Stock Tackle/Harden/Swift/Growl animations remain explicit placeholders.

Fresh B02 save required; old saves are not migrated to new moves. No save-layout
change. Move IDs remain within existing 9-bit learnset encoding. Names, descriptions
and animation pointers were added together; unrelated move records are unchanged.
Old milestone replay routes intentionally belong to their tested revisions.

Battle sprites/species/type labels and menu language remain listed placeholders.
B03 capture/storage/breeding/evolution entry audit is next; this task does not claim
those mechanics removed. Original scheduled art stays in S02 within the slice.
No active build/runtime blocker. The full Stage 5 slice is not yet complete.
