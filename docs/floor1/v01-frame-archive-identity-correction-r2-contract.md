# Offline archive identity comparison correction

The pre-authority orchestration STOP remains immutable:
`1cdf61781a87ceb436934d1b76088dccc60f27b744441b2514e1a849d93516e8`.
No authority, controller, verifier or removal occurred. Its equality comparison
incorrectly treated the six direct admission files as the complete proposal
closure.

The new read-only validator authenticates the original proposal and admission
bytes, then the accepted historical Howler handoff and its sealed contract,
mapping, two verifier receipts, synchronization receipt and terminal result.
It requires the literal six direct keys and exact fifteen inherited keys, their
disjoint 21-key union, unchanged commit binding and all 222 exact providers.
Every source hash must also match the supplied current bytes. There is no broad
subset allowance and no execution or authority API. Existing pinned sources,
receipts, contracts and wrappers are unchanged.

One fresh bounded inert suite uses the existing sealed receipts as fixtures and
checks their source bytes against the original committed blobs and current files.
The positive commit identity is explicitly the old frozen source
`3fa36fb0f18e3fb8db4fe6a647992d4764bd6543`, not the new correction checkout.
The new checkout identity must be rejected by that old comparison. Passing the
fixture cannot rebind the old proposal or grant actual execution authority.

Negatives cover every missing direct, inherited, union and current-source key,
extra keys, wrong direct/inherited/current hashes, overlap, stale commits,
missing/extra/changed providers, missing/extra/replaced historical receipts and
replaced proposal/admission bytes. Mutations remain in memory. Historical
receipts and all 31,254 original frame identities remain retained.

Fresh private output is only
`/workspace/scratch/v01-frame-archive-offline-r1-20261011/identity-closure-offline-r2-20261011`.
Limit: one run, 2,000 negative cases, 1 MiB receipts with terminal reserve,
240-second internal and 300-second outer limits. Complete future ledgers,
other receipts and the 2 MiB STOP reserve remain inside the aggregate 64 MiB
metadata accounting. First failure is terminal; no automatic retry.

This increment publishes only reviewed source. No authority, controller,
archive verifier, replacement, compression, materialization, gameplay, Save,
upload, merge or dashboard change is permitted. Warden runtime remains closed.
Independent review and a separately named execution remain future dependencies.
