# V01 offline snapshot validity diagnosis — runtime correction blocked

Parent authority for this increment is offline only: source review, focused
fixtures, host compilation and existing draft PR114 publication. Zero emulator
frames, execution claims, reconstructed inputs, saves or captures were produced.
The four blocked approaches and all original exclusive claims/controllers remain
unchanged. Parent review is the next dependency; no retry or merge is authorised.

The existing `bv_trace` performs full 2560-byte comparisons after `runFrame`.
Its assumption that all data is then in a stable serialized representation is
unproved. The published baseline frame1304 is transient plaintext; its adjacent
frames are encrypted. Candidate STOP103 did not retain its failed bytes or CPU,
so its exact cause and gameplay equivalence remain unproved.

The implemented runtime change is diagnostic only: snapshot raw CPU PC/LR/SP/CPSR
directly from the pinned mGBA ARMCore without calling its CPSR accessor; report
availability and explicitly unresolved serialization authority. At first trace
mismatch, retain complete actual and available expected records in local mode0600
files. These denied buffers remain outside uploads. Safe JSON reports exact
actual/expected byte values only for party offsets32–99 within each member,
flags and the existing scalar/control tail. It redacts party key/header bytes,
all BattleMons bytes and owned-resource bytes. Truncated expected records carry
their actual byte count and never claim a captured expected value. Existing
native phase, controller, sprite/copy and lifecycle diagnostics remain intact.

The separate offline contract reuses the existing read/defer/reentry design:
record every frame/control independently; stop on unknown authority; read no
party buffer proven transient; never accept it or replace a reference; compare
all other bytes exactly; compare the complete 600-byte party at the same-frame
valid reentry. Explicit checkpoints cannot defer. Native encrypted checksums and
BadEgg checks are necessary at valid snapshots, never sufficient CPU authority.
Persistent mutations fail even if checksums are valid. Deferred samples never
increment accepted counts. Synthetic tests supply explicit modeled authority;
they do not establish that any real CPU position qualifies. This contract is
deliberately disconnected from the live host, which still has its original
strict comparisons. It is not an implemented runtime validity correction.

## Exact remaining blocker

A reliable source/build-specific classifier has not been established for an
after-runFrame CPU suspended inside the complete in-place serialization interval,
including nested helper calls and interrupts. The retained candidate has no CPU
position, so offline data cannot reconstruct that missing authority. A broad
callback or function-range predicate, plaintext/checksum recognition, or offset170
exception would not supply it. No such predicate or exception was installed.

Verified scoped STT_FUNC identities and extents from both pinned ELF files are in
the evidence package. The baseline getter alias group starts0806a4f4/1590bytes;
its compiled Decrypt call is0806a546, checksum call0806a54c and Encrypt
call0806ab14. Between these calls its mon pointer is r8 and field argument is
stack-resident. Before decrypt, that same function also handles unencrypted
fields. Encrypt/Decrypt each modify12 words with two separate XOR stores per
word, so partially transformed representations exist. The getter calls other
functions while plaintext exists. SetBoxMonData has its own decrypt/mutate/
checksum/re-encrypt path, including invalid-checksum early return. These reviewed
addresses illustrate the compiled source; they are not runtime allowlist ranges.

mGBA0.10.5 `runFrame` stops on video timing through `ARMRunLoop`, rather than a
game callback boundary. Its CPU PC is a prefetched register; IRQ entry switches
register banks and saves CPSR. PC/LR/SP/CPSR are useful diagnostics, not a proved
completion indicator. Nested calls, banked interrupted context and the native
pointer/field state need a verified classifier before any live deferral.
Sources: [mGBA core](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/core.c#L673),
[ARM stepping and IRQ](https://github.com/mgba-emu/mgba/blob/0.10.5/src/arm/arm.c#L114).

## Audit of the remaining trace fields

| Private trace offsets | Source and serialization finding | This increment |
| --- | --- | --- |
| 0–599 party | pokemon.c3546/3556/3733/4082/4160/4426; header plus in-place secure payload and outer fields | Unresolved native validity; offline contract only |
| 600–951 BattleMons | battle_main.c3408/3416 copies the controller response byte by byte, then changes types/ability/stages/status; Pokemon header layout includes personality/otId | Completion cannot be inferred from a callback; exact runtime comparison retained; diagnostic values redacted |
| 952–1251 flags | event_data.c206/214 modifies individual flag bits; SaveBlock relocation can expose incomplete copies | No encrypted party payload, but whole-region transaction validity not proved; no deferral added |
| 1252–2523 owned resources | load_save.c84–132 relocates SaveBlocks, then rekeys multiple domains before publishing the new key;274–293 performs sequential XOR changes; item.c bag rekey loops | Raw values cannot be assumed stable/canonical during relocation/rekey; existing checkpoint logical comparison retained; no speculative region waiver; all diagnostic values redacted |
| 2524–2532 native battle scalars/hardware keys | Independent native scalar updates, not a serialized BoxPokemon payload | Every frame stays exact; never defer controls |
| 2533–2548 canonical controller IDs | Verified ELF identities; pointer assignments/controller dispatch | Exact every frame; existing ambiguity/unresolved failures retained |
| 2549–2559 zero padding | Host-owned constants | Exact unchanged |

The audit identifies additional transaction assumptions; it does not prove that
any occurred at the historical failure. No raw-field waiver, byte mask, engine
change, policy change, frame exception, timing/RNG search or new battle occurred.

## Validation and status

The actual observer/native-layout/symbol/lifecycle regression passes, including
safe mismatch values, retained local records and redacted resource diagnostics.
The synthetic contract passes encrypted/plain/partial payloads, unread deferred
pointers, symmetric reference/candidate deferral, complete reentry, persistent
mutation, invalid checksum outside transient, missing/invalid authority and
mandatory complete checkpoints. Full generated host compiles with warnings as
errors against installed mGBA0.10.5. Sole inherited `runFrame` site, no busWrite;
compiled binary was never invoked. Source/host/build hashes and safe logs are in
[snapshot evidence](../evidence/floor1/v01/battle/snapshot-validity/README.md).

Baseline PASS42/17671 and candidate STOP103/22 remain historical observations.
Candidate readiness, moves, action poses, complete budgets and gameplay
equivalence are unverified. Original missing legacy inputs, C01/human pacing and
full-floor gates remain limitations. Existing private Library runtime archives
remain separate and unchanged; no new runtime input requires private retention.
