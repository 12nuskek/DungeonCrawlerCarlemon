# Retained export failure and proposed bounded export

Read-only diagnosis from the retained encoder logs, export STOP receipt, file
sizes, frame index and existing capture verification. No export retry, probing
decode of the incomplete file, encoder, emulator or cleanup is performed here.

The FFV1 level3/bgr0 output stopped nonzero at exactly503,316,480 bytes (480 MiB),
the imposed per-file RLIMIT_FSIZE. Both encoder stderr logs are empty; the parent
export driver asserted the FFV1 exit and ended1. The exact encoder return code/
signal and encoded frame count were not retained. The exact-cap file and imposed
limit support a cap explanation; they do not prove SIGXFSZ, codec fault, disk
exhaustion, or which frame was last encoded. The incomplete file is preserved.

The complete source is31,258 RGB24 frames ×115,200 bytes =3,600,921,600 bytes,
16 original chunks, native240×160 at16777216/280896 fps (equivalent262144/4389).
A whole-stream480 MiB file required average output ≤16,102.01 bytes per frame,
about14% of raw RGB; no such compression guarantee was admitted. The earlier
three-frame synthetic codec check did not validate this long-output capacity.
The actual failure does not invalidate the retained raw frames or12 exact PNGs.
The existing MP4 was independently probed complete31,258 frames/523.343513s/
3,707,653 bytes; it is lossy review material, not lossless replacement evidence.
No complete actual FFV1 decode/RGB roundtrip is claimed.

## Deterministic plan for review, not execution authority

Use a **new** export root, outside both immutable r2 roots and current512 MiB
export budget. Export sequential fixed1,000-frame chunks with no omitted,
duplicated, interpolated or retimed frames:1–1000,1001–2000,…,31001–31258.
There are32 slots,31 full chunks and one258-frame chunk. Read each range from
the original indexed raw chunks; do not create a second full raw concatenation.
Preserve every original raw byte, incomplete FFV1, MP4 and prior receipt.

Freeze encoder/decoder executable hashes, version/build configuration, exact
arguments, source/index identities privately, range manifest, new output root,
exclusive export claim, capacity and first-failure stop before a later launch.
Use FFV1 level3/bgr0/native FPS; decode each new successful container to RGB24
through a bounded pipe. The reader compares every decoded frame to its original
indexed RGB frame and checks width/height, exact count/range, order, native rational
time base and final EOF. Timestamp quantization from Matroska must be explicitly
accounted for, not mislabelled as changed native FPS. No concatenated decode
artifact or duplicate `.part`/final copy: a same-filesystem rename is permitted
only after complete verification. A pending or failed slot never becomes verified.

| Capacity reservation | Retained31,258-frame export | Potential100,000-frame run/export |
| --- | --- | --- |
| Raw RGB (preserved separately) | 3,600,921,600 bytes already retained | 11,520,000,000 bytes |
| Fixed maximum output slots | 32 | 100 |
| Hard per-file FFV1 slot cap | 268,435,456 bytes (256 MiB) | same |
| All slot caps combined | 8,589,934,592 bytes | 26,843,545,600 bytes |
| Additional fixed reserve for logs/index/manifest/MP4/synthetic admission | 268,435,456 bytes | same |
| New export reservation | **8,858,370,048 bytes** | **27,111,981,056 bytes** |

This is a worst-case **storage** bound because every slot has a hard cap and no
compression ratio is assumed. It is not a mathematical FFV1 packet-size or
successful-compression guarantee. A slot may exceed its cap: then stop once,
retain its partial output and all raw frames, record exact exit/signal/stderr,
and do not split/re-encode/retry automatically. Full raw remains the complete
lossless authority even if a container export fails. All-file capacity is reserved
before starting; free space is checked again between chunks without changing
parameters or launching parallel encoders. No extra private backup is implied.

Analysis-time free space was10,527,772,672 bytes, exceeding the retained export
reservation by1,669,402,624 bytes. This is a read-only measurement, not a durable
reservation or permission to export; recheck before any later launch. The current
r2 retained4,169,008,742 bytes plus the new export ceiling would total
13,027,378,790 bytes, without counting other retained workspace histories.
A new100,000-frame capture plus these export slots requires at least
38,631,981,056 bytes **before** trace/CPU/capture/Save/cold/other history overhead.
The current33,770,192,896-byte filesystem cannot satisfy that combined plan.
Keep export as a separately reviewed retained-data operation, or resolve future
capacity explicitly before any new runtime contract. Do not weaken raw coverage
or assume that observed compression savings solve the reservation.

## Offline admission before a later export

The new source-only checks already verify six boundary/range/capacity geometries
(1,999,1000,1001,31258,100000 frames), exact contiguous coverage and arithmetic;
zero encoders are launched. They do not certify codec completion or a decoder.
Before a separately authorized export, admit the complete range reader/verifier
using deterministic synthetic RGB fixtures (solid, alternating/checkerboard and
fixed algebraic high-entropy patterns; no game RNG), native FPS, full and partial
1,000-frame chunks, and a separately bounded synthetic output budget included
in the256 MiB reserve. Verify decoded pixel equality/count/EOF and hard cap handling.
Negative fixtures must reject missing/duplicate/reordered frames, wrong range,
size/dimensions/rational rate, truncated output, decode failure and any pixel change.
The immutable r2 frame index/raw manifest must then pass read-only coverage/hash
checks. Synthetic success is codec/verifier admission, never actual-stream export
acceptance. No actual export occurs until that separate operation is authorized.
