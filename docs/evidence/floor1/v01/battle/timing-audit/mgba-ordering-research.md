# mGBA 0.10.5 VBlank and IRQ ordering: offline source audit

Audit input checkpoint: `9a0903ea153d00e200725c34a3cf30196e2a9e88`. This note contains read-only primary-source research, not a game execution or a diagnosis of the missing historical IRQ state. Historical execution counts remain five baseline / three candidate. Source bodies downloaded from the official `0.10.5` tag were hashed; already retained `arm.c`, `gba.c` and `core.c` matched byte-for-byte. No engine or host behavior changed.

## Event ordering

At `_startHdraw` with `vcount` becoming 160, mGBA completes renderer output, starts VBlank DMA, optionally raises VBlank IRQ, runs frame-end callbacks/sync, then increments `video.frameCounter` and sets `earlyExit`. The next video event has already been scheduled. Video-event priority is 8. `frameCounter` measures this event, not completion of the game's VBlank handler or main loop. [Official video.c, lines 55–63 and 140–189](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/video.c#L140).

`GBARaiseIRQ` sets the matching IF bit. `GBATestIRQ` schedules the IRQ event only when `IE & IF` is nonzero, with delay `7 - cyclesLate`; an already scheduled IRQ event is not duplicated. IRQ priority is 0. At delivery, `_triggerIRQ` releases halt, rechecks `IE & IF`, and enters ARM IRQ only if IME is set and CPSR.I is clear. Raising, scheduling and CPU delivery are distinct. The CPSR callback named `GBATestIRQNoDelay` still calls this seven-cycle scheduling routine with zero lateness. [Official gba.c, IRQ initialization and raise/test/delivery](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/gba.c#L128).

IE, IF and IME writes retest IRQ with lateness 1; IF uses write-one-to-clear and IME keeps bit 0. This supplies another possible six-cycle scheduled IRQ delay without proving the captured deadline belonged to IRQ. [Official io.c, lines 571–583](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/io.c#L571).

The timing queue sorts first by timestamp and then ascending priority, preserving insertion order for equal timestamp/priority. `mTimingTick` drains all events due at the current master time; it does not consult `earlyExit`. Thus a punctual VBlank can leave the IRQ event pending seven cycles later, but sufficient lateness can make IRQ delivery occur in the same timing drain, after the video callback has incremented the counter. Other due events can run too. [Official timing.c, scheduling and tick](https://github.com/mgba-emu/mgba/blob/0.10.5/src/core/timing.c#L37).

`GBAProcessEvents` folds relative CPU cycles into timing, zeroes the relative counter, updates the next deadline, then tests `earlyExit`. It clears that flag before returning. CPU blockage/halt can alter the resulting cycle state. Consequently the frame-end return does not universally imply `cycles=0`, seven cycles remaining, or an unserviced IRQ. [Official gba.c, lines 293–340](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/gba.c#L293).

CPU IRQ entry changes privilege to IRQ, saves CPSR, sets the vector/return register, selects ARM mode and sets CPSR.I. It does not itself execute the game's handler. `ARMRun` drains due events and then executes one instruction; `ARMRunLoop` executes an instruction batch until the deadline and then processes events. Calling `ARMRun` on a due event can therefore cross a frame stop before the caller checks it. [Official arm.c, IRQ entry and execution loops](https://github.com/mgba-emu/mgba/blob/0.10.5/src/arm/arm.c#L123).

The original `runFrame` outer guard checks the video counter and elapsed-time bound after each `ARMRunLoop` return. An empty initialized core has a dummy renderer; its frame callback is inert. This permits separately identified synthetic event fixtures, without a ROM, Save or reset. [Official core.c, initialization and frame loop](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/core.c#L186).

## Native wait flag and the two mechanisms

The retained engine's `src/main.c` has distinct operations: `WaitForVBlank` clears `gMain.intrCheck` bit 0 and busy-waits for it; `VBlankIntr` sets that bit near its end, after callback, queued transfers and sound/link work. These stores are native instructions, later than mGBA's video-counter increment and CPU-vector entry. The separately pinned ELF/source audit establishes their actual compiled positions.

These are mechanism hypotheses, not explanations of the actual STOP117:

1. **Delayed boundary with preserved iteration cadence:** the video event ends before Wait entry, but Wait clears the flag before the pending handler's final set. The same VBlank handler satisfies the wait; the next ReadKeys/callback iteration can still occur without waiting an additional VBlank. A boundary can move to the next host video interval while the main-loop iteration opportunities remain intact.
2. **Late clear after serviced VBlank:** the handler has already set the flag before Wait clears it. That clear discards the serviced notification; the loop waits for the next VBlank's handler. This can cost a main-loop update opportunity. A matching screenshot does not exclude the lost opportunity.

A synthetic audit must record callback completion, video event, CPU IRQ entry, native flag set/clear, Wait entry/exit, and the next ReadKeys/callback iteration, together with IE/IF/IME/CPSR, event identity/due time and elapsed cycles. Fixtures should include pending IRQ, same-drain late IRQ, masked IRQ, and late flag clear. Their constructed initial phases explain mechanisms only; they cannot recover the actual baseline cycle phase or failed candidate IRQ/flag state.

The actual diagnostic proves F before expected B4894 and gives next-event deadline 6. It lacks event identity, interrupt-controller state, native wait-flag value and the preceding flag-store history. Neither mechanism is selected by that evidence. No realignment, count waiver, frame exception or remedy follows from this source audit alone.

## Exact source and installed-tool identities

All source files are retained locally under `/workspace/scratch/v01-runtime-binding/source-review/`. Links name the official tag; SHA256 pins the exact bytes actually inspected.

| Official source | Bytes | SHA256 |
| --- | ---: | --- |
| [src/gba/video.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/gba/video.c) | 12307 | `c99391529cce6729400ae199ca9ddb65fec7c0d7f1945d214b8941c61e1e694c` |
| [src/core/timing.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/core/timing.c) | 3699 | `f1290a60ea28cce32ef54c383397b2e2beff852dc02f8d44a69ef78ca7989d51` |
| [src/gba/gba.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/gba/gba.c) | 27870 | `92b0fd214bfa563a1694921661c4413ffd96871cd6162cd762542fb5c2a2c098` |
| [src/gba/io.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/gba/io.c) | 28202 | `bad3cda245d78e2d51669bdb079918537d9fe60c17e78810e216e444ea0149e3` |
| [src/arm/arm.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/arm/arm.c) | 7226 | `16205d016e4d61a1c1f0b53e1fd3035b0720b8cf5f871b511a6f5495b6f6f442` |
| [src/gba/core.c](https://raw.githubusercontent.com/mgba-emu/mgba/0.10.5/src/gba/core.c) | 52545 | `57cc9ac807357a5bf27a5e44aec83e3e0696e7be41bddf26ac4f653aa23fc723` |

Installed container `dcc-party-resource`:

| Path | SHA256 |
| --- | --- |
| `/usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5` | `a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63` |
| `/usr/include/mgba/internal/gba/video.h` | `c1adf164b0f88680c5dbba2742f48a86caa4b7a9564998507d99e8479c42a328` |
| `/usr/include/mgba/internal/arm/arm.h` | `dea6a59d0f8a8cb553cd414b54e1790ff03d5107725830a4222b679f54247715` |

This note does not assert a reproduced build of the installed library from the tag. Installed-library synthetic fixtures must separately establish observed behavior against this source-pinned ordering. The primary tag lookup API was unavailable through the direct network path; exact file hashes, rather than an unverified peeled tag commit, are the source pin.
