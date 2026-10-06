# Durable checkpoint

Handoff date: 2026-10-06. **Stage 0, E01, E02 and B01 complete; B02 active.**
This is a restartable checkpoint, not completion of the authorized Stages 0–5.
Single implementation writer: this Cloud task. Parent explicitly resumed E01.
Cloud task: `01a10f4b-596b-700b-b8ba-241e3ca2c000`.
Parent/source thread: `01a10e89-0c59-737a-8ede-620d02be2034`.
Parent owns sole continuation automation `6ac46da8df5881918271382eed68361e`:
hourly flexible schedule anchored 2026-10-06 03:40:24 UTC; skips active/uncertain
tasks, resumes idle checkpoint, stops at awaiting user playtest. No scheduler here.

## Initial reconciliation

Local branch `work` was unborn, no tracked/untracked user files. `git ls-remote
origin` returned no refs. Connected GitHub branches and PR searches returned empty.
Parent's independent read-only audit confirmed no commits, files, PRs, Actions
runs or rulesets; classic protection read was 403, not proven absent. No prior
instructions, `.agents/skills`, checkpoint or running implementation process found.
No relevant local missing skill reference to install. All three complete source
Pages read successfully and copied into docs with links and handoff date.

## Execution capability

Saved Cloud environment provides shell, Git, GCC, Make, Python. Initial environment
lacked ARM binutils, PNG development headers and emulator. Packages are being
extracted under /workspace/toolchain without changing system installation.
Git network reads work. `gh` GraphQL and REST reads return Forbidden; connected
GitHub tools successfully read branches/PRs. No Cloud submission/status tool is
exposed inside this worker; parent reconciles running Cloud tasks. Do not duplicate.

Upstream selected: `pret/pokeemerald` at
`731ad5bfd6e6f265508d0efcca0ba42f9dcf5881` (2026-10-01).
Compiler selected: `pret/agbcc` at `da598c1d918402c42c0c0d7128ba14567f3175e9`.
The upstream workflow has push/PR CI and symbol-branch writes, no schedule; preserve
its text as provenance but do not activate it in this repository.

## State

Implemented: F01 pinned engine, setup/build scripts, emulator harness and evidence.
Compiled: PASS, matching upstream ROM. Runtime verified: PASS, real mGBA title →
New Game menu → Birch introduction from fresh state. Merged: PR #2 at
`1af617261881fcc26c6bb0fbd924d4c8a3c56d9a` (server-confirmed merge).
No gameplay changes. Stages 1–5 and improvement cycles not started.

## F01 checkpoint — 2026-10-06

Branch: `task/f01-foundation`. PR: https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/2
Base: `8ac45a70f39bddf5fd50de7b3a40f436784ee3b8`, docs-only initial main commit.
Engine/build tested: `ef471fc90335bacce3e23aa6349fd7eea80e958e`.
Final runtime harness and route: `e9c8df785c4ed438a8d8938118c69c65349f4ec9`.
All commands, checksums, limits and observed frames: [F01 evidence](evidence/f01/README.md).
Clean separate checkout + fresh agbcc cache also builds the identical ROM; fresh
OS provisioning remains F02. Source import audit found all retained files match
upstream exactly. No generated ROM/build binary tracked. No workflow activated.

Resolved setup issues: initially absent apt lists; PNG development package missing
matching shared runtime; strict C mode incompatible with mGBA headers (use gnu11).
No current build/runtime blocker. GitHub CLI reads remain Forbidden; Git push and
connected GitHub PR creation work. Classic branch protections unreadable; honour
server merge result. F01 merged successfully without bypassing protections.
Next action: F02 provision a fresh environment and reproduce matching build/boot.
Only then select E01 tutorial room. Never claim the adaptation is playable yet.

## F02 start — 2026-10-06

Branch: `task/f02-reproducible-environment`; base/merged F01:
`1af617261881fcc26c6bb0fbd924d4c8a3c56d9a`. Docker daemon 28.4.0 is available.
Objective/scope/acceptance in backlog. No gameplay changes. Initial Cloud Git
refspec fetches only HEAD; explicitly fetch `refs/heads/main:refs/remotes/origin/main`
before reconciling main. Do not assume a plain `git fetch` updates origin/main.

## F02 validation — 2026-10-06

