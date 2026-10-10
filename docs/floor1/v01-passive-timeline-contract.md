# Cached-pose return and passive native timeline

Parent accepts offline checkpoint ed4039b32c6fd6b04d1bb96475cc8a07081a3e0a
and authorises this one implementation increment: exact tested early cached-pose
return, passive bounded tracing, offline regression checks, game/host compilation,
review and normal publication to existing draft PR114. **No gameplay or merge.**

Apply returns for the cached pose after graphics/id/pose guards and before sprite
position/ownership reads. Changed poses retain all original write-time guards,
four 2048-byte frame-buffer copies and the one original sprite-copy request.
No art, mechanics, route, controller, strategy, RNG or timing search changes.

The host observes source/ELF-pinned ReadKeys, callback dispatch/resume, Wait
entry/clear/exit, native VBlank flag stores, copy processing and IRQ-dispatch
entry. Dynamic callback entries require the native caller LR and Thumb SYSTEM
context. Records retain next/raw PC, LR, CPSR/modes, emulated cycles/time,
controller IE/IF/IME, flags, video/input/iteration counters, queue-root identity,
deadline/priority, pending IRQ deadline/priority and queued copy descriptors.
OTHER events remain OTHER. SYSTEM alone is not main-loop authority.

Before/after event-drain records observe video increments **after the entire
original drain**; they do not pinpoint an increment within that drain. No callback
is replaced, instruction added, event rescheduled, CPU field written, key set,
acceptance comparator changed or typed stream realigned. Callback timing comes
from entry/resume emulated timestamps; wall-clock logging time is not game time.

Records use a distinct private mode0600/O_EXCL sidecar: 4096 buffered records,
1,000,000 total records, 64 event-queue nodes, 64 copy requests, 184-byte records
plus a 16-byte versioned header. File writes occur outside instruction/event
dispatch. Invalid/missing pins, opcode/mode mismatch, overflow/cyclic queue,
capacity exhaustion and I/O failure stop with119. The adapter's optional failure
query stops a sidecar failure before another instruction or due event. It does
not dispatch work; positive execution ordering is unchanged. An existing strict
117 remains the first failure even if its sidecar retention also fails119.

Offline fixtures may execute installed interpreter/timing mechanisms with
synthetic instructions/data and retained native Wait bytes; they load no game
ROM/Save, perform no reset, execute no route or battle and claim no gameplay
acceptance. Runtime binary data/key-bearing material, full symbols, ROMs,
executables and Saves remain outside Git/uploads. Synthetic trace hashes do
not describe actual gameplay traces.

Historical totals remain **five baseline/three candidate executions**. Preserve
all historical STOPs, all three strategy failures, controllers, captures and
evidence. Historical missing legacy inputs and timing/cycle/IRQ/flag history
remain missing. The optimization is not a proven remedy for the actual F-before-B
failure. No acceptance is transferred from old or reconstructed inputs.

Next dependency is parent review of the frozen candidate/host and these offline
proofs. Only after new review/explicit execution authority may a proposed pair
start: one fresh instrumented original baseline, then one matching candidate
only after complete baseline PASS, unchanged fixed route/policy/inputs and
30,000 battle/36,000 visual bounds. First divergence stops with no dependent
execution, retry, post-stop stepping, count waiver or realignment. **This
increment does not prepare, claim or execute that pair.** Original legacy,
C01, full action/victory/cleanup/equivalence, human pacing and full-floor gates
remain pending. Nine-district Floor1 accepted scope and all earlier history stay
intact; no expansion, platform/protection change or public ROM release.
