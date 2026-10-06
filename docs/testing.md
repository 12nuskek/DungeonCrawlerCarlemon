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

## E01 custom gameplay replay

With the same build tools plus mGBA development library and Python Pillow, run
`bash scripts/test-e01.sh` from a clean committed tree. It builds the custom ROM
and runs the input routes in `docs/evidence/e01` against a new flash save, then a
separate emulator process loading that save. Nineteen map/position/persistent-flag
assertions supplement visual inspection. See the [tested E01 report](evidence/e01/README.md).
Workspace-local mGBA flags use DCC_TEST_CFLAGS and DCC_TEST_LDFLAGS; do not pass
them as CFLAGS/LDFLAGS to the GBA compiler. Saves/executables/ROMs stay ignored.

## B01 duo replay

Run `bash scripts/test-b01.sh` with the same compiler and mGBA dependency flags.
It exports the committed source into an isolated directory, hydrates the exact
upstream inputs and rebuilds the pinned compiler via setup-foundation.sh. It then
creates a fresh game and real flash save via the E01 route, then separately
boots loss/retry, victory/save and cold-reload routes. Inputs are ordinary GBA
buttons; RAM diagnostics only read protagonist HP/names/count, battle membership,
both offensive PP counters, outcome and the saved trial flag. Read offsets are
bound to the pinned source structures. Review the captured images as well.
B01 requires a fresh save: earlier E01 saves have no protagonists. The binary save
layout is unchanged; no migration is claimed. Battle art/labels are placeholders.

## Screenshot reporting requirement

Every gameplay issue and PR embeds representative actual emulator captures, with
exact tested source commit and route/assertion labels; use before/after for fixes
where useful. Link immutable evidence paths so later art changes cannot rewrite a
past result. Retain input routes and logs: images alone are not test proof.
Nonvisual build/docs issues say screenshots N/A or link relevant actual runtime
evidence. Do not fabricate screenshots or present mockups as running game output.
This requirement was explicitly added by Kurt on 2026-10-06.

## E02 guide/recovery replay

Use `bash scripts/test-e02.sh` for the current E02 milestone. It builds an isolated
committed snapshot with pinned setup, retains complete logs and fails on emulator
errors. Routes cover pre-trial guide dialogue, inherited defeat/retry, a win with
real injured/depleted protagonists followed by guide recovery, repeat use, map
return and actual cold save reload. `roster` assertions read party HP, decrypt the
saved attack substructure locally to inspect actual party PP, and read persistent
status. The harness never writes game RAM. Battle PP is not used to prove healing.
Nonzero status curing awaits a reachable status-inflicting encounter and is not
claimed from a zero-status check. Historical B01 victory routes expect auto-heal;
run those at their recorded revision, not against E02's intentional guide flow.

Use a fresh E02 save. Old B01 saves can retain a cached map object list without
the newly authored guide until map re-entry; no cross-milestone migration is
claimed. Final E02 verification always begins with a new game under the E02 ROM.

## B02 crawler action replay

Use `bash scripts/test-b02.sh` at the B02 revision with a fresh save. The isolated
runner covers both new offensive choices, refused zero-use SPARK and alternate
WEAKEN, BRACE/WEAKEN stat changes, one actor fainted while the other acts, both
fainted with local recovery/retry, guide recovery and cold reload. `uses` reads
all four actual party PP slots, including both support slots; it does not use stale
battle records to claim restoration. `support` reads current battle PP and stat
stages to prove effects and the surviving actor's action. Resource budgets and
magic/physical types are provisional balance, using stock engine effects.
Previous milestone fixtures must be run at their recorded revisions because move
IDs and resource budgets intentionally changed. Nonzero status curing remains
pending; these test enemies still only use Tackle.

## B03 collection boundary replay

At the B03 tested revision run `bash scripts/test-b03.sh` with the same dependency
variables as B02. Seven production routes plus a separate GBA-side policy fixture
prove the reachable UI and defensive entry points. The fixture is generated only
inside the archived test snapshot and has its own ROM hash/log; the snapshot's
final engine ROM is that fixture. Use a normal checkout/README build for play.
[Evidence and 110 assertions](evidence/b03/README.md), [reachability audit](collection-audit.md).
Screenshots are real emulator captures; host `pocket`/`policy` diagnostics read RAM
only. The fixture explicitly constructs test inputs in game code, never a hidden
production debug route. Preserve this distinction in future acceptance reports.

## R01 XP/equipment replay

Run `bash scripts/test-r01.sh` at its tested revision with the documented toolchain
variables. It preserves a local production ROM before generating a separate damage/
capacity fixture. Eight production and two fixture routes cover ordinary obtain,
repeat, equip/take, wins with/without gear, XP/stat growth, depleted and immediate-
defeat saves, cold reload/retry, and capacity refusal followed by freeing a slot.
`growth` decodes saved encrypted XP/held-item fields; `item` reads real bag quantities
with the save encryption key. `stats`, `foes` and `flag` read actual game state.
No host RAM writes. [174-assertion evidence](evidence/r01/README.md).

## R02 achievement/loot replay

Run `bash scripts/test-r02.sh` at tested revision `fbfb9e9` with the same toolchain
variables. Four production routes (132 assertions) and two explicit capacity
fixture routes (37 assertions) prove locked states, one-time flags/quantities,
consumption, no-effect preservation, map re-entry, cold reload, atomic failure
and retry. Six empty error logs; [full evidence](evidence/r02/README.md).
