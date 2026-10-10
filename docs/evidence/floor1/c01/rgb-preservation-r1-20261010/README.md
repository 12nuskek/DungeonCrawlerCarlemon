# C01 recordings preserved losslessly; native sampling remains blocked

Completed the separately frozen local preservation operation authorized by Kurt
at2026-10-10 13:28:29UTC. Audit start704e5950760551f53be5453515b39914187def42;
tested/frozen tooling `e5073a511b62041f4356932c7fcc3c355cc3ff76`;
main/base `b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`. DraftPR117 review only.

Exactly31 redundant raw RGB files were replaced **after both complete verification
passes and measured cap/savings admission**. Original pixel bytes, every frame,
chunk boundaries, native timing and indexes remain available through the new
local representations. No game/observer/policy changes, emulator, new runtime
freeze/claim/process, actual Save/cold or new screenshot/motion occurred.
Screenshots N/A for this nonvisual byte-preservation increment. Existing actual
[STOP90 evidence](../uninterrupted-unprepared-r2-20261010/README.md) and
[STOP104 evidence](../guard-choice-r1-20261010/README.md) remain unchanged.

| Retained recording | Frames / chunks | Original RGB bytes | Gzip bytes |
| --- | ---: | ---: | ---: |
| STOP90 opening2, helper978cbf03 | 31,258 / 16 | 3,600,921,600 | 118,854,998 |
| STOP104 opening3, helper44180157 | 28,707 / 15 | 3,307,046,400 | 97,327,154 |
| Total | 59,965 / 31 | 6,907,968,000 | 216,182,152 |

Recording-only logical savings: **6,691,785,848 bytes**. This excludes audit
overhead; the complete audit/cap ledger below includes that overhead.

## Frozen contract and actual verification

[Source contract](../../../../floor1/c01-rgb-preservation-r1-contract.md), private
frozen contract SHA256
`ca0bfd555ee52349c9a470222c62639283dc01af7b34c410902f34fd95f27975`.
Every original path/lstat identity/size/hash/frame range was reconciled with its
historical retention manifest before compression. All31 original hashes and
both full frame indexes matched. The frozen contract includes59965 per-frame
SHA256 digests in31 ledgers and139 protected non-RGB evidence files.

One format/settings: locally available **GNU gzip1.13, `gzip -6 -n -c`**, standard
single-member RFC1952 gzip containing the exact RGB24 bytes. No package install,
codec/settings search, lossy substitution, upload or actual-operation retry.
Fixed source, compressor/Python executable hashes and zlib version are recorded
in the [sanitized receipt](preservation-receipt.json).

- First pass: bounded Python zlib streaming decode, all31 chunks/all59965 frames.
- Second pass: separate cold Python process, independent GNU gzip streaming
  decode, freshly reopening and rehashing all completed compressed files.
- Both passes compare EVERY decoded frame byte-for-byte with its still-retained
  original and frozen frame hash; verify original chunk hashes, frame counts,
  dimensions/order and exact original/ledger/decompressed EOF. No second full
  decoded recording is allocated or written. Decoder output blocks are64KiB;
  frame comparison uses a bounded working set.
- Both complete receipts are bound to the frozen contract/mapping. Only afterward
  did the removal barrier recheck protected evidence/original identities,
  replacement hashes, cap and measured savings. Exactly the frozen31 raw paths
  were unlinked. All139 protected files were checked unchanged again afterward.
  Replacement files were fsynced by the compressor and directories synchronized
  at completion. Fresh compressed-file/ledger readback passed.

Private receipt SHA256:

| Receipt | SHA256 |
| --- | --- |
| Representation mapping | `3fbe0ccd8834c96c992a393b57fca85156b6d7007b6ecfa049d954749b3c9aee` |
| Pass1 zlib | `0e790913662af9ed24a1e816b522a1124f745b45bb6f062c76accbf803a2bf8a` |
| Pass2 independent gzip | `91fc5b58a31c8e746c3a1ea0767a67ad05da46ed948a982236afb41b4292616d` |
| Removal admission | `eea535b95ab51dd875032fe60a2aba5d5fae4e65abcb2a1d339f0a4b94dfb097` |
| Completed preservation | `652a2ac2638791b9d55ef686260047f23334994e7d65626637592cae011d12ed` |

