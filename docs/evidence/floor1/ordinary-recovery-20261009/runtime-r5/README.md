# Actual r5 result — fresh manual Save passed; setup STOP40

First unexpected gameplay failure preserved. No retry or dependent patrol/cold
execution. [Exact original/private and public-extract log hashes](log-hashes.json)
keep raw telemetry private; public extracts contain only PASS/clock/result lines. [Exact summary](summary.json), [STOP](STOP.json),
[read-only diagnosis](seed-stop-diagnosis.json) and claims/logs below distinguish
new ordinary executions from historical six baseline/four candidate runs.

Publication base6e4b8d4573c717b12c4da91b17027dec0ec67955;
preparation/helper sourcefca57ec86ed41122c81dace994201b6dc9fe26bd;
pre-execution freeze and both execution claims9b2cdee62eabb71fe1b82d8975ce009725e004de.
Tested main is c6d647a815ffce44a2419a2cf83b6c2c094359f0. Reused one main build;
no new game build/tool acquisition. Its actual ROM/ELF/compiler/libmGBA hashes
remain in [frozen identity](identity.json). Recovered compiler identity stays
qualified; original byte identity/oracle/legacy inputs remain missing.

## Actual ordinary executions

1. Fresh New Game, note, supplies, guide, trial and actual first manual Save:
   exit0,54 assertions,19642 frames,8308 trial battle frames. [Claim](fresh/execution-claim.json),
   [inputs](fresh/input.route), [safe log extract](fresh/replay.log), [errors](fresh/errors.log).
   Save SHA256 f866e7c61a7bb91333822d435a3ad9f395ec62839bf5c4dc7c939b15b48c8281.
   [Safe full persistence report](fresh-save-result.json): all14 latest native
   sector checksums,600 party/count,300 flags,1272 canonical resources, counter,
   map/position exactly equal the legal live saved checkpoint. Carl/Donut9/9,
   XP495/805, HP17/33 and24/28, clear statuses, uses3/40/0/37, friendship75/75,
   counter50, two Potions, no Scrap, map35,1 at10,7; trial set, patrol/boss flags
   unset. This is a successful trial Save, not the requested patrol-complete Save.
2. Setup independently Continues that Save and earns Scrap in volatile gameplay.
   Actual Bag/field-context/party/healed readiness pass at55/0/50/4 wait frames.
   At absolute3040, the next item-count command hits inherited native field-only
   gate and returns40 while the real party callback is still running. Exit40,
   13 assertions. [Claim](seed/execution-claim.json), [inputs](seed/input.route),
   [safe log extract](seed/replay.log), [error](seed/errors.log). The actual stop image shows
   Donut28/28 HP and the ongoing healing message. Ownership/PP post-use assertions
   and return-field were not reached; no pending setup Save or guide recovery.
   Input/output flash Save hashes remain exactly the successful fresh hash.

Totals: two new ordinary emulator processes, one trial encounter, zero patrols,
zero final full-state cold executions, zero gameplay retries. The legacy
PATROL_CLOCK battle_attempts field is patrol-only; zero there for fresh does not
mean no trial. The initial-stage adapter separately forbids a second trial and
requires trainer855; fresh victory/assertions and8308 battle frames establish
its one actual encounter. No Warden, candidate pair, merge or full-floor claim.

## Actual captures and motion

- [Fresh saved field PNG](fresh/saved.png), [trial start](fresh/battle-start.png),
  [trial result](fresh/battle-result.png), [guide](fresh/guide-rest.png),
  [fresh motion MP4](fresh/motion.mp4).
- [Earned Scrap PNG](seed/scrap-box.png), [owned Potion/stop PNG](seed/stop.png),
  [setup motion MP4](seed/motion.mp4).

All captures are from actual tested main/observer inputs and the two claims;
no emulator replay, recreated historical pixels or missing-oracle substitution.
[Capture verification](capture-verification.json) records4910/760 samples,
240x160 native size, ordinary-speed FPS/durations and hashes. Private FFV1
independently decodes to the exact original RGB hashes for both streams. Public
H264 CRF18/YUV420p viewing copies preserve frame counts/timing and are compressed
presentation exports, not pixel-acceptance oracles. PNGs remain native pixels.
Historical filenames cold.png denote ordinary boot/Continue pictures here; they
are not final independent-full-cold verification evidence.

## Exact dependency-ready next action

