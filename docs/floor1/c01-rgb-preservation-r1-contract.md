# C01 local RGB preservation r1

Authority: Kurt's2026-10-10 13:28:29UTC approval, independently reviewed at the
completed704e5950 checkpoint. Sole writer; this is a separately frozen local
preservation operation, never a gameplay/runtime freeze or claim.

Only STOP90 opening2 and STOP104 opening3 `motion-000.rgb` through the respective
terminal chunks015/014 are eligible:16+15 chunks,31,258+28,707 frames,59,965
RGB24 frames at240×160,6,907,968,000 exact original bytes. Chunk boundaries,
native rational timing16777216/280896 and all original frame indexes remain
unchanged. Traces, Saves, screenshots, MP4s, incomplete FFV1, old manifests,
failures and historical receipts are protected; no other deletion is authorized.

Private output root: `/workspace/scratch/c01-rgb-preservation-r1-20261010`.
The machine-readable frozen `preservation-contract.json` records every exact
original path, lstat identity, size, SHA256, frame range and per-frame SHA256
ledger; retained old chunk/index hashes must match before execution. It also
pins source commit/scripts, available local compressor/decoders and exact settings.

One standard format/settings only: single-member RFC1952 gzip, GNU gzip1.13,
`gzip -6 -n -c -- ORIGINAL`. No codec search, package install, lossy substitution,
upload, alternative settings or retry. One output per original chunk. The
all-inclusive replacement/audit cap is3,758,096,384 bytes. Logical and allocated
output-root usage, including synthetic tests/contracts/ledgers/logs/receipts,
are bounded;128MiB inside that cap is reserved for code/docs/Git/audit overhead.
Before freezing/executing, current free capacity must cover the entire cap.
Compression reads/writes in64KiB blocks and stops at the first cap/I/O/codec error.
Partial outputs and all remaining originals stay retained; no automatic retry.

Offline synthetic admission covers both decoders, corrupt/truncated/missing/
reordered/extra-frame/trailing streams, chunk/index order, dimensions and cap
failure. Preserve every original until ALL31 replacements pass BOTH complete
reconstruction checks: first streaming Python zlib, then a separate cold Python
process streaming GNU gzip. Each pass independently reopens compressed files,
checks their SHA256 and exact decompressed EOF, compares every decoded frame
byte-for-byte to its original and frozen per-frame hash, and verifies original
chunk hashes/counts/dimensions/order. Decoded output is bounded to a frame/block
working set; no second full decoded recording is allocated or written.

Removal requires both complete receipts bound to the frozen contract and mapping,
unchanged protected evidence/original identities, compressed-file readback, cap
admission and measured all-inclusive savings at least the frozen storage shortage.
Projected post-removal capacity must cover the full10,000,408,128-byte future
runtime reservation, including existing headroom. Only then unlink the exact31
frozen redundant raw paths. Publish a sanitized representation mapping and
verification/accounting receipts; do not rewrite historical manifests or publish
recordings/ROMs/private raw evidence. Independently recheck protected evidence,
replacement hashes and storage after removal/publication.

Local decoding remains standard: `gzip -dc -- motion-NNN.rgb.gz` emits exactly
the original chunk's RGB24 bytes in frame order. Pipe to a consumer rather than
creating an unreserved full decoded copy. The mapping supplies original SHA256,
frame range/count, replacement SHA256 and the retained rational timing/index
identity. This is local preservation, **not independently verified backup**.

Main/all other branches, issue116 and draftPR117/unmerged status remain unchanged.
No game/observer/policy changes, emulator, runtime freeze/claim or new capture.
Opening3/3,cold0/0; medicine preparation stays closed. Freshly measure full
runtime capacity after successful replacement, then checkpoint for review.
Native sampling correction or compiled exclusion proof is still required before
any separately authorized gameplay increment. Historical failures/counts,
Library5+1 unknowncause/zero originalbytes and all Floor1 scope limits remain.
