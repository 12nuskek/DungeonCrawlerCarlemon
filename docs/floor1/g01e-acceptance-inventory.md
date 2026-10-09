# G01e acceptance inventory and V01 entry — 9 October 2026

[Draft PR #108](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/108) / existing [issue #106](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/106), stacked on unchanged PR107; open/draft/unmerged. Inventory source `ba2237c8f2a9b5e338528000293d1332ff26f7de`.

Parent review accepts PR107's bounded prepared pair: PR105 first-route270 plus
PR107 cold132 =402. The failed cold25 and all older failures remain separate.
This inventory changes no game data or controller policy and runs no emulator.
Base1663abb05000374b03d0c0db3c78a974c87b3852; current game5084a1814904f1a43fd999fddf770b221bb53653,
ROM23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167.
Exact reconciliation/counts: [inventory evidence](../evidence/floor1/g01e/acceptance-inventory/README.md).

## Acceptance matrix

“Retained” means existing exact source/runtime evidence, not a new execution or
transfer to reconstructed inputs. Source comparison supports reuse for unchanged
geometry/content; runtime claims retain their original build/input identities.

| G01e requirement | Exact existing evidence | Actual remaining delta |
| --- | --- | --- |
| Reproducible current build, pinned Emerald/GBA, permanent duo, membership/no collection | [5084 build identity](../evidence/floor1/g01e/warden-fairness/build-identity.json); original [A01](../evidence/floor1/a01/README.md)100sessions/1621assertions; later diffs add live identities/migration and encounter-local Warden only, retain party/save/collection rules | No new system audit or build in this inventory; V01 must build its own committed candidate |
| Six-map ordinary legacy migration, I01/corner, flag/resource preservation, second Save/cold; invalid schema/ID/warp handling | [PR75](../evidence/floor1/g01e/README.md): 48ordinary/471,21controlled/72 at99243073/6c447; host8694+5+15; loader/identity/migration unchanged at5084 | Original16 legacy inputs are missing. Retain historical verification and unavailable reproducibility limitation; fresh inputs cannot close original-input gate |
| Fresh trial, tutorial/supply once, guide recovery and manual Save | PR75 fresh-trial partial; [PR91 recovery](../evidence/floor1/g01e/recovery/README.md): new52+44 passing ordinary assertions atc643/b025, private pending Savec11c…c67f | Closed bounded reconstruction; no need to replay fresh start |
| Both patrol orders, no forced optional preparation, meaningful retreat, persistence | PR75 Guard-first43 + cold3073, Guard14steps/224activeframes, Howler34/544; [CP72e](../evidence/floor1/g01e/current-patrol/README.md)81 atc643/b025; [PR93](../evidence/floor1/g01e/new-save-recovery/README.md)199 reconstructed Howler→Guard atc643/b025 | One current5084 Guard-first order/travel/Save/cold check, defined below. No new strategy diagnosis |
| Pre-boss recovery travel and local defeat retry | [G01d](../evidence/floor1/g01d/README.md) Howler→guide→Warden44steps/703frames versus46/735 ceiling; unchanged anchors/geometry; PR75 patrol losses recover locally; [PR95](../evidence/floor1/g01e/warden-first-clear/README.md) records real Warden defeat | Add exact current preboss-out/back measurement to the same Guard-first check without starting Warden. Preserve local zero-walk retry/source behavior; no new deliberate loss |
| Live navigation, Journal objective priorities, opening checkpoint wording | [PR79](../evidence/floor1/g01e/navigation/README.md)c643/b025,17candidate sessions/236assertions,38controlblocks/22texts retained,65536host identities; locked/cleared and full-capacity controlled branches explicit | Closed; 5084 changes Warden advice only, covered by its battle evidence. Human comprehension is later C01/playtest |
| Quest skipped/declined/accepted/completed, capacity-safe hand-in and once-only rewards | PR79 ordinary quest/repeat/Save/cold + labelled controlled capacity98SCRAP/tag retention; [T01](../evidence/floor1/t01/README.md) archived pickup/hand-in boundaries | Closed scoped matrix, identities retained; no rerun or new capacity fixture |
| Optional loop wrong side/open/two-way/persistence, wire warning/spent/recovery, recipe/cache cancel/use/repeat/missing materials | [PR81](../evidence/floor1/g01e/optional/README.md)c643/b025:8sessions/15701assertions,5full Field comparisons; [PR77 feedback](../evidence/floor1/g01e/feedback/README.md)72candidate, actual panel pixels | Closed; 5084 has no geometry, script, reward, item or presentation diff here |
| All five loaded maps, bends/doors/approaches, widths/occupancy/camera, repeat/re-entry/cold | G01d23sessions/10541assertions/94pixels; PR75 field3072 words; [PR83](../evidence/floor1/g01e/staircase/README.md)7sessions/3750,15interior buffers; PR81/85 full Field/Warden checks | Unchanged geometry evidence retained; final source-defined T frozen below. V01 rechecks only affected native views/allocation |
| Warden prerequisite/refusal, prepared/unprepared victory, two responses, award-once, actual stairsNO/YES, checkpoint/Save/cold | [PR85 sealed](../evidence/floor1/g01e/sealed/README.md)11382; [PR99](../evidence/floor1/g01e/warden-fairness/README.md)offensive204+132 and fortify204+132 at5084/23c77; [PR105](../evidence/floor1/g01e/prepared-persistence/README.md)270 + [PR107](../evidence/floor1/g01e/prepared-cold-phase/README.md)132 | Closed bounded gameplay/persistence cases. No repeated boss/stairs/optional runs; no friendship/resource diagnosis restart |
| Walkable scale and current technical budgets | [Source-only count/budget](../evidence/floor1/g01e/acceptance-inventory/geometry-budget.json), existing G01d scene peaks | T and linked budgets frozen; pilot-specific dynamic OBJ/BG/palette/heap/stack/VRAM peaks remain V01 checks |
| Full uninterrupted prepared/unprepared opening, multiple timing trajectories, human pacing/readability; D2 continuation and full-floor ending | Accepted plan Package2/C01 and later G02/S01/D02–D09/P07 | Later package requirements, not additional G01e executions or prerequisites to staged V01 pilot; no current full-route/full-floor claim |

## Frozen spatial and memory baseline

**Final live T=1449**: Field982 + Quiet115 + Workshop116 + Warden118 +
Checkpoint118. Gate-closed total1440; opening the nine-cell loop adds9. Match
provisional G01d open1449 exactly (delta0); no rebase. Full-floor band8–12T is
**11592–17388**, working10T14490 including D1/interiors. Subsequent geometry or
width changes must update both T and floor comparison explicitly.

Count actual live map words (collision bits10–11 zero, elevation3), source-defined
presentation in legal open state, fixed actor/prop occupancy excluded once, flood
from each legal arrival. Player never subtracts its moving cell. All actors remain
present/nonmoving (flag0); cleared visual markers still occupy the same cells.
Optional trap/tag/panel remain traversable; blocked stairs do not count. Interiors
count once; no borders/duplicate edge buffers. All reachable cells connect and
every actor has a reachable interaction neighbor. Existing runtime confirms both
loop states and loaded words; this inventory adds no runtime.

All25 authored probes survive actual occupancy: main5–7, side4, chosen east-pillar
junction9, interior5–7. One-cell ladder/door thresholds remain brief declared warp
cells with broad approaches, not corridor exceptions. Preserve exact probes and
G01d native walkthroughs; a source cross-section is not a new camera/human test.

Current approved ELF `cafc512d915d01ff1b598b1a7050261f5990bc50fc0faed533b0ec6d7309336b`
re-read unchanged: EWRAM249704/262144 (12440static remaining), IWRAM30892/32768
(1876remaining), SaveBlock1=15752/15872, SaveBlock2=3884/3968. ROM file16MiB;
existing linked allocation is not spare runtime heap/stack or peak VRAM proof.
Field buffer79×62=4898cells/9796bytes versus10240cell ceiling; each interior
31×28=868/1736. Each map has no scrolling connection; doors are warp transitions.
Current tileset source General512 + Dcc192 8×8 tiles (primary512/secondary512
allocation); secondary320 slots are source capacity, not promised free VRAM or
palette banks. Existing13 BG palette budget/16objects/64sprites unchanged.

G01d observera2b24f6/a2a42cd on diagnostic824069ff/e0745ee6 observed Field9/13
objects/sprites closed,8/12open; Quiet6/10, Workshop5/9, Warden2/6, Checkpoint3/7.
These are diagnostic measured peaks, never relabelled current5084 runtime peaks.
Actual live declared Field14objects+player=15/16; compact maps6/5/2/3 including
player. Reuse existing actor slots for staging, measure affected V01 scenes before
adding allocations. Existing 112KiB heap reservation is within EWRAM, not unused
memory; no additional broad feasibility run is needed for unchanged geometry.

## Smallest current Guard-first check (plan only; no execution authority here)

Retained **ordinary** pending Save
`c11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f`
exists locally at recovery/runtime-menu-repair/seed.sav and was retained privately
by PR91. It is reconstructed input: Field37,31, trial clear, both patrols/boss/
preparation unset, levels9/9, healthy, PP8/40/2/40, Potion1/SCRAP2. Never call it
an original legacy save. Review/freeze complete native identity before any route.

One prespecified Guard→guide→Howler→guide travel/repeat/manual Save route plus
dependent cold; reuse the original recorded Guard-first offensive policy, no
optional quest/cache or Warden. Freeze actual controls/cadence and whole-battle
bound before execution; use readiness-aware input, unchanged asserts, no timing/
RNG search, resources injection, extra walking or retry. Preserve trial gating,
flag2136 before2137, once-only XP/money, healthy recovery, restored PP, unchanged
optional/prep/boss/checkpoint flags, legal positions and exact native persistence.
Measure both named Guard legs ≤28steps/448activeframes total, both Howler legs
≤38/608, and Howler→guide→Warden *approach only* ≤46/735. Require strict exact
name/both-leg gate; don't infer frames as16×steps or from total route time. Old
accepted measurements were14/224,34/544,44/703. Stop/diagnose first divergence;
no further execution. No fresh-start, Warden, stairs, optional or intentional loss
replay. This closes a current order/travel delta, not C01 uninterrupted routes.

## Safe integration and direct V01 dependencies

All17 existing PRs75..107odd are open/draft/unmerged. Mainb694da1 and61 remote
heads unchanged at inventory start; [exact stack](../evidence/floor1/g01e/acceptance-inventory/reconciliation.json).
CP72e has no own PR and is PR91's exact base. No integration occurs here.

1. Parent review this inventory and scope the single current Guard-first check.
   Keep unavailable original legacy inputs as an explicit integration limitation
   requiring scoped parent acceptance; never silently waive or reconstruct them.
2. After the narrow check passes and parent authorises integration, merge the
   reviewed stack in order75→77→79→81→83→85→87→89→91→93→95→97→99→101→103→105→107
   →inventory. Retarget each next PR to main only after its predecessor integrates,
   inspect fresh base/diff, honor checks/protections, use merge commits preserving
   tested SHAs; no squash/rebase/force/delete/old-branch update. PR91's retargeted
   diff must explicitly include the CP bridge89headf817→72e as well as recovery;
   verify72e ancestor of its merge and final main. No duplicate CP PR is needed.
   Preserve historical failure records/unpublished denied ancestry. Reconcile the
   resulting engine tree to5084 before future V01 build; no broad acceptance from
   merely merging the stack. CI query returned no PR-triggered first-page runs;
   no checked-in workflows at current head/main, not a CI-pass/protection claim.
3. Start staged **V01 pilot**, holding this geometry/anchors/widths fixed: native
   junction, workshop/optional cue and safe doorway/Quiet contrast; reuse existing
   environment91native PNGs/architecture and staged full-floor material references.
   Use authoritative nine16×32 Carl masters (mirrored right), three16×16 Donut
   directions and staged attention pose for a short native reaction. Reuse staged
   Carl STRIKE/BRACE, Donut SPARK/WEAKEN and five Warden keyposes/lift8 variants;
   bind warning hold to actual WIND UP and SLAM contact/recovery to actual action,
   not idle playback or reaction-time input. Compile one committed pilot, measure
   changed scene/battle allocation, compare equivalent native states and record
   normal-speed direction/reaction/battle clips before broader rollout.

Genuine remaining art work is native16×16 Donut reaction cleanup and action-bound
pose/tileset/export integration, not another reference-generation batch. Missing
Donut corrected source prevents complete regeneration, **not** reuse of verified
native WEAKEN PNGs; missing environment prop source/optional4bpp likewise does
not block existing native PNG reuse. Carl gait masters already exist; do not
import the flawed right-facing reference into a left slot or invent a follower.
Generated district stitch is concept only and not required for this pilot.

Current staged checks pass: battle250native +180package, full-floor231,
environment123checksums/91PNGidentities/721static. No game compilation/runtime/
visual improvement was performed here. Old legacy saves/raw deleted-environment
logs/patrol-complete input were not recovered; denied raw datasets/keys are not
uploaded. C01 uninterrupted/timing/human pacing and nine-district8–12T remain
their own later gates. This list ends at the V01 pilot, not another diagnostic queue.
