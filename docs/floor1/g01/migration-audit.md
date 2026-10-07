# F1-G01c identity and saved-state audit

Issue70; parent issue63. Base `ef5c012aba10b61cbcdbbc3313d7e25c5f448473`,
2026-10-07, Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`.
This increment changes documentation and read-only host tools. Production engine,
maps, art, save ABI, battles and resources remain at the accepted C5 behavior.
Live migration/adoption is the next separately compiled and runtime-tested change.

## Ownership evidence and proposed allocations

Run `python scripts/floor1/audit-migration-state.py`. The report resolves every
FLAG_/VAR_ macro with the committed headers and the host C preprocessor, then
retains all matching symbols, raw numeric literals, typed API/opcode matches,
JSON state fields and direct saved-array references. See
[source audit](../../evidence/floor1/g01c/source-audit.json).

| Candidate | Numeric identity | Save storage | Finding |
|---|---|---|---|
| Layout version | VAR_UNUSED_0x404E = 16462 | SaveBlock1 vars[78], byte0x1438 | Only header declaration; no other alias, raw literal or typed/JSON use |
| Far-side D1 loop | FLAG_UNUSED_0x031 =49 | SaveBlock1 flags[6], bit1, byte0x1276 | Only flag alias declaration; no typed raw/JSON use; all351 raw occurrences reviewed separately |

These are **proposed**, not engine allocations in this PR. Raw49/0x31 is also a
move/species/ability/trainer identifier, opcode, audio value, level, coordinate,
palette/text offset and battle threshold; equality to49 does not establish flag
ownership. All351 tracked literal lines are retained, including upstream tools,
sound and constants. None of the nondeclaration lines is a persistent flag49
assignment or state table entry.18 direct SaveBlock1 flags/vars accesses cover
new-game initialization, temp/daily clears, generic accessors, contest graphics
and named fanclub vars; none independently owns these candidates. Generic APIs,
script operands, object flag IDs and dynamically passed special vars remain
indirect access paths: this audit is a source review, not arbitrary C data-flow
proof. Rerun against the implementation base before adopting any allocation.

Flags0..31 are temporary; daily flags2336..2399 clear on daily rollover.49 is
outside both. Vars0x4000..0x400F clear on map load;0x404E is outside this range
and inside256 persistent vars0x4000..0x40FF. InitEventData/new-game clears both
arrays: stamp version **after** initialization, never before. The old crawler
flags32..48 and old trainer flags2135..2139 retain their identities and values.
In particular, UNUSED labels0x23..0x30 already alias owned crawler flags.

`MAX_TRAINERS_COUNT=864`; trainer flags0x500..0x85F; SYSTEM_FLAGS=0x860;
FLAGS_COUNT=2400,300 saved bytes. Current trainer table has860 entries; only
IDs860..863 fit the remaining reserved boundary. Raising MAX_TRAINERS_COUNT
shifts every SYSTEM_FLAGS-derived flag and changes the save ABI. Do not do that
for the18–24 encounter plan. Review encounter instances/reuse or genuinely unused
stock definitions separately. Trainer901 yields0x885, already system space;
never instantiate it. No trainer allocation/balance change belongs here.

## Full identities and legacy content

Current35 groups occupy0..34; group34 holds the six delivered maps. Current447
layouts include legacy IDs442..447. Keep these entries/order and their source
register; append a distinct production group35 and layouts448 onward only in the
live adoption change. The immutable disposable geometry diagnostics also use
35/0..2 in isolated test ROMs; those saves were never delivered and are **not**
supported production legacy inputs. A production file must never be confused
with one of those fixture saves just because its numeric ID matches.

Proposed new production names/IDs (not yet generated):

| New map | Full ID | Proposed appended layout | Role |
|---|---|---|---|
| DCC_F1D1Field |35/0|448|Accepted64×48 third-design field, opening and patrols |
| DCC_F1D1Quiet |35/1|449|Accepted16×14 guide/trial/recovery interior |
| DCC_F1D1Workshop |35/2|450|Mara/Lev/crafting/preparation; width review still pending |
| DCC_F1D1Warden |35/3|451|Accepted16×14 arena, actual encounter/staircase pending |
| DCC_F1D1Checkpoint |35/4|452|Old Exit review beat; width review still pending |

Explicit full-ID membership must include each supported production map. No
group-only/number-only comparisons. Preserve old full-ID members while their
legacy headers are retained; do not copy geometry fixture membership assumptions.
Later districts append explicit entries without moving any old layout index.

The source report records every old object with localID, script, graphics,
coordinates, movement, trainer type and flag, every warp and coord/bg event.
This is the semantic relocation plan; exact final coordinates/localIDs for the
two remaining interiors and additional field content must be reviewed before
engine migration is committed:

| Old map/layout | Position destination | Preserved content/persistence |
|---|---|---|
|34/0 Entrance442|Field arrival8,38; note/supply approach anchors selected in live contract|Note/reader achievement, two rubble objects, supply box; flags32,33,36,38; no reward replay |
|34/1 Vestibule443|Quiet arrival4,3, guide approach4,5; trial approach10,7 as appropriate|Local IDs1 wrap,2 trial,3 guide,4 rack,5 Donut remain in that order; flags34,35,37,39/trainer855 |
|34/2 Service444|Workshop arrival/nearest legal interaction anchor (pending widths)|Mara1,Lev2,warning3,tag4,workbench5,cache6 relocate by script identity; flags40..46 unchanged; tag/wire/secret belong on field branch per third design |
|34/3 Corridor445|Field Guard37,31 or Howler51,27 according to old encounter side|Guard1/Howler2/rules3 become stable distinct field local IDs; trainer856/857 unchanged; no moving patrols |
|34/4 Boss446|Warden arrival4,3 or encounter approach8,7 according to old position|Encounter localID1 and flags46/47/trainer858/859; stair BG event moves to12,10; optional cache advantage retained |
|34/5 Exit447|Checkpoint legal arrival, pending width review|Guide review1/Donut2; old flag48 means opening checkpoint only, never D9 floor completion |

Field combines three old maps, so their duplicate local IDs **cannot** remain
duplicates within one header. Assign a semantic object identity table, preserving
Quiet and Warden local order where possible; update any explicit script operands
and all presentation tables. Old scripts currently use lockall/releaseall and
persistent flags, rather than explicit numeric object movement/removal. Graphics
identity alone cannot distinguish two NPCs/objects of a shared role.

Old Service trap coord event8,6 uses VAR_TEMP_0=0; optional secret BG sign12,2;
old Boss stairs BG sign12,4. Regenerate these against the field/arena anchors.
Move all presentation metatile entries and ON_LOAD/ON_RESUME scripts deliberately;
do not retain old coordinates in DccRestoreMapPresentation or change collision
through resolved-state art. Keep existing reward/craft/quest/gate assertions.

## Migration policy and load ordering

Version0 means delivered six-room production format. Version1 will mean the
reviewed live D1 map/position schema. Fresh version1 saves must start at Field8,38
with a closed loop. Version0 migration sets1 only after all spatial changes are
prepared; it sets no achievements/rewards/quest/boss flags and consumes no items.
Existing flag48 remains intact. The new loop is initially closed, including on
completed legacy files: only reaching the reviewed far-side interaction opens it.
No guessing from boss completion, copied art or fixture open state.

Version1 repeats do not reset positions, loop or outcomes. A layout-version stamp
is independent of the ROM/title save checksum and the later final-floor completion
flag. Known invalid legacy coordinates use declared semantic legal fallback
anchors, excluding collision, object occupancy, accidental warp and locked side.
Any nearest-cell mapping must be deterministic and tested against all old cells,
not based on bounding-box validity alone. Warp returns get explicit WARP_ID_NONE
and valid coordinates where old warp indices no longer mean the same destination.
Leave stock/nonmember records and the -1 dummy sentinel unchanged. A current
unsupported identity must never reach unbounded gMapGroups/GetMapLayout lookup.

An unknown future version must **reject Continue before migration/header lookup**,
show a readable unsupported-save message and return to the main menu without
writing a save. It must not silently downgrade or relocate an unknown schema.
This policy requires a dedicated main-menu/callback path and runtime fixture;
it is a proposed implementation requirement, not a working protection today.
Stock noncrawler Continue must keep its existing path/state.

| Saved/loaded field | Required treatment |
|---|---|
|pos at0x00; location0x04|Select full ID and semantic legal player cell together; location x/y agrees, no stale warp index |
|continueGameWarp0x0C|Remap even if use-continue-warp bit is unset; if set, it must load a valid remapped target |
|dynamicWarp0x14|Map old full ID/warp index/coords independently; future return must not enter old rooms |
|lastHealLocation0x1C|Remap owned crawler destinations; leave stock existing values untouched; crawler local defeat retains accessible zero-walk retry |
|escapeWarp0x24|Remap owned crawler records even though escape is disabled; preserve dummy/stock values |
|mapLayoutId0x32|Replace with selected new header's exact ID **before GetMapLayout**, independent of old saved value |
|mapView0x34,256u16|Invalidate/reconstruct from new source+event flags; never copy old cached metatiles |
|objectEvents0xA30,16×36|Saved and live arrays exist separately; rebuild player and NPCs, previous/current/initial coords, map IDs, local IDs, movement/facing/elevation; no stale live array |
|objectEventTemplates0xC70,64×24|Clear/repopulate new header templates; scripts/gfx/flags/order/coords all new identities; do not only patch script pointers |
|flags0x1270;vars0x139C|Preserve all existing outcome state; only version and audited new loop allocation change |
|party/inventory/money/equipment|Byte/value preservation checks; no heal/resource/XP adjustment during migration |
|SaveBlock2 continue flags/player gender|Preserve; support alternate continue-warp path and valid facing reconstruction |

Actual chain: LoadGameSave copies party+saved objects to live RAM **before**
CB2_ContinueSavedGame. That callback currently calls LoadSaveblockMapHeader at1740;
it indexes group/number directly then GetMapLayout indexes saved layout ID. The
new version check and identity/layout fix must run before that call. Current
LoadSaveblockObjEventScripts refreshes only scripts/gfx by template index and
matching active localID; it does not relocate. InitMapFromSavedGame reconstructs
the map+ON_LOAD presentation, and the crawler cache guard already clears mapView.
CB2_ReturnToField uses SpawnObjectEventsOnReturnToField, which only respawns
**existing active objects**. Clearing arrays and using that normal return path
would remove the player. A successful migration must instead take the local map
load path which calls InitObjectEventsLocal: ResetObjectEvents → InitPlayerAvatar
from legal saved position → TrySpawnObjectEvents from current header. Preserve a
valid initial facing and reset transition state. Explicitly repopulate saved
templates before spawning. Check camera focus, palette, collision, scripts and
save-object sync on the first frame and after a manual save/cold restart.

Transient sWarpDestination/gLastUsedWarp/dive/hole/camera/avatar state is not a
sixth persistent WarpData: rebuild/reset via the normal local load path. Check
them on first transition/battle/menu return. The existing Continue branch using
continueGameWarp must not overwrite the selected migration destination or leave
pre-migration active objects. Test that branch explicitly, not only ordinary files.

## Acceptance before live adoption

Audit cold loads only establish existing state/fixtures, **not** migration.
The following implementation must compile from a fresh committed snapshot and
run all required migrated ordinary saves (I01 motion/craft/quest/playtest,
N02 corner and current guide/patrol/prepared/boss/checkpoint states), plus controlled
invalid/stale-layout, dummy/owned/stock warp, continue-warp, unknown-version and
all-old-cell boundaries. Preserve original hashes. For every old map, check first
legal player/NPC/camera state, meaningful normal interaction, transition, manual
save and a second cold load with version1/idempotent outcomes. Test battle win/
one-down/both-down/zero-walk retry and repeat awards/quest/craft/ending after reload.
No API-only boundary probe substitutes for migrated controller routes.

Then adopt live geometry/content only after migration acceptance: immutable third
anchors and travel ceilings (28/448 Guard,38/608 Howler,46/735 preboss), widths,
persistent far-side loop in both directions, both patrol orders, all old beats,
Workshop/Checkpoint interiors and final unique reachable T measured once.
15/8916 accepted diagnostic assertions remain available; they do not close live
G01 or establish human pacing. No new material geometry attempt is being started.
