# V01 bounded diagnostic retention and retained-reference binding

2026-10-09. Parent accepts publication268fa9a8 capacity arithmetic and offline validation, but its28672406296-byte full-history trace envelope exceeds available storage. This increment authorises storage/binding implementation, offline file/counter/retained-record tests, compilation and normal publication to existing draftPR114 only. No game process, CPU/event execution, ROM/Save load, baseline restart, candidate preparation/claim/execution, Library retry or merge. Six baseline and three candidate executions remain historical and unchanged.

Source checkpoint: `214a10a214bda76422bf59aaa71df9c42766360e` on `task/floor1-v01-battle`, descended normally from268fa9a8. Game source remains2feadf56764c0d89c3dde9ef4622ea6d43b32f69, enginebaac7fee52e2133fa6192799ef3851f629f188d7, ROMa022b2a5030214f8cbeb0621af47e6cb9a47208424aa86f56b67862b5028f8d4, ELFf31a5a8b2cb1602df378a7ca66b3cee8bbcea86de000536ab6f55acd727d0218. No engine, route, gameplay policy or art change here.

## Observation and retention

All passive observations and strict typed B/F/E metadata, count, ordinal, epoch, ordinary input and complete2560-byte comparisons remain enabled. A new detail anchor is accepted only after the existing native metadata/party-checksum/full-state comparison succeeds. The matching BEFORE/Wait record is retained with every following generated record through the current frame. A failed comparison cannot advance the anchor. Hashing, truncation and file writes run at the existing outside-CPU frame flush; the fixed4096-record buffer remains753664 bytes. The additional storage context is88 bytes; SHA work uses bounded stack arrays, with no growing trace allocation.

The summary file retains every frame/terminal chunk's observation count, accepted-boundary count, cumulative count, latest anchor, retained count/window, first terminal reason and final raw PC/CPSR. Each184-byte summary includes previous chain, SHA256 of **all** that chunk's generated184-byte records (including records subsequently discarded), and SHA256(previous chain +88 metadata bytes +frame digest). This proves continuity against the original retained input in offline tests. It does **not** reconstruct discarded history or establish lossless full-history retention.

Detail uses BVTD0003; summaries use BVTS0003; both have32-byte headers binding46 words,4096 records/chunk,2046 startup chunks and250 active chunks. The older BVTIME01/02 data and parsers stay available and unchanged. Only a newly created exclusive recorder file is truncated; prior outputs and history are never rewritten.

## Window derivation and failure

The exact original complete PASS reference contains15379 B records,15627 F records,248 total zero-boundary frames, a maximum consecutive zero run of12, no initial zero run and real typed E. Therefore248+boundary/current headroom gives a conservative250 active-chunk window, above the actual maximum consecutive requirement. There are2044 previsual boot frame calls with **no accepted strict boundary**. They require2044+current/terminal headroom=2046 startup chunks, preserving the complete boot prefix until the first accepted boundary. A188MB whole-run promise would be incorrect.

| Allocation | Maximum bytes |
| --- | ---: |
| Startup detail (32 +2046 ×4096 ×184) | 1,541,996,576 |
| Active detail (32 +250 ×4096 ×184) | 188,416,032 |
| Full-run summaries (32 +38045 ×184) | 7,000,312 |

The startup file becomes the active suffix at the first accepted boundary; these detail maxima are alternative phases, not simultaneous files.250 chunks without a new accepted boundary,2046 startup chunks without an anchor,4096-record per-frame overflow,38044 frame-call exhaustion, invalid anchor/ordinal, short writes, flush/truncate/close failure or summary overflow fail closed119 before further CPU execution. Existing strict first failures retain precedence. First STOP/FINISH freezes summaries; subsequent flushes cannot add observations or replace the first reason. This assumption may stop a future candidate; it never authorises truncating validation or proceeding after failure.

## Combined storage preflight