Review the narrow setup observation order: return-field; ready; item13=1;
uses3/40/0/37, before guide walking. Item/uses assertions advance no frames; moving
them after the existing native return preserves actual button cadence and both
resource assertions, with field phase required before reads. Native source
shows CB2_UpdatePartyMenu owns RunTasks and the HP-restored task does not switch
to overworld. Keep the field-only gate, native menu readiness and all behavioral
assertions. Freeze a separately named setup claim using the successful fresh
Save; do not repeat the completed trial, use transient STOP RAM as a Save, or
restart this exhausted setup blindly. No proposed ordering was implemented or
executed after STOP. Parent review precedes any further dependent gameplay.

## Retention and unchanged history

All private raw Saves/snapshots/context/RGB, lossless clips and native objects
remain under /workspace/scratch/ordinary-recovery-r5-20261010; no raw file,
ROM/ELF or game executable is added publicly. [Local archive receipt](private-retention-receipt.json)
records verified local bytes, not an independent backup or successful transfer.
The evidence archive excludes ROM/ELF and requires the separate tooling-r3/main
build. Private user-held download or an authorized private connected destination
could be byte-verified after a successful transfer; neither has happened.
Five failed Library uploads and one supported existing-backup download failed,
zero original bytes recovered, cause unknown; no retry. Original oracle/legacy/
lost Save remain missing. All historical six/four, STOP117 at requestedvisual8536
before expectedB8402, wrappers/pins/claims/assertions and accepted nine-district
Floor1 plan remain intact. Active poses remain compiled/offline-only without
runtime acceptance. The pre-execution freeze record follows unchanged.

---

# New ordinary recovery — r5 executable freeze

Parent accepted the narrow archive-verifier correction after r4 STOP. r4 build,
failed preparation and full diagnosis remain untouched. Reused its one verified
integrated-main build; no rebuild or tool reacquisition. Main source
c6d647a815ffce44a2419a2cf83b6c2c094359f0, preparation source
fca57ec86ed41122c81dace994201b6dc9fe26bd.

[Full frozen identity](identity.json), [exclusive preparation claim](prepare-claim.json),
[nine focused offline source cases](source-tests.log) and [preparation result](prepare.log)
are verified before any emulator execution. This fixes only exact expected
archive bytes derived from pinned attributes; actual inputs are never broadly
normalized. All11960 archived tracked engine/helper files pass. Pinned attribute
files themselves remain exact; three untracked multiboot blobs are separately
checked. Tests reject content/attribute corruption, unmarked EOL changes and
missing/extra tracked inventory.

The generated observer compiled once. All51 raw bindings verify, including the
unchanged ordered duplicate healing-task assignment to party_menu.o; four unused
probe bindings remain absent/fail-closed. Native compile-only ABI checks verify
22 constants and3 bitfields. No emulator was invoked for preparation. Exact
host source/binary/symbol/ROM/ELF and four route SHA256 pins are in identity.json.
Fresh/setup route bytes are [fresh](fresh.route)/[setup](seed.route); reviewed
patrol/cold route hashes remain unchanged. No historical behavioral assertion
or source/helper/wrapper/contract/STOP is modified.

The output root is /workspace/scratch/ordinary-recovery-r5-20261010/prepare-01.
Identity freezes one fresh/setup/patrol/cold attempt each,100000 native frames
per stage,36000 per battle,600 wall seconds,13GB total output and7GB free-space
minimum. RGB sampling every4 actual frames is bounded2.88GB per stage; FFV1 uses
native speed and the frozen encoder, never emulator replay. Input Save bytes
must come only from normal gameplay and completed actual manual Saves. Native
party/count/checksums/flags/logical resources/counter/map/legal tile and friendship
checks remain binding. Independent cold must compare complete state and leave
Save bytes unchanged. First unexpected actual gameplay failure is terminal.
Stop before Warden. Reconstructed bytes cannot substitute for missing historical
oracle or legacy-save acceptance; active poses remain offline-only.

This document is the pre-execution freeze checkpoint. Runtime results, actual
screenshots/motion and Save/log hashes will be appended only after their real
execution. No ROM/ELF, private Save/raw snapshot/RGB/context is published.
Workspace-local retention is not a verified independent private backup. Historic
Library5+1 transfer failures and historical six baseline/four candidate counts
remain unchanged; new ordinary counts are recorded separately.
