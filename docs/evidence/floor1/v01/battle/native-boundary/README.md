# Local offline native-boundary prototype

Publication clarification — 2026-10-09: routine source/documentation/art Git blobs are authorised and the original offline checkpoint0d9e93f5 is published through existing draft PR114. The local-only wording below records its initial offline authority, superseded for this publication only. ROMs/playable releases/secrets/private raw diagnostics remain excluded; runtime binding and gameplay remain unstarted. Offline source, tests and derived pixels are unchanged. See docs/evidence/floor1/v01/battle/native-boundary/publication.json.

Proven offline: both exact ELFs' WaitForVBlank entry/direct caller/opcode and call
order; installed mGBA passive hardware breakpoint capability without CPU-state
change; synthetic original-loop/frame/input neutrality, authority/order/count/
checkpoint/full-state/persistent-mutation negatives. Prototypes compile with
warnings as errors. No ROM/Save/reset/CPU instruction/gameplay/frame/claim.

[Contract and source/interrupt review](../../../../../floor1/v01-native-boundary-prototype-contract.md).
`before-boundary.json`/`after-boundary.json` pin verified scoped function extents
and compiled hashes. `result.json` pins installed library and compiled fixture
identities. Capability and model logs are actual offline tool output.
`offline-validation-history.json` preserves initial compile, default-breakpoint
scheduling, fixture cleanup and palette-CRLF diagnoses separately from gameplay.

Runtime binding/integration is NOT enabled and game/frame equivalence is
UNVERIFIED. Existing host/route/engine/inputs/graphics/lifecycle checks stay
unchanged. Corrected boundary records would need a separately authorised fresh
reference; old raw-video traces cannot be reclassified as boundary evidence.

Preserved: STOP35/107/105/103; baseline PASS42/17671; candidate STOP103/22 before
readiness/moves/poses and missing failed bytes/CPU; all original strategy/
controller records; exclusive counts4 baseline/1 candidate. No retry/reset.
Original legacy/C01/full-floor limitations remain.

Local derived Donut master:10 native sources,12 reproducible definition files,
all10 PNG/pixel/palette/transparency/RGBA roundtrips byte exact. No integrated
asset changes or new approval/runtime claim. No public upload, Git push or PR
mutation in this increment. Existing remote draft PR114 remains a86ceca9.
Parent review of this local prototype/source package is the next dependency.
