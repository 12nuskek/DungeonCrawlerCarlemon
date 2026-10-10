# Foundry and Arcade to Commons: refuge handoff

**Authored preparation only; not implemented, compiled or runtime tested.**
Prepared on accepted documentation checkpoint
`9ec85c7f94fc7c388b35fdfcfbb616822a5896ac`. PR114's gameplay/legacy limitations
and six baseline/four candidate execution totals remain unchanged. Screenshots
N/A; future routes below have not been prepared or executed.

Original Carl/Donut adaptation wording by Codex, within the Book 1 opening
ceiling. The districts, shelter and exchanges are invented game geography and
connective fiction, not chapter quotations or verified canonical locations.
Carl and Donut remain the permanent duo; no new NPC, party member, purchase,
catching/storage/breeding or later-floor content is introduced.

## Gameplay purpose and route

After either branch objective, the player should recognise a place to recover,
save and choose when to tackle the unfinished branch. Warm shelter around the
Commons' collapsed fountain contrasts with the cold Foundry and ruined Arcade.
Place the eventual recovery/save cue and exit labels where they are readable
without a dialogue or optional quest. Exact staging, native assets, camera
anchors and clear interaction tiles await graybox and production review.

The [accepted graph](accepted-plan.md#main-route-and-optional-loops) and
[Sluice brief](d2-sluice-orientation-brief.md) govern the handoff:

- Either Foundry (D3) or Arcade (D4) can be completed first from Sluice (D2).
  Each branch has its reviewed connection to Commons (D5).
- After **either** milestone, that branch's route reaches free Commons recovery
  and save access. Completing the other branch is not a refuge prerequisite.
- Commons guidance names the unfinished branch and its reviewed connection.
  Entering or returning through a branch never awards its milestone or bypasses
  its own objective checks. Retreat to Sluice and Quiet Landing stays legal.
- Commons-to-Pumpworks (D6) progression requires **both** branch milestones.
  The closed exit must remain distinct from the freely usable refuge services.
- Optional Warrens (D7), quests, rewards and preparation remain skippable.
  No new D2-to-Commons connection or extra shortcut is authored here. The later
  Pumpworks-to-Sluice service return retains its separate unlock and persistence.

## Symbolic conditions

These are design conditions, not allocated flags, map IDs or save fields.

| Condition | Meaning |
| --- | --- |
| `FOUNDRY_COMPLETE`, `ARCADE_COMPLETE` | Existing proposed branch outcomes, read independently for guidance; this scene writes neither. |
| `COMMONS_ARRIVAL_SEEN` | Proposed optional introduction marker; set only when its exchange completes, never required for recovery, saving or travel. Allocation awaits F1-S01. |
| `ARRIVAL_FROM` | Current arrival context, Foundry or Arcade; not a proposed persistent field and not proof of completing that branch. |
| `SERVICE_RETURN_OPEN` | Read the separately reviewed Pumpworks/Sluice passage state for late-return guidance; this scene does not open it. |

Conceptually, the main onward access condition is
`FOUNDRY_COMPLETE AND ARCADE_COMPLETE`. This gate belongs to reviewed progression,
not to a conversation-complete marker, held item, money, quest or resource count.
Seeing Commons or taking its recovery service does not complete either branch.

Use the actual milestone state before arrival direction when choosing words:
returning through a completed branch must still identify the other unfinished
objective. An unexpected legal visit with neither milestone uses neutral
orientation and the established recovery service. An invalid migrated spawn or
contradictory progression state needs diagnosis under F1-S01; dialogue must not
invent completion or repair it silently.

## First refuge arrival: F1-D5-HANDOFF

Offer one short optional exchange after legal arrival, clear of the movement
path and services. Select the outcome row, then leave ordinary control with the
player. A completed introduction never repeats. If skipped or interrupted, it
stays optional on request after re-entry; current guidance and retreat remain
available throughout. This uses the same handling as the clarified D2 brief.

| Current outcomes | Short original arrival exchange |
| --- | --- |
| Foundry complete, Arcade unfinished | Carl: “Foundry behind us. Warm light ahead.” Donut: “I am choosing the warm light.” |
| Arcade complete, Foundry unfinished | Donut: “For once, a sign leads somewhere useful.” Carl: “Rest here. The Foundry can wait.” |
| Both complete | Carl: “Both routes checked. We can stop here.” Donut: “We can. We will.” |
| Neither complete on a legal visit | Carl: “A place to stop.” Donut: “Then stop, Carl.” |

The service cue remains available without the exchange:

> **CRAWLER COMMONS — REFUGE**
>
> Free recovery. Saving available here.
>
> Take the other branch when you are ready.

The final sentence is shown only while a branch is unfinished. With both
milestones, use “Both routes checked. Pumpworks is the next main route.”
An optional conversation must not become the only way to learn where to recover
or save. These draft lines still need native text-width/page-break review.

## State-aware revisits: F1-D5-ROUTE

Optional route-board inspection supplies the current cue. Same-state repeats
stay short and useful; the arrival introduction and AI interruptions do not
repeat. No scene achievement or reward is proposed.

| Current outcomes | Short original exchange | Board/access agreement |
| --- | --- | --- |
| Foundry only | Donut: “Arcade next?” Carl: “After we recover. We still have that choice.” | Mark Foundry checked, point to the Arcade connection, keep free recovery/save accessible; Pumpworks remains closed. |
| Arcade only | Carl: “The Foundry is still ahead.” Donut: “Then it can wait while we recover.” | Mark Arcade checked, point to the Foundry connection, keep free recovery/save accessible; Pumpworks remains closed. |
| Both complete, service return not yet open | Carl: “Pumpworks is open to us now.” Donut: “After a sensible pause.” | Both branch marks checked; Commons-to-Pumpworks access open; refuge remains freely usable. |
| Both complete, service return open | Carl: “The Sluice passage gives us another way back.” Donut: “Good. Rest is still here.” | Retain both branch marks and refuge cues; identify the existing service return through Pumpworks/Sluice without granting its state or inventing a Commons-to-Sluice shortcut. Later onward guidance follows reviewed Pumpworks progress. |
| Neither complete on a legal visit | Carl: “Foundry or Arcade. Nothing checked yet.” Donut: “We can choose after we rest.” | Neutral branch directions and free refuge services; no false milestone or Pumpworks access. |

With either protagonist incapacitated, use the service/route cue without staging
a healthy reaction or requiring both to speak. Keep recovery reachable and free;
the scene itself does not restore health, status or action uses. Any restoration
is the established recovery interaction. Depletion, spent preparation, skipped
quests, full or empty inventory and skipped optional content change no required
access rule. Saving remains the ordinary manual service outside combat.

## Future routes and checks — not executed

| Route | Required later evidence |
| --- | --- |
| Sluice → Foundry milestone → Commons → recover/manual Save/cold → Arcade milestone → Commons | Commons accessible with Foundry alone; unfinished-Arcade cue correct; free service and ordinary return preserved; both-complete cue and Pumpworks access only after Arcade's actual milestone. |
| Sluice → Arcade milestone → Commons → recover/manual Save/cold → Foundry milestone → Commons | Mirror the preceding order with unfinished-Foundry guidance and no imposed branch preference. |
| Reach Commons after either milestone with depleted uses or one incapacitated protagonist | Service/board reachable without healthy-duo acting, items, currency, quest or introduction completion; no dialogue-triggered heal or forced fight. |
| Skip/interrupt arrival → retreat/re-enter → progress the other branch → inspect board → request introduction later → Save/cold | Introduction stays optional until completed; current-state guidance updates independently; completed introduction never repeats or changes access. |
| Inspect Pumpworks exit with exactly one branch milestone, then with both | Visible gate, text, Journal and actual access agree; healing/saving remain available in both states; inspection grants nothing. |
| Leave toward the unfinished branch through its Commons connection, retreat before its objective, return through either cleared route | Milestones unchanged by travel, remaining objective still named, services usable, no wrong-side objective bypass or mandatory rematch. |
| Skip optional Warrens, quests, caches and preparation; revisit with full/empty inventory | Either branch order and legal onward/refuge route remain available without consumption, reward pickup or optional completion. |
| Return after Pumpworks opens its Sluice service passage; use both directions and Save/cold | Late-return cue agrees with persistent actual passage state, both branch marks retained, no new link or shortcut unlock from the conversation. |
| Both branch approaches, refuge-service approach and onward exit in the eventual native camera | Recognisable shelter, readable short pages, clear reviewed widths and interaction tiles, no Carl/Donut staging obstruction. |

## Dependencies and next ready work

The current ledger had Sluice preparation and existing D1 scenes, but no authored
Foundry/Arcade-to-Commons handoff. This entry adds the refuge arrival/revisit beat;
it does not replace a branch objective or change any historical scene.

F1-C01 resource/combat work, F1-G02 graph/ports/widths/camera validation and F1-S01
audited state/refuge/migration design still precede district production. Encounter
counts, rewards, numeric flags, save fields, coordinates, engine binding and
native staging remain provisional. These conversations neither establish a
completed district nor close any whole-floor acceptance gate.

Missing ordinary Save and complete original runtime reference inputs still block
gameplay validation. Original legacy inputs remain unavailable; preparation is
not a substitute. The private failed-transfer diagnosis is closed at unknown
cause; this task makes no recovery attempt. All prior failures/controllers and
accepted offline evidence retain their separate status.

Next genuinely independent work, after parent review: a docs-only Pumpworks
drainage/service-return scene brief. It can author the environmental consequence
and both-way return cue using symbolic states while leaving encounter/resource
budgets, native geometry and persistence allocation to their dependencies.
