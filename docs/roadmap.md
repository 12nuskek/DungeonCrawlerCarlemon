# Emerald implementation and Codex Cloud roadmap

Handoff date: 2026-10-06. Source: https://chatgpt.com/space/page_6ac46a99bf648191834bad00708eb7db

Snapshot of the accepted plan; implementation status lives in [progress.md](progress.md).
The launch instruction explicitly approves the defaults and delegates the sole continuation mechanism to the parent. Do not create another scheduler.

---

Implementation roadmap for [DungeonCrawlerCarlemon](https://github.com/12nuskek/DungeonCrawlerCarlemon). The Dot handoff uses working defaults and authorises Stages 0–5 when Kurt sends the launch prompt. Repository preparation, implementation and continuation setup belong to that subsequent run.

## Foundation choice

Start from a pinned revision of [pret pokeemerald](https://github.com/pret/pokeemerald). Preserve upstream history or record its exact revision and provenance when importing into the existing repository. Prove a clean baseline build before changing gameplay.

Evaluate expansion forks only if the approved slice requires capabilities missing from stock Emerald. Extra battle features also introduce additional dependencies and a larger codebase.

The first deliverable is a GBA ROM. A browser emulator wrapper is a separate later deliverable if web testing is wanted.

## Engine adaptation boundaries

These source areas exist in upstream; the changes below are implementation hypotheses to validate during the first audit.

| Area | Existing starting point | Planned work |
| --- | --- | --- |
| Battles | src/battle_main.c, src/battle_setup.c, battle controllers and scripts | Duo encounter setup, crawler actions, enemy behaviour and capture blocking |
| Character data | src/pokemon.c, party_menu.c, pokemon_summary_screen.c | Use existing records behind a crawler-facing interface; audit hidden species assumptions |
| Exploration | src/field_control_avatar.c, field_player_avatar.c, fieldmap.c | Carl avatar, interactions and encounter triggers |
| Inventory | src/item.c, item_menu.c, item_use.c | Crawler consumables, explosives and one equipment effect |
| Persistence | src/save.c, load_save.c and save structures | Quest and achievement flags, progression, save version policy |
| Content | data, graphics and sound | Authored maps, scripts, sprites, tiles, dialogue and audio |

Keep existing internal Pokémon naming where renaming would create widespread churn. Player-facing language must describe crawlers, skills and enemies. Add small crawler interfaces around reusable engine behaviour; do not maintain two competing combat or progression models.

Remove catching at both the interface and battle-rule levels. Audit capture scripts, item effects, tutorials, rewards, shops and storage entry points so hidden paths cannot reintroduce it.

Prototype equipment with the held-item slot. Multiple equipment slots, custom stats and extensive save changes need separate design work after the slice.

## Staged delivery

| Stage | Deliverable | Exit check |
| --- | --- | --- |
| 0 Foundation | Pinned upstream, reproducible setup, baseline build and provenance notes | Clean checkout builds; unmodified ROM boots |
| 1 Exploration | Carl avatar, one room, interaction, dialogue and safe-room access | Movement, collisions, transitions and save reload work |
| 2 Duo combat | Carl and Donut versus a small enemy encounter | Both act; win, defeat and return to map work; catching is blocked |
| 3 Rewards | XP, one achievement, one loot box and one equipped item | Rewards persist and cannot be duplicated accidentally |
| 4 Dungeon systems | Trap, optional quest and one explosive recipe | Quest branches and item consumption survive reload |
| 5 Playable slice | Connected maps, guide, NPCs, boss and staircase | Full completion route passes the game design criteria |
| 6 First floor | Expanded encounters, art, balancing and story | Fresh-player playtest passes; no progression blockers |
| 7 Later floors | Reusable content pipeline and approved new systems | Each floor passes regression and content review |

Stages are dependency ordered. Commit a working increment before starting the next major engine change. Defer schedule estimates until the baseline and duo-combat work reveal the engine constraints.

## Proposed repository documentation

At handoff, add a concise README, AGENTS.md, docs/game-design.md, docs/roadmap.md, docs/backlog.md, docs/content-ledger.md, docs/testing.md and docs/progress.md alongside the imported engine. Copy the current Page design, record its links and handoff date, and use repository documentation as durable task context.

AGENTS.md should state build commands, module boundaries, no-catching requirements, save rules and required validation. It should also require the agent to identify unsupported assumptions instead of silently inventing book canon.

## Codex Cloud task contract

Each task needs a narrow outcome, dependencies, allowed scope, acceptance checks and a short list of exclusions. Keep content work and high-risk engine changes in separate reviewable changes.

Example task briefs to create after approval:

1. **Establish the baseline:** import the agreed upstream revision, document provenance and toolchain, build it and record the boot check. Make no gameplay changes.

2. **Create the tutorial room:** add Carl’s avatar, map, interaction and exit using placeholder assets where necessary. Do not alter battles or the save layout.

3. **Prove duo combat:** initialise Carl and Donut, trigger a two-character encounter, validate victory and defeat, and block capture behaviour.

4. **Add achievement rewards:** award one event once, persist its state and show a readable reward notice.

5. **Complete the slice:** connect the approved content and run the full playtest route.

The launch prompt is the execution handoff. Start with repository preparation and Stage 0, then continue through Stage 5 using [Dot development loop and task backlog](https://chatgpt.com/space/page_6ac46c92905c8191b32234b2aeaf42d2). Stages 6–7 remain a proposal until Kurt reviews the slice.

## Build and validation strategy

Use the upstream installation instructions at the pinned revision as the baseline. Record compiler and dependency versions and cache toolchain inputs where the chosen environment supports it.

A successful compile proves only that a ROM was produced. Runtime checks must include boot, new game, exploration, each battle outcome, inventory effects, rewards, staircase transitions and saving.

Maintain short deterministic test routes and representative save fixtures. Check ordinary GBA limits: palette and sprite budgets, text overflow, map boundaries, ROM space and save data capacity. Establish a known baseline before modifying any of them.

Automate compilation and content checks where practical. Add targeted logic tests for reward duplication and progression only where they exercise meaningful behaviour. Capture emulator screenshots and report runtime checks separately from compile results.

## Risks that affect the design

| Risk | Response |
| --- | --- |
| Battle code assumes Pokémon species and abilities | Adapt through a narrow crawler interface and validate a duo encounter early |
| More equipment and custom progression exceed existing data structures | Begin with existing slots and a small skill set |
| Engine changes break old saves | Version saves and declare compatibility for each development milestone |
| A complete book series is too much content for the first release | Ship a short slice, then one floor |
| Procedural maps weaken authored story and testing | Use authored maps first |
| AI text and item descriptions overflow windows | Enforce text limits and review in-game screens |
| Campaign chronology becomes inconsistent | Require a content ledger and a defined spoiler ceiling |

## Sources

- [pret pokeemerald README](https://github.com/pret/pokeemerald/blob/master/README.md)

- [Upstream installation guide](https://github.com/pret/pokeemerald/blob/master/INSTALL.md)

- [Upstream source directory](https://github.com/pret/pokeemerald/tree/master/src)

The source confirms the engine and build foundation. The roadmap and module adaptations are proposed work and need validation against the revision selected for implementation.

## Foundation gate and delivery evidence

Before gameplay work, record the upstream commit, compiler path, installation inputs, actual build command and emulator version. Choose exact commands from the pinned source and verify them rather than copying an assumed setup. For an unchanged matching build, compare against the upstream expected ROM hash where applicable; custom builds need their own identity and boot checks.

The baseline deliverable includes build logs and an emulator boot result. If the environment cannot run an emulator, mark the gate awaiting runtime verification and continue independent setup work.

Keep generated ROMs and build products out of source commits. The review package should identify the tested commit and build checksum, provide reproducible build and play instructions, and provide accessible runtime evidence. Respect existing artifact and release permissions.

## Task review and integration

Each task branch must record its base commit. Inspect current repository state before integrating; never overwrite concurrent work. Review the diff for acceptance coverage, accidental Pokémon-facing mechanics, save changes and unrelated edits. Passing compilation is insufficient for runtime-sensitive merges.

Within the authorised slice, the Dot may push, create PRs and merge verified changes when repository permissions and protections allow. If integration is blocked, preserve the branch or PR, record the blocker and continue only genuinely independent tasks.

Keep Cloud task IDs and status in the checkpoint when Cloud execution is available. Reuse existing task results instead of submitting duplicates. If Cloud submission is unavailable, perform supported implementation directly and report the actual execution method.

## Slice completion gate

Deliver a fresh-save playthrough, alternate boss strategy, defeat recovery, reward duplication checks and save/reload evidence. Report implemented, compiled, runtime verified and merged states separately.

Once the slice passes, perform up to five evidence-led improvement cycles. Fix failures before expanding scope. Stop early when no meaningful defect remains, present the review package and await Kurt’s playtest before Stage 6.

