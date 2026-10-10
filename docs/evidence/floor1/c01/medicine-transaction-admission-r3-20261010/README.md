# C01 r3 final offline checks PASS; gameplay CLOSED

The current-source full aggregate, production observer compilation and all37
closed-gate/hash negative cases completed with exit0. Tested clean source:
`32a25769c5427656a010287bed6cf03c5f62b45c`; start
`3270cdb0819fd29cc06cf9716e027911db75511f`; main/base
`b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`. This supersedes earlier pending-check
status only. Independent review remains pending; no runtime acceptance is claimed.
[Exact identities and results](results.json) bind the source, generated/compiled
observer, ELF, library, native proof/bindings and both final receipts.

Read-only review found saved memcpy operands were read at SP/SP+4 before frame
validation. The three-file correction validates the whole caller frame first.
At admitted SP0x03007e3c, a new fixture forbids every bus read at/above0x03007e40:
the old validator deliberately aborts on this fixture; the corrected source
rejects without reading beyond the bound. Ten such negatives pass. Retained
native WAIT SP0x03007e24 still passes before copy/after cleanup, normal/freshIRQ.
No assertions or party/resource ownership checks were weakened.

Full aggregate PASS includes74124 medicine policy vectors,24180 normal/IRQ
transaction positives,116756 negatives,32970 physical snapshot corruptions,
65760 native HP/WAIT lifecycle byte corruptions,26 aligned prefixes ×6records,
both party orders/recipients,8UI cases and2successive uses. Independent pinned
Thumb execution exercises2140 direct outer Update checks/all22 admitted offsets,
60 post-Free completions including40 skipped prior observations, unmerged/native
previous-next coalescing, with0 freed-payload reads. Exact600 party bytes and all
other3324-byte snapshot fields remain guarded.90 ELF bindings and native ABI
checks pass. Inherited phase/resource/legal-field and30 synthetic disk Save/cold
fixtures pass; those are inert fixtures, not actual gameplay or cold verification.

The final37 closed-gate cases cover ten identity fields, malformed/old/boolean
records, changed source reads, altered generated/compiled observer, bindings,
proof, ELF/library and opened receipts. Corruptions use owned fixture copies;
original bytes remain untouched. The actual prepare wrapper rejects after
valid identities; ordinary and optimized-Python CLI prepare reject without output,
and opening/cold stages are unsupported. Preparation remains unconditionally
CLOSED. Production observer compiled with warnings-as-errors, never invoked.
No emulator init/gameplay/freeze/claim/new actual Save/cold. All new screenshots
and Save files are synthetic/private; no new actual screenshots or motion.

The initial3270cdb0 aggregate was safely interrupted(exit130) when this concrete
review finding arrived, before receipt completion. Its directory/log/bytes are
retained separately as superseded diagnostics. All earlier proofs, aggregates,
failed offline diagnostics and historical wrappers/contracts/STOPs remain intact.
Unknown nested helper/IRQ cuts fail closed; identical-word images cannot prove
invisible duplicate/skipped execution. Historical occurrence is not inferred.

Game/tree/ROM/ELF/libmGBA pins remain unchanged, with no game rebuild.
GCC14.2.0/ARMbinutils2.44-3+23+b1/agbccsource
`da598c1d918402c42c0c0d7128ba14567f3175e9`; recovered binaries differ from originals.

Fresh read-only preservation check rehashes98entries/218729208B including31gzip
chunks/216182152B, and verifies both original full-frame receipt hashes. No new
decompression/preservation/compression/evidence deletion/upload or representation
change. New offline root remains below128MiB including8MiB audit reserve; exact
capacity/full10000408128B reservation and retention-manifest hash in results.json.
Local readback is not independent backup. Library5failed uploads+1supported
backup-download failure,unknowncause/zerooriginalbytes/no retry are unchanged.

C01opening3/3,cold0/0,STOP82/90/104 unchanged. V016baseline/4candidate,STOP117
visual8536 beforeB8402,lateraccepted1/1,ordinary5,C01aactual5/3/1 andclaims6/3/1
remain separate. Oldr2/engine/routes/policy/cadence, acceptednine-district plan,
main/all69otherheads and issue116 preserved. DraftPR117 remains unmerged.
Originaloracle/legacy/C01/G02/prepared/human/full-floor gates remain open.

Next dependency: independent read-only review of this exact corrected source
and final offline results. Any later runtime needs a separately reviewed contract
and authorization. Yield cleanly now; no automatic continuation.
