# Route-derived recorder capacity — offline only

**Implemented and compiled; offline checks pass; no gameplay execution or merge.**
Parent accepts the actual STOP119 at publication4c1a2800 as the total recorder
capacity fault and authorises this scoped offline correction. Compiled source:
`6217e6e630f0cd6a23133b9bc762f19ed93ff26a`. Previous outputs and all historical
strategy/controller/failure records remain intact. Counts stay six baselines and
three candidates; the optimized candidate has not been prepared or executed.

## Conservative bound and storage

The pinned route's nine boot steps are720,1,360,1,180,1,180,1,600: exactly2044
frame calls. Other pre-visual commands only inspect state; `ready` executes no
frame. The sole generated frame driver checks `visual.frames >= 36000` before
calling its native frame function, increments after success and stops on first
failure. `visual start` appears once; `visual finish` is followed only by `quit`.
Thus at most38044 frame calls are possible under this exact route/host.

Each frame flushes its fixed4096-record buffer, including its FRAME/STOP marker.
The largest pre-observation reserve is70 (event reserve3 is smaller); the final
FINISH can occur separately after the last frame. The conservative ceiling is:

```text
maximum frame calls = 2044 + 36000 = 38044
total ceiling = 38044 × 4096 + 70 reservation slots + 1 terminal
              = 155828295 records
```

This is derived from route bounds and allocation capacity, not the observed
maximum104 or an extrapolated average. Per-frame overflow, bad pins, queue
limits, strict B/F/E acceptance and fail-closed I/O remain unchanged. The reserve
is checked before the same original observation/instruction; no CPU cadence or
controller change is introduced. The generated host with its entire timeline
header replaced by the previous header reproduces the exact frozen host hash,
so no surrounding host/policy/input code changed; all13 setKeys calls remain.

| Resource | Exact bound |
| --- | ---: |
| Fixed allocated record buffer | 753664 bytes (736 KiB) |
| Record | 46 words / 184 bytes |
| Binary header | 16 bytes |
| Total record ceiling | 155828295 |
| Maximum file envelope | 28672406296 bytes (~26.7 GiB) |

Current free storage at review is7215865856 bytes (~6.72 GiB), below the worst
case file envelope. No worst-case file is preallocated, RAM growth or disk/
platform change occurs. Streaming disk exhaustion still stops119; this bound
does not promise available storage for every possible future trace. The full
ceiling stress test writes to a checked counting sink, not a28.7GB disk file.

## Format and production writer

New header magic is `BVTIME02`, followed by little-endian words46 and derived
limit155828295. Record payload layout/serialization is unchanged. Historical
`BVTIME01` accepts only words46/limit1000000. The bounded streaming decoder
rejects unknown headers, wrong capacity, malformed phase/events, incomplete
records, per-frame/total overflow and records after a real terminal. Complete
EOF without a terminal remains explicitly partial. It does not confer gameplay
equivalence or execution authority.

The existing record serialization/flush loop is factored into a shared buffer
writer so retained actual records can be rewritten offline without a core or
CPU. Production `flush` still collects its same marker, writes complete records,
flushes, stops on first I/O error and preserves prior failure precedence. No
new internal video hook, callback substitution, relaxed comparator or game edit.

## Actual offline evidence

- PASS352 C writer/counter cases: all38044 maximum4096-record frames plus separate
  FINISH, original999932/70 fault under old cap only, old-million neighborhood,
  derived-ceiling neighborhood, UINT_MAX, per-frame overflow, STOP/FINISH at
  exact global limit, every184 short-record length and16 short-header lengths,
  strict117 preceding retention119 and idempotent stopped flush.
- PASS216 bounded parser cases, including rejection past the old million limit
  and successful decoding past it under version2, truncated headers/records,
  per-frame overflow, malformed events and post-terminal bytes.
- All999932 records of the actual retained failed baseline were fed through
  the production writer. Version1 and version2 decoded tuples match exactly;
  all payload bytes match. Source SHA
  `aac0963fde9fbd6237f44dd8082ddca59f6b40627a8b6857a017c82673b8669a`,
  rewritten SHA`c7658e69bab567c852a9304569abf2acad7c1431b967c10c64f3efe542026cbd`.
  Original trace untouched; no invented terminal/capture or extended timeline.
- Generated gameplay host compiles with Wall/Wextra/Werror, never invoked.
  Prior synthetic interpreter fixture compiled only; interpreter regressions
  were not rerun because this increment permits zero CPU execution.

Exact corrected host source SHA256:
`64a924e8ec7130040b822a500f93b4692751b65008e83bb767c2b31a51c841de`.
Compiled binary SHA256:
`6a23c9bf3740f46afb123caf72f8ce588f1fccc13a5c6cfbc42eb913192687ce`.
Pinned mGBA0.10.5 library:
`a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`.
Original game4938927/ROMae1e9d36/ELF2fb481bd and compiled optimized
source2feadf56/ROMa022b2a5/ELFf31a5a8b remain unchanged; exact identities are
preserved in [the prior checkpoint](../passive-validation/README.md).

Reproduction uses the checked-in capacity C fixture (cc/gnu11/O2/Wall/Wextra/
Werror/USE_DEBUGGERS, linked to pinned mGBA), run once for its stress log. Then
`scripts/test-f1-v01-timeline-capacity.py` takes `--output`, the identical compiled
`--fixture`, its `--stress-log` and retained private `--trace`. It recompiles the
fixture to verify reused stress identity, compiles the host, and invokes only
file-replay mode. No gameplay runner is invoked or preparation produced.

## Preservation and next dependency

The retained historical original reference is independently available and
reverified:40269443 bytes, SHA
`849a1585f27b0de4a0e68e4036d88986847a9ece3f72dc8377dfec4214fae13d`,
15379 complete boundaries/15627 F/248 zero-boundary frames and real terminal E.
Its actual summary matches the historical published PASS42 metadata. This is
the old reference's identity, not a new PASS or recovered historical timeline.
The scratch structural probe initially confused B's pre-frame counter with its
next input epoch; source-pinned B/F/E semantics diagnosed it, without reference
edits/realignment. Historical STOP117 cause remains unresolved.

All14076 original PPMs byte-match the verified local archive. The archive, Save,
previous host and all actual captures remain unchanged. No Library tool/transfer
was attempted; the five failed/cancelled transfers were not retried or bypassed.
No durable fresh-backup claim. Raw traces/references/actual keys/binaries/ROMs/
Saves remain private/local and excluded from Git/uploads. Only safe source,
aggregate results and documentation are published.

All68 heads/65 PRs reconciled; PR114 remains the only open draft/unmerged PR.
Main/basec6d647a8 and all other branches/history stay intact. Checks/status/runs0
are absence, not CI PASS. Accepted-plan SHA9b3e5d6f and historical status bodies
remain unchanged.

Parent offline review is next. Proposed later validation is **one candidate
against the independently reverified retained complete PASS reference**, with
the failed baseline supplying matching partial timeline evidence only through
requested frame13956. No baseline restart or candidate execution here. Existing
runner's fresh-baseline PASS gate remains unchanged; the proposed retained-
reference contract/binding needs separate review before preparation. Stop
dependent work if the original reference is unavailable; never reconstruct it.
Legacy/C01/full candidate actions/motion/cleanup/reward/Save/equivalence/human
pacing/full-floor gates remain pending; nine-district Floor1/Book1 scope unchanged.

[Current contract](../../../../../floor1/v01-timeline-capacity-contract.md).
