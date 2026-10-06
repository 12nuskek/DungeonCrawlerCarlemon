# B01 duo prototype — 2026-10-06

Implemented: YES. Compiled: PASS. Runtime verified: PASS. Merge state is recorded
in [progress](../../progress.md); this report describes the tested source commit.

- Base: `91afb3deb6f856b4565e00bb65e81f0f1497a05f` (E01 merged).
- Tested: `9fc11212c465008e3571d9f77e98b41454ce919d`.
- ROM SHA256: `e6692036e3804d20d585ab6d0086fcf276d4d71561c105f6135f858152f4f8fd`.
- Real emulator: mGBA 0.10.5, headless software framebuffer, ordinary GBA inputs.
- Local run: `artifacts/b01/run-jQnN25`; no ROM/save/executable is committed.
- Toolchain/source provenance: [testing](../../testing.md), [foundation](../f01/README.md).

Reproduction with installed build tools and mGBA headers/library:

```sh
bash scripts/test-b01.sh
```

Actual Cloud command:

```sh
PATH=/workspace/toolchain/root/usr/bin:$PATH \
PKG_CONFIG_SYSROOT_DIR=/workspace/toolchain/root \
PKG_CONFIG_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu/pkgconfig \
LIBRARY_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu \
DCC_TEST_CFLAGS=-I/workspace/toolchain/root/usr/include \
DCC_TEST_LDFLAGS='-L/workspace/toolchain/root/usr/lib/x86_64-linux-gnu -Wl,-rpath,/workspace/toolchain/root/usr/lib/x86_64-linux-gnu' \
bash scripts/test-b01.sh
```

The script builds with `make -C engine -j2`, compiles the host harness with
`-Wall -Wextra -Werror`, and boots four separate emulator processes against actual
flash saves. It rejects dirty tracked source at entry and changes during execution.
These are custom gameplay builds, not claims of the stock Emerald hash matching.

| Route / log | Checks and result |
| --- | --- |
| E01 `new-game.route` / setup.log | 16 PASS: fresh intro, four directions, collision, crate persistence, reciprocal transitions, manual save; fixed duo initialized |
| defeat.route / defeat.log | 8 PASS: both names/HP, four battlers, ordinary support-only play until both fall, local recovery with trial flag unset, movement and retry encounter |
| victory.route / victory.log | 9 PASS: four battlers, Carl Tackle PP 35→34 and Donut Swift PP 20→19 in the same turn, won outcome, local restored duo, resolved repeat text, movement, manual save |
| reload.route / reload.log | 5 PASS: separate-process Continue, saved duo and position, trial won flag retained, repeat interaction cannot restart the battle, movement restored |

Total: **38 assertions**, all four error logs empty. The battle checks also require
Donut's placeholder ability to be NONE, preventing inherited random Pickup loot.
The RAM checks read only: no game-state injection, health patch or savestate.
Offsets follow the pinned source's SaveBlock1, Pokemon, BattlePokemon, ObjectEvent
and Main structures; inspect them if those layouts change. Raw inputs and logs
are included. Captures were visually inspected for action choices, readable text,
local return and reload. A screenshot alone is not the acceptance evidence.

## Play manually

Start a **fresh save** (E01 saves have no protagonists). Follow the entrance note
and northeast ladder. On the quiet landing talk to the attendant at (9,6). Carl
has Tackle/Focus Energy; Donut has Swift/Growl. Choose actions for both. After a
loss both recover on the landing and the trial is available again. After winning,
both recover and the attendant reports completion. Save from START outside battle.

## Scope and review

One optional technical encounter, not the finished combat system. The temporary
Machop/Meowth records and all battle art, enemy species, trainer labels, send-out
animation and Pokémon menu language remain placeholders. B02/B03/S02 are pending.
Trainer XP/prize behavior is provisional; no achievement or loot system is added.
No save-layout change; the trial uses existing reserved trainer flag 0x857. Fresh
B01 saves required. Full safe-room services are E02, not delivered by this trial.

Review caught and fixed: missing explicit post-battle script continuation;
inherited whiteout text on trial loss; and accidental random Pickup loot. An
initial cold-reload test failed because its inputs stopped at the overwrite
confirmation; the corrected final route saves and reloads successfully. Final
diff review covered trainer flag capacity, source-only assets, callback scope,
save compatibility and all documented placeholders. No repository workflow or
scheduler was added. No known B01 acceptance blocker remains.
