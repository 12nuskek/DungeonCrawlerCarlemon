# Active-pose implementation — offline checkpoint

2026-10-09. Source `9c83611e8e9b61d55388c18496c361d3362e462e`, engine tree `8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a`, descends normally from documentation checkpoint `6d6a80aaea6eb7e6a54e17f6f210c8f87167e1e9`. Implemented, compiled and tested **offline only**. Existing draft PR114 remains unmerged. No gameplay preparation/execution, runtime capture, baseline restart, upload retry or replacement environment/container. Counts remain six baseline/four candidate executions; all original stops, strategy failures and controller records remain historical evidence.

## Behavior and source review

`DccBattlePoseUpdate` still runs immediately before `AnimateSprites` in `BattleMainCB2`. The unchanged four-byte state layout remains sixteen bytes across four battlers. Two separate byte masks record active transitions and pending native conditions. An empty mask returns before the old per-battler scan. Notifications set pending work and perform no pose copies; the existing callback resolves final HP/absence/species/animation/attacker conditions. End/restart, attacker-away/back, HP-zero/restored and absence/reappearance between callbacks therefore do not trigger early recovery or clearing.

Move start and real SLAM impact keep their existing state mutations and wake active countdowns. Standard anticipation/contact transitions, recovery and failed applications continue ticking. REST sleeps only when its final idle pose has applied successfully. WINDUP stays active through age eighteen, preserving the unchanged warning observer, although pose fourteen first appears at age sixteen. Settled WINDUP/SLAM and standard contact holds sleep until a native event.

The age byte deliberately freezes while a settled pose sleeps. Equivalence compares action, recovering, applied pose, warning condition, all buffer pixels, writes and queued transfers; it does not claim bytewise equality of the old redundant sleeping-age increments. Failed application attempts remain active and advance age on the original callback ticks. A missing graphics registry retains pending work and preserves the original no-progress behavior until restoration.

`Apply` retains the same null registry, sprite-ID range, pose range, cached-pose, live-sprite, native frame-ownership and buffer guards in the same order. A real change still copies four 2048-byte frames in order and queues one 2048-byte transfer. Its result now tells the mask when application succeeded. Cached-pose behavior retains the original guard placement.

Source review covers all direct animation-active and animation-attacker assignments, including move/general/special/status launches and utility/argument/position tasks. Notifications also cover direct HP and absence writers, HP zero before faint, bytewise switch replacement, bytewise Transform, battle-intro replacement, party-data replacement and item restoration. Existing faint, graphics allocation and free hooks reset state and both masks. The fixture audits direct writer coverage and key bytewise replacement sites; it makes no pilot-unreachable assumption for those alternative animation writers. No observer assertion, native callback phase, pose asset, battle policy, route, mechanical mutation, Save ABI or floor content was changed.

The final diff was reviewed against the pinned parent. Native notifications only add pending work beside existing mutations; braces preserve previously conditional HP/absence writes. The four-copy ordering, recovery thresholds, warning gate and original encounter guards were checked. No further implementation change was needed after review. Historical status/history files and the accepted plan remain untouched; denied private publication material is excluded.

## Completed checks and integrity preservation

The original repository lifecycle fixture passed. New fixed synthetic schedules passed **11202 ticks across 91 scenarios** against the old module from the pinned parent: all six actions, both pilot trainers, threshold edges, long holds, end/restart and attacker changes, repeated/overlapping moves, interruption, zero HP separately from faint, absence/reappearance, replacement/reset, all guard failures/restoration and nonpilot negatives. Every compared tick matched pose pixels, action/recovery/applied/warning state, backing-copy order and queued transfer order. The module made no BattleMon writes in these fixtures.

The instruction fixture passed **56 cases** across old/new actual compiled modules. It covers idle, settled holds, active thresholds, transitions, recovery, final REST, zero HP, failed ownership, pending native end, pilot/nonpilot notifications and all seven direct/cached application guards. Existing native ABI assertions compile; compiled pose state remains sixteen bytes. The candidate instruction bytes equal the module in the complete isolated game build. All **17 authored pose pixel arrays** match the compiled ELF bytes.

After the transport interruption, one readiness check and one harmless shell command succeeded in the same workspace. Source SHA256 still matched `f80a396e4a9828736410e431b5f5676a25022e2f01bdd389c9a44dc7cc2d639a`; fixtures, traces, result files, build logs and ROM/ELF were retained. Integrity inspection confirmed the 11202 matching trace rows, recorded results and source/build correspondence. Executables and completed checks were not rerun in this preservation increment. Current build identities and pose-byte hashes are recorded separately.

## Observed costs and limits

The fixture executes bounded module instructions with synthetic RAM and unit ROM-bus costs. GetBattlerSide, position, BIOS copy, queue and memset are counted stubs; their native cost is excluded. These values are **not game cycle predictions**.

