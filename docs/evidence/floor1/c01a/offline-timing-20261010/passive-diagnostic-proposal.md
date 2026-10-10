# Missing evidence and minimum passive diagnostic proposal

No game remedy is justified by STOP124. Do not change fonts, rendering, copies,
DMA scheduling, padding or comparisons on proximity alone. This proposal is for
review; instrumentation and execution are not implemented or authorized here.

The retained candidate stayed in CB1 invocation3665 from physical frame3170 to
3171; CB2 remains5043, dispatch/read5044. Carl's move-init callback assignment
has completed and opponent bit1 is clear. The current controller index and
command are not captured. A later opponent/controller path within that pass is
consistent with the state; identifying battler3 or CHOOSEMOVE as observed would
be unsupported. Baseline has only summary PC/CPSR/counts for this interval,
not its detailed invocation positions. The candidate stack above
GetSubstruct is absent. The recorded CopyToVram queue is distinct from the DMA3
manager; an empty former queue does not prove the latter completed.

Keep the original native B/F/E/EOF and full2700-byte physical-frame comparison
unchanged. Bind a separate passive sidecar to each actual ELF. Directly read
memory/registers before original instructions at these selected points:

- BattleMainCB1 before/after the battle-state call (+6/+10) and controller
  indirect call/return (+36/+40); record actual gActiveBattler, command byte,
  exec flags, per-battler callbacks, invocation count and original LR/SP.
- PlayerHandleChooseMove before/after InitMoveSelectionsVarsAndStrings and
  after its callback store; entry/return of the two printers, synchronous
  AddTextPrinter, and the first HandleChooseMoveAfterDma3 check.
- OpponentBufferRunCommand dispatch, chosen handler entry/return and
  OpponentBufferExecCompleted before/after the bit clear. Resolve the actual
  command table and current battler instead of assuming an AI branch.
- RequestDma3Copy entry/return and ProcessDma3Requests entry/return with queue
  cursor, manager lock, accepted request index, size/mode, busy mask, pending
  request count/bytes; VBlank entry/exit with VCOUNT, IE/IF/IME, event/IRQ context,
  existing emulator cycles and frame counter.

At each physical frame end retain actual PC/LR/SP/CPSR and a fixed bounded stack
slice plus those controller/DMA fields. Record only source-bound points, not
every glyph/instruction. No bus API with side effects, function invocation,
debugger CPU modification, keys, scheduling, file I/O inside CPU/event dispatch,
or additional step/frame. Reuse the passive before-instruction mechanism and
buffer host writes for the existing frame drain/terminal close. Preserve
original STOP codes and test terminal retention before any execution claim.

Limit the added sidecar to the existing first-Fight handoff: its one A frame,
24 neutral frames and unchanged first move-ready900-frame maximum, at most925
frames per case. Proposed hard bounds:64 words/record,4096 records/frame,
925 summaries of184 bytes plus one terminal marker and48 bytes of headers:
`(925 * 4096 + 1) * 256 + 925 * 184 + 48 = 970103304` bytes per case,
1940206608 bytes for two cases. Freeze executable capacity/passivity checks and
combined retained/pair allocation before execution. Any overflow stops at a
distinct diagnostic failure; no dropped
records, longer waits, coalescing of differing context or replay. Outside that
window retain the existing original observer behavior.

Review the precise source-bound point set, byte arithmetic, passivity
and success/error fixtures first. Only a later separately frozen claim may
collect new baseline/candidate timing. Reconstruct neither the lost original
oracle nor unflushed STOP124 observations by synthesis.