The source-derived conservative bound includes startup detail, summaries,36457 native240×160 PPM files (36000 numbered plus457 helper files), helper PNG exports, the40269443-byte reference copy,1,024,051,072 bytes of bounded textual logging,13,488,067 working bytes, fixed metadata and4096-byte filesystem rounding for every independent capture/export file. The helper count covers18 poses,40 cues,128 motion captures,256 native uint8 turn values and15 static/route filenames. PNG allowance is twice the RGB PPM size; controlled inputs carry no extra metadata. Logging uses bounded formats/controlled strings, four battlers per frame and a conservative64-slot multiplier per pinned route command. Pinned original/optimized ELF symbol/JSON output sizes are measured read-only without preparing a trial.

Required available bytes: **7,064,285,184**. The final offline validation observed7,192,756,224 free bytes and passed; this is a point-in-time check, not a future storage guarantee. The runner checks before preparation and again immediately before Save copy/claim/game process. It credits only bounded already allocated regular prepared files, rejects invalid credit, and leaves old evidence untouched. Insufficient space stops before execution. No preallocation, old-evidence deletion, disk/platform change, billing or usage-meter login is authorised.

## Explicit retained original oracle

`--retained-reference` is a separately reviewable **candidate-only** opt-in. Without it, the existing fresh-baseline PASS gate remains. The opt-in rejects `--case before` before output creation. It requires the exact historical original executionf3ceae890dbf9821ffade08c3cba4de40af31aa9, original game4938927da512543ca9aeea9527c103c84955e632/engine76001ee128785714b7c15aef6d9c95630587d0a9, its ROM/ELF/host/binary/library/symbols/verified functions/native-boundary pins, exact Save/route/fixture bytes, original identity/claim/summary/replay hashes, published identity/summary equality and the complete raw typed stream.

The raw reference must be40269443 bytes with SHA256 `849a1585f27b0de4a0e68e4036d88986847a9ece3f72dc8377dfec4214fae13d`. Revalidation streams all snapshots, checks all six encrypted party checksums/BadEgg flags, exact ordinary input epochs, full metadata/state/control hashes and typed E at the last accepted B, with strict EOF. The accepted typed-finish hash is `6ee2fb2d533d763cd4f3dd4da9a29a2833139ef1810a935b236947c1d20b1e1a`. Detailed pins are in the safe evidence reference-verification.json. A summary alone, partial newer baseline or reconstructed oracle is rejected. Missing original bytes stop dependent work.

The newer failed baseline4e295249 contributes matching partial diagnostics only through13956. Its13721 B/13956 F records have no E. It remains STOP119/27 assertions, never PASS. Neither binding nor offline replay transfers historical acceptance to the new host/candidate or restores unavailable original legacy inputs.

## Results and next dependency

Offline PASS2968 writer/rotation/I/O/first-stop/comparison cases,425 format/provenance/preflight cases and352 legacy capacity cases. Every one of2560 state bytes and29 metadata bytes is independently mutated and rejected before anchoring. Retained actual999932 observations produce16001 complete summaries with all frame payload hashes/chain counts equal to the original; the18-record suffix byte-matches the original from its last accepted boundary. No CPU instructions/events or new emulator captures occurred. Host source1647352d92b3fa6f0135cf80f4c48df1c2a8a3818b711fd94651390a6334977f; production observer.c binarya17ea5134e700efd77552d9a279fd4d6dd94294d443683b8e9fbfe142361ccbd, compiled only.

Parent review of this storage contract and exact frozen host is next. A later separately authorised ONE candidate may use the explicit retained complete reference only after fresh integrity/storage checks; no baseline restart is prescribed. Stop first divergence/failure with no retry, timing/RNG search, realignment, assertion waiver or policy change. Candidate preparation/execution remains unauthorised in this increment. The historical F-before-B cause/remedy, complete candidate action/motion/victory/cleanup/equivalence/reward/Save, legacy/C01, human pacing and full-floor gates remain unresolved. Five failed/cancelled Library transfers are not retried or bypassed; no durable fresh-backup claim. Nine-district Floor1/Book1 opening scope and all historical failures/controllers/three strategy failures remain intact.
