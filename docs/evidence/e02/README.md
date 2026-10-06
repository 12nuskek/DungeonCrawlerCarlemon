# E02 guide/recovery — 2026-10-06

Implemented YES; compiled PASS; runtime verified PASS; integration tracked in
[progress](../../progress.md) and [issue #10](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/10).

Base `66bcbb3c6b8cc0600a0108b56a882942db12ae24`.
Tested source `520aebaf04503be97218966bfb36c35f1958cdb6`.
ROM SHA256 `2d850f9c9217e1c2a99ed9eb57449fb0e48f19b0d8e9403f452eb5267cfbb7c0`.
Real mGBA 0.10.5; 240×160 software framebuffer; ordinary controller inputs only.
Local evidence: `artifacts/e02/run-zqRzqG`. No ROM/save/executable distributed.

## Reproduce

Install the [pinned toolchain/dependencies](../../testing.md), then run
`bash scripts/test-e02.sh` from a committed tree. Actual Cloud invocation:

```sh
PATH=/workspace/toolchain/root/usr/bin:$PATH \
PKG_CONFIG_SYSROOT_DIR=/workspace/toolchain/root \
PKG_CONFIG_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu/pkgconfig \
LIBRARY_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu \
DCC_CACHE=/workspace/dcc-toolchain-cache \
DCC_TEST_CFLAGS=-I/workspace/toolchain/root/usr/include \
DCC_TEST_LDFLAGS='-L/workspace/toolchain/root/usr/lib/x86_64-linux-gnu -Wl,-rpath,/workspace/toolchain/root/usr/lib/x86_64-linux-gnu' \
bash scripts/test-e02.sh
```

The runner exports the exact Git commit into an isolated directory, hydrates the
verified upstream inputs, rebuilds the pinned compiler, regenerates game products,
builds the ROM and compiles the host harness with warnings as errors. Clean pinned
source caches were reused; workspace generated/untracked game inputs were excluded.
Full raw setup/build logs are archived without trimming native tool output or its
trailing spaces. Every emulator error log must be empty. Each route boots a new
process using an actual flash save, never a savestate or injected game RAM.

## Results

| Route / log | Assertions / outcome |
| --- | --- |
| E01 new-game.route / setup.log | 16 PASS: fresh E02 game, exploration, normal save |
| guide-before-trial.route | 8 PASS: first guide meeting, healthy roster, repeat rest and pre-trial advice; does not save, so later routes retain fresh meeting state |
| B01 defeat.route / defeat.log | 8 PASS: ordinary defeat, restored duo, trial flag unset, local movement and retry |
| guide-recovery.route | 16 PASS: duo victory, actual party HP 22/16 and PP 32/17; guide restores HP 30/26 and PP 35/20; repeat rest, entrance/landing round trip, manual save |
| reload.route | 7 PASS: cold Continue, saved guide flag, restored party HP/PP, completed trial flag, repeat dialogue and movement |

**55 assertions passed. Five empty error logs.** Guide dialogue and final recovery,
save, return and reload captures were visually reviewed. Checksums cover all report
files. Route `expect` flags are intro/crate/guide bits (0x20–0x22).

The `roster` checks read HP and persistent status from actual party records and
locally decode the encrypted attack substructure to read party PP. They never
modify RAM. This matters: after healing, old battle PP remains 32/17 while actual
party PP is 35/20. `duo healthy` alone does not establish resource restoration.
Normal status values remain zero; curing an inflicted nonzero status is explicitly
not proven by this encounter and remains later combat validation.

## Play and limits

Start a fresh E02 save. Reach the landing and talk to the guide by the south wall
at (4,8). Rest is free and repeatable. Win the AI trial, then return to the guide to
recover; losing still restores the duo locally and allows another attempt. Save
outside battle using START → SAVE.

E02 intentionally replaces B01 victory auto-heal with guide recovery and updates
the promised dialogue. Historical B01 victory routes belong to their recorded
revision. Old B01 saves can retain a cached object list without the new guide;
no cross-milestone migration is claimed. Save structure sizes are unchanged.
Guide flag 0x22 was unused. No reward/quest/crafting or capture-audit work is claimed.

The guide is an invented unnamed tutorial character with original text, not a
claim about a specific book scene. Guide/cave/battle art remain explicit upstream
placeholders, scheduled for S02 inside the slice. New text fits the inspected
screens. The initial return test correctly stopped at the trial attendant; the
final route walks around it. A preliminary old-save test correctly exposed the
cached-object limitation; the final run starts fresh. No E02 acceptance blocker.
