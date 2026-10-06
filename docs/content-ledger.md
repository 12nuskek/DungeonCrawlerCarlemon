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

## B02 action records (implementation under validation)

Dedicated moves 355–358 are STRIKE (40-power physical normal hit, 8 uses), BRACE
(self defense +1, 40 uses), SPARK (50-power magic/stock psychic type, both foes,
2 uses), and WEAKEN (both foes' attack -1, 40 uses). These are provisional authored
adaptation names and tuning, not claimed Book 1 skill names or unlock chronology.
They use existing effects and placeholder Tackle/Harden/Swift/Growl animations;
upstream enemy move records are unchanged. Original descriptions are in the move
text table. Both protagonists initialize with these two role-specific actions on
New Game; fresh B02 saves required. No save-layout change, and IDs remain below
the existing 9-bit learnset encoding limit. Original battle art/type-label cleanup
remains scheduled within S02; capture/evolution/storage audit remains B03.

B03: crawler-facing normal/battle menu labels and original capture refusal text.
Inventory width enlarged after actual clipping observed. Roster exposes Summary
and Item; permanent protagonist order. Stock species summary, TM/HM/berry pocket
labels, pocket indicator spacing and battle art remain explicit S02 placeholders.
No new canon claims or adaptation chronology. [Collection audit](collection-audit.md).

## R01 equipment and progression (2026-10-06)

- `EQUIP_WRAP_01`: optional safe-room crate, no prerequisite; grant one WRIST WRAP
  (`ITEM_DCC_WRIST_WRAP`,377), persistent `FLAG_DCC_WRAP_TAKEN`0x23 only after a
  successful inventory add. Repeat shows resolved text. Full inventory leaves the
  item available. Original teeth joke/equip instructions/optional-route dialogue.
- Equipment reuses the held-item slot and stock normal-type attack modifier at20.
  This scales the attack input by20% with integer rounding; it is not a promise of
  exactly20% final damage. Useful for STRIKE, not psychic SPARK. No multiple slots.
- WRIST WRAP icon/palette currently reuses pret Silk Scarf artwork (upstream pin
  in provenance); explicitly replace/review in S02. Item name/description/dialogue
  are original adaptation content, not a quoted book item or canon unlock claim.
- Tutorial Carl/Donut begin level8,20 XP before level9 on existing growth curves.
  This deliberate compression makes earned XP/stat growth visible in the trial.
  Species/stat curves and battle presentation remain technical placeholders;
  creature evolution/automatic species learning remain blocked by B03.
- Test route: new game→landing crate→repeat→Inventory/Give to Carl→save/cold reload→
  trial→level growth→guide→save/reload→take/re-equip. Also win without the optional
  item and exercise full-inventory refusal in a separately labelled test fixture.

## R02 achievement and loot ledger (2026-10-06)

| Persistent ID | Trigger / prerequisite | Authored result | Flag |
| --- | --- | --- | --- |
| ACH_READER_01 | Read the original entrance note | AI: Careful Reader; south supply box unlocks |0x24|
| ACH_DUO_01 | Win the duo trial | AI: Better Together; workshop box unlocks |0x25|
| LOOT_SUPPLY_01 | ACH_READER_01; interact entrance(10,9) | Exactly two Potions, one successful grant |0x26|
| LOOT_SCRAP_01 | ACH_DUO_01; interact landing(11,8) | Exactly two Scrap (item378), one successful grant |0x27|

All names/notices are original compressed-tutorial adaptation text, not quoted book
achievements or claims about canon chronology. Box flags are set only after the
whole inventory addition succeeds. Locked, insufficient-space and resolved text
remain available. Optional rewards never gate the main route. SCRAP is reserved
for the already planned D02 recipe; its description explicitly says it is not
usable alone. No recipe or random reward system is claimed implemented here.

Both stationary box props reuse upstream Moving Box art, and SCRAP reuses the
Metal Coat icon/palette from the pinned upstream. These are explicit S02 art
placeholders. Positions hug room edges and preserve the established row8 entrance
path and row7 landing path. No new map or authored battle behavior in this task.

## D01 original service-room adaptation (2026-10-06)

Original neutral scene, no direct book quotation or uncertain canon identification.
MARA wants reliable escape routes; LEV wants overlooked supplies. Neither is claimed
to be a book character. This optional service room compresses tutorial chronology.

| Scene/state | Prerequisites and effect | Persistent ID / test route |
| --- | --- | --- |
| Service room | Quiet Landing west ladder, always reversible | New authored 16×12 map; no random encounter |
| Warning/trap | Sign warns of cracked tile; routes on both sides | 0x28 spent; first crossing damages Carl by4 to minimum1, paralysis if healthy |
| Mara offer | Decline freely, return to accept | 0x29 declined;0x2A accepted (accept clears declined) |
| Route tag | Accepted quest; north crate, non-tossable key item379 | 0x2C found; once only |
| Return tag | Two Scrap fit before tag removal/completion | 0x2B complete; repeat dialogue, no duplicate |
| Lev/panel | Optional clue to north wall beside crate | 0x2D secret medicine claimed after capacity check |

Guide recovery cures the actual trap status; walking cannot cause poison damage or
KO. Trap does not respawn across map/reload. Quest/secret never gates the ladder.
All dialogue authored for this adaptation. Cave tiles/NPC/box/item graphics remain
upstream placeholders for S02. New metatile0x39E copies upstream cracked-floor
visuals with ordinary floor behavior; it never invokes stock falling-floor logic.
Route tag uses the Metal Coat icon temporarily. Source map data are authored assets,
not generated ROM binaries. Runtime verified: [D01 114-check evidence](evidence/d01/README.md); integration pending.

## D02 explosive recipe and optional cache (2026-10-06)

Original compressed tutorial adaptation, not a quoted book scene. Service-room
workbench6,8 turns two bag-held SCRAP378 into CHARGE380. Obtain Scrap2 from R02
trial box and another2 from Mara; either source supports the one-recipe tutorial.
Workbench checks materials then output capacity before removing inputs. Cancelling
or failure consumes nothing. It conservatively requires room before crafting,
even when consuming materials could free a slot. Explain that refusal in dialogue.

Sealed east cache13,8 offers explicit consent to spend Charge1 for SuperPotion22
quantity1. Check reward capacity before charge consumption, then flag0x2E prevents
repeat rewards/spending. It never gates return or main progression. This flag is
reserved for S01 preparation advantage; no boss effect exists yet. Empty inventory
and spent materials leave the main route available. Charge menu use is inert and
its description directs players to the cache. Super Potion is immediately usable
recovery, so crafting already has a practical benefit. New dialogue original;
MovingBox/MetalCoat icon/explosion sound are upstream placeholders for S02.
Runtime verified: [D02 111-check evidence](evidence/d02/README.md); integration pending. No new save layout or battle item framework.

## S01 connected route and authored encounters (2026-10-06, runtime verified)

Entrance→Quiet Landing↔Service Room→Supply Gauntlet→Gate Chamber→First Staircase.
All routes allow backtracking. Southwest service ladder leads onward; northwest
returns to the guide. Northeast gauntlet ladder reaches the gate. Inspect the
northeast gate stairs after winning; confirm or cancel; review-room ladder returns.
No live timer. Floor rule: cleared encounters stay cleared across saves.

| Encounter | Prerequisite / role | Persistence and adaptation |
| --- | --- | --- |
| Trial855 | Existing simple melee lesson | Existing trainer flag2135 |
| Guard856 | Durable SPINDA base record; BRACE first turn, then TACKLE; melee partner | Trainer flag2136; original patrol, stock art placeholder |
| Howler857 | WHISMUR uses WEAKEN turn0 and every3 turns, otherwise TACKLE; melee partner | Trainer flag2137; original patrol |
| Warden858 | Trial + both patrols clear; LOUDRED12 alternates WIND UP/SLAM with helper9 | Boss clear0x2F after actual win |
| Prepared warden859 | Same gates plus cache blasted0x2E; levels10/helper8 | Same boss flag, optional advantage; no required item spend |
| Staircase | Boss flag; confirmation; review room | Slice complete0x30, save/reload required |

This is original compressed tutorial fiction, not a claimed Book1 canonical boss
or place. Boss alternates attack-up and physical65-power hit, aiming at Carl while
able, then Donut. BRACE/WEAKEN or faster prepared offense are intended responses,
subject to real playtesting. Existing AI is fallback when the pattern move is
unavailable. No second combat model. Both-defeated recovery remains local/free
for all authored encounter IDs. New trainer portraits/species art, cave maps,
move animations and review NPC remain S02 placeholders, explicitly not final art.

S01 isolated357-assertion acceptance PASS across18 production sessions; both boss
strategies, local defeat/cold retry, stairs/cold completion pass. [Evidence](evidence/s01/README.md).
S01 integration pending; S02 visual replacement remains next.

## S02 original asset provenance (in progress)

Non-protagonist assets: Codex-authored indexed geometry in scripts/content/slice_art.py,
2026-10-06; no external illustrations traced. Protagonist assets now use the
user-approved generated references and native conversion/cleanup documented below.
Files live under graphics/dcc and data/tilesets/secondary/dcc.
Carl has bare torso/feet and heart shorts; Donut is a long-haired cat with a small
collar, no later-book costume/class implied. Enemy silhouettes are original
tutorial adaptations, not claims about canonical Book1 enemies. All seven use
16-color64x64 front/back and two-frame32x32 icons; static duplicate animation
frames retain engine timing. Carl battle-intro repeats one approved back pose in four engine frames.
Donut stands in the landing/review scenes; following movement remains deferred.
New item icons cover wrap/scrap/tag/charge and shared medicine silhouette.
Dungeon metatile art is original; behavior attributes derive from pinned upstream
Cave to preserve movement. Rugs mark rest/review spaces; amber stripes mark boss
lanes; wall lamps and debris add occupancy. No changed warp/collision semantics.

Additional original assets: guide, Mara and Lev stationary overworld sprites;
visible scuttler/guard/howler/warden tokens; title lettering/portal and battle
arena. Existing fixed graphics IDs are reused in the authored maps, without
expanding save/object structures. Human NPCs and enemy tokens are intentionally
stationary; only Carl needs directional walking. All share the original prop
palette to stay within existing palette slots.

Remaining placeholders: upstream copyright/boot sequence, press-start glyphs,
ball send-out effects and summary ball marker, music/sound/attack animations,
menu frame/bag/summary backgrounds and baked labels (e.g. trainer memo/ribbon).
These are inherited assets, not original work. Summary lore still uses engine
nature/ability/type terminology; no class/race story claim. No contest page or
collection action is reachable. Title copyright credit is retained as provenance.
S02 is not accepted until real captures and relevant runtime checks are archived.

S02 visual review fixes: title tile0 transparency regression; removed clipped
redundant summary heading; light Carl anatomy/shading and layered Donut fur;
arena floor now uses stone seams rather than elliptical pads. This remains
simple original prototype art with stationary NPCs and duplicate animation
frames. Do not call it finished/polished merely because provenance is original.


### Approved replacement protagonist art (2026-10-06)

The user rejected the first geometric prototype and approved the improved native
battle appearance, with matching exploration required. Source images, prompts,
hashes and conversion provenance are in docs/art-references (asset-only PR28).
Battle masters are the validated 64×64 candidates; front animation and trainer
intro frames intentionally duplicate static poses. Menu icons derive from native
fronts at 32×32. Each protagonist has its own 15-color opaque palette plus index0
transparency. Enemies keep shared icon slot0; Carl/Donut use slots1/2.

Exploration uses scripts/content/masters indexed text, manually cleaned after
reference normalization. Carl has nine 16×32 frames with consistent head/torso
anchors and alternating contacts; right mirrors left. Donut has three 16×16
standing directions, with back-paw margin restored. No follower is introduced.
Donut's palette tag0x1124 loads into the existing NPC1 slot on dungeon map init;
authored map NPCs use the special slot, so no new hardware palette bank is added.
The palette change and all four movement directions require real runtime review.
Old generators delegate to protagonist_art.py and cannot overwrite replacements.
Battle-only ae32d3f passed182 checks; exploration integration pending its own run.

Runtime caught paletteSlot truncation: the upstream field is four bits, so +16
never selected its legacy patch branch. The fix loads Donut on dungeon palette
initialization and resolves the tag consistently for reloads. Hardware-palette
assertions now cover field, menu return, battle return and cold reload.

### Current presentation and acceptance status — S03

S02 approved replacement art is merged atd8f8ae6; S03 tested50435d1 passes1053
checks/62 sessions with42 actual reviewed captures and380 reviewed walking frames.
Older pending/placeholder entries above are historical milestone notes. The
current five enemies have original S02 first-pass art, now selected for the user's
requested improvement. They are original tutorial adaptation identities, not
claims about canon monsters. No later-book spoilers or new roles are authorised.
See the I01 contract in backlog and issue29 native palette/asset handoff. Current
stock interface/audio/ball-effect/static-animation limitations remain as listed.

### I01 opponent replacement — runtime verified

The five existing original adaptation enemies now use the native package in
art-references/opponent-native-candidates (asset-only PR33). Generated references,
original prompts, deterministic conversion and limited source-detail corrections
are preserved; no third-party image was supplied. This is source-derived art,
not hand-drawn native animation or a claim of book-canon monster identity.

Runtime battle export lifts the unchanged opaque pixels8 rows inside each64×64
canvas to avoid duo HP-panel overlap. Source masters are untouched; no scaling or
recoloring. Guard's former Spinda procedural spots are disabled. Battle palettes
remain independent; five icons/four stationary tokens retain the existing shared
palette. No Grub map token exists. Front/back and animation-pair duplicates remain
explicit; no new rear view, movement, attack animation or mechanics were authored.

Tested81b232a: all5 battle fronts and4 map tokens match every source opaque pixel
in actual RGB555 emulator output; all1053 gameplay assertions pass. Existing
Carl/Donut art, NPCs, map layout/collision and UI palettes are unchanged.
Remaining inherited audio, UI frames/labels, ball effects and static animation
limitations stay listed above. Await human playtest before broader work.

### N01 native environment candidates / first prop selection

PR40 is a partial source handoff:124 added reference files including all91 native
PNG candidates. Its omitted original main reference PNG prevents full source-sheet
reproduction; optional packed diagnostic output is also absent. Do not recreate
or publish either omission. Historical full-kit reproduction is not current-tree
reproduction. Prompts, hashes, accepted native masters and current-tree checks are
preserved in art-references/environment-native-candidates.

The first game export selects rubble, sign, workbench, quest tag, sealed cache and
storage rack. Original generated-reference-derived candidates, static16x16;
shared palette unchanged. No claim of hand-drawn animation or canon object design.
Remaining crates, inactive-state feedback and room architecture await later
increments. Native PNG masters are authoritative for deterministic game export;
compilation/runtime acceptance recorded separately in progress/evidence.
