# Causeway: refuge and final-approach orientation

**Authored preparation only; not implemented, compiled or runtime tested.**
Prepared on accepted documentation checkpoint
`022473cf21a56893c4a393abc1ec09071adbfcec`. PR114's gameplay/legacy limitations
and six baseline/four candidate execution totals remain unchanged. Screenshots
N/A; future routes below have not been prepared or executed.

Original Carl/Donut adaptation wording by Codex, within the Book 1 opening
ceiling. The district and exchanges are invented connective fiction, not book
quotations or verified canonical geography. The permanent duo and authorized
nine-district Floor 1 scope remain intact; no new NPC, party member, purchase,
catching/storage/breeding or later-floor content is introduced.

## Purpose and accepted routes

Give the player a recognisable place to recover and save before choosing to
approach the final challenge. Pale fractured bridges over dark void convey
anticipation; the small refuge and its service cue must remain legible without
finishing a conversation. Exact shelter staging, bridges, collision, camera
anchors, costs and encounters remain pending production review.

The [accepted graph](accepted-plan.md#main-route-and-optional-loops) and
[Pumpworks brief](pumpworks-drainage-scene-brief.md) govern access:

- Both Foundry and Arcade milestones precede Pumpworks; actual drainage opens
  the route to Causeway (D8). Arriving here does not award those prerequisites.
- Causeway's planned refuge provides established free recovery and manual Save
  access before the D9 commitment, without a quest, payment, consumable, optional
  preparation or dialogue-complete requirement.
- The existing D8 ↔ D6 ↔ D5 retreat remains available; the separately opened
  Pumpworks ↔ Sluice passage retains its persistent two-way state. Neither route
  requires a new milestone, rematch or Warrens visit to return to a refuge.
- Warrens (D7) remains optional. Its far gate opens only by the reviewed gate
  interaction from the D8 side. Once opened, it persists for D8 ↔ D7 ↔ D5 return
  travel in both directions; orientation dialogue neither opens it nor substitutes
  for reaching D8 through the required route.
- D9 contains the separate final challenge and actual descent boundary. Arrival,
  refuge use, preparation and conversation grant no victory or floor completion.
  The D1 Warden remains the opening checkpoint, not that final challenge.

## Symbolic conditions and readiness

These are design conditions, not allocated flags, map IDs or save fields.

| Condition | Meaning |
| --- | --- |
| `FOUNDRY_COMPLETE`, `ARCADE_COMPLETE`, `PUMPWORKS_DRAINAGE_COMPLETE` | Reviewed main-route outcomes; read for valid access and guidance, never granted by this scene. |
| `CAUSEWAY_ACCESS` | Proposed legal route state following reviewed Pumpworks progression; arrival is not independent proof of its prerequisites. Allocation and consistency await F1-S01. |
| `WARRENS_RETURN_OPEN` | Proposed persistent far-gate outcome, set by the separately reviewed D8-side gate interaction, never by dialogue or a D7-side approach. |
| `CAUSEWAY_ARRIVAL_SEEN` | Proposed optional introduction marker, set only when the exchange completes; gates no service, travel or challenge. |
| `D9_VICTORY`, `FLOOR1_COMPLETE` | Separate proposed authoritative outcomes; scene reads them without awarding, clearing or equating them. Descent still has its reviewed main-milestone and victory checks. |
| `SCENE_READY` | Conceptual ordinary-field readiness, safe staging and both protagonists able to speak; no live encounter/interaction. Not a persistent field or prerequisite for refuge service or retreat. |

Journal, doors, route cues and actual access must agree with reviewed state.
Contradictory prerequisites, illegal migrated positions or inconsistent shortcut
state require diagnosis under F1-S01; dialogue cannot repair them by awarding
progress. Active-refuge selection, safe retry spawns and persistence belong to
the reviewed refuge/state implementation, not this introduction.

## Refuge arrival: F1-D8-REFUGE

After legal arrival, offer one short optional exchange clear of services and the
onward approach:

Carl: “One more place to stop.”
Donut: “Then stop. The arch can wait.”

Keep the independent service cue readable before any D9 commitment:

> **CAUSEWAY REFUGE**
>
> Free recovery. Saving available here.
>
> Descent Gate ahead: final challenge, then a separate descent.

The conversation does not heal, revive, refill actions, save automatically,
consume supplies or start combat. Completed introductions never replay on
re-entry or cold load. If skipped, interrupted or not ready, keep the marker
unset and the exchange optional on request later; do not auto-start it on return.
Current route/service guidance remains available throughout. Native text width
and page breaks await review.

## Final approach and return: F1-D8-ROUTES

Optional inspection explains the current route state. It must remain distinct
from the reviewed action that actually commits to D9 combat; merely inspecting
the board, recovering, saving or hearing a line never starts that challenge.
Exact challenge-entry interaction and staging await production review.

| Current state | Short original exchange when ready | Independent guidance |
| --- | --- | --- |
| D9 not won; Warrens far gate closed | Carl: “The gate to Warrens opens from this side.” Donut: “A way back, if we want it.” | Gate interaction optional; retreat through Pumpworks remains available. Refuge and D9 approach require no Warrens opening. |
| D9 not won; Warrens return open | Carl: “Warrens takes us back to Commons.” Donut: “And brings us here again. Good.” | Persistent two-way optional return; Pumpworks retreat still available; final challenge not won. |
| Reviewed D9 victory recorded, full-floor completion unset | Carl: “The challenge is behind us.” Donut: “The descent still lies ahead.” | Challenge cleared; descent remains a separate boundary with its reviewed checks. Safe field refuge/return services remain usable; no victory reaward or automatic descent. |
| Reviewed full-floor completion already recorded on a legal return | Use concise route/service cue only. | Reflect the existing completion truth without awarding it again, replaying arrival or introducing later-floor content. |

Same-state repeats use short current cues without recurring AI interruption,
reward or preparation charge. Re-evaluate state after an interrupted inspection;
do not replay stale pre-victory or closed-gate text after its real outcome changes.
Interrupting conversation changes no gate, preparation resource, challenge or
descent state. Gate persistence and challenge transactions remain separate
implementation responsibilities; requesting dialogue again never reruns them.

With depleted uses or either protagonist incapacitated, show service/route cues
without healthy-duo acting. Free refuge recovery and ordinary manual Save outside
combat must be reachable before choosing D9, without potions, currency, Charge,
quests, rewards or a forced fight. Restoration belongs to the established service;
the scene never performs it. Optional preparation may help later reviewed combat
but cannot become a required key to D9 or recovery. Defeat/retry handling awaits
F1-S01/C01 and must preserve cleared encounters, milestones and opened shortcuts.

## Future routes and checks — not executed

| Route or condition | Required later evidence |
| --- | --- |
| Complete Foundry then Arcade; separately Arcade then Foundry → reviewed drainage → D8 refuge | Both orders obey main milestones; free recovery/manual Save reachable before D9; no arrival/dialogue completion grant. |
| Skip Warrens, quests, caches and preparation → D8 refuge → choose D9 approach | Refuge and main approach require none of the skipped content, payments or consumables; actual unprepared combat fairness remains F1-C01 work. |
| Arrive depleted or with either protagonist incapacitated → service/manual Save/cold → return to approach | Service and retreat usable without healthy-duo acting, introductions or forced combat; actual service restores according to reviewed rules. |
| Skip/interrupt arrival or route inspection → retreat/re-enter → request later; separately complete introduction → Save/cold | Incomplete exchange stays optional on request, completed introduction never replays; service, resource ownership and progress unchanged by dialogue. |
| Approach far gate from D7 before D8 unlock; then reach D8 legally and use its reviewed gate interaction → D8 ↔ D7 ↔ D5 → Save/cold | Wrong-side approach cannot unlock/bypass drainage; D8-side outcome persists in both directions without objective awards, rematches or optional salvage requirement. |
| Leave Warrens gate closed; retreat D8 → D6 → D5 and separately use the opened D6 ↔ D2 passage | Existing return paths retained with correct cues; recovery does not depend on the optional gate and Sluice's wheel remains broken. |
| Interrupt dialogue before gate interaction; separately after its reviewed commit; reopen board after state changes | Dialogue never opens gate; genuine unlock retained without repeated interaction, cost or reward; latest cue agrees with access and Journal. |
| Inspect D9 approach/recover/prepare with victory unset; separately return in safe field after reviewed victory but before descent | No accidental combat from service/orientation and no victory/full-floor grant; post-victory cue distinguishes the still-separate descent checks. |
| Future reviewed defeat/retry and final-descent tests, including cold persistence and legal completed-state return | Cleared encounters, refuges and shortcuts retained; only real D9 outcome and reviewed descent establish their respective states; no dialogue reaward. No such execution is authorized by this brief. |
| Refuge, onward boundary, both gate approaches and Pumpworks return in native 240×160 views | Legible refuge and distinction between inspection/commitment; reviewed clear widths, interaction tiles and unobstructed duo staging. |

## Dependencies and next ready work

The ledger has no dedicated Causeway refuge/final-approach scene before this
entry. F1-C01 combat/resource work, F1-G02 graph/ports/widths/camera validation and
F1-S01 audited state/refuge/migration design remain prerequisites for production.
Encounters, rewards, flags/save fields, geometry, native assets, engine binding
and actual recovery/shortcut/challenge/descent persistence proof remain pending.
This preparation closes no district, visual-rollout or whole-floor acceptance gate.

Missing ordinary Save, complete original runtime reference and original legacy
inputs remain unavailable. Authored preparation or fresh inputs cannot replace
the original oracle or legacy acceptance gate. The failed private-transfer
diagnosis remains closed at unknown cause; no transfer, reconstruction or gameplay
is attempted here. Historical failures/controllers and six baseline/four candidate
totals retain their status.

Next bounded preparation after parent review: one docs-only Warrens optional-route
and far-gate revisit brief. Reconcile its D5 entrance and D8-side unlock with this
brief, keeping salvage, rewards and encounters undecided and the main route
available when Warrens is skipped, without adding a district or mandatory objective.