Implemented: digest-pinned Debian environment, captured-commit validation launcher,
dirty compiler-cache rejection and strict mGBA runtime checkpoints.
Compiled: PASS in fresh OS/container with empty compiler/source cache.
Runtime verified: PASS, all three frame fingerprints and visual screenshot review.
Ten positive/negative tests PASS. Merged: PR #3 at
`03353fb3f1287074102a5bc98df4f19b0d4c189f` (server-confirmed).
PR: https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/3
Tested commit: `fcf3bd049e5369b8fcc3015244fe53c2f557e744`; base:
`1af617261881fcc26c6bb0fbd924d4c8a3c56d9a`.
Commands/results, package/image identity and screenshots:
[F02 evidence](evidence/f02/README.md). Build/ROM identity remains F01's exact hash.

No current build/runtime blocker. Managed Docker proxy/DNS/CA and writable client
cache issues are resolved and documented; do not retry old failed approaches.
No engine changes in F02, no ROM artifacts in Git, no running test container.
Next: E01 on a new branch from current main after reconciling remote PR/task state.
E01 objective: Carl overworld presentation, one authored tutorial room, readable
interaction and an exit; test four directions, collision, transition and save/reload
in the emulator. Audit actual map/start/save paths before editing. Record any
placeholder assets and deliberate Book 1 chronology compression in content-ledger.
No battle engine or save-layout changes in E01; B01 follows its own narrow task.
Use custom-build identity/runtime checks, not a false stock `make compare` pass.

## Continuation checkpoint — 2026-10-06

F01 merged in PR #2 at `1af617261881fcc26c6bb0fbd924d4c8a3c56d9a`.
F02 merged in PR #3 at `03353fb3f1287074102a5bc98df4f19b0d4c189f`.
Checkpoint documentation branch: `docs/stage0-checkpoint`, based on that F02 merge.
Working source and validation scripts are committed; no pending implementation
edits or unresolved build/runtime failures. No CI workflows or schedules added;
validation evidence is local execution committed to `docs/evidence/f01` and `f02`,
not GitHub Actions checks. Parent's sole hourly continuation remains responsible
for resuming this Cloud task after its current turn ends.

Exact next action: explicitly fetch main (`git fetch origin
refs/heads/main:refs/remotes/origin/main`), read this checkpoint and live PR/task
state, create a single E01 task branch, audit `engine/src/new_game.c`, map/layout
data and starting-field flow, then implement and runtime-test the narrowly scoped
tutorial room described above. Preserve baseline history and evidence. Do not
repeat upstream import, create another writer or create another scheduler.

Stages 1–5, full fresh-save slice completion, defeat/reward/save regression,
original scheduled assets and post-slice improvement cycles remain outstanding.
Stage 6 is still gated on the user's eventual playable-slice review. No playable
DungeonCrawlerCarlemon adaptation or public release has been delivered yet.

## E01 active — 2026-10-06

Branch `task/e01-tutorial`; base `fbc28d44529347e5f4f24108c1f9b7a518729b6a`.
Reconciliation: main clean/current, no open PRs or concurrent implementation work
observed. The parent reported an environment-disconnected notification at 04:10;
actual shell and live emulator calls succeeded at 04:10:52 UTC, so execution was
available and no duplicate writer was started.

Implemented: fixed Carl new-game identity, authored entrance/returnable landing,
original walking sprite/palette, original intro/crate/rock text and existing save
flag bits 0x20/0x21. No battle/party or save-structure changes. Stock title/UI and
tile/object art placeholders are explicit in content-ledger.
Compiled: PASS (custom ROM; stock comparison deliberately not used).
Runtime: exploratory real mGBA route passed 16 map/position/flag assertions,
normal manual save and a separate-process cold reload. Final committed replay
with recorded routes is next, including repeat crate interaction after reload.
Merged: no PR yet. No current blocker. One C compile error from inline use of
Emerald's text macro was fixed with a named static string; dialogue timing was
calibrated to allow pages to finish. Neither required engine/save changes.

Save policy E01: format/layout unchanged, existing unused flag bits allocated and
new maps appended. Start a fresh E01 save; stock baseline saves are not supported
as crawler campaign starts. Cold reload of an E01 in-game save is required before
merge. Test runner `scripts/test-e01.sh` records commit, custom checksum, button
routes, read-only RAM assertions and screenshots. It never writes game RAM.

## E01 final validation — 2026-10-06

