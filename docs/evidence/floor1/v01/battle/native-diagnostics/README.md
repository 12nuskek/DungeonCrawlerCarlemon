# STOP117 retention implemented and tested offline; unmerged

This increment adds first-failure diagnostics to every original STOP117 branch
and all host exit paths that can expose them. It changes no game/route/policy,
comparison, input cadence or emulated timing. Full host compiled and never
invoked; zero ROMs/Saves loaded, zero gameplay executions/new claims.

Host SHA256 `d7bf57cadb8d4a78ac217b62e3c4a6e855424f2cbd6027e0131d5b676e170057`.
Compile-only binary SHA256
`1efcd983ab92e90060ec1135a5a2b977c70d3a9582013896dd2160051a3acc18`.
Pinned mGBA library `a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`.
Source/file/build/fixture identities are in `result.json`; binaries/ROMs/Saves
and exact private fixture diagnostics are excluded from publication.

| Offline evidence | Result |
| --- | --- |
| STOP117 origin and emitted-schema fixtures |193 first-failure/private-safe JSON cases across all10 origins. |
| Typed B/F/E metadata |87 independent byte mutations, every byte of every kind. |
| Installed hardware boundary entry |29 independent metadata mutations, retained PC080008ae/LR080004bf; no entry instruction or accepted snapshot. |
| Short metadata reads |All0..28 lengths,58 EOF/EIO cases; earlier prefix mismatch, unavailable stream position, error/write/end paths. |
| Guard failures |Wrong ordinal/video/input; actual installed due-event changed keys; four frame-count and four finish-count cases. |
| First failure |Immutable diagnostic, stream position, full CPU/event timing and sequence across subsequent sample/frame/finish/observe/fail/retention calls. |
| Privacy and retention |Exact private headers/keys, safe decoded non-key projection, mode0600, exclusive create/no overwrite, truthful failure flags. |
| Installed interpreter regression |12 arithmetic/BX/mode/IRQ/due cases, eight fixed input frames, original timeout/event/frame parity. |
| Production complete snapshot reader |All2560 byte mutations, native checksum/BadEgg, ordering/count/end/zero/stale/missing/short negatives stay strict; full-reader installed variant passes. |

Run only inside the pinned environment:

```sh
python3 scripts/test-f1-v01-native-diagnostics.py --output /workspace/scratch/unique-offline-diagnostics-output
```

`result.json`, `diagnostic-fixture.log`, `interpreter.log` and
`complete-reader.log` record actual offline execution. Empty build logs mean
both full host and fixture compilation completed with `-Wall -Wextra -Werror`.
`source-review.json` verifies unchanged native authority/event/instruction
functions, complete snapshot/visual lifecycle observers, comparisons and fixed
route/controller; one driver and13 original setKeys sites.
`preservation.json` verifies216 unchanged historical source/art/evidence files,
the two authorised host/runtime replacements with old sources preserved in
execution commitf3ceae89, all25 latest actual evidence files, five identical
ordinary Save copies030b, both ROM/ELF builds and engine32199a3.

Exact headers and key values will be retained privately on a future separately
authorised failure. Typed guard projections, matching headers and absent metadata
are explicitly identified; offset29 means no differing header byte. No reference
bytes are fabricated when no read occurred. Full raw headers/keys/trailer are
omitted from the safe projection. No actual new diagnostic was produced for
the historical candidate STOP117.

[Contract](../../../../../floor1/v01-native-diagnostics-contract.md) and
[unchanged actual pair](../native-boundary-validation/README.md).
The actual failed header/count/full snapshot remain missing; alignment remains
inference. Partial WEAKEN/warning-through-BRACE/recovery/HUD review is accepted;
the narrower Warden warning silhouette needs later judgment. STRIKE/SPARK/SLAM,
victory/cleanup/field/rewards and complete candidate equivalence remain unverified.
STOP35/107/105/103/117 and all five baseline/two candidate histories/inputs/passes
are preserved. Original legacy inputs remain missing; C01/human pacing/full-floor
limits are unchanged. Existing draft PR114, unmerged; parent offline review next,
with live execution and merge paused.
