# Durable checkpoint

Handoff date: 2026-10-06. **Stage 0 complete; next task E01, not yet started.**
This is a restartable checkpoint, not completion of the authorized Stages 0–5.
No active engine writer or running build/container at this checkpoint.
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
