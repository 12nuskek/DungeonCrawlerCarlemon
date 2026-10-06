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

D01 exploratory cold reload found a real field-input defect: the spent coordinate
script kept starting while standing on the tile, so START could not open Save.
Fix attempt1: disable its coordinate trigger with VAR_TEMP_0 immediately, and seed
that temporary variable from the persistent spent flag on map load. This preserves
repeat/reload behavior without adding a save field. Cold persistence must be rerun;
the earlier in-memory assertions did not prove the attempted save succeeded.

D01 exploratory checks now pass: decline13, accepted/trap16, tag/secret15,
completion/guide22, final cold18; explicit capacity/boundary fixture21 and cold9.
The coordinate-trigger fix passed cold persistence and restored menu access on the
spent tile. One production defect fixed on first hypothesis; no unresolved blocker.
Actual paralysis64 persists, then guide cures to0; HP26→30. Full bag/Scrap98
refuses reward2 while retaining ROUTE TAG and incomplete state; toss1, retry grants
2→99, removes tag and marks completion once. Final isolated committed run next.

## D01 final verification — 2026-10-06

Executor connection confirmed by successful tools after parent's07:07 disconnect
notice. Existing verification session continued; no duplicate run/reset. Tested
`060864caa9aecfa48c38c810fe2a7f87895b308e` passed isolated `test-d01.sh`:114
assertions (84 production/30 fixture), seven empty errors,19 reviewed actual PNGs.
Production SHA256 `427c16b312869f2dd575bac6f0b736953c524bf96753273a88d2429444b0cfec`.
[Evidence](evidence/d01/README.md). Implemented YES / compiled PASS / runtime PASS /
merged NO, pending scoped PR for issue #20. One coordinate-input defect fixed on
first hypothesis; no unresolved blocker. Actual status curing now proven; total
action exhaustion remains S03. Next push evidence/draft/review/merge, then D02.
Cloud task remains `01a10f4b-596b-700b-b8ba-241e3ca2c000`; sole writer/scheduler
ownership unchanged.

## D01 integration / D02 start — 2026-10-06

PR #21 merged `c42d444b8c2ae1b665105baad133094859bf8fa5`; issue #20 closed.
Evidence `15703bb7d6d83bde5abf5b7fb3d6a35533179261`, tested `060864c`. Main
reconciled, no open PR. Parent independently reviewed R02 with no material defect;
its remaining Scrap-box capacity branch joins D02 inventory-limit coverage.
D02 issue #22, branch `task/d02-explosive-crafting`, base this merge. Recipe
Scrap2→Charge1; optional sealed cache consumes one charge for SuperPotion1 and
persistent preparation flag, reserved for S01 boss advantage. No boss effect yet.
Inputs/output capacity checked before consumption; no save-layout/battle/schedule
change. Implemented/compile/runtime/merge pending. Next author bench/cache and test.

D02 source compiles; fresh materials route passes16 assertions: recipe missing/
cancel, cache needs-charge, quest obtains exactly Scrap2 and saves. Workbench and
cache both add outputs successfully before consuming checked inputs, with no yield
between transaction operations. Craft/use/capacity/cold routes still in progress.
No blocker or failed production fix. S02 retains new icon/prop/audio placeholders.

D02 exploratory input routes complete: materials16, craft13, blast/use17,
cold recovery13, final cold8; explicit inventory fixture33 plus cold11.
Crafting spends exactly Scrap2; cancellation/missing/output-full preserve inputs.
Charge menu use is inert; cache cancel/full/repeat preserve charge. Successful
blast gives SuperPotion1, used for Carl26→30 without curing paralysis; guide then
cures it and saves. Capacity tests cover R02 workshop98→failure, toss1→grant2→99;
two successful crafts each spend2 after freeing output space; cache output failure
retains charge, retry spends1. No failed production fix/blocker. Route navigation
was adjusted to avoid a known sign object. Final isolated111-check run next.

## D02 final verification — 2026-10-06

Tested `b53b8e6a2c64fe3e9e22d37bca5277c97ac46b02`, isolated `test-d02.sh`:111
PASS (67 production/44 fixture), seven empty errors,19 reviewed actual screenshots.
Production SHA256 `a4c542bae88f85f8e537c4590bdafb2830b386844bc4806a783b5825b2793972`.
[Evidence](evidence/d02/README.md). Implemented YES / compiled PASS / runtime PASS /
merged NO pending scoped issue #22 PR. No blocker or failed production fix.
R02 Scrap-box full-capacity edge now exercised. S02 must replace inherited DAD
menu-refusal wording and stock icons/props/audio as scheduled. Next push evidence,
draft/review/merge, then S01 connected encounters/boss/staircase. Cloud task remains
`01a10f4b-596b-700b-b8ba-241e3ca2c000`; no overlapping writer/scheduler.

## D02 integration / S01 start — 2026-10-06

PR #23 merged `369a9ea0dbe8aa61d7f091da533d18c6efafd5fb`; issue #22 closed.
Evidence `824a6ff1a7f36a008fc340715e42967f38d63a8e`, tested `b53b8e6`. Main clean
and reconciled, no open PR. An initial PR-create response produced no PR; a read
confirmed none before retry successfully created #23. No duplicate execution.
Parent independently reviewed D01 with no blocker (114 checks,19 actual PNGs).
Current evidence READMEs now include actual integration updates. Parent retains
S03 declined-quest/avoided-trap completion route plus low-HP/existing-status trap
edges; D01 fixture covers HP1 and production covers ordinary paralysis/cure.

S01 branch `task/s01-connected-slice`, base this merge. Connect second encounter
zone/boss/stairs, distinct durable/disruptive enemies, readable boss cadence and
optional preparation advantage, local defeat recovery, persistent progression.
No Stage6 expansion or save-layout change. Implemented/compiled/runtime/merge
pending. No blocker. Next author narrow connected content/encounter changes.
User asked about earlier visuals; parent offered reordering, but none approved yet.
Safe sequential visual candidate: Carl/Donut battle/icons/overworld and existing
room tiles/palettes with unchanged collisions/events. Preserve S01 if that steering
arrives. Cloud task remains `01a10f4b-596b-700b-b8ba-241e3ca2c000`, sole writer.

User confirmed “continue like normal”; keep S01→S02→S03, no visual reorder.
S01 source authoring now connects Service→Gauntlet→Gate→Review staircase. Four
trainer IDs add guard/howler and prepared/unprepared warden; authored cadence
uses existing turn/move machinery. Local defeat callback extended only over these
authored IDs. Boss/stair flags use existing save bits. Compilation/runtime pending.

S01 incremental build PASS after source inspection and move-availability guard.
New host `pattern` diagnostic reads trainer/turn, enemy PP/attack/defense/level and
Carl attack from real RAM; no writes. Fresh existing setup replay is starting before
new gate/encounter routes. No S01 runtime acceptance or integration claim yet.

## S01 runtime checkpoint — 2026-10-06 (partial, not acceptance)

