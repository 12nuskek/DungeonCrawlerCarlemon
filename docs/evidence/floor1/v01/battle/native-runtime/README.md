# Concrete host binding; installed synthetic interpreter evidence

Implemented and compile-tested; actual installed synthetic interpreter fixtures pass. **No game execution or new baseline/candidate pair; unmerged draft PR114. Game equivalence remains unverified.** Parent source/evidence review is the next dependency before separately authorised fresh gameplay.

[Contract](../../../../../floor1/v01-native-boundary-runtime-contract.md) describes exact native authority, original frame/event batch ordering, complete snapshot stream and preserved gates. Core implementation is `scripts/floor1/v01-native-boundary-runtime.h`, bound at the sole generated host driver and to the extracted original complete2560-byte snapshot reader.

| Evidence | Claim |
| --- | --- |
| `result.json`, `host-build.log` | Full concrete host compiled with Werror; generated host/binary/source identities; gameplay host never invoked. |
| `interpreter.log` | Actual installed ARMRunLoop versus guarded ARMRun, GBA event/timing and passive hardware APIs with synthetic instructions/events. |
| `complete-reader.log` | Same installed fixtures with production complete snapshot reader/native bus APIs and synthetic EWRAM; generated host main never invoked. |
| `before-boundary.json`, `after-boundary.json` | Exact pinned ELF authority; unique AgbMain call sequence/WaitForVBlank entry/opcode/LR. |
| `observer-regression-*` | Preserved graphics/lifecycle/ABI/symbol/diagnostic memory fixtures; no emulator game execution. |
| `prior-model-regression-*` | Prior capability probe/generic scheduler models; separate from actual interpreter instructions. Its historical harness result says not integrated: that describes the old model harness, not this concrete binding. |
| `development-history.json` | Two retained development fixture failures and diagnoses; never counted as gameplay or substituted for historical failures. |
| `installed-source-review.json` | mGBA0.10.5 source/installed-library receipts and reviewed interpreter/event semantics. |
| `preservation.json` | All142 prior battle evidence/Donut source/route/policy/accepted-plan files byte-exact, engine/builds/ordinary Saves unchanged; exclusive counts4 baselines/1 candidate and all four failures retained. |
| `review.json` | Scoped diff and negative-case review, public-material exclusions and remaining limits. |
| `artifact-index.json` | SHA256 for every public evidence artifact except the index itself. |

Each interpreter variant passes12 mode/event/IRQ combinations, exact due-frame stop, eight fixed input/frame epochs and original long-batch timeout parity. Actual stream tests verify four complete boundaries and all29 metadata/2560 snapshot byte corruptions, missing/duplicate/reordered boundaries, zero/missing/corrupt frame counts, stale checkpoints, checksum/BadEgg, truncation, trailing data, foreign SYSTEM caller and sticky first STOP. These are synthetic instruction executions in empty GBA cores, with synthetic frame-counter events; no ROM/Save/reset/gameplay capture/execution claim occurs.

Prior original candidate STOP103 still has missing actual failed values/CPU. Its exact cause and visual/game equivalence are not retrospectively proved. STOP35/107/105/103 and all strategy/controller records remain unchanged. Original legacy inputs remain missing; fresh ordinary Saves do not substitute. C01, human pacing and full-floor limits remain.

Public package contains safe source/docs/logs/receipts only. ROMs, ELFs, executables, saves, raw trace/VRAM/key buffers and private fixture diagnostics remain outside Git. No new private runtime archive or recovered-input claim is made in this increment; existing Library archives remain separate and unchanged.
