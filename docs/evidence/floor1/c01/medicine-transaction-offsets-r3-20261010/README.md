# C01 r3 outer-function correction — split PASS, checkpoint/idle

Executor responds at2026-10-10 15:59:38UTC. Latest revised inert command exited0;
no active command. Kurt requested checkpoint/idle after the15:51 recovery notice.
Start `fd827ad64309e99c26866ec2e7b9456d25fccd86`; main/base
`b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`. DraftPR117 remains unmerged.

Read-only review identified missing independent coverage of the outer
UpdatePartyToFieldOrder offsets and a false requirement that a copy had already
been sampled before its post-Free completion. Both are corrected narrowly.
The new independent Thumb decoder executes the pinned outer function, memcpy,
Free and FreeInternal instructions. Alloc and GetPartyIdFromBattleSlot are
explicit source-derived fixture primitives; this is not mGBA runtime execution.
All22 admitted outer offsets are exercised:2140 direct checks across both party
orders/recipients,8UI cases and2successive uses.60 completion checks include40
with no previous copy sample or only one real interpreted partial-copy sample,
with unmerged and previous/next-coalesced headers. No intermediate observation
is invented.24,180 normal/IRQ checks and116,746 negatives PASS;32,970 physical
snapshot-byte/metadata corruptions; all26 aligned prefixes for all6 records.

At exact compiled Update+0x46, Free has just returned. PreservedR4=6/R6=100/R5,
R0/LR and four untouched system-stack slots bind the actual freed buffer operand
and both native return addresses. These current sampled bytes establish that
specific call context without requiring an earlier observation. An already
observed buffer still must match. Only header metadata is read: native FreeInternal
preserves/increases size and clears flag/magic during coalescing. Full600-byte
final party permutation and every other3324-byte snapshot field remain exact,
with ordinary6 checksum/reencoding/empty-slot checks. Fixtures poison freed
payload and forbid any bus read from it; none occurs. Wrong/stale operand,
return slots/registers,live/malformed header,early completion and unrelated
party/Bag bytes are rejected. Exit completion is not latched inside Update.

A further source/retained-context check found the arbitrary128-byte stack
headroom would reject native WAIT SP0x03007e24. The context bound now requires
the minimum actual word; every stack access remains separately bounded.
Retained WAIT PC/SP/CPSR and compiled AgbMain return are positive normal/freshIRQ
fixtures before copy and after cleanup; wrong SP/top/return are rejected.
Unknown nested helper/IRQ contexts still fail closed. Identical-word images still
cannot establish invisible execution history. Historical cut occurrence is not
claimed. Screenshots N/A: all new captures/Save files are synthetic/private.

Full aggregate and production observer for **fd827ad6** PASS, separately retained
at private `aggregate-final`; sourceSHA51da4501…71488, production executable
`4e1da73e0f52888d8f913f1779f90e2a6239d3162bf67075879b9a4e75816f24`, receipt
`2582731069ff24ab3bda9a93c0997cf0399f443487c058f68355230223505c0b`.
That result predates these corrections and cannot admit this current source.
The latest full aggregate, latest production build and closed-gate negatives
remain OPEN at this user-requested boundary. The gate fixture script is written
but unexecuted. Preparation remains unconditionally CLOSED, with no execution
path/freeze/claim. Independent review continues; no review PASS is claimed.

Latest source/generated-observer/inert executable/proof/bindings/log hashes and
exact statuses are in [checkpoint.json](checkpoint.json). Revised proof lives in
private `reviewed-offsets-proof`, preserving all earlier proof/diagnostic bytes;
native ABI [568,4,16,0,2,4,8,12] and leaf Free call/return instructions verified.
Game `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, tree
`0fedd142f43f136ceee189c54101b095fc88f495`, ROM
`79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246`, ELF
`7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d`,
libmGBA0.10.5 `a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`
unchanged; no game rebuild. GCC14.2.0/ARMbinutils2.44-3+23+b1/agbccsource
`da598c1d918402c42c0c0d7128ba14567f3175e9`; recovered binaries differ historically.

Read-only recheck:98 preserved entries/218729208B, including31 compressed chunks/
216182152B, all SHA256/size exact; both original full-frame receipt hashes verified.
Preserved manifest `a7aef855c4e60a5ea861d93a8c7e029bf4fae97d9eb8a1f9e6f64ec32b0e55b7`.
No decompression/preservation/compression/deletion/upload added. New private root
`/workspace/scratch/c01-medicine-transaction-offline-r3-20261010` retains earlier
aggregates/split diagnostics, all revised tests and launch/proof-format diagnostics,
bounded128MiB. Local readback is not an independent backup. Capacity measured
13791711232B versus full10000408128B reservation; storage cannot admit runtime.
Library5 failed uploads+1 supported backup download,unknowncause/zerooriginalbytes,
and no independent backup remain unchanged. No evidence is released.

No new emulator/Save/cold/claim; C01 opening3/3,cold0/0 andSTOP82/90/104 unchanged.
V016/4 STOP117 visual8536 beforeB8402,lateraccepted1/1,ordinary5,C01aactual5/3/1
andclaims6/3/1 preserved. Main/all69otherheads/issue116 unchanged; no merge.
Originaloracle/legacy/C01/G02/prepared/human/full-floor gates and accepted
nine-district plan remain open/unchanged. Next only on explicit continuation:
run the latest aggregate into `aggregate-reviewed-offsets`, build the production
observer without executing it, run `closed-gate-fixtures.py`, verify exact hashes,
then independent review. Return idle now.
