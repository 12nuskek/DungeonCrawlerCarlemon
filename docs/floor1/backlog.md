Current focused increment (2026-10-08 Brisbane): F1-G01e-NC implemented,
compiled and runtime verified; issue78 / draft PR79, pushed and unmerged.
17sessions/236assertions (5ordinary147;12explicit controlled89), real native
NPC/Journal pages on all5live maps, Save/cold and capacity checks.38controls and
22unchanged texts preserved;21live text labels corrected; legacy/geometry/save/
combat unchanged. [Evidence](../evidence/floor1/g01e/navigation/README.md).
PR77/75 remain draft; three-strategy combat stop and full/finalT/V01 gates unchanged.
Next: reconcile NC review, then independent optional loop/trap/craft/re-entry/cold
checks using existing ordinary inputs. No new strategy, scheduler or writer.

## Preserved SF checkpoint

Current focused increment (2026-10-08 Brisbane): F1-G01e-SF pickup feedback is
implemented, freshly compiled and ordinary-runtime verified; draft PR77 / issue76,
not merged. See [evidence](../evidence/floor1/g01e/feedback/README.md). Baseline and
candidate each2 sessions/72 assertions; immediate/re-entry/cold panel pixels agree,
movement and once-only reward unchanged. Broader PR75 gates remain pending.
Next dependency-ready task: F1-G01e-NC live navigation/Journal copy correction,
preserving archived scripts and state/reward ownership. No combat attempt reset.

# Dependency-ready full-floor backlog

Source/authority: [execution contract](README.md). One implementation writer.
Each row may split into focused PRs; no package is complete from compilation alone.
All changes retain useful assertions, exact build/source identity, actual screenshots
and motion where affected, rollback commit, blocker attempts and next action.

| ID | Dependencies | Scope and acceptance | State |
|---|---|---|---|
| F1-P01 | Delivered baseline | Preserve identities; complete plan; old anchor/flag/engine register; no engine edits | Merged PR54 |
| F1-T01 | P01 | Runtime reproduce/fix tag Journal and spent sign; completed priority, full-inventory pickup and hand-in; immediate/re-entry/cold | Merged PR56;96/1609 runtime assertions |
| F1-A01 | P01 | Explicit full map identity and encounter membership; preserve old/nonmember behavior, recovery/palette/cache | Merged PR60 cee81f8;100/1621 runtime assertions |
| F1-G01 | T01,A01 | D1 64×48 graybox + compact interiors; relocation/version migration; both patrol orders, widths, loop, camera, measured T and recovery | G01a merged PR62 535b080,13/7066; travel rejected. G01b issue63/PR69 third coordinated diagnostic15/8916 passed; Guard14/224,Howler34/544,preboss44/703 within frozen ceilings. G01c audit PR71 merged0cb6674,18/78; G01d issue72 complete five-map diagnostics23/10541 and94pixels verified; G01e draftPR75 implemented/compiled:69state sessions543assertions;3partial live sessions3162. Three Howler-first strategy routes failed (lastHowler won, laterGuard lost); further blind attempts/dependentV01 stopped. Live loop/remaining gameplay/finalT pending; see migration evidence and navigation copy audit |
| F1-V01 | G01, readable art | Native junction/workshop/safe-door proof; Carl gait, staged Donut, Carl/Donut/Warden motion; budgets and clips | Pending |
| F1-C01 | V01 | Useful duo decisions, resource model; uninterrupted prepared/unprepared opening, multiple timings, no health inflation | Pending |
| F1-G02 | C01 | Nine-district graph; both branch orders; D7 optional; both service loops; three refuges;8–12T measured; exact ports/widths/headroom | Pending |
| F1-S01 | G02,C01 | Bounded ledger/content/resources; audited distinct flags, active refuge, D1 versus D9 ending, full legacy migration matrix | Pending |
| F1-D02 | S01,V01 | Sluice native production and matching D1 seam, readable hub and branch exits | Pending |
| F1-D34 | D02 | Foundry/Arcade milestones in either order; meaningful encounters, optional marker quest, return to Commons | Pending |
| F1-D05 | D34 | Commons refuge/recurring consequences; both-milestone gate, D7 access | Pending |
| F1-D06 | D05 | Pumpworks state change; route to D8 and persistent return to D2 | Pending |
| F1-D07 | D05,S01 | Optional Warrens salvage/discovery; D8 far-side loop must not bypass gates | Pending |
| F1-D08 | D06,D07 | Causeway/refuge/preparation; far-side gate opens both ways, persists | Pending |
| F1-D09 | D08 | New final encounter and distinct final descent; fair prepared/unprepared routes, persistent floor completion | Pending |
| F1-P06 | D09 | Whole-floor menus/sound/art/animation consistency, resource and busy-scene headroom review | Pending |
| F1-P07 | P06 | Exact-candidate regression, fresh/migrated route matrix, human playtest evidence honestly separated; private package | Pending |

No later floors, follower, tenth district or other stretch production before the
nine-district core. No filler to satisfy area/time. Human playtime/comprehension
requires actual human observations; automation cannot impersonate that evidence.
If unavailable, report that final evidence item pending while completing technical work.

Historical P01 allowed files: docs, AGENTS and read-only baseline audit script. P01 excludes
engine/art/map/save edits. F1-T01 limits engine edits to the two map scripts and adds
focused runtime routes; UI paging redesign is separate. Every subsequent PR states
its own file/system boundary. Preserve failed traces; max3 different approaches per
blocker, then stop its dependents and take another ready task.
