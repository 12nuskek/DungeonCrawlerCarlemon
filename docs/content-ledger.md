# Content and asset ledger

Handoff: 2026-10-06. E01 adds the first authored adaptation scenes and Carl sprite.
Book ceiling: opening of Book 1. Exact chapter chronology remains unverified.
Do not treat proposed design counts or roles as book canon.

| Asset/content | Source/author | Status | Replacement/verification |
| --- | --- | --- | --- |
| Baseline engine, maps, sprites, music and text | pret/pokeemerald pinned source; original game's material retained upstream | Technical baseline only | Not claimed as original adaptation art; replace scheduled slice assets in S02 |
| Carl walking sprite and palette | Original indexed pixels by Codex, source `scripts/content/carl_sprite.py`; no tracing or upstream sprite edit | E01 implemented and runtime reviewed | Simple prototype, S02 refinement; walking only |
| Donut overworld and both battle presentations | To be authored | Missing | B01/S02; E01 describes Donut on Carl's shoulder but does not draw her |
| Entrance and quiet landing maps | Authored map geometry/events in `engine/data/maps/DCC_*` and `data/layouts/DCC_*` | E01 implemented | Upstream cave tiles, crate and rock graphics remain placeholders |
| E01 dialogue and AI announcements | Original Codex adaptation text in `DCC_Entrance/scripts.inc` and `DCC_Vestibule/scripts.inc` | Implemented and runtime reviewed | No book text copied; source is the accepted design brief, not a verified chapter quotation |

For each scene record ID, purpose, prerequisites, characters, book reference,
intentional adaptation, map, dialogue, reward IDs and deterministic test route.
For each asset record path, source, author, provenance and placeholder/replacement
status. A compressed duo tutorial is permitted only with a labelled departure.

## E01 scenes and state

| Scene | Purpose / prerequisites | Characters and original dialogue | Reward/state / test route |
| --- | --- | --- | --- |
| E01-INTRO | Fresh New Game spawns at entrance (4,8) | Carl reacts to the dungeon; Donut described on his shoulder; AI teaches movement | No reward; persistent `FLAG_DCC_INTRO_SEEN` (existing bit 0x20). New-game route, then map re-entry/cold reload must not repeat |
| E01-CRATE | Face crate at (4,5), press A | Empty crate, original note explains START → SAVE and northeast ladder | No item/reward; `FLAG_DCC_CRATE_READ` (existing bit 0x21) selects repeat text. Test before/after real save reload |
| E01-ROCK | Interact with either visible rock at (7,6)/(7,7) | Original observation suggests walking around | No reward/flag. Test two eastward approaches and path around; optional rock dialogue not yet replayed |
| E01-LANDING | Ladder at (12,4) in either room | Original quiet-room crate observation | No recovery service yet (E02); reciprocal warp IDs 0; test out/back/reload |

Intentional departures: the opening is compressed into a small authored tutorial;
the crate, room layout, ladder, AI lines and quiet landing are game inventions,
not asserted Book 1 locations or quotations. Outfit is an original early-Carl
visual interpretation (brown hair, bare torso/feet, patterned shorts); exact
chapter/visual canon has not been independently checked. No later-book spoilers.

Remaining E01 placeholders: stock Emerald title/logo/music, cave tiles, crate/rock
sprites, Bag/Options/Save/Badge labels and trainer-card/battle/running art inherited
from upstream. Running/cycling remain disabled; B01 adds the optional landing trial. These
are scheduled for later scoped tasks/S02, not claimed as finished crawler UI/art.

## B01 duo trial and placeholders

B01-TRIAL: interact with the rehearsal attendant at landing (9,6), with both
protagonists conscious. Original AI text explicitly calls this a rehearsal and
promises restoration. The invented trial compresses duo combat into the tutorial;
it makes no claim about Book 1 chronology or a canonical encounter. Only victory
sets persistent trainer flag `TRAINER_FLAGS_START + TRAINER_DCC_TRIAL` (0x857).
Loss restores both locally without the stock whiteout narrative; retry remains
available. Victory also restores both and repeat interaction gives resolved text.
See `docs/evidence/b01/*.route` for ordinary-input victory/loss/save/reload routes.

Fixed protagonist records: Carl uses temporary Machop stats/art at level 8, Tackle
and Focus Energy; Donut uses temporary Meowth stats/art at level 8, Swift and Growl.
These are implementation proxies, not authored character art or canon skill names.
Two level-8 trial targets use upstream Zigzagoon/Wurmple records and Tackle.
The attendant MAN_1 sprite, Pokémaniac battle portrait, Pokémon/trainer/battle menu
labels, send-out animation, skill names and enemy artwork are upstream placeholders
requiring B03/S02 replacement. No new downloaded assets. Original code and AI lines
were authored in this task. Final presentation and two useful tuned actions per
character are not claimed complete; B02 and S02 remain required.

Existing XP and trainer prize behavior is provisional, not the R01 reward design.
No achievement, loot or inventory reward is added. Donut explicitly uses the
placeholder species' unused ABILITY_NONE slot to prevent random Pickup loot. Trainer index 855 uses existing
reserved flag capacity; 8 reserved trainer IDs remain. Both protagonists are
initialized only on New Game; E01 saves lack that roster and are unsupported here.

## Visual quality acceptance clarification — 2026-10-06

Kurt asked whether the levels will eventually look substantially better than the
E01 cave screenshots. Parent confirmed the existing in-slice commitment: custom
dungeon tiles and protagonist sprites, props/signage/damage, distinct palettes and
more deliberate room composition within Emerald's readable GBA style. Current
stock cave rooms are functional placeholders, not final quality. Deliver scheduled
art in S02 before Stage 5 review; do not defer all artwork until Stage 6. Follow the
gameplay dependencies first, then implement the visual pass in the real engine.
Include actual before/after emulator screenshots and list every remaining
placeholder explicitly. This clarifies accepted scope, not a platform expansion.

## E02 guide and recovery

E02-GUIDE is an original unnamed guide at landing (4,8), motivated by keeping
crawlers alive rather than carrying them. This is an invented compressed tutorial
scene, not a claim about a named Book 1 character or chapter. First meeting uses
existing unused flag 0x22 (`FLAG_DCC_GUIDE_MET`); repeat conversations skip the
introduction. The guide freely restores both protagonists using the existing
party-healing function, then explains the trial before victory or return/save
instructions afterward. No reward or inventory cost; save structures unchanged.

The guide's EXPERT_M overworld sprite is an upstream placeholder scheduled for S02.
B01 trial victory now preserves actual injuries/action depletion so visiting the
guide is meaningful; its text directs the player to the south wall. Defeat still
restores both at the same landing and permits retry. This intentionally supersedes
B01's victory auto-heal behavior; historical B01 evidence remains attributed to its
own tested revision. Actual party HP and encrypted party PP are asserted before/
after healing, with normal status values checked. Curing a nonzero persistent
status is not runtime-proven yet: this encounter's enemies only use Tackle.