| Synthetic path | Old steps / cycles | Candidate steps / cycles | Candidate copies / queues |
| --- | ---: | ---: | ---: |
| Fresh REST | 270 / 882 | 20 / 75 | 0 / 0 |
| All-REST pattern | 398 / 1322 | 20 / 75 | 0 / 0 |
| Held WINDUP | 343 / 1130 | 20 / 75 | 0 / 0 |
| Held SLAM | 339 / 1118 | 20 / 75 | 0 / 0 |
| WINDUP threshold | 343 / 1130 | 299 / 957 | 0 / 0 |
| STRIKE transition | 488 / 1619 | 446 / 1454 | 4 / 1 |
| Recovery | 495 / 1641 | 446 / 1456 | 4 / 1 |
| Final REST | 468 / 1555 | 413 / 1348 | 4 / 1 |
| Failed ownership | 381 / 1249 | 314 / 1007 | 0 / 0 |
| Pending native end | 497 / 1650 | 595 / 1961 | 4 / 1 |
| Direct four-frame Apply | 172 / 574 | 176 / 586 | 4 / 1 |

Candidate pilot notification alone takes 32 steps / 100 synthetic cycles; the nonpilot guard takes 19 / 72. The empty-mask guard costs 20 / 75, not zero. Pending wakeups and the new Apply result can add overhead; no aggregate timing improvement, avoided boundary divergence or runtime remedy is proved.

The all-REST case is a **synthetic pattern inspired by the published frame8536 description**. Exact historical previous-frame bytes are unavailable. This fixture is not recovered evidence, a replacement runtime oracle or a reproduction of the original STOP117 interval. The corrected historical timestamps remain baseline2971920685/candidate2971920688, with Wait914 cycles before its own drain observation or917 before the candidate observation. No lost iteration or post-stop behavior is inferred.

## Build identity and reproduction

The full isolated build used GCC14.2.0, binutils2.44-3+23+b1 and agbcc source commit `da598c1d918402c42c0c0d7128ba14567f3175e9`. Supported Debian tool packages were extracted locally and the repository's agbcc build/install instructions were followed. No container or OS package installation was performed. Three required upstream multiboot blobs were verified against their recorded Git identities and used only in the isolated build.

Rebuilt agbcc SHA256 is `58078c3fe54c564bf23496d355f498a394fd5bb2b3a933e35cc835cc9bb14e0e`, differing from historical `6347d07ec65fb1a5df58f4fa79a807db11ac7bef32ffb6162ffb79bc68512684`. Both auxiliary compiler binaries also differ; all identities are in `build-identity.json`. The source commit/tool versions are pinned, but original compiler binary identity has not been restored. mGBA0.10.5 library SHA256 matches its recorded identity. This full game build was never executed.

ROM SHA256: `6b7a83f27ede2dac9a124c0e267f34c9d0747db4a68cff05425fb9966f5b2459`.

ELF SHA256: `98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d`.

Reproducible offline commands, after providing the recorded isolated toolchain and source/build prerequisites:

```sh
python3 scripts/test-f1-v01-active-pose.py --output /workspace/scratch/v01-active-pose-equivalence
python3 scripts/floor1/v01-active-pose-cost.py --engine /workspace/scratch/v01-active-pose-build/engine --tool-root /workspace/scratch/v01-active-pose-tooling/root --output /workspace/scratch/v01-active-pose-cost
PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/bin:$PATH PKG_CONFIG_SYSROOT_DIR=/workspace/scratch/v01-active-pose-tooling/root PKG_CONFIG_LIBDIR=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu/pkgconfig CPATH=/workspace/scratch/v01-active-pose-tooling/root/usr/include LIBRARY_PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu LD_LIBRARY_PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu make -C /workspace/scratch/v01-active-pose-build/engine -j2
git diff --check
```

The first command invokes the original hook fixture before the paired synthetic comparison. The second compiles native layout assertions and bounds the instruction experiment to module segments; it opens no game ROM or Save. The third compiles only and is not an instruction to execute gameplay.

## Remaining input and review gates

Initial supported workspace locations had no retained private runtime dataset; the former toolchain container was absent. The retained files reverified here are the newly written implementation, synthetic fixtures/results and isolated build. Original private legacy saves, the historical patrol-complete save, complete runtime reference streams, raw logs and private media were not recovered or independently reverified. No Save or original runtime input was recreated in this increment. Published historical projections are preserved as historical projections.

Next dependency: parent source/fixture/build review, then availability and exact verification of the original retained runtime inputs before any separately authorized candidate-only runtime validation. Synthetic evidence cannot substitute for those inputs or legacy acceptance. No baseline restart or new battle policy. Existing STOP117 and all other recorded failures remain failures. C01, human pacing, full-floor and original legacy gates remain limitations; no battle victory, cleanup, field return, reward, resource, manual Save/cold persistence or visual rollout is accepted by this offline checkpoint.