Tested commit `b28143b56f9413ff211473a70ca8429414335412`. Implemented: YES.
Compiled: PASS. Runtime verified: PASS, 16 fresh-game plus 3 separate-process
cold-reload assertions; final screenshots visually inspected. Merged: PR #5 at
`91afb3deb6f856b4565e00bb65e81f0f1497a05f` (server-confirmed).
Full commands, checksums, inputs, logs, screenshots and limits:
[E01 evidence](evidence/e01/README.md). No current blocker. Follow-up commits for
this task are documentation/evidence only. Review found no save-layout or battle
changes. Title/menu/tile/music placeholders and missing Donut presentation remain
explicit; this is a tutorial increment, not the completed slice.

Next after E01 integration: B01 (dependency F01 already passed), a narrow Carl/Donut
duo encounter prototype with both actors and victory return. This ready task
enables meaningful protagonist recovery validation in E02; no change to the
authorized scope. E02 safe-room guide/recovery is still pending, not silently done.

## B01 start — 2026-10-06

Branch `task/b01-duo-prototype`, base `91afb3deb6f856b4565e00bb65e81f0f1497a05f`.
E01 PR #5 merged; main explicitly fetched and fast-forwarded. Single writer.
Contract in backlog. Two fixed protagonist records and one optional double-battle
trial; trial-specific callback restores both and returns to the current map on
loss, never the old hometown. Both victory and ordinary-input defeat/retry require
runtime checks. No save-layout changes; fresh B01 save required. Battle species,
sprites and trainer labels are technical placeholders, not final character art.

B01 exploratory runtime: both actors spent offensive PP; victory restored both
and returned movement; deliberate support-only defeat restored both with trial
flag unset, and re-entry started a new four-battler encounter. Corrected the
explicit post-battle script continuation and suppressed trial-only stock whiteout
text. First cold-save check correctly failed because the input route had not
confirmed the fully displayed overwrite prompt; adjusted the route, not save code.
Final committed replay and evidence still pending. No scheduler/workflow added.

B01 first committed replay passed 38 assertions at f90d227. Review then found the
placeholder Meowth Pickup ability could silently award random items. Disabled it
using the existing unused ability slot (ABILITY_NONE), without a species-table or
save-layout change. Battle assertions now also require Donut's ability to be NONE.
Rerunning the committed revised build before declaring final runtime verification.

## B01 final validation — 2026-10-06

Tested `9fc11212c465008e3571d9f77e98b41454ce919d`, base `91afb3deb6f856b4565e00bb65e81f0f1497a05f`.
Implemented YES; compiled PASS; runtime verified PASS (38 assertions, empty
emulator error logs, visually inspected screenshots); merge pending PR integration.
Commands, input routes, ROM identity and evidence: [B01 report](evidence/b01/README.md).
Single writer; no running implementation duplicates or open PRs found before
integration; origin/main still equals the recorded base. Diff reviewed; no
save-layout change or committed ROM/save/build executable. No B01 acceptance blocker.

