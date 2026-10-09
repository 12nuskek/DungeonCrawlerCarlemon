# Scoped source, runtime and capture review

Reviewed against PR105/base84cbb196. Historical host/gates/contracts/evidence and
game remain byte-identical. New generator pins historical generated hostSHAa15f,
replaces only its new observer/clock adapter, centralises callback validity before
actual SaveBlock reads and gates legacy telemetry. Frozen routeSHA/cadence matches
failed cold route exactly, with no extra inputs. No game writes/RNG calls.

Source gate references gMain offsets0/4/0x0c and pinned CB1_Overworld/
CB2_Overworld/VBlankCB_Field restoration order. Native copy/rekey happens before
field callbacks restore; no state is read/accepted while invalid. Pure shared
sample code gates reader before access, retains accepted/expected snapshots on
defer/failure, compares full600 native party/count/counter/prescribed flags and
canonical resources on re-entry, preserves narrow source-valid friendship rules.
Unconditional battle/whole-process bound checks surround the one frame site.

4225 focused host cases and fresh warning-as-error compile pass. One actual cold
route132 assertions/6258frames/empty errors/zero battles/unchanged Save. Actual19
deferred frames/two complete re-entry comparisons,4195 valid frame samples/nine
explicit checkpoints separate. Offline13 full snapshot decodes all exact; counter
8→35 via27 strictly timestamped steps, no friendship events. Actual native boot,
resolved-repeat/NO/YES/arrival/final images inspected with assertions.

No original CPU-phase inference, retry or rewritten historical STOP. Prepared
pair acceptance evidence402 assertions is separate from failed cold25. Public
outputs contain no raw contexts/buffers/decoded identities; private whitelist
excludes ROMs/executables/credentials/old denied data. Parent review and remaining
F1-G01e evidence inventory next; unmerged, no CI/full-route/V01/legacy claim.
