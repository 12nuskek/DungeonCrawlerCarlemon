# New integrated main build and terminal preparation checkpoint

One isolated normal agbcc build succeeded from integrated main
c6d647a815ffce44a2419a2cf83b6c2c094359f0, engine
76001ee128785714b7c15aef6d9c95630587d0a9. Publication base was
5b1c108557ecdb2704dea94c61aff1fb28845acd; new runner/preparation source is
2580b38eeda5c1b56b988ae04bbd24b7ac131006. [Actual build result](build-result.json)
records outputs, compiler executable hashes, attempt/exit and full-log hash.
Official upstream commit731ad5bfd6e6f265508d0efcca0ba42f9dcf5881 supplied only
three exact multiboot blobs, independently rehashed in the diagnosis.

ROM SHA256 ae1e9d36a94ed2eaa9d8fc79d790a2dc47173b932551891d889c657e12ca8461
matches the recorded integrated main ROM. Newly emitted ELF SHA256 is
6e56b32192e1a861b39c70e62bb5c43e762b9f5cc8ce0389d3cb494c3ee6dde6.
Compiler binaries differ from original and prior recovered binaries. No
original-tool identity, recovered Save/oracle, or runtime acceptance transfers.

## Exact stop and read-only diagnosis

The new prepare command failed its source byte comparison at
engine/asmdiff.ps1, before generating/compiling the host, exporting bindings or
running any emulator. [Traceback](prepare.log), [terminal stop](prepare-stop.json)
and [read-only source diagnosis](source-diagnosis.json) preserve exact evidence.
No preparation retry, archive edit, second game build or dependent gameplay.

The verifier incorrectly required raw Git bytes for an archive whose pinned
engine/.gitattributes explicitly specifies text/eol=crlf. Complete read-only
inspection compared11714 tracked engine files:9037 raw exact,2677 CRLF-only
transformations (one.ps1/2676.pal). Every differing path reports text/eol=crlf;
main, archived and current attributes bytes match SHA256
8e7bf56ce252073f32772ef09e8e562ee28e117f70597c69ddd22d122140dd20.
No tracked non-EOL discrepancy was found. Three hydrated binaries are untracked
upstream inputs and separately pass their pinned blob/SHA256 checks. This
explains the new wrapper failure; it does not turn a stopped prepare into a
verified executable freeze or permit gameplay under this claim.

## Work prepared and remaining review

The separately named [contract](../../../../floor1/ordinary-gameplay-recovery-20261009-contract.md)
and new runner/host/native-ABI source implement prospective fresh/setup/patrol/
cold dependencies, actual Bag/party readiness, native friendship validators,
create-only claims, first-failure STOP,100000-frame/600-second limits and bounded
ordinary-speed RGB/FFV1 captures. Python syntax checks passed. The generated host
and native ABI have not compiled, bindings/routes/complete identity.json have
not frozen, and the observer has no runtime verification. There are no new
ordinary executions, Saves, screenshots or motion. No Warden or candidate pair.

Next dependency-ready action: review the diagnosed source-verifier correction
for pinned Git archive attributes, then a separately named prepare claim. It
must retain every native gate and prove exact expected archive bytes for each
explicitly CRLF-marked path, rather than broadly normalizing arbitrary files.
Re-use the verified single game build; do not reacquire tools or search for ROM
parity. Only after source/observer/ABI/route identities freeze may the authorized
single ordinary reconstruction/manual Save/independent cold proceed. This
increment stops for review on draft PR114, without merge.

Six historical baseline/four candidate executions and STOP117 at requested
visual8536 before expected B8402 are unchanged. Active-pose source
9c83611e8e9b61d55388c18496c361d3362e462e and engine
8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a remain compiled/offline-only without
runtime acceptance. Original runtime reference, legacy inputs and lost Save
remain missing. No legacy-save or full-floor acceptance claim.

## Private retention

New source archive, tools, build outputs, full build log, full read-only source
diagnosis and stopped runtime directory are workspace-local under
/workspace/scratch/ordinary-recovery-r4-20261010. No ROM/ELF or private raw file is
published. Existing verified tooling-r3 local archive remains40878056 bytes,
SHA256244aff8e919782ad49ebbdfee05711e93ca44994169eafa86e88ebc897dfcc81.
It is downloadable locally if needed, requires the identified installed
runtime/compiler prerequisites, and is not an independent backup. No separate
backup of the new build is verified. A private user-held copy or an explicitly
authorized connected private destination can be verified after a successful
transfer; neither has happened. Five failed Library uploads and one supported
existing-backup download yielded zero recovered bytes, cause unknown; no retry.