Exact next task after integration: E02 safe-room guide and recovery service, with
original spoiler-limited dialogue and a meaningful damaged/depleted-roster recovery
route. B02 actions/resource/incapacitation coverage and B03 capture/storage audit
remain pending. E02 must not be marked done from the trial's healing callback.
The nonblocking baseline-harness unsigned-overflow defect remains in the backlog
for its own validation-only change. Full Stages 0–5 slice is incomplete.
Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`; parent owns the sole continuation
mechanism. No new workflow, schedule, public playable release or binary artifact.

## Screenshot reporting handoff — 2026-10-06

Parent relayed Kurt's request for screenshots on each gameplay issue/PR. Added the
requirement to AGENTS.md and testing.md. B01 PR will embed real final-run action,
recovery and saved-state captures; E01 PR #5 is being backfilled using its existing
verified evidence. Parent handles the current chat preview; no duplicate delivery.
Repository issue search returns only an item titled Deleted (#1), no known live
E01/B01 gameplay issue; verify before any issue-body mutation. No new issue or
implementation writer is needed merely to duplicate the PR evidence.

Parent's E01 review follow-up: corrected ledger wording to two eastward rock
approaches; optional rock dialogue and landing crate remain unexercised. Archived
E01 compiler log is abbreviated; do not rebrand it as raw complete output. B01
retains raw complete logs and rejects nonempty emulator error logs. Its runner now
exports the committed source with git archive, regenerates all game assets and
uses pinned setup inputs, excluding workspace generated/untracked contamination.
E01 PR #5 screenshot backfill succeeded. Issue #1 is confirmed closed/not_planned
with title Deleted and no body, so it was preserved unchanged.

Isolated runner review caught three build/hash/symbol paths still relative to the
workspace. Corrected them to the snapshot, then stopped the exploratory run and
committed the correction before starting final verification. The interrupted
run-ufeHbo is not accepted evidence; no game-state or source data was discarded.

## B01 isolated verification — 2026-10-06

Final tested source `0e5e6a46e02252ed76dd06a1025dca2c92649ec9`; clean git archive,
pinned compiler rebuilt, all game products generated from scratch. ROM SHA256
`e6692036e3804d20d585ab6d0086fcf276d4d71561c105f6135f858152f4f8fd`, identical to
prior workspace build. Implemented YES; compiled PASS; real mGBA runtime PASS:
38 assertions, four empty error logs, fresh captures reviewed. Complete raw build
and setup logs and checksums replace earlier incremental B01 evidence. See report.
PR #6 opened as draft with actual screenshots; final evidence update and authorized
integration are next. No source/runtime acceptance blockers remain. No other
active writer/task/scheduler was created. E01 PR #5 screenshot backfill confirmed.

## Integration checkpoint — 2026-10-06

B01 PR #6 merged, server-confirmed commit
`86160253801b53dd7b1cc8c6ee417422779a1651`. Its tested source is
`0e5e6a46e02252ed76dd06a1025dca2c92649ec9`; final pre-merge head
`335c62fbcfbc27b442874d75685e4020c736a5fd` changed only documentation/evidence
since that test. Main explicitly fetched and fast-forwarded; no user work removed.
Implemented YES / compiled PASS / runtime verified PASS / merged YES.
[E01 PR #5](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/5) and
[B01 PR #6](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/6) embed actual
emulator screenshots labelled by tested commit and route; no live gameplay issue
exists to backfill. Nonvisual checkpoint screenshots are N/A; these PRs provide
relevant actual visual evidence. Complete raw logs intentionally retain upstream
trailing spaces; authored source/docs whitespace checks exclude only raw log files.

Next continuation: reconcile current main/PRs and this checkpoint, then branch for
E02 (safe room, guide, recovery). Contract in backlog. Require an ordinary-input
route with genuinely injured/depleted protagonists, guide recovery, return path,
and cold save reload; do not mark recovery proved merely because an already-healthy
party remains healthy. Keep the B01 trial loss bypass of stock lastHealLocation;
any newly reachable losing encounter needs its own safe-return runtime check.
Only one writer, no duplicate Cloud task or scheduler. This run stops at a clean
reviewable increment so the parent-owned mechanism can resume E02. No E02 gameplay
was started. The complete Stage 5 slice and final user playtest package are pending.

Remaining known follow-ups: baseline boot harness unsigned-overflow validation;
E01 optional rock/landing-crate dialogue routes; B02 skills/resources/incapacitation;
B03 no-catching/storage audit; R/D/S tasks and original final battle assets. No
current access/build/emulator blocker. Cloud task ID remains
`01a10f4b-596b-700b-b8ba-241e3ca2c000`. Parent continuation only; no new workflows.

User visual-quality clarification relayed by parent: functional cave placeholders
are not final. Scheduled custom dungeon/protagonist art, environmental detail,
palettes and layout polish remain S02 acceptance within the slice. Recorded in the
content ledger; actual before/after engine captures and remaining-placeholder list
required. Gameplay dependency order remains unchanged; no scope/platform expansion.

## E02 start — 2026-10-06

Parent requested immediate continuation. Main reconciled at
`66bcbb3c6b8cc0600a0108b56a882942db12ae24`, clean tree and no open PRs.
Branch task/e02-guide-recovery; tracker #10. Backfilled completed E01/B01 issues
#8/#9 with real screenshots, assertions, tested commits and PR backlinks; closed
as completed. Existing Deleted issue #1 preserved. One writer, no new scheduler.
E02 moves victory restoration to a guide so ordinary play can test real injured/
depleted recovery, preserves automatic defeat recovery, and updates promised text.
Current implementation not yet compiled/runtime verified/merged. Fresh saves
required for reproducible milestone tests; save layout unchanged.

E02 exploratory emulator checks: guide restored actual party HP 22/16→30/26 and
persistent PP 32/17→35/20; repeat use passed. Return route initially ran into the
trial attendant, correctly failing the map assertion; rerouted through the clear
row below the attendant. Full revised recovery route passes 16 checks. No runtime
claim yet for curing nonzero status. Corrected README build instructions to use
the custom-game build on current main; matching-stock comparison is Stage 0 only.
Final isolated committed replay and screenshots pending; no implementation blocker.

E02 cold save reload passed 7 checks, including healed persistent HP/PP, guide
flag and repeat dialogue. A preliminary pre-trial test using an old B01 save
correctly failed: the saved map object list lacked the newly added guide. Treat
E02 as fresh-save-required (documented); final tests start a new E02 game. This is
not a claim of save migration. No new engine workaround or forced save rewrite.

## E02 final validation — 2026-10-06

Tested source `520aebaf04503be97218966bfb36c35f1958cdb6`, isolated pinned build and
55 real mGBA assertions passed. Five empty emulator error logs. Actual party HP/PP
restoration and cold reload proved; nonzero status curing remains explicitly
unverified. Screenshots visually reviewed. [Full evidence](evidence/e02/README.md).
Implemented YES / compiled PASS / runtime PASS / merge pending scoped PR.
No E02 acceptance blocker. After integration continue B02 without routine pause.
Issues #8/#9 backfilled and closed; #10 tracks this task and receives final captures.

## E02 integration / B02 start — 2026-10-06

PR #11 merged at `471a9c183752ed27f8bfa51b5a451f6722d1e69b`; issue #10 closed with
actual final captures and PR backlink. E02 implemented/compiled/runtime/merged YES,
55 checks. Current main fetched/fast-forwarded, clean tree, no open PR. Continue
without routine pause: B02 branch task/b02-crawler-actions, base equals that merge.
Task issue #12: four dedicated crawler moves using existing effects/animations,
resource depletion/alternative action, both support effects, one/both incapacitated,
local recovery, guide restoration and cold reload. No new framework/save layout.
Fresh B02 save required; original skill names are adaptation choices, not canon.

B02 source compiles successfully. Real mGBA fresh game reached both new action
menus; first offensive turn spent STRIKE 8→7 and SPARK 2→1. Runtime acceptance is
still in progress (depletion/support/incapacitation/reload), not claimed complete.
No command/environment stall or active blocker. Parent requested checkpoint and
was given E02 PR #11/merge/test details plus B02 issue #12 status. Sole writer.

B02 exploratory victory and guide route passed 21 checks before extending party
resource assertions. Empty SPARK refuses the choice with PP unchanged; WEAKEN
permits continuing to victory. BRACE raises defense and WEAKEN lowers both attacks.
Support-only route: Carl fainted with Donut still at 1 HP; Donut then acted (WEAKEN
uses 30→29 while Carl's BRACE stayed 30), then both fainted. Local recovery/retry
passed. New `uses` assertions cover all four real party resource slots; cold reload
passes 10 checks with 8/40/2/40 restored. Final 83-check isolated replay pending.
Source branch remains the only writer; environment available after 05:15 notice.

## B02 final verification — 2026-10-06

Tested `3bd031cb00439fdb4433930e5972fcce2bf01b84`: isolated pinned compiler/game
build and 83 real mGBA checks passed, five empty error logs, screenshots reviewed.
Both support effects, empty action rejection/alternate choice, surviving actor
acting, both defeated/local retry, all four party resources restored and saved.
[Complete evidence](evidence/b02/README.md). Implemented YES, compiled PASS,
runtime PASS, integration pending. No blocker. B03 is next after scoped merge.
Inflicted-status healing remains explicitly pending, not inferred from zero status.

## B02 integration / B03 start — 2026-10-06

B02 PR #13 merged `4c76d692b37a2fa934e89e4b057e0b83568e64f0`; issue #12 closed.
Implemented YES / compiled PASS / runtime PASS / merged YES. Main reconciled,
no open PR, one writer. B03 issue #14 and task/b03-no-collection based on that merge.
Initial guards/UI compile; emulator validation in progress, no runtime acceptance
claim yet. Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`, parent owns continuation.
No new workflow/scheduler. Next: verify roster/pockets, defensive collection fixture
and B02 regression, then scoped review/PR. Fresh saves required, layout unchanged.

