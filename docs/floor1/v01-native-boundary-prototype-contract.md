# Offline native-boundary adapter prototype

This increment is offline source review, installed-capability testing, synthetic
adapter fixtures and local derived Donut source work. Zero gameplay frames,
loaded ROMs/Saves, CPU instructions or new execution claims. No runtime adapter
is integrated/enabled, and no public upload/push or PR mutation is authorised.
The existing remote draft PR114 remains at a86ceca9. Parent review is next.

## Corrected sampling contract

Complete matched **native-boundary** snapshots must replace the invalid raw
video-frame serialization comparisons in any separately authorised integration.
This is a corrected sampling contract, not a runtime mask/exception and not
retroactive acceptance of either historical execution. Raw video frames remain
the input, capture, graphics and lifecycle clock. Every original frame, key
sequence, input cadence, fortify/offence controller decision and behavioural
assertion remains. The original30,000 battle/36,000 visual bounds remain.

At every verified AgbMain -> WaitForVBlank entry, capture the complete600-byte
party,352-byte BattleMons,300-byte flags,1272-byte resources and existing exact
scalar/hardware-key/canonical-controller fields. Verify native encrypted party
checksums/BadEgg at complete snapshots. No region or byte may be masked, omitted,
partially accepted, re-anchored or inferred from a checksum. Keep existing
logical-resource/counter/count/identity assertions and readiness/battle/reward/
field/save gates; canonicalisation remains only the existing verified contract.

Each complete snapshot has an ordinal, video/input epoch and authority record.
Compare **every** boundary against the same ordinal and epoch in the complete
reference stream. Record every video frame's boundary count, including zero;
reject missing, duplicate, reordered, wrong-epoch and trailing boundaries. Do not
assume exactly one native boundary per video frame. Explicit checkpoints require
a complete matching boundary from the current video/input epoch; a missing fresh
snapshot fails without advancing time to obtain one. Existing assertion counts
and conditions cannot be waived by a snapshot-validity result.

Per-frame graphics/lifecycle checks and captures stay at the original frame end.
Keep diagnostics, every controller/input record and all historical failed roots.
The retained old state-trace files are raw-video records, not boundary records;
they cannot serve as a complete native-boundary reference stream. Creating such
a stream would require separate parent authority for live validation.

## Native boundary and interrupts

Both exact ELF files resolve scoped `L:main.o:WaitForVBlank` at080008ac, size48,
entry `push {lr}` opcodeb500; unique AgbMain BL at080004ba, callerLR080004bf.
The preceding consecutive calls are PlayTimeCounter_Update at080004b2 and
MapMusicMain at080004b6. AgbMain source main.c89–168 returns from all CB1/CB2
dispatch paths, then play-time and music, before this entry. The symbol resolver
verifies ELF STT_FUNC scope/extents, compiled bytes, direct BL targets/order and
the entry opcode in both pinned builds. Addresses are derived, not guessed.

Boundary authority requires the installed hardware breakpoint's exact point ID
and entry address, raw Thumb PC=entry+2, exact callerLR, Thumb/SYSTEM mode,
prefetched opcodeb500, nonhalted CPU and no pending event dispatch. Unknown ELF,
CPU, breakpoint, caller, opcode or phase is an error, never a deferred acceptance.

SYSTEM mode alone is unsafe: native crt0.s90–129 switches interrupt callbacks
into SYSTEM mode. WaitForVBlank is a private main.c function whose sole source
caller is AgbMain; the verified direct LR distinguishes that caller from an
interrupt trampoline or nested getter. At the actual entry, callbacks and their
in-place crypto, bytewise BattleMons and SaveBlock relocation/rekey calls have
returned. The observer reads while CPU execution is suspended and performs no
CPU step during a snapshot. An interrupt delayed until the next event cannot
interleave with that host read. No interrupted getter snapshot is accepted.

Reviewed ordinary battle/field VBlank callbacks update graphics/RNG/audio/native
interrupt counters; they do not establish party serialization authority.
Battle_main.c2086, overworld.c1846 and main.c340 retain their original effects.
The source review covers the pinned ordinary route; it claims no general link,
frontier/recorded battle, soft-reset or arbitrary callback support.

