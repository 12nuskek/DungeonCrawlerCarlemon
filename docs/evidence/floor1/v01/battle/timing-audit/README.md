# Offline timing and unchanged-pose cost audit

Implemented offline audit tools; **56 synthetic cases pass**. No engine or live
host edit, ROM/Save load, reset, gameplay, fresh battle attempt or merge.
The actual new F-before-B4894 failure remains proven; its cause and native
cadence impact remain **unproved**. An early cached-pose return is a supported
optimization opportunity, not a demonstrated STOP117 remedy.

## Reconciled input and exact pins

Audit input HEAD/remote `9a0903ea153d00e200725c34a3cf30196e2a9e88`, branch
`task/floor1-v01-battle`; main/base
`c6d647a815ffce44a2419a2cf83b6c2c094359f0`. The initial tracked tree was clean.
All68 remote heads and all65 PR records were reconciled: PR114 is the only open
PR, draft/unmerged. Historical stacks remain in the repository record; their
October8 status is not presented as current. Current-head checks, statuses and
workflow runs are all0. Workflow definitions were not freshly available through
the connector/direct path; absence of checks is not a CI pass. Repo AGENTS,
progress/backlog and all37 Floor1 documents were inventoried; accepted-plan SHA
`9b3e5d6f607a5345f73ea06dc38211d1c1a085bcd1d505a5772d4fb88e71ef27`
stays unchanged. No applicable local `.agents/skills` exists. The research skill
explicitly delegated one read-only primary-source review; no other writer ran.

| Retained build | Before | After |
| --- | --- | --- |
| Game source | `4938927da512543ca9aeea9527c103c84955e632` | `dbcc859c0ef15fc6d94b1f43052fb9e7b51803bf` |
| Engine identity | `76001ee128785714b7c15aef6d9c95630587d0a9` | `32199a30f0d7013e64f7ec1e274211ecc45df8ed` |
| ROM SHA256 | `ae1e9d36a94ed2eaa9d8fc79d790a2dc47173b932551891d889c657e12ca8461` | `830fbb45861e2c20c32c2a68862cabc9800972c4243b9f9cf65726fef7e656f9` |
| ELF SHA256 | `2fb481bdb041772fef7aa0ed15deb6a30b7a24c54f9f6d487c2b733fe26fb066` | `0bbce8cce6485cf6860ac19ce3b75b580ca8b2d5735909b40906f64c056eb98f` |

Actual last execution remains sourcefe6bda55009bb2b21aa4641f988c8a94655a0ebc,
hostd7bf57cadb8d4a78ac217b62e3c4a6e855424f2cbd6027e0131d5b676e170057,
binary1efcd983ab92e90060ec1135a5a2b977c70d3a9582013896dd2160051a3acc18.
These were not invoked here. Save030b12fd3516351b0935b9298f24d0a2078fb33afecbccb6ba3a9b4c2db6b73c,
routeafbd80b02d9d5acb9f63669f967fac3edc8eb00a2d2352e778f4114acb51bc27,
policy, inputs, assertions and bounds remain fixed. GCC14.2/binutils2.44;
agbccda598c1d918402c42c0c0d7128ba14567f3175e9, compiler binary SHA
`6347d07ec65fb1a5df58f4fa79a807db11ac7bef32ffb6162ffb79bc68512684`.
Installed mGBA0.10.5 library SHA
`a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`.
Exact official source/header identities are in
[the source review](mgba-ordering-research.md), not an assertion of a reproduced
mGBA library build.

## Compiled native path

`elf-path-identities.json` pins bounded STT_FUNC bodies in both ELFs and source
files; scoped locals disambiguate Apply. No full symbol table is published.
IntrMain is intentionally NOTYPE assembly, reviewed separately through its
literal pool:08000248–080003a4,348 bytes/SHA
`49bf55ee55f86c70681c09a8dfa1cd1f45be41d317f6ffb3c20e129c5617ffb4`,
identical in both. Native InitIntrHandlers copies2048 bytes to IWRAM, installs
INTR_VECTOR, enables IME/VBlank and fills gIntrTable.

Both AgbMain loops use ReadKeys callsite0800042a. Native CallCallbacks invokes
CB1 then CB2 if nonnull; UpdateLinkAndCallCallbacks returns through080004d6
BX r0, the captured next Thumb instruction. Its return leads to AgbMain's
link-receive test; a link branch can clear keys/copy requests and call callbacks
again. Both compiled branches are retained, rather than inferring an uncaptured
branch state. The common tail calls PlayTimeCounter_Update at080004b2,
MapMusicMain at080004b6, WaitForVBlank at080004ba, with LR080004bf. After native
Wait returns,080004be branches back to0800042a.