B03 exploratory menus pass 14 assertions: roster/actions/summary return, all four
non-capture pockets in both directions and wrap, unchanged duo/resources. Initial
label clipping fixed; navigation test corrected after tracing actual screens.
No game softlock found. Separate GBA-side API fixture and isolated complete replay
pending; production gate remains unverified until those finish.

B03 validation correction: first isolated attempt `a763280` compiled and passed
setup/menu/guide, but the historical B02 loss route failed its exact HP checkpoint:
Donut fell first and both were already restored by that frame. No defeat softlock.
New observed route proves Donut down/Carl acting (BRACE 33→32 while Donut remains
33), both down and full recovery/retry: 19 checks pass. Victory/depletion passes
28 unchanged checks. Battle inventory adds 10 checks. Fixture initially failed to
link because upstream linker discards unused libc memcmp; replaced with explicit
byte comparison, then all 3 fixture assertions / mask127 passed. No production
engine workaround or RAM injection. Final isolated suite still pending.

Parent B02 review independently confirmed 83 assertions, 33 evidence hashes and
14 PNGs. S03 still needs total action exhaustion, depleted/immediate-defeat saves,
and actual nonzero-status cure once status encounters exist. B03's new route covers
the complementary Donut-down/Carl-acting case; preserve both milestone records.