## Installed capability and timing neutrality

Installed library SHA256a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63,
package libmgba-dev0.10.5+dfsg-1; projectVersion0.10.5, gitCommitunknown.
`USE_DEBUGGERS` is required for the installed debugger ABI declarations. The
probe initialises an empty core, attaches a custom debugger, sets a synthetic
register fixture, installs/hits/clears a hardware breakpoint and checks the
complete ARMCore byte-for-byte. No game, reset, CPU instruction or frame runs.

Two default paths cannot be used unchanged. Standard debugger stepping handles
pending events and then executes an instruction, which can cross the original
frame end. Default ARMDebuggerEnter also writes nextEvent=cycles on a hardware
hit; the original installed probe caught that nonneutral state. The prototype
uses a per-instance passive hardware-only entry hook: record the hit without
calling that default CPU-mutating entry handler. It does not compensate by
restoring CPU fields. No software breakpoint, memory shim, watchpoint or stack
tracing is used. The installed passive-hook probe verifies unchanged CPU state
and frame count; debugger frontend state alone is resumed.

The frame-loop prototype keeps the original frame counter/time guard and its
ARMRunLoop instruction-batch/event boundary. Within that batch, observe before
each instruction; when an event is due, process it and recheck the **original**
outer guard before any next instruction. Original time limit remains
VIDEO_TOTAL_LENGTH+VIDEO_HORIZONTAL_LENGTH=282128. Never runFrame and then step
to a snapshot; never set keys inside the adapter. Never change CPU/timing fields
or ROM opcodes. Source: [original core frame loop](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/core.c#L673),
[ARM batching/stepping](https://github.com/mgba-emu/mgba/blob/0.10.5/src/arm/arm.c#L212),
[debugger entry scheduling](https://github.com/mgba-emu/mgba/blob/0.10.5/src/arm/debugger/debugger.c#L284).

Synthetic fixtures compare the original batch model and prototype for identical
instructions/events/cycles/video/input sequence, initially due events, time-limit
batch completion, unchanged8-epoch key cadence and first-stop before another
instruction. They reject missing authority, IRQ/wrong caller/opcode, incorrect
boundary order/count/epoch, stale checkpoints, trailing records, BadEgg/invalid
checksum even if both records match, and persistent mutation in each of all2560
bytes. This is source/model proof plus installed passive-breakpoint capability;
installed CPU stepping and complete game/frame equivalence have not been run.
The generic driver is disconnected from the frozen gameplay host; concrete
live binding/integration and live validation remain parent-reviewed dependencies.

## Preserved evidence and local deliverables

Historical baseline PASS42/17671 and sole candidate STOP103/22 at visual1304
remain unchanged. The candidate failed bytes/CPU were not retained; exact cause
and gameplay equivalence stay unproved. STOP35/107/105 plus new103 are four
distinct blocked approaches. Four baseline/one candidate exclusive claims and
all original strategy/controller histories are intact. No attempt reset or new
input reconstruction occurred. Original legacy inputs remain missing and fresh
inputs do not restore their gate. Candidate visuals, C01 and full-floor gates
remain unverified.

[Local offline evidence](../evidence/floor1/v01/battle/native-boundary/README.md)
contains exact ELF/build/source hashes, capability/model logs and all initial
offline failure diagnoses. These are source/capability fixtures, not runtime
captures. Previous private runtime archives and denied raw records remain
unchanged/separate. No new runtime private archive was needed.

Optional independent deliverable: [derived Donut source master](../art-references/derived-donut-master-20261009/README.md),
ten native PNGs serialized as indexed-pixel text and full16-color palette with
pinned provenance. Two derivations are byte reproducible; rebuilding all ten
PNGs gives identical file bytes, indexed pixels, palette/transparency and RGBA.
It is derived source, not original illustration, new approval or runtime proof.
Integrated assets remain byte unchanged and no image is publicly uploaded.