Source `f784d58fe9692ef696224742cfa279cf3211ead4`, incremental build PASS. Reused
R02 setup32/trial53/re-entry-rest34 pass; new gates17 verify boss/stairs locked,
guard19 verifies pattern/victory/no duplicate XP/save, guard-rest12 verifies cold
depletion/backtrack/recovery/save; howler opening5 verifies attack-down pattern.
Carl after guard level10 XP627, Donut9 XP937; depleted HP25/6 and resources3/40,0/37
survive cold save, guide restores36/28 and8/40,2/40. No S01 production defect/fix.
Exploratory movement timing needed a direction-aware correction; longer1800-frame
action waits finish animations before asserting the turn counter. No blocker.
Current local save artifacts/s01/playtest.sav is before howler at gauntlet10,5;
before-guard.sav and before-howler.sav are normal saved checkpoints. Host binary
/workspace/toolchain/playtest-s01; symbols artifacts/s01/game.sym.
Next exact action: finish howler route, local defeat/retry, prepared/unprepared boss,
stairs/cold reload; isolated committed suite and scoped PR still pending. User kept
normal S01→S02→S03 order. No parallel writer/scheduler.

## S01 complete exploratory routes — 2026-10-06

Shell/executor healthy at07:53:31UTC after07:51:52 disconnect callback; existing
process continued, no duplicate writer/run. Parent independently reviewed D02
without blocker. PR17/19/21/23 metadata now explicitly records actual merged SHAs.

All S01 exploratory routes pass357 assertions across18 production-ROM processes.
No game-state fixture: prepared and defeat routes branch ordinary manual flash
saves from the same fresh-play progression. Unprepared warden12 defeated with
BRACE/WEAKEN then attacks, no gear/explosive/healing use; Carl12 XP974/Donut10 XP1284,
HP8/10 survive. Prepared warden10 defeated by faster offense with no BRACE or
healing item; Carl11 XP940/Donut10 XP1250, HP21/24. Both staircase/end saves survive
cold reload; unprepared ending returns to gate and cannot repeat boss XP.

Controlled loss deliberately uses ordinary STRIKE ally-targeting to incapacitate
Donut, then the warden defeats Carl. Both HP0 observed, local outcome2 restores
HP38/30 and all four resources, leaves boss/stair flags unset, retains prior patrol
progress. Immediate loss save/cold retry opens a new full-health battle. This is
an intentional defeat test, not a recommended tactic or RAM-injected state.

No S01 production defect/fix or unresolved blocker. Input timing/navigation
adjustments only. All implementations compiled; final isolated committed357-check
suite still pending. Next commit these routes, run test-s01.sh, review/archive
actual evidence, scoped issue24 draft PR and integration. S02 original visuals/UI
then S03 complete regression remain pending; no Stage6 expansion.

## S01 isolated acceptance — 2026-10-06

Tested `2e8de08292a8a4fe380fda06accdb2b97c798401`, base `369a9ea0dbe8aa61d7f091da533d18c6efafd5fb`.
`bash scripts/test-s01.sh` PASS357 assertions/18 production sessions,18 empty errors.
ROM SHA256 `ce16d2fd150917e8d865563fd76fedea571cefc6aaf74da4fdbd780f38617248`.
Run artifacts/s01/run-4uGUcD. Reviewed30 actual PNGs and focused source diff; no
production defect or blocker. docs/evidence/s01 contains85 hash-verified artifacts.
Implemented/compiled/runtime verified PASS; issue24 PR/integration pending.
Shell healthy after context resume; source/evidence preserved, no duplicate run.
Next push evidence, draft/merge verified S01; continue S02 original art/UI, thenS03.
Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`; parent owns continuation.

## S01 integrated / S02 active — 2026-10-06

PR25 merged `abf9875af2ffead2a342b8a5835c1e3dff157ec0`; issue24 closed.
Evidence `8e34180de438a291067fdb2ec8d8bb08d3ec316d`; issue/PR include actual images
and actual merge metadata. Main reconciled. S02 issue26 branch
`task/s02-original-presentation` uses that merge as base. Sole writer healthy.

Original geometry generator scripts/content/slice_art.py produces seven indexed
battle/icon sets (Carl, Donut, scuttler, grub, guard, howler, warden), Carl trainer
back pose, item silhouettes, crate and Donut exploration sprite. Dedicated Dcc
secondary tileset preserves used behavior/collision bits, adds stone walls, lamps,
rugs/route stripes/debris to distinguish rooms. Original assets use16 colors.
Crawler summary labels and planned flag-derived Journal implemented; contest
summary page inaccessible. Shared internal species names retained in code.

Incremental compilation PASS. Authoring errors fixed: overly broad text substitution
changed BERRIES_POCKET (restricted to intended text); new icon extern declarations
added; Pillow lookup extended to256 slots. No repeated unresolved blocker.
Exploratory fresh setup32 PASS; actual room/first battle captures show original
art. Old R02 trial replay stops at its exact foe HP14 expectation (now7 after
a critical hit); no combat rules changed. New object/presentation timing can shift
RNG. Do not claim old damage golden routes pass. Next update S02 replay against
actual input outcomes, inspect Journal/Donut/menus/palettes, finish remaining
presentation audit, then isolated committed build/runtime and scoped PR.
S02 implemented partial, compiled PASS, runtime partial, merged NO. S03 pending.
Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`; no new scheduler/writer.

## S02 presentation/runtime checkpoint — 2026-10-06

Checkpoint source `5963c8fdd3f719fb207760230e913e286e79aafb` pushed; continued
original NPCs/visible enemy tokens, title/portal, battle arena and medicine UI
corrections. New object art reuses fixed8-bit IDs without increasing the table or
save format; shared16-color prop/NPC palette. Asset validation checks49 indexed
PNGs, seven sprite dimension contracts, battle/title tile budgets and all used
metatile behavior matches. Collision/elevation bits match S01 on all12 binaries.

Exploratory updated trial31, cold/re-entry/recovery34 and gates17 PASS; earlier
fresh setup32 and UI13 PASS. UI proves Journal objective/rules/recovery/optional
text and return to movement, summary page boundary, inventory/crawler selection.
Actual screenshot review found and corrected title clipping/tiled blank background,
medicine labels, and missing wall lamps. Original NPCs/encounter sprites render
with the intended shared palette. New damage golden after timing changes: trial
CarlHP22 after victory, resource4/40; Donut0/38, healed28. No combat-rule change.
Prepared S01 strategy was offense-focused with WEAKEN after SPARK exhaustion,
not attacks-only. Parent independently audited S01 without blocker. S03 retains
decline-to-ending, all-actions-exhausted and individual encounter loss coverage.

Next exact action: commit final S02 source/routes, run isolated test-s02.sh, review
and archive final actual captures and original asset provenance; draft PR26 issue
link (actual PR number TBD), integrate only on relevant PASS. S03 fresh full route
regression remains separate. No new writer/scheduler; no unresolved blocker.

## S02 first isolated pass and visual fixes — 2026-10-06