Playtime function before08083c04/after08083c1c,104 bytes and identical compiled
body: state check, ordinary frame increment and conditional carries/max handling.
MapMusicMain before080a29f0/after080a2a08,248 bytes: music-state dispatch may
start/fade music or inspect stopped/fanfare state. These calls occur after
callback return, so that captured return is not a Wait-entry observation. Music
and playtime branch states/costs were not captured for the failed baseline or
candidate. Several other compiled hashes differ through relocated calls/data;
this report does not claim complete surrounding code byte identity or cost
identity from unchanged source.

Wait080008ac,48 bytes/SHA
`6dd32b0546df4097a69177989a0096e2f435738b7d2a2145a036aa18d0371cb4`
is identical. It reads gMain.intrCheck at030022dc, masks bit0, stores the clear
at080008b8, loops on that flag and returns at080008d2. Volatile code includes a
second load before its clear; the stored result still derives from the earlier
read, so an intervening service can also be erased.

IntrMain samples IE/IF, saves SPSR and registers, disables IME initially,
prioritizes VCOUNT/serial/timer3/HBlank before VBlank, acknowledges IF, installs
selective nested interrupt enables, enters SYSTEM and calls gIntrTable. It then
restores IRQ mode, IE/IME/SPSR and returns through the BIOS IRQ return path.
Native VBlankIntr08000738,200 bytes, runs link sync/counters, the installed
VBlank callback, GPU/DMA requests, sound/link/random/status work, then sets BIOS
INTR_CHECK at080007ca and gMain.intrCheck bit0 at080007d4. CPU IRQ entry or IF
acknowledgment therefore does not establish flag-set completion. HBlank,
VCOUNT and serial handlers set their respective other bits; the main Wait
specifically clears/tests VBlank bit0.

## Source-pinned synthetic mechanisms

Official mGBA video callbacks were hash-checked and extracted into private
fixture compilation with names changed and read-only trace wrappers. Their
video/IRQ ordering is unchanged. Installed timing/GBARaiseIRQ/_triggerIRQ and
ARMRun execute; native Wait bytes and its branch back to ReadKeys callsite are
extracted from each ELF. The fixture initializes an empty core without reset;
no game ROM or Save enters it. Callback completion/post-callback NOP delays,
the small flag-setting IRQ body/IF ack, instruction bus costs and next callback
markers are explicit synthetic constructs. It does not execute native
VBlankIntr, music, playtime, ReadKeys or the battle. The separate compiled audit
pins those real paths. Trace records include time, frame, nextPC, flag,
IE/IF/IME/CPSR, deadline and queue identity, IRQ entry/service/return, Wait
entry/clear/exit, next native ReadKeys callsite and synthetic callback iteration. Region-switch hooks explicitly label the
selected target before prefetch and retain rawPC separately; an unfinished
pipeline PC is not presented as a stable next-instruction observation.

Seven cases per ELF pass; both seven-case trace sets are byte identical:

| Constructed case | Observed result |
| --- | --- |
| Wait clear before video | IRQ flag set satisfies the same VBlank; next iteration after1 video event |
| Video before Wait, IRQ masked until clear | Video already ended, pending service sets after clear; next iteration after1 event |
| Flag serviced before late clear | Wait discards the serviced flag; next iteration waits2 events |
| Punctual timing tick | Frame increments with installed IRQ event still pending |
| Tick8 cycles late | Same tick drains IRQ after frame increment, despite earlyExit |
| IRQ deadline6 | Queue root is GBA IRQ Event |
| Unrelated deadline6 | Same numeric deadline, different event and controller state |

These prove two different mechanisms. A boundary can shift between host video
intervals while preserving an iteration opportunity; a late clear can instead
lose an update. Neither proves the actual failure's mechanism. Its cycles0 /
nextEvent6 do not identify the event, delivery, native flag state or baseline
phase. A lost callback opportunity would also delay sprite/task/action age,
playtime and music updates relative to video service; identical pixels cannot
waive that impact. Synthetic phase/cost choices do not recover actual IRQ
history or baseline cycles.

## Pose traversal, transitions and compiled opportunity

After BattleMainCB2 adds DccBattlePoseUpdate before AnimateSprites, OAM/text/
palette/tasks. DccUpdate in extra ROM08e3ddbc (440 bytes) checks pilot/gfx then
loops battlers, character/side/species, absence/HP, action/recovery/age and Apply.
Applied REST and a settled WINDUP continue traversal; age saturating255 does
not skip it. Character and Apply use far-ROM native call veneers for the side
and position lookups. This is steady callback work even with no picture change.
Sprite code separately traverses64 slots and runs live sprite callbacks and
animation; BuildOamBuffer arms copy processing. This report does not measure
the actual complete per-iteration cycles, ROM prefetch state or branch phase.

