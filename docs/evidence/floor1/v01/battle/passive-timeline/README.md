# Cached-pose return and passive native timeline

**Implemented and compiled; offline checks pass; gameplay unexecuted; unmerged.**
This is the one parent-authorised implementation following accepted ed4039b3.
Actual F-before-B4894 remains proven, with its cause unresolved. The return
optimization is not a demonstrated remedy. No fresh baseline/candidate was
prepared, claimed or executed. Historical totals remain five baselines/three
candidates; all STOPs, three strategy failures and controller histories remain.

## Frozen identities

| Item | Identity |
| --- | --- |
| Compiled implementation source | `2feadf56764c0d89c3dde9ef4622ea6d43b32f69` |
| Engine tree | `baac7fee52e2133fa6192799ef3851f629f188d7` |
| Candidate ROM SHA256 | `a022b2a5030214f8cbeb0621af47e6cb9a47208424aa86f56b67862b5028f8d4` |
| Candidate ELF SHA256 | `f31a5a8b2cb1602df378a7ca66b3cee8bbcea86de000536ab6f55acd727d0218` |
| Generated host source SHA256 | `ee269bb94ce4ab112f89035ae8e5d2b340972934f1f341e1993eae406376c504` |
| Compiled host SHA256 | `357a8b9b5c67f6a4ae00b389300191bab5850367dee734509a5163413506fcb3` |

The separate `build-cache-return` copy preserves earlier build directories.
All 11,734 tracked copied engine files match frozen Git blobs after existing
CRLF normalization only. The new pose object's executable text exactly equals
the accepted scratch counterfactual, SHA
`b5383fd351b53e0e82bf1c94bda6c6dc17276802f388da8d02d47760c6fc6672`;
Apply is 240 bytes. Compilation is not gameplay verification.

Original baseline source 4938927/ROMae1e9d36/ELF2fb481bd and original candidate
dbcc859c/ROM830fbb45/ELF0bbce8cc are byte preserved. Pinned agbcc da598c1d,
binary 6347d07e, GCC14.2/binutils2.44 and installed mGBA0.10.5/library a1d7713c
are unchanged. Exact values are in [build identity](build-identity.json).
No claim of rebuilding the installed mGBA library is made.

## Exact implementation and trace boundaries

Only one engine file changes: Apply's cached-pose return moves after its initial
graphics/id/pose checks and before position/ownership reads. Changed poses keep
every original write-time guard, all four 2048-byte buffer copies and the one
original transfer request. Art, policy, route, resources and mechanics stay fixed.

The standalone host sidecar pins 21 native points from each ELF, plus two dynamic
callback entries qualified by actual callback pointer/native caller LR/Thumb
SYSTEM. It samples ReadKeys iterations, callback entry/resume, Wait entry/clear/
exit, native BIOS/main VBlank flag stores, battle VBlank/copy processing and
native IRQ-dispatch entry. Direct CPU/GBA reads retain raw/next PC, LR, CPSR,
modes/cycles/time, IE/IF/IME, flags, video/input/iteration counters, actual queue
root identity/deadline/priority and pending IRQ identity/deadline. Source-pinned
copy count/armed state, ordered descriptors, total bytes/signature are retained.
The named video record observes increments **after the entire original event
drain**, not at an internal callback instruction. OTHER stays OTHER; a deadline
of 6 and SYSTEM mode alone are never treated as proof of IRQ/main-loop identity.
Callback elapsed time is derived from native entry/resume emulated timestamps.

No bus write/read API, callback replacement, scheduling change, input call or
execution advance occurs in the observer. File I/O is outside instruction/event
dispatch. A 4096-record buffer, 1,000,000-record total (184,000,016-byte maximum),
64-event traversal and 64-copy bound fail closed 119. Startup requires complete
source pins and loaded-code opcodes/modes; private file create is mode0600 and
exclusive. Invalid pins/opcode, oversize/cyclic queues, capacity and I/O failures
stop before further execution. The adapter gains only a pure failure query to
stop errors raised by void instruction/event hooks. Existing strict 117 wins
over simultaneous trace 119. Full 2560 snapshots, typed B/F/E order/count/epochs,
original input cadence, timeout guards and acceptance comparators remain intact.

## Offline evidence

- PASS 38 installed synthetic timeline cases: 12 original-loop parity cases,
  eight fixed input epochs, full CPU/GBA observation byte neutrality, complete
  strict-stream match, capacity/pin/opcode/queue/file failures and sticky first
  divergence without post-stop stepping or realignment.
- PASS three additional native Wait phase cases: exact retained 48-byte Wait
  instructions observe flag clear before/after and exit, including 1→0 after
  earlier service. Synthetic IRQ stores are explicitly separate from native
  VBlankIntr. The original event/frame/flag stdout trace stays byte identical;
  each hook leaves the entire CPU/GBA unchanged. Original due ARMRun calls are
  uninstrumented in this mechanism fixture; production event-drain ordering
  has the separate parity tests. Its 14 retained original mechanism cases pass.
- PASS existing boundary/model/capability, source pose/lifecycle/guard tests,
  native observer ABI/lifecycle tests, complete snapshot contract, installed
  interpreter/full 2560 reader, 193 diagnostic origins/privacy cases, 87 typed
  header mutations, 29 installed hardware mutations and 58 EOF/EIO short reads.
  Full production host compiles with warnings treated as errors, never invoked.
- PASS game compilation and native 21-point manifest resolution for new ELF;
  native pose object text exactly matches the accepted counterfactual.

These fixtures execute synthetic mechanisms only: **zero game ROMs/Saves loaded,
resets, route/battle executions or new exclusive claims**. They prove observation
neutrality for tested mechanisms, not whole-game equivalence or actual timing
ground truth. The unchanged older diagnostics regression retains its original
historical count field 5/2; current authoritative counts are 5/3 in preservation
and this document. Older test output scope strings are historical model labels.

Safe results/logs and bounded pin manifests are here. Synthetic binary sidecars,
raw typed/key-bearing data, full symbols, binaries, ROMs and Saves stay private/
local outside uploads. No new actual gameplay captures or durable runtime-trace
claim is made. The previous actual captures/private Save archives remain
historical evidence; missing original legacy Saves/deleted patrol logs and
uncaptured historical baseline cycles/IRQ/controller/flag history remain missing.

## Preservation and next dependency

Initial 68 heads/all 65 PRs reconciled; PR114 is the only open PR, draft/unmerged.
Main/base c6d647a8 and accepted-plan SHA 9b3e5d6f stay unchanged. Prior 19,074 Git
files include 19,063 unchanged blobs and 11 authorised modified files; 364 protected
art/route/evidence/accepted-plan files remain byte exact. Four status documents
gain prefixes with complete old bodies intact. No history rewrite, new PR/task,
merge or scope expansion. See [preservation](preservation.json) and
[initial reconciliation](reconciliation.json). Check/status/workflow counts 0
are absence, not CI PASS; definitions are not freshly available.

Parent review of these frozen identities/proofs is next. A future pair needs new
explicit authority: one fresh instrumented original baseline, candidate only
after complete baseline PASS, same Save 030b/route afbd80b0/fixed fortify policy,
30,000 battle/36,000 visual bounds. First divergence stops all dependent work,
with no post-stop step, blind retry, RNG/timing search, count waiver or realignment.
No pair is executed here. Original legacy, C01, complete action/victory/cleanup/
equivalence, human pacing and full-floor gates remain pending. The nine-district
Floor1 accepted scope stays intact. [Current contract](../../../../../floor1/v01-passive-timeline-contract.md).
