# Content and asset ledger

Handoff: 2026-10-06. E01 adds the first authored adaptation scenes and Carl sprite.
Book ceiling: opening of Book 1. Exact chapter chronology remains unverified.
Do not treat proposed design counts or roles as book canon.

| Asset/content | Source/author | Status | Replacement/verification |
| --- | --- | --- | --- |
| Baseline engine, maps, sprites, music and text | pret/pokeemerald pinned source; original game's material retained upstream | Technical baseline only | Not claimed as original adaptation art; replace scheduled slice assets in S02 |
| Carl walking sprite and palette | Original indexed pixels by Codex, source `scripts/content/carl_sprite.py`; no tracing or upstream sprite edit | E01 implemented, runtime review in progress | Simple prototype, S02 refinement; walking only |
| Donut overworld and both battle presentations | To be authored | Missing | B01/S02; E01 describes Donut on Carl's shoulder but does not draw her |
| Entrance and quiet landing maps | Authored map geometry/events in `engine/data/maps/DCC_*` and `data/layouts/DCC_*` | E01 implemented | Upstream cave tiles, crate and rock graphics remain placeholders |
| E01 dialogue and AI announcements | Original Codex adaptation text in `DCC_Entrance/scripts.inc` and `DCC_Vestibule/scripts.inc` | Implemented, runtime review in progress | No book text copied; source is the accepted design brief, not a verified chapter quotation |

For each scene record ID, purpose, prerequisites, characters, book reference,
intentional adaptation, map, dialogue, reward IDs and deterministic test route.
For each asset record path, source, author, provenance and placeholder/replacement
status. A compressed duo tutorial is permitted only with a labelled departure.

## E01 scenes and state

| Scene | Purpose / prerequisites | Characters and original dialogue | Reward/state / test route |
| --- | --- | --- | --- |
| E01-INTRO | Fresh New Game spawns at entrance (4,8) | Carl reacts to the dungeon; Donut described on his shoulder; AI teaches movement | No reward; persistent `FLAG_DCC_INTRO_SEEN` (existing bit 0x20). New-game route, then map re-entry/cold reload must not repeat |
| E01-CRATE | Face crate at (4,5), press A | Empty crate, original note explains START → SAVE and northeast ladder | No item/reward; `FLAG_DCC_CRATE_READ` (existing bit 0x21) selects repeat text. Test before/after real save reload |
| E01-ROCK | Interact with either visible rock at (7,6)/(7,7) | Original observation suggests walking around | No reward/flag. Test collision from two directions and path around |
| E01-LANDING | Ladder at (12,4) in either room | Original quiet-room crate observation | No recovery service yet (E02); reciprocal warp IDs 0; test out/back/reload |

Intentional departures: the opening is compressed into a small authored tutorial;
the crate, room layout, ladder, AI lines and quiet landing are game inventions,
not asserted Book 1 locations or quotations. Outfit is an original early-Carl
visual interpretation (brown hair, bare torso/feet, patterned shorts); exact
chapter/visual canon has not been independently checked. No later-book spoilers.

Remaining E01 placeholders: stock Emerald title/logo/music, cave tiles, crate/rock
sprites, Bag/Options/Save/Badge labels and trainer-card/battle/running art inherited
from upstream. Running/cycling and battles are not enabled in these rooms. These
are scheduled for later scoped tasks/S02, not claimed as finished crawler UI/art.