Native Apply08e3db6c (244 bytes) already returns without copy, queue request or
applied write on unchanged pose. It currently calculates position, checks
inUse, frameImages ownership and backing buffer before testing the cache. A
transition copies the same2048-byte pose into four native backing frames
(8192 bytes), requests one2048-byte OBJ transfer (subject to native queue capacity), and changes applied. Request
queues work; VBlankCB_Battle calls ProcessSpriteCopyRequests between LoadOam
and palette transfer. That later CpuCopy16 work can delay the final VBlank
flag set independently of main-loop copies. Other native sprite requests,+GPU/DMA/audio work also remain. Captured copy count0/armed1 at STOP cannot
reconstruct earlier VBlank work.

The last recorded actual pose transition is visual4516,432 video frames before
STOP4948; Warden warning3989 is earlier too. We do not attribute the stop to an
immediate new8 KiB pose copy. Steady traversal, placement/prefetch and preceding
VBlank queues remain timing questions; no missing copy/IRQ log is fabricated.

Scratch compilation with the retained flags reproduces the original object
text SHA5948a4f29b577fbc0a4507a90a3d896e148dd2fde67d8ff3a8a40223d8c85fa6
byte for byte. A scratch variant moves the unchanged-pose return just after
gfx/id/pose guards and before position/ownership lookups; changed poses retain
every native write-time check. It is not applied to engine or a game build.
Three extracted/linked instruction fixtures test native Apply, retained
recompile and counterfactual across same/changed pose and valid, null gfx,
invalid id/pose, unused sprite, foreign images and null backing buffer:
**42 cases pass**, with no writes on blocked paths and all four transition
frames byte exact. Native and retained traces are identical.

| Valid Apply path | Native | Scratch early return |
| --- | ---: | ---: |
| Unchanged pose interpreter steps |79|36|
| Position calls |1|0|
| Copy calls / transfer requests |0 /0|0 /0|
| Transition steps including synthetic call stubs |184|183|
| Transition copied bytes / requests |8192 /1|8192 /1|
| Function bytes including literals |244|240|

Unit-ROM-bus fixture costs are251→117 synthetic cycles for unchanged pose;
these are not real game cycles. Copy/queue stub costs and native ROM prefetch/
WAITCNT state are excluded. Removing43 interpreter steps and a far lookup is
a bounded optimization opportunity. All tested write guards remain; this does
not prove a whole-engine timing remedy or equivalence.

## Review checkpoint and smallest next dependency

Parent review is next. No remedy is demonstrated for actual STOP117. The
smallest useful next implementation would be read-only timeline instrumentation,
reviewed offline first: callback entry/return/iteration, native ReadKeys,
Wait read/clear/entry/exit, both flag stores, video event/frame increment, IRQ
queue/delivery/controller flags, installed callback and cycles, plus queued
transfer counts. Observation must preserve interpreter/event order, inputs,
comparisons and first-stop authority; synthetic negatives establish that first.

Only new parent authority could permit one frozen bounded baseline and one
dependent candidate after complete baseline PASS, with the existing Save/
policy/cadence/bounds and strict first divergence. A fresh baseline timeline
would be a new execution, separate from the five historical baselines, not
restored old evidence. If first-stop traces still end before Wait, post-stop
cadence remains unresolved; observing further would require a distinct explicit
contract and could not count as comparison PASS. No early-return engine edit,
diagnostic continuation, realignment or retry is authorised by this audit.

All five baseline/three candidate histories, STOP35/107/105/103 and both distinct
STOP117 records, original strategy failures/controllers and passed baselines
are preserved. Original legacy inputs/raw logs and deleted patrol Save remain
missing; C01, candidate full actions/victory/cleanup, human pacing and full-floor
gates remain. Nine-district authorized plan and private review scope are fixed.

Safe JSON/JSONL here are synthetic records or bounded source identities, never
denied actual raw/key datasets. ROMs, Saves, binaries, complete symbols and
private Library IDs stay outside Git. Existing current capture/clip provenance
remains in the previous candidate evidence; no new visual is produced here.
An accidental unbounded local symbol-listing tool result was neither committed
nor uploaded. All subsequent ELF extraction was bounded.

Reproduce inside the pinned container, using local retained inputs:

```sh
python3 scripts/floor1/v01-timing-path-audit.py --output /workspace/scratch/v01-path-audit
python3 scripts/floor1/v01-timing-audit.py --output /workspace/scratch/v01-mechanisms --official-video /workspace/scratch/v01-runtime-binding/source-review/video.c
python3 scripts/floor1/v01-pose-cost-audit.py --output /workspace/scratch/v01-pose-cost
```

[Authority contract](../../../../../floor1/v01-timing-audit-contract.md).