Offline verifier admission passed36 positive/negative cases covering corrupt CRC,
truncated/missing/reordered/extra/trailing streams, chunk/index order, dimensions,
cap failure and incomplete/misbound deletion receipts. One initial synthetic
middle-bit corruption fixture still reconstructed identical bytes; that fixture
was diagnosed, retained and corrected to guaranteed CRC corruption **before
freeze or original compression**. No assertion was relaxed. Both fixture sets
and the preparation failure receipt remain private; actual operation failures0,
operations1, automatic retries0.

## Representation access and unchanged history

[Public representation mapping](representation-mapping.json) supplies every
original chunk hash, frame range/count, replacement size/hash and ledger hash.
The exact original absolute paths and file identities remain in the private
contract/mapping. Output root:
`/workspace/scratch/c01-rgb-preservation-r1-20261010`.
`DECODING.txt`, both verification receipts, all31 gzip chunks and31 frame ledgers
are retained there. Standard local access, without creating a full decoded copy:

```sh
gzip -dc -- STOP90/motion-000.rgb.gz | sha256sum
```

Run from the output root; compare with that row's original `raw_SHA256`. Feed
decoded chunks to a streaming RGB24 consumer in mapping order:240×160,
115200bytes/frame, native rational timing16777216/280896. Both original indexes
retain all four native columns and their exact bytes/hash; no retiming or index
rewrite. Traces, Saves, screenshots, MP4s, incomplete FFV1, failures, manifests
and historical receipts remain unchanged. Historical raw paths now resolve
through this separate representation mapping; old evidence is never rewritten.

This is **local preservation, not independently verified backup**. No recordings,
compressed data, ROMs or private raw payloads were published. Library uploads
remain unapproved; five prior upload failures plus one supported existing-backup
download failure/unknown cause/zero original bytes recovered remain unchanged.
The original runtime oracle and legacy inputs are still missing.

## Byte accounting and remaining gate

[Fresh capacity ledger](runtime-capacity.json): private output logical218,744,315
bytes, allocated218,992,640; conservative inclusive footprint **353,210,368 bytes**
including128MiB reserved for code/docs/Git/audit overhead, below the unchanged
**3,758,096,384-byte cap**. All98 newly indexed private files/218,729,208 bytes
passed SHA256 readback; manifest
`a7aef855c4e60a5ea861d93a8c7e029bf4fae97d9eb8a1f9e6f64ec32b0e55b7`.
The index excludes its own manifest, which accounts for the logical-byte difference.

Measured free **13,808,525,312 bytes** covers the full future reservation
**10,000,408,128 bytes**: opening8,837,820,160, conditional cold894,152,512,
headroom268,435,456. Surplus after the complete reservation3,808,117,184 bytes.
Publication consumes additional small metadata bytes; final report freshly
measures capacity again. Storage capacity is available, but **native sampling
remains unadmitted and the medicine preparation gate stays closed**.

Next dependency: review a narrowly bound source-correct PC/task/full-byte
transaction correction or compiled observation exclusion proof. A later gameplay
increment requires separate authorization/freeze and fresh complete identity/
storage admission. No runtime is launched here. Opening3/3,cold0/0 unchanged.

Main/all69 other heads and issue116 preserved; no merge/new writer/schedule.
V01 six baseline/four candidate and STOP117 requestedvisual8536 beforeB8402,
later accepted1/1,ordinary recovery5,C01a actual5/3/1 andclaims6/3/1,all C01
STOP82/STOP90/STOP104 and archives remain. Engine/game4a92a9de/tree0fedd142,
ROM79a0ed76/ELF7895d09e and observer56c5f719/0a9ed4fb are unchanged; no rebuild.
C01/G02/prepared/human/full-floor gates stay open; accepted nine-district Floor1
plan/T1449/8–12× area/widths/permanent duo/recovery/stock Emerald-GBA/Book1 ceiling
remain unchanged.
