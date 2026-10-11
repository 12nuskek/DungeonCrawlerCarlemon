# Proposed archive-backed frame preservation — review only

Base `61c181d6fe67a9b9987351e63daf353449826ce7`. This increment prepares source,
one bounded inert suite, and a private immutable proposal. It does not replace
frames, invoke future verification/controller processes, recompress, run gameplay,
change Save/engine/build products, upload, merge, or change public metadata.

Exactly 31,254 native PPM exports are proposed: baseline and candidate each
contain `battle-00000.ppm` through `battle-15626.ppm` under the existing
`new-input-visual-pair-20261010` private directory. Each has the exact 15-byte
P6 header and 115,200 RGB bytes. All other captures, including similarly named
start/result captures, remain protected. Videos, traces, receipts, failure
records, Saves, build inputs and tools are retained. This is not build cleanup.

The immutable existing archive SHA256 is
`f43bdc3b80c55a3b566c1f4058e2ece2844ec6c051164c7605ab73c2843dbcd3`.
Its existing manifest SHA256 is
`2800fe68cd6978934b08f9cec1a7fcd54816d14ec264e52d5aec2779c44dbe76`.
The strict reader rejects ambiguous/duplicate effective names, unsafe paths,
links and nonregular members, malformed/unexpected PAX fields, wrong padding,
truncation, extra TAR content and trailing gzip members. Every target has a
complete original hash, exact integer-safe identity, and archive-member identity.
Device/inode/mode/uid/nanosecond timestamps use canonical decimal strings.
The historical auxiliary 21 ns timestamp-rounding STOP is retained separately.

Proposed private output roots are fixed in source. Preparation, inert output and
future execution together have a 64 MiB metadata bound, 128 MiB external audit
reserve and 249,856-byte selected-frame materialization reserve: 201,576,448 bytes
total. New archive/data staging is zero. Original allocation is 3,712,475,136 bytes;
conservative potential reclamation after all allowances is 3,510,898,688 bytes.
No space is reclaimed in this increment.

Whole historical directory restoration requires 3,712,475,136 allocated bytes.
The adapter permits at most two explicitly selected materializations in a fresh
private workspace directory, with byte provenance and new inode identities.
It restores exact mapped nanosecond timestamps rather than rounded archive times;
it does not recreate original inodes or rewrite old receipts. Selected
materialization requires fresh space for the unchanged Warden reservation plus
all preservation/restore allowances. There is no automatic restoration or alias.

Historical `capture-retention.py` reads the complete numbered series to encode
FFV1. It is dormant. The new read-only adapter can instead verify each existing
FFV1 decoded frame against its archived PPM pixels and compare the complete
ordered RGB digest to the unchanged historical receipt; no directory restoration
is needed. These checks are not game execution or new historical acceptance.
Current Warden input/configuration and required-history paths are independently
enumerated, protected and rechecked; none may overlap the proposed frame scope.
Whole-directory restoration concurrent with Warden is not admitted. Warden's
17,694,519,296-byte reservation and all runtime authority remain unchanged/closed.

Future replacement requires separate exact parent review authority. The
controller creates an exclusive fresh operation and starts two distinct fresh
child processes, one with the accepted built-in zlib decoder, one with GNU gzip.
Each must compare every archive target byte-for-byte with its original, validate
full native frames, ordered proof ledger, complete hashes, all archive member
identities, and exact TAR/gzip EOF. Complete source/provider/protected/input
rechecks, positive all-inclusive savings, and fresh metadata/restoration/Warden
headroom are mandatory. Archive, mapping, protected inventory, operation,
admission/authority, both ledgers and receipts must be fsynced with containing
directories before a one-use removal ticket can be minted. Premature removal is
rejected. Only exact directory-bound single-link originals can be unlinked.

First failure is terminal; no automatic retry. Pre-batch failures retain every
original and artifact. A failure after batch start retains all remaining
originals, archive and completed receipts, with actual remaining-member STOP
evidence. Historical receipts/pins/STOPs remain untouched. Archive retention is
local only and is not a verified independent backup. Independent review of this
proposal and inert evidence is the next dependency; no replacement authority
is created by proposal preparation.
