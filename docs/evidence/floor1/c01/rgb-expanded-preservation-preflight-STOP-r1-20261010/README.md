# Actual preservation freeze preflight STOP — originals retained

Corrected scope admission passed27 cases at clean source
`f72fb97a537c69e0b68923579c87864b764dc7e0`. The first43-to42 count failure and
separate transport rejection remain preserved. After confirming no process/output
existed, one separately admitted freeze ran as PID185808. No replay occurred.

It reconciled all42 original chunk hashes against retained manifests/summaries,
all82482 frame/sample ledger entries, source-native indexes and opening4's existing
per-frame ledger. It then stopped before writing the machine contract:

```text
AttributeError: module 'zlib' has no attribute '__file__'
```

The active Python exposes zlib as `built-in`, version1.3.2. Its actual executable
SHA256 remains `fa67443527ed9647f760d807e2a38f26340757123e643c4639cf273ed15d5ea7`.
The metadata lookup incorrectly assumed a separate extension file. This is a tool
identity preflight failure; no gzip compression/decoded pass/replacement started.

[Exact failure and partial inventory](preflight-STOP.json) records42 original paths
still present/9501926400 bytes,42 retained per-frame ledgers/82482 entries, and
2645422 logical/2760704 allocated partial-output bytes. The terminal r1 STOP and
every partial file remain unchanged. No machine contract, operation record, full
protected-file receipt or capacity admission was completed. No savings claim.
[The corrected27-case admission](scope-admission.json) retains its exact tested
source and source/tool pins; old36 tests/31 STOP90-STOP104 replacements were reused,
not repeated. These are original inventory hashes, not decoded replacement proofs.

Proposed correction: distinguish built-in zlib from a regular extension binary,
pin the actual provider and linked libraries, and recheck module origin. Reject
unknown/missing/contradictory identities. New provider fixtures are added but
**UNTESTED**. A separately named r2 output/admission protects failed r1 output,
old admission and earlier failure receipts. No r2 directory/receipt or new attempt
was created. The [bounded contract proposal](../../../../floor1/rgb-expanded-preservation-r1-contract.md)
retains42 paths,82482 frames/samples,9501926400 bytes, the unchanged GNU gzip1.13
`-6 -n` codec,3758096384 total cap/134217728 audit reserve and TWO complete independent
decoded byte/frame/chunk/EOF passes before any exact-path redundant-raw replacement.
Original recorded sampling/index semantics remain unchanged; no footage relabeling.

At the receipt checkpoint, available5974306816 bytes versus10000408128 unchanged
Howler reservation leaves4026101312 shortfall. All originals remain, and runtime
is CLOSED. No emulator, gameplay claim, runtime freeze, actual Save/cold, merge,
game change, unrelated deletion, upload or delegation. Opening5/5, cold2/2,
current Howler0, ordinary recovery5, V016/4/STOP117/later accepted1/1, every historical
failure and Library5+1 remain unchanged. Local preservation approval stands;
independent private Library backup remains unapproved/unverified.

Next: independently review the provider correction and r2 bounds before a new
scope admission/freeze. First-failure behavior prevents automatic continuation or
retry of failed r1. Source/proof metadata only are public; private raw streams,
Saves, symbols and per-frame hash ledgers stay local.