## B03 final verification — 2026-10-06

Tested `769196afc57635b98aa2de8b9ddc43ed1847a4ef`, isolated pinned build and 110
mGBA assertions PASS. Eight empty error logs, 17 actual PNGs visually reviewed.
Production ROM `8ffe93dde477e54c9d23a52532e73b1ca7087595250afc3b8b0ed16384256f2d`.
[Full evidence](evidence/b03/README.md), [audit](collection-audit.md). Implemented YES,
compiled PASS, runtime PASS, integration pending scoped PR. No current blocker.
Next after merge: R01 XP/equipment, one writer, no new scheduler or expansion.

## B03 integration / R01 start — 2026-10-06

PR #15 merged `4a27fc4b082b8d8b6dfa1840eb6d5f01ce554363`; issue #14 closed.
B03 implemented/compiled/runtime/merged YES. Main reconciled, no open PR.
R01 issue #16, task/r01-xp-equipment based on that merge: existing XP/stat growth,
one optional held WRIST WRAP, persistent acquisition/equip/take/XP and cold reload.
No save-layout change. Compressed tutorial starts 20 XP before level9; original
adaptation choice, not canon. Gear is optional; no mandatory item spending.
Fresh milestone save required. Compile/runtime/integration pending. Next: compile,
normal acquire/equip/combat and XP routes, no-gear victory, cold reload/repeat.
Cloud task remains `01a10f4b-596b-700b-b8ba-241e3ca2c000`; single writer, parent scheduler.

R01 source compiles. Exploratory fresh save passes16 existing movement/save checks;
acquire/repeat/equip/save route passes15 checks. Ordinary cold boot confirms
Carl held-item377 and zero duplicate bag quantity. Both equipped/plain trial opens
pass7 checks each. New RAM-read diagnostics report level/XP/held item, actual stats,
bag quantities, flags and foe HP; no game RAM writes. XP dialogue/level sequence,
full win/reload, equipment fixture and isolated acceptance remain in progress.

R01 exploratory routes now pass: setup16, plain victory25, acquire/equip15,
held-item defeat/save23, cold defeat/retry9, equipped victory/depleted save24,
depleted reload/guide/take/re-equip/save20, final cold repeat12; separate fixture
setup19 and full-bag/free-space/retry11. Carl attack20→23, Donut magic13→14 at level9;
XP399→495 and709→805 persist. First foe after opening turn: equipped12HP versus
plain14HP; fixture real damage calculation10→11 at fixed inputs. Defeat preserves
held gear and XP, then cold retry works. Full-bag refusal leaves flag unset;
tossing one Potion allows exactly one wrap. Input routes were adjusted for extra
level-up pages and menu return states; no engine failure found. Final isolated
committed replay pending; compilation alone is not acceptance. Next run test-r01.sh.

## R01 final verification — 2026-10-06

Tested `d9db8b3a61fa36035236cb5764f732ea20d88736`, clean isolated pinned build;
174 mGBA assertions PASS, ten empty error logs,18 actual PNGs visually reviewed.
Production ROM `aece986da533253d66fa77151d2972d81160002e5fbd17bd8374d50c400355d0`.
[Full evidence](evidence/r01/README.md). Implemented YES / compiled PASS / runtime
PASS / integration pending scoped PR. No blocker. R02 persistent achievements and
loot is next after merge. Depleted/immediate-defeat saves now covered, while actual
status curing and total action exhaustion remain explicit S03 edges. No scheduler.

