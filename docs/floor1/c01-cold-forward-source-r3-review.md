# Cold forward correspondence r3: source-only review

## Current r5 correction: SOURCE ONLY

Start c777d649bb5715be1caf66d006188e36a8152a74. No checker, preflight, fixture
or suite is authorized in this increment. The older r4 execution wording below
describes its completed failed attempt and provides no new execution permission.
Source-preflight failures remain two, with no retry or counter reset.

Every shared operand hash, including interpreter startup and both before/after
maps, now uses declared path/role/type/exact-size/hash descriptors and64KiB
streaming reads. Require regular non-symlink identity, matching opened descriptor,
exact byte count/EOF/hash and unchanged dev/inode/mode/uid/gid/size/mtime/ctime/
link count. Compare identity maps across the whole comparison too. Interpreter
size remains exactly30,894,944 bytes and its existing hash is unchanged; it is
never retained as a whole-file byte string.8MiB per receipt and64MiB metadata
remain unchanged. Source/cache/helper retention is limited to1MiB, JSON/config/
inventory retention to8MiB, and every retained read still has an exact declared
size/hash. There is no blanket increase of record limits.

An independently reviewed private operand manifest is an explicit CLI input:
schema/source_commit/direct_operands/auxiliary_operands. Each descriptor has
exactly path,role,type,bytes,SHA256. Preserve all18 earlier direct operands and
add the r4 STOP and handoff, yielding20. Four current reviewed sources are bound
to the reviewed Git commit; the16 immutable descriptors are fixed explicitly.
The six accepted helper/config/provider operands are separate. Their helpers are
unchanged; GCC/ldd remain declared unused providers, Git is used, and interpreter
identity shared with the accepted helper is already in the direct partition.
The manifest itself is size/hash pinned and checked before and after use.
No import discovery or typed-union admission populates any of these sets.

The actual sealed r2 interpreter object already contains path and all seven
fields. Preserve it exactly, rather than add/replace path. Preserve the complete
actual_metadata object too; it records an observed code label, not authenticated
distributor provenance. Both r4 STOP2784a906…b9424 and handofffd4534ac…c4be0 are
required in construction and validation. Failure history distinguishes filename
assumption1, operand-size rejection1, earlier closure suite1, missing-summary
serialization1 and earlier auxiliary metadata-query1. Older files remain exact.

Both payloads are pre-serialized and validated before either output exists.
Write/fsync those exact bytes; then open/read both with exact size, EOF and stable
identity, revalidate full schemas, and compare all bytes and SHA256 before PASS.
The proposed outer wrapper independently repeats complete persisted schema and
byte/hash readback before the conditional fixture invocation. Exclusive logs,
90-second limits/kill-reap reserve/terminal STOP and fresh r5 names remain required.
No entrypoint itself supplies the outer execution records.

The accepted fresh-invocation ownership fixture remains unchanged. Prepared
additional tests cover interpreter streaming above the receipt cap, declared
size/hash/role/type failures, short/extra streams, changed metadata, complete
sealed interpreter/diagnostic schemas, both persisted payloads and same-size
corruption. Tests and all corrected production paths remain UNEXECUTED.

Exact final manifest path/bytes/hash, private wrapper identity and proposed outer
command are in the private source-review handoff. These commands require a new
independent review and explicit execution scope:

```text
python3.12 -B /workspace/scratch/c01-warden-cold-forward-wrapper-r5-20261011.py --source <reviewed-commit> --inventory <reviewed-manifest> --inventory-bytes <exact-bytes> --inventory-sha256 <exact-hash>
```

All source/preflight/summary/fixture/outer r5 roots must be new. No source-consistency
success, provider addition admission or runtime readiness is claimed here.

## Historical r4 preparation and execution scope

R4 narrow fixture correction starts at daee549dc78eace8859dba95f249f11ba6377e43.
The second modeled invocation has fresh LocalIO process ownership and shares
only retained lifecycle/STOP state and the total event ledger. Keep the first
process reference; require one creation, that process stopped/reaped once,
actual_processes=1, no verdict, unchanged first failure and no second creation
or stop of the prior process. Production failure handling is unchanged.

Independent review now admits one r3 source preflight and, only after complete
success/readback, one r3 fixture invocation. The private outer wrapper has a new
r4 root: /workspace/scratch/c01-warden-cold-forward-outer-r4-20261011. Before launch
it must serialize its complete command/bounds/source/input contract and record
its own exact source hash. Each command gets exclusive stdout/stderr logs and
creation/PID/exit clock records, a90-second creation-through-reap limit,8MiB log
limits and64MiB total outer metadata. The parent entrypoints retain60-second
internal limits. A failure kills/reaps the owned child/process group, records a
terminal STOP with exact logs/partial outputs and skips the conditional command.
No automatic retry. Complete receipt bytes/hashes are independently read back
before success is reported. If setup cannot meet these bounds, stop before launch.
These are source-check/fixture children, never runtime/emulator processes.
Actual results belong in the private outer handoff, not in older STOPs below.

