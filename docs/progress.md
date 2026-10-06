# Durable checkpoint

Handoff date: 2026-10-06. **Stage 0, E01 and B01 complete; E02 active.**
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