## R01 integration / R02 start — 2026-10-06

PR #17 merged `5a0fd8eaef6b4746c745e128bd9923f00afeeee0`; issue #16 closed and
body updated to merged. B03 PR #15 merge remains `4a27fc4b082b8d8b6dfa1840eb6d5f01ce554363`.
Parent independently confirmed B03 110 and R01 174 (144 production/30 fixture)
checks without material blocker. Main reconciled, no open PR. R02 issue #18 and
task/r02-achievements-loot start here: two authored achievements, two deterministic
boxes, unique persistent IDs, capacity/repeat/reload correctness. No new maps,
save layout, random loot model or scheduler. Compile/runtime/merge pending. Fresh
save required for new map objects. Next: compile and build input-driven reward
routes, including full-stack/full-bag atomic failure and successful retry.

R02 source compiles. Fresh setup-rewards route passes32 checks: both locked states,
reader achievement/repeat, exact Potion grant/repeat and save. Trial route reaches
both level9 and sets the duo achievement,31 checks before adding workshop/use
steps. Extra dialogue required a replay close-state adjustment; no source game
failure or blocker established. Capacity fixture prepares all slots occupied with
Potion98 to prove an attempted grant of2 neither partially grants nor consumes its
flag; after tossing1, retry should grant2 to99. Final acceptance still pending.

R02 exploratory routes complete: setup32, victory/loot/use53, cold reload/map
re-entry34, final cold13; explicit full-stack fixture28 and cold fixture repeat9.
Both achievements and both box states survive reload/re-entry. Potion2→1 after
healing Donut12→28; use at full health does not consume the remaining Potion.
Repeat boxes leave Potion1/Scrap2 unchanged. Failed two-Potion reward at stack98
and full bag leaves98 and flag unset; tossing1 then retry grants exactly2 to99,
repeat and cold reload retain99. Menu timing for toss confirmation was adjusted;
no production source fix was necessary. Final isolated169-check replay is next.

## R02 final verification — 2026-10-06

Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`, single writer on
`task/r02-achievements-loot`; base `5a0fd8eaef6b4746c745e128bd9923f00afeeee0`.
Tested `fbfb9e9cad1854b5b03e2a006d1ed1745348f365` with isolated
`bash scripts/test-r02.sh`:169 PASS (132 production/37 fixture), six empty errors,
17 visually reviewed actual screenshots. Production SHA256
`dec6f1db138ed1a622da477cf14495086fe5ea7c20ca9caaa6b5016a3f42ab32`.
[Evidence](evidence/r02/README.md). Implemented YES / compiled PASS / runtime PASS /
merged NO, pending scoped PR and issue #18 integration. No blocker or unsuccessful
production fix; exploratory replay timing adjustments resolved dialogue/toss states.
Next: push evidence, draft/review/merge R02, reconcile main, then D01 trap/secret/
optional quest. Parent owns sole continuation; no new workflow/schedule created.

## R02 integration / D01 start — 2026-10-06

PR #19 merged `ae4679e2e19a94fd60ac879c9dd18e89f7de2c41`; issue #18 closed
with actual screenshots and merged state. Evidence commit `de8af8914a030bbfb41769de8a74f339f0144e74`,
tested implementation `fbfb9e9cad1854b5b03e2a006d1ed1745348f365`. Main clean;
no open PR. D01 branch `task/d01-trap-secret-quest` starts at this merge.
Objective: service room, marked avoidable nonlethal trap, optional secret and
retrieval quest with persistent decline/accept/complete states and repeat safety.
Two original neutral crawlers; no canon claims. Existing guide must cure actual
inflicted paralysis. No save-layout/battle/crafting expansion or scheduler.
Implemented/compiled/runtime/merge pending. No blocker; next author room/events.

D01 issue #20 source implementation compiles. New Service Room links via the west
landing ladder; authored optional Mara/Lev dialogue, retrieval key item, atomic
Scrap reward, hidden medicine and marked single-use trap. Trap bounds HP at1 and
uses paralysis (no step damage). No save-layout changes. First runtime route now
checks fresh access and decline/save; final acceptance not yet established.
