Current live navigation verification (2026-10-08): [F1-G01e-NC evidence](evidence/floor1/g01e/navigation/README.md),
compiled/runner c643f01;17real mGBA sessions236assertions,5ordinary and12explicit
controlled save-input branches. Native text is compared to compiled labels and
captured paragraph by paragraph. Host font/source/65536identity checks supplement
runtime. Original files, raw evidence and saves remain local; no public ROM.
PR75/full gameplay/finalT/V01 gates remain pending despite this focused pass.

# Build and runtime validation

For the current crawler build, use the custom commands below. The matching
Emerald baseline sections document Stage 0 at its recorded revision, not HEAD.

```sh
bash scripts/setup-foundation.sh
make -C engine -j2
sha256sum engine/pokeemerald.gba
```

Install Linux build-essential, binutils-arm-none-eabi, git, libpng-dev and
pkg-config first. Runtime regression additionally needs libmgba-dev (verified
0.10.5), Python3, Pillow and NumPy. The latest full run is N05 plus the N04
recovered-save extension; see the final sections below for mandatory legacy inputs,
commands and actual acceptance state. Historical S03 runs cover their recorded subset. Never run baseline `make compare` on the custom game.


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

## D01 trap/quest replay

At tested revision `060864c`, run `bash scripts/test-d01.sh` with the documented
toolchain variables. Five production routes84 checks and two explicit fixture
routes30 checks cover optional decline/accept/complete, tag/reward atomicity,
secret/repeat, backtracking, cold saves and actual paralysis/guide cure.
[Evidence and fixed coordinate-trigger defect](evidence/d01/README.md).

## D02 crafting replay

At tested revision `b53b8e6`, run `bash scripts/test-d02.sh` with the same toolchain
variables. Five production routes67 checks and two explicit fixture routes44
checks cover missing/cancel/craft/use, output capacity before consumption, repeated
crafting, cache/medicine effects, cold saves and R02 workshop capacity/repeat.
[Full 111-check evidence](evidence/d02/README.md).

## S01 connected-slice replay

At tested revision `2e8de08292a8a4fe380fda06accdb2b97c798401`, run
`bash scripts/test-s01.sh` with the same toolchain variables. All357 assertions
across18 processes use the production ROM. Prepared/unprepared strategy and
defeat branches copy normal manual flash saves, never injected game state.
[Full logs,30 actual screenshots and route details](evidence/s01/README.md).

## S02 presentation checks

`bash scripts/test-s02.sh` at c9062dabb81341bf0525eead8d89ea7ba62043f5 passes
199 assertions across11 production mGBA processes, with11 empty error logs.
[Evidence](evidence/s02/README.md) records the ROM identity, full logs, route inputs,
actual captures and before/after palette regression. Includes fresh UI/reward
checks, battle/medicine/recovery, four-direction walking and menu crafting/Journal.
Ten hardware-palette assertions detect Donut color loss after map/menu/battle/
reload transitions. Python3/Pillow validates native palettes, packing and budgets.

The rejected initial sprites are replaced with the approved native battle look
and matching exploration art. Current captures were visually reviewed; source
provenance and inherited placeholders remain explicit in the content ledger.
S03 full completion/alternate strategy/defeat regression remains the next gate.

## S03 full-slice acceptance

At50435d1c7db1e6778ad71e639e7a1a8ff4175653, `bash scripts/test-s03.sh`
passes1053 assertions across62 mGBA0.10.5 sessions:860 production/193 explicitly
labeled diagnostic fixtures,62 empty error logs. Production checksum remains
7a0a87273a6b53bd9104afa2029fd99fe6cee93d30f56dc01881b6adbdcb7b72.
[Complete routes, logs,42 actual captures and motion](evidence/s03/README.md).
Continuous route25m16.655s includes scripted waits and automated battle input;
a novice's20–30minute playtime remains a human-playtest question. No midroute
reboots/savestates in that timing. Other sessions intentionally cold-load saves.
The runner creates separate fixture ROMs for capacity/status/exhaustion checks;
never distribute those as playable builds. No save layout changes in this task.

## I01 final review regression

Install Python3/Pillow/NumPy in addition to the existing build/mGBA dependencies.
At81b232ae41647b5e456e45ed73d51a170f17fb58, `bash scripts/test-i01.sh`
passes1053 runtime assertions/62 sessions (860 production,193 labeled fixture),
62 empty error logs,9 exact native rendered-image checks and clean-source guard.
ROM SHA256:f46643a4a2eb0065e75ed33ea2baafe533d5508a8ee45922282108e778e43948.
[Complete evidence and precise limits](evidence/i01/README.md). Two full content
regenerations preserve7385 art files; palette text line endings are normalized
according to upstream attributes. PNG comparisons are exact.

