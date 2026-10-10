# Tooling continuation — executable tools, new identities

Base and tooling-check commit:
`6d05b559e0bfde1044015f7fbbe13ea0e1b172c6`.
The parent-authorized independent resources completed without a new access
denial or pinned-package mismatch. No denied metadata-host access, new inih
download, system/configuration/permission changes or Library transfer.

libmgba-dev/runtime 0.10.5+dfsg-1 and libzip5 1.11.3-2 each downloaded once from
the three supplied exact official Debian URLs, then passed full manifest
SHA256, Package/Version/Architecture checks and local extraction.
Previously verified binutils/epoxy packages were rehashed and re-extracted,
with zero network reacquisitions. Exact libpng-dev 1.6.48-1+deb13u5 headers were
resolved by official directory links, using installed source-package metadata
and the committed manifest; one acquisition passes SHA256/control checks.
No guessed package path or denied metadata lookup was used.

Extracted libmGBA SHA256:
`a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`,
exactly the recorded pin. Actual ldd resolves all dependencies. A warning-as-error
native header/link check reports 0.10.5; it instantiates no emulator core, loads
no ROM/Save and executes no emulated CPU. libpng header/pkg-config/link check
reports 1.6.48 without loading or decoding game assets. Existing owned exact-version
PNG/zlib dependencies were identified; PNG runtime bytes were copied locally
without any system change or claim of original package-byte identity.

Exact official agbcc source `da598c1d918402c42c0c0d7128ba14567f3175e9`,
tree `dd8b159e245cc1e01b98a42581101e473ba0743d`, was fetched once and verified.
One upstream build succeeds with GCC 14.2.0/ARM binutils 2.44-3+23+b1; tracked
source remains unchanged. Local installation, ldd and source-documented tiny
compiler/assembler checks pass for all three compilers, producing ARM ELF32
objects. These compile tooling probes, not game source, ROMs or acceptance fixtures.

| Compiler | Actual new executable SHA256 |
| --- | --- |
| agbcc | `0eb17d598f1e7318a1ad7aa9864480fcc8d30d29c3a855d7f43c01909277158f` |
| old_agbcc | `e3dc2daec27cf4bd23172905631c3937e0eba0c7cb2bcfdce2264559e7535f24` |
| agbcc_arm | `20c9d2f83f43a67c44eb6b16240a1702d5eb6d8fe1d1feebc3e04373b7d32f19` |

All three differ from historical and previously rebuilt binaries. No original-tool
identity, cause of hash differences, emitted-game parity or runtime acceptance
is inferred from a source pin or compiler probe.

Installed inih 59-1/amd64 ownership/version and actual linkage are verified.
Its current library SHA256 is
`24ac7fa9821b61a4ef2e628cefcd2c7dcf2acccad88b8e7e95fa2d33bfc5eb6b`.
No historical extracted-inih hash was found in committed docs/scripts; no new
inih download or .deb identity claim. Installed zip library bytes equal those
extracted from the separately hash-verified official package; library hashes
were never compared with .deb hashes.

Two new caller-check errors are retained separately: isolated pkg-config search
omitted existing zlib metadata, and an initial compiler probe used unsupported
modern-only `-quiet`. Existing zlib metadata/headers were verified before the
completed link check; source-documented compiler syntax completes one check
per compiler. No compiler rebuild, source variant search, game test repetition
or acceptance weakening followed those diagnostics. The prior APT failure,
incorrect inih-pool 404 and metadata-host tunnel 403 remain separate unchanged
records; no metadata-host retry or count reset.

**Tooling is executable in the selected environment.** Historical compiler/inih
byte parity remains unverified. These gaps do not prevent the tooling probes;
they prevent unqualified original-tool identity claims. The new ordinary contract
must review/freeze the actual identities and verify the isolated main build/
observer outputs before gameplay. That contract is unchanged/unfrozen here.
All historical gameplay wrappers/pins/assertions remain intact.

[Exact tooling records](tooling-result.json) /
[verified local bundle receipt](bundle-receipt.json).
The workspace-dependent bundle is 40878056 bytes, SHA256
`244aff8e919782ad49ebbdfee05711e93ca44994169eafa86e88ebc897dfcc81`;
2461 file entries including 11 hardlinks and 16 symlink targets verified once.
It relies on recorded installed GCC/runtime libraries; it is not an OS image
or independently verified private backup. ROMs/Saves/game raw buffers are absent.

No game build/gameplay/new Save/Warden/Library retry/merge; screenshots N/A.
Six baseline/four candidate executions and STOP117 visual 8536/expected B8402 remain
unchanged. Main c6d647a8 and accepted Floor1 plan are untouched; active-pose source
9c83611e/engine 8d8c7761 stays historically offline-only. Original oracle/legacy
inputs remain missing. Five upload failures/one existing-backup download failure
remain unchanged. Next: parent tooling review, then separate ordinary main
contract/build/observer freeze and its authorized normal reconstruction.
