# One Potion intervention — failed controller check, combat stopped

F1-G01e-PT, 2026-10-08 Australia/Brisbane. Branch `task/floor1-g01e-potion`,
base `f4e568d582430dc9fc118f0af4afbc26b781e884` (draft PR85).
[Issue86](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/86) /
[draft PR87](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/87), pushed
and unmerged; evidence package `3528fb8cd5ad5dc5d796435da316581beffcafa7`.
The [hypothesis and stop conditions](../../../../floor1/g01e-potion-contract.md)
were committed at `9e2ebf3` before the single actual execution. This is a failed
verification increment; no game change, merge or full-route acceptance.

## Identity and result

Game compiled source `99243073ebead4ecd4fa9e4f4362d9e0d70c86df`;
actual tested runner `fa175347918b580cbdda47738407bf3857fa21ca`. ROM SHA256
`6c447159ae6d3cf62b5c8860d1fd0ff62e0cb93a0a603553c3d2a0ca14bce7cb`.
This historical compile was reused to preserve the diagnosed failure exactly.
Fresh host compiled with GNU14.2.0 / `-Wall -Wextra -Werror`; actual mGBA0.10.5.
A prepare-only run compiled the host without emulator or save-copy execution.
The committed runner then claimed one execution and ran once. Its persistent
claim prevents rerunning; do not remove it or invoke an alternative controller.

All59 battle input pulses preceding frame24673 equal the retained exact trace.
Howler victory passed; guide recovery and travel reached the same Guard turn4
Carl action. The read-only decision check passed: Carl3/36 HP, Donut30/30 HP,
PP4/40 and0/38, Guard0HP, Scuttler18HP, exactly one owned Potion. The earlier
three failed blind strategies remain counted; this targeted test is separately
recorded under the parent's explicit one-test instruction.

The host sent RIGHT at24673, A to open Bag at24685, then A at24721 when the Bag
input task existed. It advanced its own state to awaiting the item context menu,
but the captured screen was still black during the fade. The host omitted a
palette-fade readiness check; pinned `Task_BagMenu_HandleInput` in
`engine/src/item_menu.c` processes selection only when `!gPaletteFade.active`.
Premature A is consistent with the observed black capture and stalled context
wait. No further RAM/frame probe or retimed test was run to refine that diagnosis.

The36,000-frame Guard pilot bound expired with exit32 after26 passed assertions.
`errors.log` contains only the host's `pilot exceeded frame budget`; no mGBA
fatal/error was logged. The resulting failure is not a Guard defeat or proof
that a20HP Potion would fail to help. The Potion hypothesis remains untested
past its exact decision point because the controller did not verify actual use.

| Acceptance | State |
|---|---|
| Exact ROM/save/route identity and pre-intervention inputs | Passed |
| Exact Carl survival decision / one owned Potion | Passed |
| Actual20HP heal / exactly one consumption / PP at use | **Pending** |
| Guard flag2136 after Howler2137 / victory return | **Pending** |
| No duplicate XP / resolved interaction / guide return | **Pending** |
| Actual manual Save / cold Continue | **Pending** |

[Bounded verdicts](summary.json), [capture provenance](captures.json).
The ordinary original and owned run copy are byte-identical after the failure;
no actual Save completed. Complete logs/route/host/symbols and failed outputs are
preserved locally at `artifacts/floor1/potion/runtime-_16gl_zj`. The prepare-only
host is at `prepare-9p38yvzf`. No raw memory/key dumps, prior denied diagnostic
outputs, saves, ROMs or denied ancestry are published. Only bounded fresh evidence
is included here; the retained private diagnostic trace was used locally.

## Actual native evidence

These untouched240×160 frames are from the actual failed run, on the exact game
source/runner/ROM above. They prove neither healing nor victory.

![Carl at the exact turn4 decision before the Potion intervention](decision-before.png)
![Bag fade was still black when the controller prematurely sent A](owned-potion-bag.png)

## Commands and continuation

```sh
PATH=/workspace/toolchain/root/usr/bin:$PATH \
DCC_TEST_CFLAGS=-I/workspace/toolchain/root/usr/include \
DCC_TEST_LDFLAGS='-L/workspace/toolchain/root/usr/lib/x86_64-linux-gnu -Wl,-rpath,/workspace/toolchain/root/usr/lib/x86_64-linux-gnu' \
python3 scripts/test-f1-g01e-potion.py \
  --retained /workspace/DungeonCrawlerCarlemon/artifacts/floor1/g01e \
  --original-save /workspace/DungeonCrawlerCarlemon/artifacts/floor1/a01/run-I7PJq0/both-pending.sav
```

Historical command, **do not repeat**. Same command with `--prepare-only` passed
static host compilation first. The input contract depends on these preserved local
artifacts and their recorded identities; no fresh-save/full-route claim is made.

Combat is stopped under the explicit one-test instruction. Do not fix the input
cadence and retry, search policies, inject resources or change stats/PP. Report
the failed controller check to parent. Independent live no-collection source and
ordinary menu/summary audits remain the next ready work. Any further combat work
requires a new focused parent instruction addressing this failure; it is not
implicitly authorised by routine continuation. Newerc643/b025 combat, first-clear,
full route, finalT, human pacing, V01 and whole-floor acceptance remain pending.
PR85/83/81/79/77/75 remain draft/unmerged; main unchanged. No new writer, workflow,
scheduler, quota check, rollout or public playable release.