Six saved retry routes prove re-entry only; wins are checked separately. Prepared
play has the successful uninterrupted fresh route; unprepared victory is segmented.
90,586 emulated frames include53,700 fixed idle frames; this does not prove human
pacing. User playtest remains the next gate, before any Stage6 expansion.

### N01 native rooms and older-save compatibility

`bash scripts/test-n01-rooms.sh` runs434 assertions from a clean committed build.
For the additional41 older-save checks, first reproduce the ordinary I01 saves
using tested81b232a and its `scripts/test-i01.sh`, then set `DCC_LEGACY_RUN` to
that run directory. The runner copies motion.sav, craft.sav and playtest.sav,
records input hashes, and loads them normally. No binary fixtures are committed.
The DCC map viewport is a render cache: reload reconstructs current authored
metatiles and applies existing state flags, avoiding stale atlas IDs. Matching
static object graphics refresh from current headers without resetting progress.
Save structure is unchanged; tested cases/limits are in evidence/n01/rooms.

`python3 scripts/content/slice_art.py` delegates native rooms/props to
`environment_art.py`. Accepted PNG masters are authoritative; partial reference
source omissions do not prevent deterministic game export. Do not claim complete
source-sheet reproduction or publish the omitted source/packed artifacts.

N02 full regression: `DCC_LEGACY_RUN=/path/to/I01/run
DCC_CORNER_SAVE=/path/to/N01-normal-corner.sav bash scripts/test-n02.sh` (set both
on one shell command). Accepteddec2c5e,73 processes/1210 checks:1017 production,
193 diagnostic fixture. Includes all newer Journal/alternate-order/legacy checks.
See evidence/n02/final for exact inputs, clean build, raw runtime, actual forward
and center views,26-cell geometry contract and two corrected route obstructions.

### N03 full acceptance

Both N02 and N03 full runners now require the ordinary legacy inputs; missing
variables/files stop before a build. There is no implicit partial full-pass mode.
Use the same pinned environment documented above, then:

```sh
DCC_LEGACY_RUN=/path/to/completed/I01/run \
DCC_CORNER_SAVE=/path/to/ordinary/N01-corner.sav bash scripts/test-n03.sh
```

N03 testedb530fa6 passes76 sessions/1303 assertions (1110 production,193 labeled
fixture) and38 actual rendered comparisons. The full-success message enforces
those totals. N02 enforces73/1210. Exact inputs, complete logs, current state views,
source export checks and the runner-only validation are in evidence/n03/final.
The production ROM copy remains separate from the diagnostic fixture rebuilds.

### N04 exact recovered-save victories

`DCC_RECOVERY_BASE_RUN=/path/to/accepted/N03/run python3 scripts/test-n04.py`
extends all six accepted retry inputs to victory, manual save and cold reload.
It requires the76/1303 baseline, checksum and identical engine/harness source;
no engine rebuild is claimed for this test-only task. Test-sourceee340e1 passes
12 production sessions/216 checks and12 empty errors. Same-ROM combined coverage
is88 sessions/1519 checks. See evidence/n04 for exact inputs, outcomes and snapshots.
This supersedes the earlier re-entry-only qualification for compiledb530fa6.

### N05 final overnight acceptance

Use the pinned environment above and both required legacy inputs with
`scripts/test-n05.sh`, then set `DCC_RECOVERY_BASE_RUN` to its accepted run and
execute `python3 scripts/test-n04.py`. The latter now accepts the exact N03
76/1303 or N05 78/1315 baseline, validates the two six-check guide routes for N05,
and still rejects engine/harness mismatch or missing fixture coverage.

Tested eaf073d434a9347dfc2ed921f5f44d163563964b: clean production build,
78 sessions/1315 checks plus12 recovered-victory/cold sessions/216 checks on the
same ROM. Combined90/1531, with1338 production and193 labeled fixture assertions;
90 empty emulator error logs;38 exact rendered comparisons. Production checksum
and complete raw logs: [N05 evidence](evidence/n05/final/README.md). First-use
instruction preserved; before/after-trial repeat control return visually verified.
Prepared continuous completion and segmented unprepared wins remain distinct.
Human playtime is not inferred from scripted waits.

## Opening-field diagnostic preview (F1-G01a)

Use the pinned build environment and accepted A01 artifact path with
`scripts/test-f1-g01.py`; disposable snapshots only. Follow
[exact reproduction, identities and evidence](evidence/floor1/g01/README.md) for
read-only whole-buffer/cold checks and continuous frame capture. Do not load
diagnostic map35/0/layout448 saves into production. Candidate doors/bays and
closed/open loop variants do not implement live state or migration. Geometry
travel still fails its comparison, so these checks do not unblock V01 or finalT.
