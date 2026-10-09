# Current Guard-first: first milestone STOP, no retry

The ONE parent-scoped route stopped at native validation immediately after
Guard victory. Current order/travel/Save/cold acceptance remains **unverified**.
Parent review of the observer's source-defined friendship modifier is next;
no integration or V01 execution authorised by this result.

Frozen source/host/execution `cad9eadfd8405f8eb040e478a7f7c7fb8948788c`, based on
PR108 head `3e0ace22ce82fcee61a6e945be219dd8849e6ea3`. [Contract](../../../../floor1/g01e-guard-first-current-contract.md),
[complete frozen ordinary inputs](input.route), [identity](identity.json),
[exclusive claim](execution-claim.json), [complete assertion/controller/HP trace](replay.log),
[exact STOP](STOP.json), [errors](errors.log), [read-only native diagnosis](diagnosis.json).

Game remains `5084a1814904f1a43fd999fddf770b221bb53653`;
ROM SHA256 `23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167`;
ELF SHA256 `cafc512d915d01ff1b598b1a7050261f5990bc50fc0faed533b0ec6d7309336b`.
Approved existing game build reused and rehashed; no new game compilation or edit.
New host compiled `cc -std=gnu11 -Wall -Wextra -Werror … -lmgba`; empty [build log](host-build.log),
mGBA0.10.5. Host SHA256 `b651ff60034b0c432d2b96f4aba3c7a54466c2f940e64ac334e195b996b6a1e6`;
binary `60977f782c422f820f63c09922e50f1d28c9361b0f66b0901ed9eb1f9a115b1d`.
42 focused native phase/domain/clock/state/travel/policy cases passed before
execution. They proved rejected phases perform no SaveBlock reads and historical
offensive decision block unchanged; the matching-location input case was missed.
Historical hosts/gates/failures/accepted plan and all62 existing remote heads
preserved; [18 open/draft/unmerged PRs75..108 and CI reconciliation](reconciliation.json).
No workflow runs returned for inventory head; not a CI-pass/protection claim.

## Actual execution and stop

Input is the retained **ordinary reconstructed pending PR91** Save
`c11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f`,
not an original legacy input: Field37,31, levels9/9, XP495/805, full health33/28,
PP8/40/2/40, Potion1/SCRAP2, trial2135 won and patrol2136/2137 pending.
All14 latest sector checksums validated offline; exact600 party/count/counter72,
300 flags and all1272 canonical owned bytes matched the first stable boot.

23 completed emulator assertions;14680 exact absolute frames =2044 unarmed boot
+12636 declared battle-mutation frames. One trainer856 battle,11272 actual
battle-bit frames, outcome1/no incapacitation. Real stable return Field37,31:
Carl level10/XP627,19/36HP, PP1/40; Donut level9/XP937,5/28HP, PP0/35.
Flag2136 became true while2137 stayed false. No ordinary walking frame occurred.
At `checkpoint guard-win`, frozen validator line79 rejected its precondition
`met_location != current_section`. Exit71,815-byte explicit Python/gate error
log, no emulator error. Last accepted snapshot remains boot/frame2044; live STOP
snapshot/frame14680 was retained separately, not silently accepted/re-anchored.

Pinned `AdjustFriendship` uses grow-level base5 at75 friendship, then **+1 when
native met location matches the current region section**. Both input members
match Field; Carl gained a level and changed75→81, while Donut remained75.
The frozen guard incorrectly required the nonmatching-location case. This is an
observer expectation error, not a failed offensive battle policy or save damage.

Read-only independent reconstruction from captured native bytes confirms complete
600 party/checksums/reencoding/identity/XP/EV/source level stats match with that
source-derived modifier, including the other400 party bytes. HP/PP are actual
legal combat outputs. Full300 flags differ ONLY by2136; trial true, Howler false,
optional/preparation/boss/checkpoint/loop unchanged. All1272 logical owned bytes
match except exact320 money gain; all bags/PC contents unchanged. Counter72,
map/position and count2 unchanged. See diagnostic script
[`scripts/analyze-f1-g01e-guard-first-current.py`](../../../../../scripts/analyze-f1-g01e-guard-first-current.py).
This diagnosis does not retrofit a pass or alter the frozen host/claim/STOP.

Guide restoration, Howler, all six named measurements, preboss approach, manual
Save and cold **were not reached**. There are no measured trips to compare with
28/448,38/608,46/735 ceilings. Missing measurements remain rejecting evidence;
planned cadence never becomes actual measured frames. No full/current-order/
legacy/C01/human-pacing/visual-rollout claim. No further emulator frame or retry.

## Actual captures and private retention

Four actual240×160 captures, [exact image identities](captures.json):
[boot](boot.png), [Guard challenge](guard-start.png), [Guard cleared dialogue](guard-victory.png),
[first STOP](stop.png). Challenge shows the correct Guard; victory and STOP show
“The guard patrol is cleared. It will stay cleared after saving.” The latter
is game dialogue, **not evidence that a Save occurred**. All four inspected
against input/trace; victory and STOP are separately captured equivalent frames.

[Private retention receipt](private-retention.json): Library archive
`DungeonCrawlerCarlemon-guard-first-current-STOP-20261009.zip`,59668bytes/54files,
SHA256 `6396e1d1b30b27d65c3b3052f81901d4a6c6a4b74453f5c6ddab7b531e5f723e`.
Contains ONLY this new claim's raw snapshots/actual native contexts/logs/inputs/
captures/generated source and unchanged pending input copy. No newly completed
saved game exists. Disk `patrol.sav` remains exactc11c input hash. ROMs/executables/
credentials/denied old datasets excluded. Original deleted raw logs/legacy16/
original patrol-complete Save remain unavailable; fresh inputs never substitute.

## Commands and next dependency

```sh
# Within the pinned dcc-party-resource tooling container; no emulator in tests.
python3 scripts/floor1/guard-first-tests.py
python3 scripts/test-f1-g01e-guard-first-current.py \
  --build artifacts/floor1/warden-fairness/build \
  --output artifacts/floor1/guard-first-current/runtime \
  --seed artifacts/floor1/recovery/runtime-menu-repair/seed.sav --stage prepare
# ONE exclusive execution, exit71; STOP prevents another run/dependent cold.
python3 scripts/test-f1-g01e-guard-first-current.py \
  --build artifacts/floor1/warden-fairness/build \
  --output artifacts/floor1/guard-first-current/runtime \
  --seed artifacts/floor1/recovery/runtime-menu-repair/seed.sav --stage patrol
# Read-only diagnosis only after STOP.
python3 scripts/analyze-f1-g01e-guard-first-current.py \
  --runtime artifacts/floor1/guard-first-current/runtime --output …/diagnosis.json
```

Implemented and compiled: separate observer/route/rejection tests. Runtime:
Guard victory and first milestone **STOP**, remaining acceptance unverified.
Merged: **no**. Parent review must first scope the narrow source-derived
matching-location modifier and tests using the actual native map section.
Any corrected complete route/cold needs a separate explicit execution claim;
preserve this one and all older failures. Only a passing scoped check and later
explicit integration authority can advance the reviewed stack, then stagedV01.
