# Frozen cold-only phase correction

[Separate committed contract](../../../../floor1/g01e-prepared-cold-phase-contract.md),
[frozen host/source/game/input/route identities](frozen-identity.json),
[4225 focused host cases (2872+1353)](host-cases.log),
[normal input native-sector/full-state validation](native-save-validation.json).

Source commit514187f6 implements separate native gate/clock; fresh warning-as-error
host compile exit0, no compile failures. Prior host/failed cold claim/STOP/gates/
contracts/evidence and game unchanged. Historical generated host is pinned; new
route is byte-identical to the180-line failed cold route, b3e46b…72427. No ordinary
input or cadence change; no battle/Save/exploratory path. Actual normal savedbaaf…ccd7.

Native callback1/2/VBlank gate precedes actual SaveBlock-backed map/counter/flags/
resource reads. Transition samples perform no snapshot read/accept/update;
expected state retained. Re-entry validates full600 party/native exact walking,
count/counter/flags/canonical resources, then accepts. No broad tolerance or
original CPU-phase inference. Zero-battle and24000 limit active through boot/
transitions. Dedicated clock increments inside the one frame site; distinct valid
frame/deferred/checkpoint/re-entry counts. Complete exact clock asserted at end.

Review before execution: pure tests use ordinary independent fixtures/spies;
deferred snapshots/expectations unchanged, stable corruption fails,0/+1 walking
remains exact, rekey source-width validated, phase-independent battle/batch clock/
bounds tested. No game writes/RNG calls. Old unused engine-observer commands are
unreachable under this frozen route; battle/measure/inventory commands rejected,
telemetry behind the same gate. Only normal Save expectations are private inputs.
No emulator acceptance yet at this source checkpoint. One exclusive claim follows.
