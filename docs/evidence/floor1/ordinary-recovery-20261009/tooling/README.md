# Tooling recovery — partial restoration, access-denial stop

Based on committed checkpoint `5895f3af34aaddff1c49e2b6d228a2540056a286`.
This parent-authorized increment used official Debian pool listings, verified
HTTPS, exact manifest hashes/control fields and `dpkg-deb --extract` into
a workspace-local root. No system package/configuration/permission changes.

Local diagnostics show amd64, GCC 14.2.0, readable trixie snapshot sources and
an empty `/var/lib/apt/lists`. Package policy reports only installed dpkg
versions for inih/zip/epoxy; no repository candidates for ARM binutils/mGBA.
The prior unreadable APT-configuration warning remains. The earlier failed
lookup does not establish that official Debian packages are unavailable.

Two packages were downloaded once, hash/control-checked and extracted:

| Package | Version | Complete package SHA256 |
| --- | --- | --- |
| binutils-arm-none-eabi | 2.44-3+23+b1 | `c9c4944e54de852536b4f6a238a682c38a6243cdc2843dd1c4f587e046c0615b` |
| libepoxy0 | 1.5.10-2 | `4c4c8024f2175086de65bca9fdc3fbb967f2863ebf249d489c66d0c8103dd3a3` |

Actual assembler/nm/linker versions are 2.44-3+23+b1. Their version commands
succeed and ldd reports no unresolved dependencies; executable/resolved-library
hashes are recorded. Extracted libepoxy SHA256 is
`508c6214d08b997e0509e74b568f1e66f574951105cb11e59d12ed74a4239f13`,
also with no unresolved ldd dependencies. No game or compiler was compiled.

An incorrect guessed source-pool path `pool/main/i/inih/` returned 404; this
resolver mistake is preserved. Reading the parent-supplied official
`https://packages.debian.org/trixie/amd64/libinih1/download` to resolve its
actual path then failed with **URLError: Tunnel connection failed: 403 Forbidden**.
The tunnel denial occurred before an origin response; no deeper cause is
established. All acquisition stopped there, with no alternate route/retry after
denial. The prior APT attempt remains recorded separately.

**The toolchain is incomplete.** libinih/libzip/libmGBA and the additional
manifest-pinned build headers were not downloaded in this increment.
agbcc source `da598c1d918402c42c0c0d7128ba14567f3175e9` was not cloned or
compiled after the stop. libmGBA's expected
`a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`
is not verified. Missing-tool dynamic dependencies cannot yet be assessed.
No original compiler-binary identity or complete tooling-bundle claim.

A verified **partial** bundle is local at
`/workspace/scratch/ordinary-recovery-tooling-20261010-partial.tar.gz`,
11702603 bytes, SHA256
`f36780816c6ce343b0ef4ba1432c013c59d86acebd1c4b72c36ad837c2dcaadf`.
Its directory name is an identifier; acquisition date is 9 October 2026 UTC.
One archive was created. Its 114 file entries (including 11 hardlinks) and one
symlink match local bytes/targets. The first verifier lacked tar-hardlink support
and stopped at ld.bfd; a read-only hardlink-aware check of the same archive
passes, with the verifier failure retained. No archive recreation or byte/hash
mismatch. This local bundle is not an independently verified private backup.

[Exact acquisition, denial, identities and bundle receipt](tooling-result.json).
Six baseline/four candidate executions and latest STOP117 visual 8536/expected B8402
remain unchanged. No game build/emulator/new Save/Warden/Library retry/merge.
Engine/scripts/accepted plan/historical assertions are untouched. Screenshots N/A.

Next dependency: parent review of the tunnel 403 and resolver mistake, then
resolved official pool URLs plus explicit continuation, or supported platform
resolution of packages.debian.org access. Do not change restricted configuration
or bypass denial. Verified tooling must precede the next ordinary recovery
contract/build/freeze/execution increment.