Base c7a30533b26f4ef8955f55d32a3907853ad29da1. No checker, correspondence
comparison, fixture or suite was executed in this preparation. Screenshots N/A.
Historical r1 admission counts and old runtime/source STOPs remain unchanged.

The prepared source compiles the officially matched copy.py bytes in memory
using the exact filename observed inside hash-pinned copy.pyc. This filename is
a code label, not authenticated distributor build provenance. Every recursive
filename remains in the comparison, along with constants, bytecode, flags,
line/exception tables, argument/local/closure metadata and decoded line/position
tables. Header magic/flags/timestamp/size and marshal EOF stay strict. Complete
before/after source/cache/interpreter/evidence hashes must match. Nothing executes
the compiled code or regenerates, deletes or writes a cache.

Both RGB correspondence successes are reused from the sealed r2 partial-preflight
control-flow record only when current source/cache bytes and pinned Git blobs
match. No new RGB comparison and no historical provider continuity are claimed.
The exact four additions are explicit constants, never populated from discovery.
The prepared receipt is correspondence evidence only, not cold admission.

The prior r2 preflight STOP remains FAIL. Its missing fourth checkpoint summary
is a separate serialization failure, not a successful receipt. New preflight
and summary roots have r3 names. Declared Path map keys/value fields convert to
strings; converted key collisions, undeclared Paths and unsupported types fail.
All complete payloads are serialized and schema-validated before destinations
are created. Prepared fixtures cover nested conversions, collisions, unsupported
types and a valid-first/invalid-second bundle that must create no destination.

Process ownership audit: LocalIO.launch retains created_process before writing
the start record; execute() recovers it on failure and passes it to stop/reap and
terminal. The prepared stronger fixture requires one creation, identical owned
process passed to stop, modeled actual_processes=1, no verdict, unchanged first
failure and no second launch. It uses the existing ModelIO with inert factory;
it never invokes the old suite main or native observer.

Typed-union integration remains UNIMPLEMENTED and UNTESTED. The original r1
build_proposal currently classifies project provider caches as sources and merges
discovery directly into tools. A future reviewed correction must instead merge
explicit reviewed source, original sealed provider and successful forward-receipt
maps with conflict checks BEFORE examining discovery. Retain all original provider
entries, including the former launcher missing from the new import graph. Validate
project_sources against the source partition alone; validate every discovered
operand against the independently pinned union. Preserve bounded discovery,
classification, conflicts and both differences before any admission assertion.
Keep provider caches outside tracked sources; derive counts from explicit sets.
The three sealed Warden caches retain their original manifest provenance. No r3
counts replace historical r1 counts. Actual-classifier mutation fixtures remain
a dependency of that later correction, not acceptance from these serializer cases.

Review assumptions before authorizing execution: pinned interpreter version/build,
magic/code-field schema/optimize0/-B, exact Git ancestry and current clean source,
official source comparison reused from sealed r2 evidence, observed code-label
semantics and unchanged bytes. The next invocation must be bounded and have an
exclusive command log/terminal failure record; no retry after any unexpected error.
This source preparation itself provides no execution authority.

Proposed commands ONLY, after separate review/authorization, using the existing
pinned sanitized environment and exclusive private logs (each command once):

```text
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 -B scripts/floor1/warden-cold-forward-preflight-r3.py --reviewed-source <independently-reviewed-full-source-commit>
/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12 -B scripts/test-warden-cold-forward-source-fixtures-r3.py
```

Each internal limit is60 seconds; proposed outer limit90 seconds. Fresh outputs:
/workspace/scratch/c01-warden-cold-forward-preflight-r3-20261011,
/workspace/scratch/c01-warden-cold-forward-summary-r3-20261011 and
/workspace/scratch/c01-warden-cold-forward-fixtures-r3-20261011.
Neither command invokes discovery, build_proposal, a cold suite or runtime.
Independent review must precede any of these commands and any union integration.

Runtime contract unchanged:2044 frames, zero encounters,600 seconds,
17,694,519,296-byte reservation and every Save/disk/live/state comparison.
Warden1/1, Save1, cold0/0. No new authority/freeze/claim/emulator, engine build,
compression/removal, upload, merge or dashboard edit. Private records are local;
independent backup unverified; Library5+1 failure history remains unchanged.
