# Game design and campaign plan

Handoff date: 2026-10-06. Source: https://chatgpt.com/space/page_6ac46a8f43508191b2fc3db657411946

Snapshot of the accepted plan; implementation status lives in [progress.md](progress.md).
The launch instruction explicitly approves the defaults and delegates the sole continuation mechanism to the parent. Do not create another scheduler.

---

Development brief with working defaults for the Dot handoff. DungeonCrawlerCarlemon is a single-player Dungeon Crawler Carl RPG built from the Pokémon Emerald decompilation. Keep Emerald’s readable pixel art, tile-based exploration, dialogue and turn-based encounters while making crawler survival and Carl and Donut’s partnership the centre of play.

Repository: [12nuskek DungeonCrawlerCarlemon](https://github.com/12nuskek/DungeonCrawlerCarlemon).

## The intended experience

Walk through a strange, inhabited dungeon, meet other crawlers, discover dangerous rooms and improvise a way through encounters. The dungeon AI interrupts with achievements and commentary. Rewards change how Carl and Donut fight, while the next staircase gives each floor a clear objective.

The humour should come from character relationships, absurd rules and unexpected consequences. NPCs need motives, recurring conversations and visible reactions to quest outcomes. Write original adaptation dialogue; track book references separately.

## Design commitments and proposed defaults

| Area | Direction |
| --- | --- |
| Platform | GBA ROM built from Emerald source; emulator play is the first delivery target |
| Exploration | Top-down maps, four-direction movement, doors, stairs, interactive objects and secrets |
| Combat | Emerald-style turn-based battles with Carl and Donut acting together |
| Party | Permanent protagonists; allies join through story events when later supported |
| Collection | No catching, capture items, breeding or creature storage |
| Progression | XP, levels, skills, equipment and story milestones |
| Campaign | Authored floors with different rules and themes; first release focuses on one floor |
| Saving | Manual saves outside battle; explicit save compatibility policy during development |
| Scope | Single player; multiplayer and procedural generation excluded from the first release |

Confirmed requirements: the Emerald foundation, Dungeon Crawler Carl setting, no monster catching and implementation following the planning handoff. Use the working defaults below when Kurt sends the launch prompt; record later changes explicitly.

## Translating Emerald into a crawler RPG

| Emerald feature | DungeonCrawlerCarlemon adaptation |
| --- | --- |
| Towns and routes | Safe rooms, crawler hubs, dungeon corridors and themed floor regions |
| Trainer and wild battles | Hostile crawlers, dungeon mobs, ambushes and bosses |
| Double battles | Carl and Donut fight as a duo |
| Party and summary screens | Crawler roster, stats, skills and equipped items |
| Bag and item effects | Consumables, explosives, crafting materials and quest objects |
| Shops | NPC traders and dungeon service counters |
| Badges and story flags | Floor clearance and unlocked abilities or access |
| Field interactions | Examine objects, disarm traps, break obstacles and trigger environmental solutions |
| Pokédex | Optional discovered-enemy journal; never a completion requirement |
| Healing locations | Safe room recovery with clear rules |
| Contests and link features | Excluded initially; revisit only if a book-inspired mechanic needs them |

This is a substantial gameplay adaptation. Changing labels and sprites alone would leave Pokémon rules underneath.

## Exploration and floor structure

Each floor contains a hub or safe room, connected encounter zones, optional objectives, a boss or major challenge and a staircase. Hand-authored maps support foreshadowing, dialogue, secrets and intentional difficulty.

Show enemies on maps for important encounters. Use scripted ambushes in specific rooms; avoid unrestricted random encounters during the first slice. Donut appears in exploration scenes; following Carl is a later feature if it requires significant movement changes.

Floor countdowns should initially advance at story checkpoints, with clear warnings before irreversible transitions. A continuously running timer is deferred until the game is enjoyable without it.

## Combat and character identity

Use Emerald’s double-battle structure as the starting point. Both protagonists receive an action each turn when able. Begin with a small skill set, familiar HP and status feedback, and existing move resource behaviour. Shared resources, larger parties and grid combat are later decisions.

Carl specialises in close combat, endurance, explosives and interacting with hazards. Donut specialises in magic, ranged attacks, debuffs and support. These are adaptation roles; unlock timing must follow the chosen story period.

A battle might offer Carl a direct attack or an explosive that hits several enemies, while Donut can weaken a dangerous enemy or finish another. A map interaction before combat could destroy a supply cache and alter the encounter. That lets preparation matter without first implementing destructible battle arenas.

Defeat returns the player to a clear retry or load choice in the prototype. Book-style permanent death should be an optional campaign decision, not an obstacle to testing.

## Book-inspired systems

The following are proposed game adaptations. Exact names, characters and chronology need a canon check against the chosen books before final scripts.

| System | First playable version | Later expansion |
| --- | --- | --- |
| Dungeon AI | Scripted announcements and contextual dialogue | Reactions to unusual tactics and recurring player choices |
| Achievements | Several one-time achievements awarded by event flags | Hidden achievements and mutually exclusive outcomes |
| Loot boxes | Authored reward boxes with readable contents | Tiered reward pools and controlled random rewards |
| Skills and levels | A few distinct skills for each protagonist | Skill branches and build choices |
| Equipment | One equipped item per character using existing held-item behaviour | Multiple slots, affixes and equipment comparison |
| Crafting and explosives | One recipe, one material chain and a useful bomb | Workstations, recipe discovery and wider crafting |
| Traps and puzzles | Switches, marked hazards and scripted solutions | Skill checks and multiple solutions |
| Other crawlers | A small cast with persistent quest outcomes | Recurring allies, rivalries and factions |
| Safe rooms and guides | One recovery hub and guide interaction | Services, training and expanding hubs |
| Audience and sponsors | Story flavour and one reward event | Reputation and sponsor offers |
| Floor rules | One special rule expressed through maps and events | Distinct systems for later floors |
| Race and class choices | Reserved for a later appropriate story milestone | Stat changes, exclusive skills and dialogue consequences |

## Visual and interface direction

Retain Emerald’s crisp pixel presentation, small readable sprites and compact dialogue windows. Build new Carl and Donut overworld and battle sprites, dungeon tiles, portraits or trainer-style images, item icons and themed UI labels.

Rooms should look occupied: discarded supplies, signage, damage, NPC routines and recognisable safe spaces. Use lighting palettes, sound and map composition to distinguish threatening corridors from safe rooms.

Main menu targets: Crawlers, Inventory, Skills or Stats, Journal, Save and Options. Journal entries explain the current objective, floor rule and discovered clues. Show achievement and loot notices briefly, with details available afterwards.

## First playable slice

Target a 20–30 minute authored session after iteration. This is a design target, not a development estimate.

1. A short introduction establishes Carl, Donut and the dungeon entrance.

2. A tutorial room teaches movement and interaction.

3. A guide and safe room establish recovery, objectives and the AI.

4. Two connected dungeon zones contain three enemy archetypes, a trap, a secret and another crawler.

5. The player earns an achievement, opens a loot box and crafts or receives an explosive.

6. A duo battle tests distinct Carl and Donut actions.

7. A boss encounter offers a preparation-based advantage.

8. A staircase closes the slice and previews the next floor.

Prototype content can compress chronology. Label deliberate departures so they do not accidentally become canon assumptions.

### Completion criteria

- A new player can finish from a fresh save without debugging commands.

- Carl and Donut each have a useful action and readable turn feedback.

- No visible menu or gameplay path allows catching, storing or breeding creatures.

- Rewards, quest outcomes and protagonist progression survive save and reload.

- The boss can be beaten with more than one reasonable strategy.

- Defeat, item use and floor transitions do not trap the player.

- The slice has original Dungeon Crawler Carl artwork and writing where scheduled; remaining placeholders are explicitly listed.

## Campaign expansion

After the slice passes review, finish an authored first floor and use it as the content template for later floors. Add race and class progression at the selected story point, then expand NPC continuity, crafting, sponsors and floor-specific rules.

Do not promise every book or every floor in the first release. Each new floor should add one meaningful mechanic and reuse stable systems. Maintain a content ledger with book reference, adaptation choice, prerequisites, maps, dialogue, reward and test route.

## Working defaults for the handoff

| Decision | Default |
| --- | --- |
| Delivery | GBA ROM and emulator testing |
| Story | Opening of Book 1, original adaptation dialogue, no later-book spoilers |
| Combat | Carl and Donut acting together through double battles |
| Scope | Stages 0–5, then up to five focused improvement cycles |
| Defeat | Accessible retry or reload; no permanent death initially |
| Content | Authored rooms and deterministic first rewards |
| Expansion | Review the playable slice before building the rest of Floor 1 |
| Release | Development output and review package; public release is a separate step |

Sending the launch prompt adopts these defaults for implementation. They are not a claim that each choice was separately confirmed.

## Playable slice content specification

Use a small set of connected spaces: entrance tutorial, safe room, two dungeon zones, boss chamber and exit staircase. Map size follows playtesting and the 20–30 minute target rather than padding corridors.

| Content | Minimum implementation |
| --- | --- |
| Protagonists | Carl and Donut with distinct overworld and battle presentation |
| Actions | Two useful combat actions per protagonist; at least one support or debuff choice |
| Enemies | Three distinct behaviours: simple melee, durable enemy and disruptive enemy |
| Boss | One readable threat with two viable responses; preparation can give an advantage |
| NPCs | Guide plus two other crawlers with different motives |
| Quest | One optional objective with persistent accepted and completed states |
| Rewards | Two one-time achievements, two authored loot boxes and one equipped-item effect |
| Crafting | One recipe and enough obtainable materials to demonstrate it |
| Exploration | One readable trap and one optional secret |
| AI | Contextual entrance, achievement and boss commentary using authored text |
| Ending | Staircase transition and clear slice-complete screen or message |

These counts define adaptation content, not book canon. Balance values are provisional and should be tuned through recorded playtests.

## State and recovery rules

Achievement and loot rewards each have a unique persistent ID. Award once; repeat interactions show the resolved state. Crafting checks materials and inventory capacity before consumption, with no partial consumption on failure.

Quest state, boss defeat and staircase access must agree after reload. Place recovery and retry routes so the player cannot spend a required item and permanently block the main route. Optional rewards must not be mandatory for defeating the boss.

Both protagonists remain in the roster. Incapacitation removes actions until recovery; defeating both triggers the agreed recovery flow. Save behaviour and retry penalties must be explained in-game and tested rather than inherited accidentally from Emerald.

## Story and asset ledger

For every scene, record its purpose, prerequisites, characters, source reference if available, intentional adaptation, dialogue, reward and test route. If exact chronology is uncertain, mark it for review and use a neutral original scene where possible.

For each sprite, tileset, icon and sound, record source, author, provenance and replacement status. Placeholder art is acceptable in early technical milestones; the final slice review must list every remaining placeholder.

See [Dot development loop and task backlog](https://chatgpt.com/space/page_6ac46c92905c8191b32234b2aeaf42d2) for task dependencies, execution boundaries and completion checks.

## Foundation source

[pret pokeemerald](https://github.com/pret/pokeemerald) identifies itself as the Pokémon Emerald decompilation and builds a GBA ROM. The detailed adaptation above is the proposed project design, not functionality already supplied by upstream.

