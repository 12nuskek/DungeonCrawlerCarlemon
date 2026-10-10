# Pumpworks: drainage consequence and service return

**Authored preparation only; not implemented, compiled or runtime tested.**
Prepared on accepted documentation checkpoint
`2e4d0ba161b1e28406202d33afcd66ce8afd488c`. PR114's gameplay/legacy limitations
and six baseline/four candidate execution totals remain unchanged. Screenshots
N/A; the future routes below have not been prepared or executed.

Original Carl/Donut adaptation wording by Codex, within the Book 1 opening
ceiling. Pumpworks and these exchanges are invented game geography and connective
fiction, not quotations or verified canonical locations. The permanent duo and
authorized nine-district Floor 1 scope remain intact; no new NPC, party member,
purchase, catching/storage/breeding or later-floor content is introduced.

## Purpose and accepted connections

Make the drainage consequence readable through the teal pipes and changed cistern,
then identify the onward route and a useful way back. Exact machinery, interaction
steps, costs, animation, geometry and native staging remain pending. This brief
authors the response to reviewed objective success, not how to achieve it.

The [accepted graph](accepted-plan.md#main-route-and-optional-loops),
[Commons handoff](branches-to-commons-scene-brief.md) and
[Sluice orientation](d2-sluice-orientation-brief.md) retain these rules:

- Either Foundry (D3) or Arcade (D4) can come first. Commons (D5) supplies free
  recovery/save after either milestone; Commons-to-Pumpworks (D6) requires both.
- Actual Pumpworks drainage completion opens the path to Broken Causeway (D8)
  and the persistent two-way Pumpworks ↔ Sluice (D2) service passage.
- Retreat through the reviewed D6 ↔ D5 connection remains available before and
  after drainage. The service passage adds a return choice without replacing it.
- Warrens (D7), quests, caches and preparation are optional. Its far gate opens
  only from D8; this scene does not open that separate D8 ↔ D7 ↔ D5 loop.
- D9's challenge, descent and full Floor 1 completion remain separate. Reaching
  Causeway, draining the cistern or inspecting a passage completes none of them.

Show the changed local cistern and the service passage's availability without
implying that Sluice's great broken wheel turns or is repaired. No floor-wide
water change, new wheel objective or extra connection is proposed.

## Symbolic conditions and readiness

These conditions are not allocated flags, map IDs or save fields.

| Condition | Meaning |
| --- | --- |
| `FOUNDRY_COMPLETE`, `ARCADE_COMPLETE` | Both required for legal main-route access to Pumpworks; the scene reads them and awards neither. |
| `PUMPWORKS_DRAINAGE_COMPLETE` | Proposed actual objective outcome, established by reviewed machinery/objective logic, never by talking, arrival or inspection. |
| `SERVICE_RETURN_OPEN` | Separately reviewed persistent passage state, consistent with successful drainage; read for guidance, never granted by this scene. |
| `DRAINAGE_PRESENTATION_SEEN` | Proposed optional exchange marker, set only when the exchange completes; allocation awaits F1-S01 and it gates no route or service. |
| `SCENE_READY` | Conceptual presentation readiness: ordinary field control, no active machinery interaction, safe staging and both protagonists able to speak. Not a proposed persistent field or a recovery/travel requirement. |

Onward access follows the reviewed drainage outcome; service access follows its
reviewed persistent state. F1-S01 and production must specify their consistent
commit/persistence handling. Text never manufactures either state or attempts a
partial repair. Contradictory milestones, Journal, cistern appearance or actual
access require diagnosis, including on migrated saves.

## Before drainage: F1-D6-DRAINAGE-ORIENT

Optional inspection gives a short current-state cue without starting machinery:

> **PUMPWORKS — DRAINAGE INCOMPLETE**
>
> The Causeway path and Sluice service passage are not open yet.
>
> Commons remains available for free recovery and saving.

If ready, an optional exchange supplies character voice:

Carl: “A path under all that water.”
Donut: “Find the drain, Carl. I am not swimming.”

Repeats use the concise cue; no recurring AI interruption, reward, objective
completion or resource deduction is attached to the conversation. Final text
width/page breaks and the actual objective directions await native review and
the selected machinery design.

## After real completion: F1-D6-DRAINAGE-RETURN

After reviewed objective success has committed, offer the optional exchange when
ready and clear of the passage approaches:

Carl: “The lower path is clear. Causeway next.”
Donut: “And that passage goes back to Sluice. Keep it.”

The persistent route cue remains independently inspectable:

> **PUMPWORKS — DRAINAGE COMPLETE**
>
> Causeway: onward route.
>
> Sluice service passage: open in both directions.
>
> Commons: free recovery and saving on the return route.

The exchange never starts the objective, unlocks a gate, pays a cost or grants a
reward. Completing it marks only the optional presentation. Completed exchanges
never replay on re-entry or cold load. If skipped, interrupted or not ready,
leave the marker unset and offer it on request later, using current-state cues
throughout. Do not auto-start it on return or block travel, recovery or saving.

An interruption before actual objective completion leaves its progression
unearned. An interruption after objective success cannot undo that success or
make access depend on finishing dialogue. Production must preserve the reviewed
objective transaction without rerunning machinery, charging again or duplicating
rewards when a player later requests the exchange. Objective/resource handling
and interrupted-save safety belong to F1-C01/S01 and engine review.

## Revisit and recovery behavior

| Situation | Presentation and guidance |
| --- | --- |
| Drainage unfinished | Incomplete cue; Commons retreat available; neither closed route opens through inspection. |
| Drainage complete, exchange unseen | Complete cue and real exits usable; exchange optional on request when ready. |
| Drainage complete, exchange seen | Short complete cue only; no repeated reaction, objective, reward or charge. |
| Return from Sluice or after later Causeway progress | Current local drainage/service cue; both-way passage retained; do not present drainage as a new objective or D9 as completed. |
| Either protagonist incapacitated, or interaction otherwise not ready | Board/route cue without healthy-duo acting; access and retreat retain their real state. |

Depleted uses, empty/full inventory, spent preparation or skipped optional content
must not gate basic recovery or require a consumable/payment to reach Commons.
The scene itself does not heal, revive or refill actions. Direct the player to
the established free Commons recovery and ordinary manual Save outside combat;
do not force a fight or a conversation first. Before drainage, do not recommend
the closed Causeway path as a refuge. After legal Causeway access, its planned
refuge remains a separate reviewed service, not a heal supplied by this scene.

## Future routes and checks — not executed

| Route or condition | Required later evidence |
| --- | --- |
| Sluice → Foundry → Commons → Arcade → Commons → Pumpworks; then reverse the branch order | Free Commons recovery/save after the first actual milestone; Pumpworks only after both; identical drainage prerequisites in either order. |
| Exactly one branch milestone; inspect the Commons Pumpworks exit | Gate/text/Journal agree; refuge usable; no milestone awarded by travel or conversation. |
| Both milestones → Pumpworks with depleted uses or an incapacitated protagonist → Commons recovery/manual Save/cold → return | Ordinary retreat and free services reachable without healthy-duo acting, paid/consumable recovery or forced combat. |
| Skip Warrens, optional quests, caches and preparation → complete reviewed drainage → Causeway | Main route remains legal; no optional pickup or conversation-complete marker required. Machinery/resource budget itself still needs F1-C01 validation. |
| Interrupt before objective success; separately interrupt after its reviewed commit but before/during the optional exchange | Actual outcome retained correctly; no dialogue unlock, repeated cost/objective/reward or partial-state repair; unseen exchange remains optional on request. |
| Complete or skip exchange → leave/re-enter → manual Save/cold → inspect/request | Cistern, Journal and exits match real drainage state; completed exchange never replays, skipped one does not auto-start or block access. |
| Approach service passage from D2 before unlock; after drainage traverse D6 → D2 → D6 and Save/cold | Closed on the early approach; later persistent and usable both ways; Sluice wheel remains broken; no branch milestone bypass or mandatory rematch. |
| Reach D8 → optionally open Warrens far gate from D8 → return via D7/Commons; separately continue toward D9 | Separate optional far-gate rule respected; drainage scene grants no D9 victory, descent or full-floor completion. |
| Both passage directions and cistern/onward/retreat approaches in the eventual native camera | Readable local consequence, clear labels/interaction tiles and reviewed path widths; Carl/Donut staging obstructs no route. |

## Dependencies and next ready work

This is the first dedicated Pumpworks drainage/service-return scene brief in the
ledger. F1-C01 combat/resource work, F1-G02 graph/ports/widths/camera validation and
F1-S01 audited state/refuge/migration design remain production dependencies.
Machinery implementation, costs, encounter/reward budgets, numeric flags, save
fields, coordinates, native assets and runtime/persistence proof remain pending.
This preparation closes no district, visual-rollout or whole-floor acceptance gate.

Missing ordinary Save and complete original runtime reference inputs still block
gameplay validation. Original legacy inputs remain unavailable; fresh inputs or
authored scenes cannot substitute for them. The failed private-transfer diagnosis
remains closed at unknown cause; this increment makes no recovery attempt. All
historical failures/controllers, offline evidence and six baseline/four candidate
totals retain their status.

Next independent preparation after parent review: one docs-only Causeway refuge
and final-approach orientation brief. It can explain free recovery, the optional
Warrens return and the separate D9 challenge without allocating states, prescribing
encounters or claiming a playable route.
