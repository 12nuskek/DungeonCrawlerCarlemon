# Dot development loop and task backlog

Handoff date: 2026-10-06. Source: https://chatgpt.com/space/page_6ac46c92905c8191b32234b2aeaf42d2

Snapshot of the accepted plan; implementation status lives in [progress.md](progress.md).
The launch instruction explicitly approves the defaults and delegates the sole continuation mechanism to the parent. Do not create another scheduler.

---

Use this operating plan with the [game design](https://chatgpt.com/space/page_6ac46a8f43508191b2fc3db657411946) and [implementation roadmap](https://chatgpt.com/space/page_6ac46a99bf648191834bad00708eb7db). The first autonomous objective is a tested, reviewable playable slice in [DungeonCrawlerCarlemon](https://github.com/12nuskek/DungeonCrawlerCarlemon).

Kurt has requested a handoff prompt for continuous development. Sending that prompt authorises the scope it specifies. Saving this Page does not launch tasks or create a schedule.

## Scope and working defaults

Use stock pret/pokeemerald at a pinned revision, a GBA ROM target, Carl and Donut duo battles, authored maps and accessible defeat recovery. Adapt the opening of Book 1 with original dialogue; exclude later-book spoilers. A compressed tutorial may be labelled as an adaptation. These are working defaults, not a record of individual user confirmations.

Complete Stages 0–5 and improve that slice. The rest of Floor 1 and later floors remain the expansion backlog until Kurt reviews the playable result. Routine implementation choices should not require repeated confirmation.

## First run

1. Read all linked plans and inspect the current repository, branches, changes and any existing automation. Preserve user work and avoid duplicate setup.

2. Verify what the Dot can actually execute: repository edits, builds, emulator checks and Codex Cloud task submission or status reads. Use supported tools; do not assume a connection exists.

3. Copy the accepted design into repository documentation. Record Page links and the handoff date; repository docs then provide durable task context. Reconcile later Page changes deliberately.

4. Prepare AGENTS.md, README, docs/game-design.md, docs/roadmap.md, docs/backlog.md, docs/content-ledger.md, docs/testing.md and docs/progress.md.

5. Establish a reproducible baseline before gameplay changes. Choose the compiler path from the pinned upstream instructions and prove it in the actual execution environment.

6. If recurring execution is supported, configure one resumable continuation mechanism using the handoff authorisation. Report its real cadence and identifier. If it is unavailable, complete available work in the current run and leave a restartable checkpoint; do not claim continuous background operation.

## Dependency ordered backlog

| ID | Depends on | Outcome and acceptance |
| --- | --- | --- |
| F01 | None | Record upstream SHA and import provenance; clean build produces a ROM and baseline boots |
| F02 | F01 | Document setup and add repeatable build checks; fresh environment reproduces build |
| E01 | F01 | Carl avatar and tutorial map; four directions, collisions, interaction and exits work |
| E02 | E01 | Safe room and guide dialogue; recovery and return route work |
| B01 | F01 | Carl and Donut encounter prototype; both can act and victory returns to the map |
| B02 | B01 | Distinct actions, enemy turns and defeat recovery; depleted resources and incapacitation handled |
| B03 | B02 | Capture and creature-storage paths inaccessible; audit UI, item effects and scripted entry points |
| R01 | B02, E02 | XP and one equipped item affect gameplay and survive save reload |
| R02 | R01 | One-time achievements and loot box rewards survive reload without duplication |
| D01 | E02, R02 | Trap, secret and optional quest; branch outcomes and backtracking remain valid |
| D02 | R01, D01 | One explosive recipe; sufficient materials are obtainable and consumption is correct |
| S01 | B03, R02, D02 | Join maps, three enemy archetypes, boss and staircase into the complete slice |
| S02 | S01 | Review sprites, palettes, text, sound, UI language and original dialogue; track placeholders |
| S03 | S02 | Fresh-save completion, alternate strategy, defeat and save tests pass; provide a review package |

Keep one active implementation task. Tasks that are theoretically independent may still touch common engine state. Do not introduce parallel writers to the same files or branch.

## Loop for each work cycle

Read the branch head and checkpoint before selecting work. If a Cloud task or PR is still running, reconcile its state before submitting more work.

Pick the highest priority dependency-ready task. Prioritise build failures and progression blockers over new features. Write its objective, allowed scope, acceptance checks and exclusions before implementing or submitting it.

Make a focused change on a task branch, run the required checks and inspect the resulting diff. Store runtime evidence against the tested commit, including the route and result. A screenshot alone does not prove completion.

Commit and push working changes. Open a reviewable PR when available. Merge within the authorised milestone only after relevant build and runtime checks pass and the diff has been reviewed. Honour branch protections; record the merged commit before taking a dependent task.

Update docs/backlog.md and docs/progress.md with completed work, remaining checks, blockers and the exact next task. Keep Page updates to meaningful milestone changes. Then continue to the next task while the current execution permits it.

At the end of a run, save a checkpoint even if incomplete. A later run resumes from recorded state and current GitHub evidence instead of repeating imports, tasks or PRs.

## Definition of done

A task is complete only when its acceptance checks pass or its deliverable is explicitly a documented audit. Keep separate statuses for implemented, compiled, runtime verified and merged. Never mark runtime work done because compilation passed.

For the playable slice, verify:

- Fresh save through introduction, safe room, dungeon zones, boss and staircase.

- Both protagonists acting, one incapacitated, both defeated, victory and escape where allowed.

- Item use, empty inventory, recipe failure and successful crafting.

- Repeated achievement triggers and loot box interactions, including reload and map re-entry.

- Save and reload before and after rewards, quests, boss and floor transition.

- Optional quest accepted, declined and completed; main route remains finishable.

- Capture items, tutorial capture flows, breeding and creature storage cannot be accessed.

- Directional sprites, collisions, dialogue bounds, palettes and transitions are readable and correct.

Where emulator execution is unavailable, report the exact missing capability and keep the affected milestone awaiting runtime verification. Continue independent documentation or content work; do not merge changes under a false runtime claim.

## Retry and stop rules

For a failed task, identify the cause and attempt at most three materially different fixes for the same blocker. Record each hypothesis and result. Stop dependent work after repeated failure; continue another ready task if one exists.

Stop and request a focused decision only when changing the target platform or engine, adding a major unplanned system, expanding beyond the slice, facing an unresolved story contradiction essential to progress, or lacking access needed to execute. Use clearly labelled original adaptation content for nonessential canon uncertainty.

Do not purchase services, alter billing, wipe repository history or branches, force-push, bypass protections, publish a public playable release or change visibility as part of this loop. Preserve provenance and track asset sources.

## Checkpoint format

Each progress entry records task ID, state, branch, commit, PR or Cloud task reference, commands and results, runtime evidence, known issues, next action and blockers. Record the upstream revision and toolchain once in the setup documentation and link them.

The continuation mechanism should skip active work and stop or disable itself at the completion boundary. It must not generate empty tasks, repeated notifications or speculative features just to stay busy.

## Improvement after the slice

Run a full playthrough, collect concrete defects and prioritise them: progression blocker, incorrect combat or reward behaviour, confusing interaction, then visual polish. Choose one measurable improvement per cycle and rerun checks affected by that change.

Use up to five initial improvement cycles after S03. If no substantive issue remains, stop early. End with a concise review package containing how to build and play, tested commit, evidence, remaining limitations and the next-floor proposal. Await Kurt’s playtest before expanding the campaign.