Source `5fd9217c639afcc306246dded0e77aeda55f3de4` isolated build/runtime PASS128
assertions/6 production sessions in artifacts/s02/run-a7awMe;6 empty errors.
ROM `bc365b37a91326792fea400a4297a68cc5197f5a936e89970d577ca0b5f90e67`.
Reviewed29 selected captures. Do NOT treat this as final S02 acceptance: rendered
review found title horizontal repeats (affine blank tile0 contained the first
letter's bottom row) and clipped summary heading. Moved lettering clear of tile0,
added a regression assertion, removed the redundant heading; actual title retest
is clean. Also added small Carl shading/Donut fur detail, removed oval arena pads,
and corrected remaining give-item/technique labels. These are presentation fixes,
not combat balance changes. Final isolated rerun required.

Current actual preview pushed `72fc11a1523f4e6dfb5425c83b461179a961d062` under
docs/evidence/s02-preview-current (5 PNGs from5fd9217, clear WIP limitations).
Earlier preview evidence-only branch evidence/s02-wip-5963c8f points to
`d33e73f1aeec30fb55056b1efb3eb7c271cafdc9`; no implementation writer there.
Issue26 prominently links current screenshots for parent's Pics delivery.
Parent rough-art feedback retained: original geometry is still simple prototype
art; readability is verified separately from polish. Remaining inherited menus,
animations/audio/boot credits explicitly listed. No claim of finished visuals.

Trial replay retains actual action-resource, win/XP/reward/item/save assertions;
it does not reuse outdated frame/damage goldens blindly. In the new input route
the first foe falls earlier, so XP/menu advance differs; we recorded actual new
turn/resource phases and retained precise final HP/PP checks. Presentation/object
changes can shift replay RNG timing; no battle stats/move rules changed in S02.
Full branch coverage belongs to S03. Next final source commit/run, archive andPR.

## S02 visual acceptance blocked by user — 2026-10-06

User reaction through parent: “Omg these sprites are not good haha”. Treat current
protagonist quality as FAILED visual acceptance; do not merge S02 or begin dependent
S03. Parent is preparing an asset-only replacement package outside this repo; this
remains the sole repository writer/integrator. Exact dimensions, frames, palette
wiring and destinations: docs/s02-art-handoff.md. Stronger silhouettes, natural
poses and deliberate pixel shading required; original geometry was insufficient.

Latest source `a242983b6f6d061dd2c5bd4916c34f8b1fd10266`, isolated128 assertions/6
processes PASS in artifacts/s02/run-0dHXqs,6 empty errors. ROM SHA256
`26ef6bff3466499592b994de02293efe338362b79fb9da69a55039206ad0b921`.
31 actual final captures reviewed; title tile0 fix and summary heading fix verified.
Implemented/compiled/runtime PASS for current scope; visual acceptance FAIL;
merged NO. Existing preview72fc11a source5fd9217 was delivered by parent09:03.

Exact next action: receive external art package/reference, inspect dimensions and
palettes, integrate as sole writer, prevent generators overwriting replacements,
compile and capture actual updated duo/summary/overworld, seek requested visual
review before treating S02 art accepted. Independent title/menu verification may
continue. No new scheduler, no duplicate Cloud task. Task ID remains
01a10f4b-596b-700b-b8ba-241e3ca2c000. S03 and Stage6 stay gated.

## Reference delivery blocked / independent menu correction — 2026-10-06

Parent supplied exact generated reference LibraryID
libfile_bdf91f97ea7c8191a3d196d5fc3890cd, file_00000000fcac82308d3f54afcdedaa6d,
expected SHA2564c713bb73c041af17a4daf9568087fc911f63daba617c184b68e0744b51619aa.
Read current Library skill/materialization instructions and fetched current helper.
prepare_materialize resolved it, but initial supported transfer and one fresh-
preparation retry both returned “library file transfer failed: download failed”,
exit1. Destination artifacts/s02/art-reference/...png does not exist. No pixel
inspection/conversion performed, no parent path assumption, no private credential
access/guessed URLs. Issue26 reports exact consumer-local blocker. Await working
authorized asset transfer; no further blind retry.

On isolated productiona242983, independent D02 materials16/craft13/blast17 pass
46 assertions/3 empty errors. Completed-quest Journal line visibly overflowed;
shortened it to “Two scrap make one charge.” Incremental8 checks then pass with
read-only flags/status/resources and control return. Input movement corrected
from20 to12 frames because the player was already facing left (not a control bug).
Current test-s02.sh includes182 checks/10 processes; expanded isolated rerun is
pending replacement art. Archived128-check evidence is explicit VISUAL FAIL.

Next: obtain readable asset bytes through parent, inspect actual1254x1254 reference
(SHA above), preserve generated-reference provenance and author native indexed
masters rather than blindly downscaling; integrate/wire palettes as sole writer,
run182 suite and actual visual review. S02 draft/review state remains blocked,
no merge and no dependent S03. Current Cloud task ID unchanged.

User approved replacement reference style and explicitly requires it outside combat
as well. S02 acceptance includes new9-frame16x32 Carl walking and3-frame16x16
Donut standing, four-direction/walk/interaction/overlap/palette checks and actual
overworld+battle captures. This is not optional later polish. Existing reference
transfer blocker remains: no readable bytes in this consumer environment.

## S02 reviewable blocked checkpoint — 2026-10-06

Draft PR27 opened: https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/27
Do not ready/merge until replacement protagonist art passes actual visual review.
Issue26 remains open with exact Library transfer failure, art contract, previews
and active task reference. Source39e9749 committed Journal retest8 PASS, empty
errors, fixed text capture reviewed; archived in docs/evidence/s02-menu.
No running build/test remains. Repository writer is paused on unavailable asset
bytes; parent has approved reference direction and both combat/exploration scope.

Resume this Cloud task after working asset delivery. Inspect downloaded file and
verify expected hash before any pixel-dependent conversion. Then author coherent
native battle/overworld masters, preserve generator ownership/palettes, run current
182-check isolated suite and requested actual character-art review. S03 and
improvement cycles have not started; Stage6 remains excluded. No scheduler added.

### S02 replacement battle integration — 2026-10-06

Asset transport is resolved: PR #28 merged into the S02 task branch at
63678ec4cd127b14e863940f8125040c6aaaa15b; main remains abf9875.
Approved reference/native candidate checksums and deterministic conversion passed.
The battle masters now replace rejected prototype art, including trainer intro,
front/back, two static animation frames and derived menu icons. Carl/Donut use
separate battle/icon palettes (icon slots 1/2; enemies retain 0). Unreachable
upstream species sharing those icon slots are outside the fixed-roster slice.
Generator ownership prevents the slice generator overwriting battle replacements.
Implemented; asset contracts passed; compilation/runtime pending for this commit.
Exploration replacement is still in progress and remains S02 acceptance work.
Next: compile committed snapshot and publish a real battle capture promptly, then
finish native exploration frames and complete the 182-check S02 run plus movement
checks. PR #27 remains draft; issue #26 open; no new scheduler/writer.
Cloud task: 01a10f4b-596b-700b-b8ba-241e3ca2c000.

### S02 matching exploration integration — 2026-10-06

Battle preview ae32d3ff5497a117e1411195dc678192ab134a1f built clean and passed
182 assertions / ten production mGBA sessions / ten empty error logs in
artifacts/s02/run-5uuRHD. Actual battle PNG/log pushed in fe35ec5 and embedded in
issue26/PR27. User approved improved native battle candidate appearance separately.

Matching exploration masters now implemented: nine Carl frames; three stationary
Donut directions; independent existing-slot palette. Native margin/packing/palette
checks pass and all asset generators reproduce replacements without other diffs.
Added four-direction actual walking captures to S02 runner (now189 assertions in
11 processes). Compilation/runtime for this exploration commit pending. Next run
this committed snapshot; inspect captures before claiming visual acceptance.

### S02 runtime defect — Donut field palette

Tested a2de128 (artifacts/s02/run-BAptkr): clean build,189 assertions/11 sessions
passed with empty errors, but actual landing capture showed incorrect pink/blue
Donut colors. Visual acceptance FAILED despite passing behavioral checks.
Root cause: ObjectEventGraphicsInfo.paletteSlot is a four-bit field; +16 is
truncated and cannot reach the legacy >=16 palette-load path. First corrective
approach now reserves existing NPC1 palette during dungeon map initialization
and returns the same tag for palette reload consumers. No save-layout change.
Added ten hardware-palette assertions across map load, UI/battle return, cold
reload and movement (199 total in11 sessions). Full corrected runtime pending.


### S02 verified replacement presentation — 2026-10-06

Base abf9875af2ffead2a342b8a5835c1e3dff157ec0; tested source
c9062dabb81341bf0525eead8d89ea7ba62043f5; branch task/s02-original-presentation.
`scripts/test-s02.sh` isolated run artifacts/s02/run-3cmBS6 completed199 assertions
across11 production mGBA0.10.5 sessions,11 empty errors. ROM SHA256
7a0a87273a6b53bd9104afa2029fd99fe6cee93d30f56dc01881b6adbdcb7b72.
Full logs, routes, corrected world/battle/UI images and hardware-palette failure
comparison archived in docs/evidence/s02 (106-file manifest). Reviewed35 selected
scene images plus all four-direction contact/idle captures. Palette defect fixed
on first corrective approach; old ROM reproduced the new color assertion failure.
All12 map collision/elevation fields match S01; no combat/save-layout changes.

Implemented YES; clean compiled YES; scoped runtime/visual verified YES; merged
pending PR27. Diff reviewed for generator ownership, palette scope, Journal
read-only behavior, capture/storage exposure, save changes and generated artifacts.
Python cache accidentally added in ad4cc41 was removed in a2de128 and is now ignored;
no ROM/save/executable exists in the tracked tree. Static animation/remaining
inherited UI/audio assets are listed in content-ledger, not called finished art.

Next: integrate scoped PR27 when protections permit, close issue26, record merge;
then S03 full fresh-save/alternate-boss/defeat/reward/quest/capacity regression with
review package. No Stage6 work or new scheduler. Cloud task remains
01a10f4b-596b-700b-b8ba-241e3ca2c000; sole implementation writer.


### S02 merged; S03 active — 2026-10-06

PR27 merged d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530; issue26 closed. Tested
c9062da, evidence68d7a570cce1d2bb6fa6476db8fc211c9ebcef72; implemented/compiled/
scoped-runtime/merged all YES. Actual improved battle and exploration screenshots
are embedded in issue26/PR27 and source archive. User approved the native battle
look; final full-slice playtest remains pending.

S03 issue29, branch task/s03-slice-validation, same sole Cloud writer. Initial
current-ROM guard replay proves old S01 critical-hit/XP timing is not a reliable
current replay: assertions pass through turn2, then guard survives where old route
expected a knockout. Diagnostic captures show different damage, not a progression
lock; additional fixed A presses were still resolving attacks. Preserve stronger
outcome assertions and use explicit input-state-aware actions to exercise intended
strategies rather than weakening checks to fit obsolete timing. Next: add a
read-only, normal-button battle route helper and complete current progression
routes, including declined quest/avoided trap. No S03 completion claim yet.

### S03 interim diagnostics and reviewer follow-up — 2026-10-06

Production engine remains exactly S02 c9062da / merge d8f8ae6; no gameplay edits.
Current host helper drives actual input menus with normal keys, bounded frames,
read-only diagnostics and explicit win/flag/XP checks. Guard defensive route and
howler offensive route pass; unprepared boss wins with three BRACE/WEAKEN opening
turns (two BRACE failed, correctly triggering local defeat), prepared offensive
boss also wins. These are diagnostic current-ROM runs, not final S03 acceptance.

Restored trial behavior now61 assertions PASS, including four battlers, turn
damage/PP, rejected empty SPARK with unchanged turn/HP/PP, WEAKEN reduction,
level stats, no optional equipment and pre-workshop flag39/Scrap0. Explicit quest
decline/avoided-trap navigation passes23; normal completion still needs final run.
Donut actual summary/action-selector captured; consecutive-frame four-direction
motion records380frames /6.362seconds, exact46color GIF duration6.360s. Preview
under docs/evidence/s03-preview, clearly separate from final acceptance.

Independent review supports S02 and confirmed two new stationary Donut objects;
never claim unchanged object layout (only collision/elevation bits unchanged).
Retained S03 gates: full final fresh route/both bosses; every encounter defeat/
retry; both incapacitation orders; empty actions; quest/reward/crafting capacity;
collection guards; cold saves; second Donut interaction; actual pacing measurement
separate from automated waits/reboots.20–30minute fresh-player target remains
unproven. Preserve inherited assets/terminology and static animations in limitations.
Next: finish and run all S03 routes from a committed isolated snapshot, archive
review evidence, then up to five substantive improvements; user playtest before6.


### S03 acceptance suite assembled — 2026-10-06

Draft PR30 tracks issue29. Current source helper/visual preview commit0c72f45.
The assembled suite plans914 assertions in60 emulator processes (723 production,
191 explicitly labeled fixture checks), including restored61-check trial, every
encounter local defeat/retry, both boss approaches/incapacitation orders, both
Donut scenes, motion, quest/crafting branches, equipment, collection guards and
capacity failures. These counts are planned, not claimed passed as a whole.

New isolated exhaustion fixture checks HP1 with existing poison is preserved by
the trap, saves all action PP empty, proves real STRUGGLE wins without hanging,
then tests cold depleted state and guide restoration/reload. Missing HealPlayerParty
header was corrected in the diagnostic generator; its failed first build/run is
not acceptance evidence. No production source changed. Current-ROM probes prove
STRUGGLE victory with zero PP and guard loss/cold retry; final isolated run next.

Parent reviewed full walking motion; overlapping Carl/guide lower body is normal
foreground depth for adjacent tiles, with interaction/recovery and walk-away paths
independently tested. Donut's stationary object must be walked around; routes now
respect that occupancy. Main tile collision/elevation compatibility never meant
unchanged object layout. Pacing measurement remains separate, with no20–30minute
fresh-player timing claim. Continue until S03 and warranted improvement cycles
finish, then await user playtest before Stage6.

Exhaustion recovery route now goes around both the trial NPC and stationary Donut;
its original direct path hit the trial object, an input-route error rather than
changed map collision. Corrected depleted save/recovery diagnostic passes13 checks.
Final suite plans916 checks (723 production,193 fixture),60 sessions. All counts
remain provisional until the isolated run completes.

### S03 isolated run iteration — 2026-10-06

Tested fdab148 snapshot in artifacts/s03/run-p3Caxf builds the unchanged production
ROM7a0a87273a6b53bd9104afa2029fd99fe6cee93d30f56dc01881b6adbdcb7b72.
Setup/UI/trial defeat passed, but cold trial retry detected the preceding save
never occurred: replay pressed B before recovery text finished, then pressed its
save sequence into the encounter dialogue. Actual captures distinguish this from
a game save bug. Increasing post-defeat text wait240→600 frames fixes the route;
current-ROM corrected trial defeat11 and cold retry8 both pass. Apply that wait
consistently to all six defeat routes; restart isolated suite. No engine change.

Added bounded normal-A `engage` routing for a continuous pacing benchmark. The
first uninterrupted attempt lost to the unprepared boss; it is not a successful
completion timing. A new uninterrupted route explicitly exercises ordinary local
recovery and retry, preserving all real XP/rewards; no injected save/state. Report
its actual result and fixed waits separately, never extrapolate novice pacing.

### S03 current-art replay reconciliation — 2026-10-06

6231b66 isolated production run passed core progression, both bosses, all local
defeat/retry routes, both incapacitation orders and staircase cold reload before
a stale D01 route tried to walk during Lev's added third page. The corrected
S03 quest route passes22 checks. Two older collection routes also needed explicit
current-art inputs: walk around stationary Donut, and B from Carl's move selector
before selecting Items. Both corrected routes pass. Historical evidence stays
unchanged; new S03 copies document the current inputs. No production engine edits.

Continuous prepared route passed127 checks in90,586 frames (25m16.655s at
59.7275Hz), plus10 cold final-save checks. Includes53,700 fixed zero-input frames,
4,951 scripted button frames and31,935 battle-pilot frames; startup2,044frames is
included. No mid-route reboots. This is measured automated play, not novice pacing.
Two prior uninterrupted unprepared-boss attempts lost; retained diagnostics do not
count as completed routes. Main isolated unprepared strategy passed independently.

Final suite now plans1,053 checks/62 processes:860 production and193 labeled
fixture assertions. Fixture tail diagnostics are still running; final isolated
committed rerun is required before S03 acceptance/merge. Private Library build
delivery remains pending acceptance; no ROM enters git or public release.

All corrected tail diagnostics now pass, including193 labeled fixture checks.
Final committed suite rerun follows. Parent relayed the user's request to improve
opponents to the approved protagonist standard. This is authorised improvement
cycle1 after the S03 baseline, restricted to the five existing enemies' native
battle/map artwork. Parent coordinates asset-only preparation outside this repo;
this remains the sole implementation writer. Names, roles, paths, dimensions and
palette constraints are posted to issue29. Preserve baseline and await candidates.

### S03 acceptance PASS — 2026-10-06

Tested50435d1c7db1e6778ad71e639e7a1a8ff4175653; base
d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530; branch task/s03-slice-validation;
PR30/issue29. Cloud task01a10f4b-596b-700b-b8ba-241e3ca2c000.

`bash scripts/test-s03.sh` in the documented Linux toolchain produced the same
ROM7a0a87273a6b53bd9104afa2029fd99fe6cee93d30f56dc01881b6adbdcb7b72.
Isolated artifacts/s03/run-pcrKHh:1053 assertions/62 mGBA0.10.5 processes PASS,
860 production +193 explicitly labeled fixture checks;62 empty error logs;
unchanged-head/clean-source guard PASS. No production gameplay/save-layout edits.

At12:03UTC the executor transport failed on new command, retry and existing
session poll. At12:05 it recovered; session35025 was gone but originalPID733292
was alive and continued the same run. No duplicate runner or replacement writer.
That original process completed successfully and is no longer active.

Evidence in docs/evidence/s03 includes complete raw logs,62 routes,42 reviewed
actual screenshots, all source frame hashes and6.36s walking GIF. Its380 frames
are byte-identical to the already reviewed preview. Both Donut scenes/summary/
action selector, all encounter outcomes, both incap orders, reward/quest/crafting
branches, capture guards, empty actions/STRUGGLE/recovery and cold saves passed.
Continuous prepared route127 checks + cold reload10:90,586frames/25m16.655s at
59.7275Hz. Fixed zero-input53,700frames, scripted buttons4,951, battle pilot31,935;
startup2,044 included. No novice pacing claim. Failed diagnostic traces preserved.

State: implemented YES; clean compiled YES; runtime verified YES; integration
pending PR30 merge. Review found no gameplay/progression regression; inherited
UI/audio/static-pose limitations remain documented. User-requested enemy visual
upgrade is next focused improvement1/5, for the existing five enemies only.
Parent coordinates asset-only candidate PR handoff; no parallel implementation.
Exact next: merge verified S03, pause writes for asset-PR staging, then integrate
its native assets with provenance/generator protection and real battle/map checks.
Guard's SPINDA procedural spots must not alter approved native art. No Stage6.

### S03 merged; I01 asset handoff pause — 2026-10-06

PR30 merged eb73f725d0c5c1488386e56f28f8080eb3a6f884, evidence head
7807a9c286a7fa11fd35cce2065d02e280f78b2a, tested50435d1. S03 implemented,
compiled, runtime verified and merged. Issue29 complete. Original runner ended;
no build/emulator implementation process is active.

I01 issue31, branch task/i01-opponent-art, base eb73f725. Only this task integrates
code/assets. Parent has reviewed an external native candidate package for the
five existing opponents and will stage it through an asset-only GitHub PR.
Repository writes pause after this checkpoint for that handoff; no Library
materialization retry. I01 art implemented NO/compiled NO/runtime verified NO/
merged NO. Resume only after package delivery and remote branch reconciliation.
Next: fetch delivered asset PR, verify hashes/provenance/native palette contracts,
then integrate and run scoped evidence checks. Preserve approved Carl/Donut art,
all gameplay and saves. Stage6 and public release remain unauthorised.

### I01 native integration — 2026-10-06

Asset-only PR33 merged into task/i01-opponent-art at94122b57bd90532f7c8934d8141db8eba8f7d9be.
Exact candidate head2c9a1b8;54 additions only, SHA manifest/24 PNG format checks
and two41-output reproduction runs pass. Native battle/world pixels inspected.
Exporter now owns all34 native files; slice_art.py delegates rather than replacing
them with geometric art. Two complete content regenerations change only the
five intended opponent sets; shared palette, Carl/Donut and maps unchanged.
Guard's inherited Spinda spot renderer is now a documented no-op; no stats/AI/
encounters/save changes. I01 implemented YES; compiled/runtime/integration pending.
Next: isolated test-i01.sh full1053-check regression, all opponent battle/map
captures and palette/pixel review. No Grub world object is added.

Final S03 audit limits retained: six cold-retry routes prove re-entry, not victory
in that exact saved retry; separate routes prove wins. Only prepared play has a
successful uninterrupted fresh route. Segmented unprepared victory passes; two
continuous unprepared attempts lost.90,586frames includes53,700 fixed idle frames
(about15minutes);25m17s is not a human completion time or proof of20–30minute target.

I01 first isolated preflight e2c8d60 stopped before build: upstream engine
.gitattributes exports .pal asCRLF, while source references areLF. Palette
entries/order were identical. Verification now normalizes only text line endings;
PNG byte checks stay exact. No engine/art bytes changed by this correction.

I01 b82dff4 builds ROM70387da9…ec94619 and initial gameplay routes pass,
but actual trial capture revealed43 Scuttler opaque pixels in native rows55..61
covered by Carl's HP panel (canvas168,8). Run8IQ6UV stopped deliberately after
this visual failure; raw evidence retained, no full-acceptance claim. Export now
lifts only battle pixels8px within each64×64 canvas, using existing transparent
top margin. No rescale, recolor, source-master, icon or field-token change. All
opaque source pixels remain intact. New runtime pixel check requires exact
RGB555 colors for every native opaque pixel of five battle fronts/four tokens.

### I01 acceptance PASS — 2026-10-06

Base eb73f725d0c5c1488386e56f28f8080eb3a6f884; branch task/i01-opponent-art;
issue31/PR32. Tested81b232ae41647b5e456e45ed73d51a170f17fb58. Cloud task
01a10f4b-596b-700b-b8ba-241e3ca2c000; parent owns continuation, no new scheduler.

`bash scripts/test-i01.sh` in documented toolchain: isolated run-Yw6WfM clean
compile and1053 runtime assertions/62 sessions PASS,860 production+193 labeled
fixture;62 empty error logs;9 exact native pixel matches; unchanged-source guard.
ROM SHA256 f46643a4a2eb0065e75ed33ea2baafe533d5508a8ee45922282108e778e43948.
Two separate full content exports preserve all7385 checked graphic/tileset files.
Actual captures reviewed: allfive foes/four map tokens, duo HUD clear after8px
placement fix, no Guard spot artifacts, correct Donut summary/field palettes,
menu/return and ending.25 actual PNGs and full logs/routes archived in evidence/i01.

Source package first passed24 PNG/41-output reproduction checks. Palette newline
preflight and HUD-overlap failures are retained, not acceptance results. No stats,
AI, moves, event/collision or save schema changed. Enemy icons/backs have no
reachable roster/collection UI; contract validation does not invent such a path.

State: implemented YES; compiled YES; runtime verified YES; merged pending PR32.
Only comments/docs/evidence change after tested81b232a. No further substantive
defect observed, so improvement cycles stop after1. Precise S03 retry/pacing
limits remain in the review package. Next: merge reviewed I01, attempt supported
private Library build delivery, record result, then await user's playtest.
No public ROM/playable release and no Stage6 work. Original runner finished.

### Final slice handoff — 2026-10-06

I01 PR32 merged052979d38ff9800780fac66cb052896767c4f1c8. Evidence head
5635bcc02edf3e110e1dee8cb1b75bae3078cf91; tested source
81b232ae41647b5e456e45ed73d51a170f17fb58. Stages0–5 and improvement1 are
implemented, compiled, runtime verified and merged. Issue31 complete.

Final production ROM SHA256:
f46643a4a2eb0065e75ed33ea2baafe533d5508a8ee45922282108e778e43948.
Full1053/62 runtime suite,62 empty emulator error logs and9 exact native-image
checks passed. Complete evidence, source provenance and reproducible build/play
instructions are in docs/evidence/i01, docs/testing.md and docs/playtest.md.

Private delivery SUCCEEDED through the supported Library create flow; local
Library identity metadata was applied successfully. Filename:
DungeonCrawlerCarlemon-I01-81b232a.zip (7,791,421bytes), ZIP SHA256
7e7bce9f554b49ae739fc2ef3339b2b35cc2af2a340ee33a1fe6986f0732873a.
Contains one production ROM, instructions/provenance and evidence, no fixture
ROMs or development saves. ZIP integrity and all input checksums verified before
upload. Nothing playable was committed to git or released publicly; no share
grants, visibility changes, purchases or new scheduler. Library identity remains
private to the user rather than being copied into repository documentation.

No further meaningful evidenced defect warranted another cycle; stop after1/5.
Explicit limitations: six retry checks prove battle re-entry, separate routes
prove wins; only prepared uninterrupted completion passed; segmented unprepared
victory passed, two continuous attempts lost.25m16.655s is automated frame timing
with~15min fixed waits, not measured human pacing. Static poses/tokens, inherited
audio/UI/ball effects and compressed adaptation chronology remain documented.

Current execution: saved Cloud task01a10f4b-596b-700b-b8ba-241e3ca2c000; no active
build/emulator/writer beyond this documentation checkpoint. Exact next action:
**await user's fresh-save playtest and feedback**. Do not restart implementation,
create speculative tasks, or expand to Stage6. Parent owns the single continuation
mechanism and must reconcile/stop it at this boundary. No remaining tool blocker.

### Overnight dungeon refinement authorised — 2026-10-06

User request13:19:10UTC reopens existing-slice work until approximately21:19UTC.
Reconciled clean mainbf27e2692025eb4291ffbf992a3b6412340d32cd; no open PRs or
running implementation (one old exited zombie is not active work). Prior I01
ROM/private ZIP remain preserved. Parent reuses the same hourly continuation.

Actual six-room/map audit: repeated rectangle, identical palette/lamp placement,
flat grid floor, weak stair/entrance framing and sparse environmental meaning.
N01 issue35, task/n01-dungeon-materials: visual materials/palette composition
first, exact walkability/event preservation. Geometry/interaction tasks separate.
Prioritised overnight-plan.md added; pending read-only reviewer recommendations.
Cloud task01a10f4b-596b-700b-b8ba-241e3ca2c000 remains sole writer.
Implemented NO; compiled/runtime/merged NO. Next: native dungeon tile exporter
and static behavior invariants, then real six-room visual/interaction checks.

### N00 guidance defects selected before N01 art — 2026-10-06

Read-only reviewer confirmed stale Journal objective, contradictory post-stairs
Donut line and ambiguous two-ladder directions. N00 issue36 on task/n00-dungeon-
guidance is the sole active implementation; N01 kit remains outside-repo prep.
Text/event-script routing only: landing trial objective, east/west guide advice,
northwest/southwest Mara/Lev guidance, original two-page ending exchange. Same
page counts and state/interaction semantics, no map/collision/art changes.
Selected18 existing production routes retain every assertion for fresh Journal,
guide/trial/recovery, quest states and full completion/cold ending. No timing or
retry-victory claim is added. Next: committed isolated build/runtime and actual
text inspection, then merge N00 and resume environment work.

### N00 verified — 2026-10-06

Issue36 / PR37; branch task/n00-dungeon-guidance; base
bf27e2692025eb4291ffbf992a3b6412340d32cd; tested
f3514caa05d99ff60c0c666d017fced8274e11e9. Implemented YES, compiled YES,
runtime verified YES, merged pending. `bash scripts/test-n00.sh`: clean isolated
build, 18 unchanged routes / 373 assertions. Supplemental normal-input guide
route adds7; final collected total19 /380 with19 empty errors. Nine exact opponent
pixel checks pass. Actual revised pages inspected with no text overflow. Full
logs/routes and before/after screenshots: docs/evidence/n00. Source remained
unchanged throughout execution. ROM SHA256
1a9d4b248b86880d74769e4b66a2f8e1d2319be8cff2579c4587132dbf999573.
No state/save/collision changes. Next: merge verified N00, resume N01 native
materials/prop integration when the outside-repo asset kit is ready. Existing
rubber-stamp geometry, wrong-colored entrance rubble, ambiguous box props and
unresolved visual reward states remain identified overnight priorities. No blocker
attempts consumed on N00; no new automation.

N00 merged a9491f17c82a9da99fdca9acde21be612aac0260 via PR37. N00b issue38
now sole active task on task/n00b-remaining-objective, base that merge. Select the
remaining patrol using existing trainer flags; no new state or changed page
counts. Acceptance: unchanged core routes plus cold-reloaded Journal checks for
both pending, each individually pending, and both cleared; alternate-order
normal battle creates the otherwise untested guard-only state. No fixture state
injection. N01 waits on external art; no overlapping writers. Next isolated
commit/build/runtime. Implemented YES; compiled/runtime/merged pending.

N00b first run d4887a7: production build862302c8…193e0a8; all18 core routes
and3 new Journal routes passed. Alternate howler-first fortify policy lost
(outcome2, normal free recovery, no clear flag): preserved run-buUae3. This is a
strategy loss, not a successful branch proof. Second hypothesis: attack promptly
with existing offensive policy, same ordinary prebattle save/ROM. Passed11
assertions and saved the howler-only state; no gameplay/balance edits. Correct
runner's alternate-route expected count to11 (pilot itself adds an assertion).
Next committed clean rerun, cold guard-only Journal and actual image review.

### N00b verified — 2026-10-06

PR39 / issue38. Tested8e9d0d05c4529d45aa268c8cc04cbde853bf1d72 on base
 a9491f17c82a9da99fdca9acde21be612aac0260. Implemented YES, compiled YES,
runtime verified YES; merge pending. `bash scripts/test-n00b.sh`:23 production
sessions /416 assertions,23 empty errors,9 exact opponent pixel checks. All four
cold-reloaded objective pages fit; before capture reproduces the stale objective
with the same normal save in N00 ROM. ROM862302c8cad5c4d2c0c22565af7fb24cdfd7c89dbb2a405d2ad3cdae2193e0a8.
Initial alternate fortify policy lost; offensive policy succeeds and creates the
howler-first state normally. Failed trace preserved, no balance edits; blocker
resolved on second strategy. Full evidence docs/evidence/n00b. Next merge then
N01 visual integration, using prepared 1176-cell/event/49-asset invariants and
six matched unobstructed room views. Native kit external; no overlapping writer.

### Safe N01 native-kit handoff — 2026-10-06

N00b PR39 merged d36f3af20c9b690a6249141fad5e4d3e82f54e98. N01 branch
advanced without rewriting history to that verified main. Added read-only design
audit, reusable visual-only invariant checker and exact baseline contracts:
1176 map/border cells, six event/warp/script contracts,49 approved art hashes,
native tile/palette bounds. Checker passes against existing engine. Semantic OBJ
graphics IDs may change; event positions/scripts and all other fields may not.

Unobstructed before captures: docs/evidence/n01/before. N00 testedf3514ca,
ROM1a9d4b24…999573, normal completed manual save, six rooms/18 runtime assertions,
empty emulator errors. First capture-route attempt held Down too long from an
already south-facing avatar; fixed input duration, no game defect. Failed trace
kept locally; successful exact route archived. No new dungeon art integrated yet.

Parent reports native candidate kit ready:56 architecture tiles,12 recommended
shared-palette props,18 BG variants,230 unique BG tiles,721 static checks and109
reproducible outputs. These are parent-reported candidate checks, NOT integration
or runtime acceptance. Exact next: parent stages source kit via asset-only GitHub
handoff against this pushed branch; implementation writer explicitly pauses repo
writes until staging relinquishes them. Then inspect candidate manifest/provenance,
select useful assets, establish exporter ownership and integrate bounded N01 visuals.
Run invariants, clean build, actual matched six-room views and relevant gameplay
routes before review/merge. Do not treat candidate verification as game acceptance.

Cloud task01a10f4b-596b-700b-b8ba-241e3ca2c000 remains sole implementation
writer. No active build/emulator task; parent retains the same hourly continuation.
No scheduler added. Overnight scope ends approximately21:19UTC; no Stage6. Existing
I01 private package and all baseline/failed evidence preserved. N01 implemented NO,
compiled/runtime/merged NO; preparation/audit and baseline evidence complete.

### N01 resumed: static prop readability — 2026-10-06

Parent relinquished all staging writes. Audited PR40 head3a1a9c6:124 additions
only; local verifier passed123 checksums,91 PNG identities and721 static checks.
Merged reference-only PR40 into N01 atf8fc81750386032c940e82aaabf40e1c82e4e073.
Original main source sheet and optional packed output remain absent; neither will
be fetched/reuploaded. Complete source-sheet reproduction remains unavailable.
Authoritative game export uses accepted native PNG masters independently.

First visual increment selects six props: rubble, warning sign, bench, tag, cache,
shaft/tool storage rack. Uses six upstream explicitly unused graphic slots76–81;
16x16 static footprints and existing MovingBox shared palette. No dynamic-graphics
range, Donut palette, scripts, state, collision or coordinates changed. Nine
existing objects rebound; ordinary supply/wrap boxes remain for now. Native
export owns these six PNGs; old generators delegate rather than overwrite.
Static1176-cell/six-event/49-art invariants and55-image asset checks pass.
Next clean committed build;24 production sessions including matched six-room
route, all existing behavior assertions, nine opponent and six prop pixel checks.
N01 props implemented YES; compiled/runtime/merged pending. Then separate room
materials/composition and later state/layout increments. Sole implementation writer.

N01 prop increment verified c51012486790bf344883deae73d9e4df783091a0:
`bash scripts/test-n01-props.sh`,24 sessions/434 assertions,24 empty errors,
9 opponent+6 prop exact pixel checks;1176-cell/six-event/49-art invariants pass.
Actual six-room and changed-prop images inspected. Two deterministic six-PNG
exports match. ROMec3cdf914b55d36da913db570ab83ad1cffbcd59869ab71c9e47c4fe075c55f9.
PR41 pending merge; evidence docs/evidence/n01/props. Implemented/compiled/runtime
YES; merged pending. No blocker attempts. Next separate room materials/composition
increment, then collision/layout and state feedback with their own acceptance.

### N01 room materials/composition selected — 2026-10-06

Prop PR41 merged eee114c07792a37e2c281d8807f774be85b5845a. Sole active
branch task/n01-room-composition from that base. Selected native architecture,
quiet floors, opaque void borders, depth/corner bands, floor-specific warm/cold
palettes, sparse functional wear, guide rest mat/bedroll, workshop conduits/wire,
two patrol bays, framed gate and distinct exit rest patch. Native stairs centered
on existing one-cell warp anchors. This increment preserves all collision and
behavior bits, coordinates/scripts/save state; room-outline changes and persistent
visual states follow separately. No pressure-plate substitute for the wire.

Authoritative exporter packs only selected pixels:158 used8x8 tiles (160allocated),
157 metatiles, banks6–9; all1176 cell/border behavior and49 approved art checks
pass. Old grid generator delegates; expanded explicit checks retain native bounds
and behavioral invariants. Candidate source omissions remain untouched. Next
clean committed build, real240x160 arrival/center and motion review,434 behavior
assertions and15 character/prop pixel checks. Implemented YES, compiled/runtime/
merged pending. No build blocker attempts. Issue35 remains open for N01 completion.

N01 rooms candidate8e0690b passes clean build +24 sessions/434 assertions,
24 empty errors and15 exact prop/opponent checks. Actual12 room views inspected;
ROM6830b878763a27ca2b39f112ffe9010964f9484f4515439221176a5d78667bb5.
A separate old-save preview failed after4 checks: upstream restores cached map
metatile IDs from the prior atlas, garbling rooms and blocking an exit. Preserved
artifacts/n01-rooms/early-views. Do NOT merge/deliver with this known regression.

Focused compatibility fix now part of this visual PR as a separate engine commit:
DCC loads reconstruct current authored maps before existing flag-driven scripts;
refresh matching static object graphic IDs from headers, retaining positions and
all gameplay state. No save-layout/version-field change; stock map paths unchanged.
Add three ordinary I01-save reload routes: completed slice, leveled landing and
completed crafting/quest states. Check progression/resources/palettes/warps and
native refreshed prop pixels. No edited saves/fixtures. Exact next clean build,
434 current-build assertions +41 older-save assertions, actual side-by-side proof.

### N01 rooms and old-save fix verified — 2026-10-06

Testedcd6946e90fb95095ca2883509dfad19890a78848 on baseeee114c.27 production
sessions/475 assertions (434+41 legacy),27 empty errors,9 opponent+8 prop pixel
matches; all1176 behavior/collision cells/six events/49 approved assets preserved.
Extra exact same old-save recheck passes18 assertions after the prior failure;
not folded into475. ROM17e97672a2a3a6b6f7b670d3d901f4e6be21425a8eb92407a4c91be874cec637.
Actual12 room views, old-save frames and movement reviewed. Full evidence
 docs/evidence/n01/rooms; diagnostics retained. Cache blocker resolved by first
code fix; no game flags/party/inventory/save-layout changes. PR42 merge pending.

Full regeneration found old battle palette depended on removed room `colors`.
Restored its exact independent constant. Two complete isolated exports preserve
8807 tracked source assets; engine tree identical to runtime-testedcd6946e. Two
workspace exports preserve9352 source+existing ignored assets. This is exporter
validation, not a new runtime claim. Partial source kit limitations retained.
Next: merge this verified increment, then N02 room outlines/collision separately;
follow with existing-flag visual state feedback and final full regression. Sole
writer and parent-owned continuation unchanged. Deadline approximately21:19UTC.

### N02 room outlines — 2026-10-06

N01 PR42 merged c71636ac213147181eb28ab968ffd15e718501fc; issue35 closed.
N02 issue43, task/n02-room-outlines, base that merge. Explicit30-cell geometry
contract:14 new alcove cells and16 small blocked corner/support cells. All other
1146 map/border collision/elevation/behavior cells, six event contracts and49
approved assets remain unchanged. Dimensions/warps/interaction anchors unchanged.
The renderer follows real contours rather than painting fake walls on walkable
floor. No added travel requirement, enemies, floors or systems.

Static connectivity passes all six maps, all warp/object approaches, both wire
bypasses, secret/craft/cache/stair approaches, every new alcove, and an adjacent
unchanged free escape for every newly blocked old floor cell. Normal-input old
save setup at Exit13,9 passes5 assertions on pre-geometry ROM17e97672…cec637;
copy remains private. New runtime probe will load it on the clipped corner and
prove a normal step out with progression/resources unchanged.

Acceptance queued: original full1053 assertions unchanged, six-room18, focused
boundary/alcove47, old-save escape8 =1126 across65 processes (including existing
explicit fixtures). Preserve all behavioral assertions. Source-native158 used
subtiles/174 metatiles. Implemented YES; compiled/runtime/merged pending. Next
isolated committed build/full runtime, actual shapes/camera/motion review, diff,
PR and merge only if verified. Sole writer; no scheduler added.

N02 first full run111fd5c stopped in quest-decline: expected Service11,3 but
north utility protrusion stopped the original direct route at5,3. Static reachability
was insufficient to prove the existing direct path remained useful. Preserve
trace/input/initial contract and actual blocked-lane image in evidence/n02/
diagnostics/north-lane. Boundary47 and old-save escape8 supplementary probes had
passed, but they do not excuse this regression. No acceptance/merge claim.

First correction removes three north-spine blocked cells instead of padding or
rerouting the existing quest path. Contract now27 cells:14 alcove floors/13 small
blocks;1149 others unchanged. All original1053 assertion routes untouched. New
boundary route retains47 assertions, now proves the clear north spine and actual
north wall. Connectivity still passes all targets. Next clean committed full
rerun1126/65; this blocker has one design correction, no repeated speculative fixes.

N02 second full run0fc144f stopped at crafting fixture reload after57 completed
processes: Service13,3 corner blocked its original northward return to the guide.
Preserved failing route/logs in evidence/n02/diagnostics/east-return. Executor
responded normally; reported transport callbacks did not cause this assertion.
No duplicate build was launched. Previous running process exited14 and was reaped.

Second geometry correction removes that corner. Final candidate26 cells:14 added
alcoves/12 small blocks;1150 others unchanged. Added evidence-derived route-cell
envelope from all successful I01, N00b and N01 replay endpoints/straight segments.
Every previously tested floor cell must remain open; it identifies13,3 as the only
remaining conflict. All original routes/assertions stay intact. Original global
reachability alone was insufficient; the direct-route contract now supplements it.

Parent review also caught coverage omission: add all five N00b routes/43 checks
and all three N01 legacy routes/41 checks to full N02 acceptance. Both actual
DCC_LEGACY_RUN and DCC_CORNER_SAVE are supplied. Target1210 assertions/73 processes
(including193 existing fixture assertions). Normal corner save was produced by
five ordinary-input assertions on N01 ROM17e97672…cec637; no save/RAM edits.
Fresh forward camera proof comes from the existing continuous prepared route:
only previously unnamed capture filenames changed, identical controls/timings and
all assertions. Parent's wire-contrast/live-spent feedback remains N03, not hidden
inside geometry work. Next one clean committed rerun; two design corrections so
far for the route-obstruction blocker. Stop dependent work if still unresolved
under the three-attempt rule; preserve the scoped branch and accepted N01 baseline.

### N02 verified — 2026-10-06

Testeddec2c5e479cdceedf8b358d00448358640561b91, basec71636a; ROM
421d812a9a18ac1b1432dc5b831a5ba281c6e034249215364f3a99fd598d33b1.
Full73 processes/1210 assertions PASS:1017 production and193 labeled fixture.
All73 error logs empty. Original1053 +newer43+legacy41+rooms18+boundary47+
ordinary old-corner escape8 retained. Nine opponent/eight prop pixel checks pass.
All26 declared geometry changes/1150 unchanged cells/six event contracts/49 art
files verified. Two isolated complete exports preserve8807 tracked assets.

Actual six forward arrival views (Exit after closing its automatic message/save),
six center views, alcove/boundary and old-corner escape captures reviewed. Exit13,9
ordinary older save steps safely to12,9 with state/resources unchanged. Both earlier
route blockers resolved by removing obstructions; no retimed gameplay detours.
Evidence docs/evidence/n02/final includes raw logs, images, input identities and
precise production/fixture/retry/pacing limits. No ROM/save/executable committed.
Implemented/compiled/runtime verified YES; PR44 integration pending. Next merge
verified geometry, then N03 existing-state feedback: conspicuous live/spent wire,
opened cache/secret, sealed/open gate and defeated encounter markers. No new
flags/rewards/geometry; preserve approved art and full newer regression coverage.

### N03 state feedback candidate — 2026-10-06

N02 PR44 merged96f651d828dd380eb836c49493417913f390d15e; issue43 complete.
N03 issue45 task/n03-state-feedback, base that merge. Existing flags drive live/
spent wire, closed/breached secret panel, intact/broken gate supply line, sealed/
open gate and opened caches/cleared encounter markers. No new save variables,
rewards, collision changes or battle rules. Immediate successful interactions
refresh presentation; map load reconstructs it from persistent outcomes. Original
spark pixels clarify live cable; no pressure-plate art. Secret art aligns to the
wall above its unchanged interaction point. Dialogue identifies tag bag and
preparation benefit before spending charge, with existing page counts retained.

Acceptance: all1210 prior assertions retained plus read-only full tile-word checks
for immediate/return/cold states. Full state variants must preserve upper bits and
behavior;49 approved assets/six event contracts/N02 geometry unchanged. Real frames
must prove native alternate OBJ/BG art, visual readability, no capacity/cancel
side effects and save restoration. Source kit omissions unchanged. Implemented
candidate only; compile/runtime/PR/merge pending. Sole writer; parent owns scheduler.
