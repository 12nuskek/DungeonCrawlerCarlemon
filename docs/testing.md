# Build and runtime validation

## Matching baseline build

Use Linux with `build-essential binutils-arm-none-eabi git libpng-dev pkg-config`.
The selected matching compiler is pret/agbcc, not the modern target; pins and
source exceptions are in [provenance](upstream/provenance.md).
From a clean repository checkout:

```sh
bash scripts/setup-foundation.sh
bash scripts/build-baseline.sh
```

Setup fetches exact pins, hydrates three ignored upstream multiboot inputs and
builds/installs agbcc into `engine/tools/agbcc`. Build runs `make -j2`,
`make compare` and SHA-256 recording. Logs go to ignored `artifacts/`.
`JOBS` controls build parallelism. `DCC_CACHE` optionally chooses the checkout
cache (default `.cache/`). Do not point it at unrelated user repositories.
Never commit ROMs, ELF, maps, saves or compiled tools.

## Emulator boot and interactive play

For interactive play, open the locally built `engine/pokeemerald.gba` in mGBA.
Set GBA buttons in the emulator's input settings. Begin with no save file; baseline
is unchanged Emerald, not yet DungeonCrawlerCarlemon. No downloadable ROM is
provided here.

For repeatable headless execution install `libmgba-dev` and compile:

```sh
mkdir -p artifacts/boot
cc -std=gnu11 -Wall -Wextra -Werror scripts/boot-baseline.c -lmgba -o artifacts/boot-baseline
cd artifacts/boot
../boot-baseline ../../engine/pokeemerald.gba < ../../docs/evidence/f01/route.txt > boot.log 2> mgba.log
```

The harness runs the actual mGBA core with built-in BIOS and no loaded save, steps
GBA frames with recorded button masks, and writes PPM captures. Convert captures
to PNG for inspection if desired. Record the source commit and ROM checksum with
the route. It is not a mocked game or a screenshot-only test.

Runtime gate: load the matching ROM in a real GBA emulator with a clean save,
observe boot/title, press Start and reach New Game, then enter the introduction.
Record emulator version, exact input/frame route and screenshots against the
tested source commit and ROM checksum. A screenshot alone is not full validation.

Future runtime matrix: fresh-save completion; all movement/collision/transitions;
duo actions, incapacitation, victory/defeat/escape; reward repetition and reload;
inventory empty/full, recipe failure/success; optional quest branches; boss alternate
strategy; staircase; capture/storage/breeding audit; text/palette/sprite limits.
Those checks are pending until their stages exist. Stock baseline saves are not
promised compatible with future crawler milestones. No save layout changes yet.

## Fresh isolated environment (F02)

On a Linux host with Bash, Git, Docker and a readable trusted CA bundle:

```sh
bash scripts/verify-container.sh
```

Commit tracked changes first: this verifies a captured commit ID, not uncommitted
files. The launcher builds [docker/Dockerfile](../docker/Dockerfile) using the
digest-pinned Debian 13.6 base, then streams `git archive` into a fresh disposable
container. It mounts no repository directories and reuses no agbcc cache or build
products. Only dependency-image layers can be cached. It exports logs, package
versions and screenshots into a new `artifacts/container/run-*` directory each
time, preventing old evidence from satisfying a failed run. It copies no ROM,
compiled harness or save out of the container, and removes the stopped container.

Docker client state defaults to `.cache/docker` to support read-only home
directories (`DCC_DOCKER_CONFIG` overrides). Standard upper/lowercase proxy
variables are forwarded without putting their values in scripts. The public trust
bundle comes from `SSL_CERT_FILE`, or `/etc/ssl/certs/ca-certificates.crt`, and TLS
verification stays enabled. If the managed proxy name is supplied through host
DNS but cannot resolve in Docker, set `DCC_PROXY_HOST_MAPPING=hostname:address`
using the actual host resolution (`getent hosts hostname`). Do not hard-code the
Cloud environment's address in source or use certificate-verification bypasses.

The OS image and upstream/compiler source revisions are immutable pins. Debian
package repositories can receive security updates; each run records the complete
installed package manifest and must still produce the expected ROM and runtime
frames. This is verified ROM reproducibility, not a claim of byte-identical
container layers or an offline dependency mirror.

The strict baseline harness now rejects malformed/incomplete routes and requires
all three visually reviewed title/menu/introduction RGB fingerprints at their
expected frames. The assertions intentionally target the matching baseline and
mGBA 0.10.5, not future gameplay builds. `scripts/test-foundation.py` exercises
valid/wrong/incomplete inputs and dirty tracked/untracked compiler sources.
Setup refuses dirty source caches before any fetch/build; choose a separate
`DCC_CACHE` to preserve edits. Ignored generated compiler products are allowed.

After gameplay changes, use `make -C engine -j2` and record a new custom ROM hash
and gameplay runtime route; the stock-ROM `compare` and stock screenshot checks
must not be represented as passing for a modified game. Keep this baseline
evidence as the foundation reference.
