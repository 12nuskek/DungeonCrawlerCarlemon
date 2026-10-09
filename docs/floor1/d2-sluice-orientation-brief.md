# D2 Sluice: orientation and branch choice

**Authored preparation only; not implemented, compiled or runtime tested.**
Prepared on the accepted offline observer checkpoint
`01cd2432aaea72f6debca736fa8b02118b2fb1ed`. PR114's gameplay status and historical
execution totals (six baseline/four candidate) are unchanged. Screenshots N/A.

This is original adaptation dialogue by Codex within the Book 1 opening ceiling.
The Sluice, its geography, route board and exchanges are game inventions, not
book quotations or verified canonical locations. It adds no party member,
catching/storage/breeding, purchase interaction or later-floor reference.

## Purpose and graph

The broken great wheel is the player's recognition point. Damp blue-gray stone,
the cold Foundry silhouette and Arcade sign fragments distinguish the two exits;
the return-service gate is visible as a later connection. Stage Carl and Donut
at the margin so the main route, both exits and the recovery return stay clear.
Exact placements, camera reveals, assets and motion await graybox/native review.

The exchange gives Carl a practical way to compare routes and lets Donut prefer
the clues without deciding for the player. Walking into either branch is a
reversible choice, not a dialogue commitment or difficulty selection.

The [accepted graph](accepted-plan.md#main-route-and-optional-loops) remains
authoritative:

- D1's opening checkpoint leads to D2. Preserve the established trial, patrol
  and Warden requirements and the separate opening-completion meaning.
- D2 connects to Foundry (D3) and Arcade (D4), in either order. Both milestones
  are required for Commons (D5) to Pumpworks (D6) progression.
- Commons refuge is accessible after **either** branch objective; the other
  branch need not be complete to obtain free recovery and save access there.
  Backtracking to Quiet Landing remains available.
- Pumpworks drainage later restores the persistent service passage between D6
  and D2, usable in both directions. Neither inspecting it nor using it grants
  a branch objective, skips an unopened gate or signifies floor completion.
- The optional Warrens branch and its later far-side loop remain as planned.
  This scene adds no direct D2-to-Commons or D2-to-Warrens connection.

## Symbolic prerequisites and selection

These names describe future reviewed states, not assigned flags or save fields.
The brief reserves no numeric IDs, coordinates, encounters or rewards.

| Symbol | Meaning and scene use |
| --- | --- |
| `OPENING_CHECKPOINT_COMPLETE` | Existing D1 progress permits legal entry; it never means the full floor is complete. |
| `SLUICE_ORIENTATION_SEEN` | Proposed once-only presentation marker, set only after the arrival exchange completes. It grants no access or objective. Persistence allocation awaits F1-S01. |
| `FOUNDRY_COMPLETE`, `ARCADE_COMPLETE` | Independently reviewed branch milestones; read them to select guidance. The scene never writes either. |
| `SERVICE_RETURN_OPEN` | Reviewed persistent Pumpworks service-access state; select the open passage cue only when the connection is actually usable. The scene never unlocks it. |

On first legal D1-to-D2 arrival, offer the short introduction as an optional
interaction from a safe, unobstructed staging anchor. A completed introduction
never replays on re-entry or cold reload. A skipped or interrupted introduction
leaves `SLUICE_ORIENTATION_SEEN` unset and remains available **on request** on
re-entry; it never restarts automatically or blocks retreat, recovery or either
branch. Current route-board guidance remains accessible whether the introduction
was completed or not, and takes account of intervening progress. Optional
inspection supplies that guidance on every visit, including arrival from either
branch or the later service passage.

Arrival presentation and optional inspection must not require optional quests,
items, money or both protagonists being conscious. With an incapacitated duo
member, use the board/recovery cue without acting a healthy reaction; do not heal
implicitly or block travel. Depleted players can retreat without completing the
introduction or the remaining branch. No full follower is required.

## Short arrival scene: F1-D2-ORIENT

Carl notices the broken wheel; Donut turns her attention toward the branch cues.
Any gesture is a later native-animation candidate, not integrated motion.

> **Carl:** A wheel that big ought to go somewhere.
>
> **Donut:** It goes nowhere, Carl. Look at it.
>
> **Carl:** Foundry for machinery. Arcade for clues.
>
> **Donut:** Clues. Machinery rarely explains itself.

The route board supplies the practical rule, with final page breaks deferred to
native text-width review:

> **SLUICE ROUTES**
>
> Foundry or Arcade: either first.
>
> After either objective, reach Crawler Commons for free recovery and saving.
>
> Both objectives are needed for the route from Commons to Pumpworks.

The gate inspection before restoration reads:

> **SERVICE RETURN — CLOSED**
>
> Opens from Pumpworks after drainage. Choose Foundry or Arcade for now.

No scene achievement, loot, item cost or new reward is proposed. Acknowledging
the sign never substitutes for finishing a district objective.

## Revisit scene: F1-D2-REVISIT

Inspecting the board selects a concise exchange from current outcomes. Same-state
repeats retain the useful route cue; they never replay the wheel introduction or
add an AI interruption. The board marks each completed objective in words and
always retains the currently legal recovery/return information.

| Current state | Short original exchange | Useful next cue |
| --- | --- | --- |
| Neither branch complete | Carl: “Foundry or Arcade. We can still choose.” Donut: “My vote has not changed.” | Either branch first; Quiet Landing is the available recovery return. |
| Foundry only | Carl: “Foundry checked. Arcade next.” Donut: “Or the Commons first. I am not doing this tired.” | Remaining Arcade objective; Commons refuge through the completed Foundry route. |
| Arcade only | Donut: “We got our clues. Now the Foundry.” Carl: “Commons if we need a break.” | Remaining Foundry objective; Commons refuge through the completed Arcade route. |
| Both complete, service return closed | Carl: “Both routes checked. Pumpworks from the Commons.” Donut: “Good. We have done the scenic route.” | Reach Commons, recover/save freely, then its legal Pumpworks exit. Service gate stays closed. |
| Service return open | Carl: “That passage leads back to Pumpworks.” Donut: “A shortcut with manners. It works both ways.” | Clearly label the usable D2↔D6 passage and retain both completed branch markers and refuge directions. |

The final row assumes valid reviewed progression: Pumpworks access required both
branch milestones. An inconsistent migrated state must be diagnosed under the
future save contract, not repaired by this scene or hidden by a completion line.
Gate appearance, inspection, Journal guidance and actual access must agree.
The great wheel remains a broken landmark; an opened passage is not a promise
that the wheel turns or that all dungeon water changes.

## Future test routes — not executed

These are acceptance scenarios for later integration, not prepared emulator
inputs or a substitute for missing original runtime inputs.

| Route | Required future evidence |
| --- | --- |
| Legal opening checkpoint → first D2 arrival → inspect board → leave/re-enter → manual Save/cold reload | One introduction, unchanged D1 milestones, permanent duo, no later milestone/floor-complete grant, current repeat guidance and ordinary control return. |
| Skip or interrupt the introduction → retreat → re-enter with changed branch state → optionally Save/cold reload → request the introduction later | No automatic restart or travel/recovery gate; incomplete marker remains unset and the introduction stays optional. Board guidance reflects current progress. Once the requested introduction completes, further re-entry/reload never replays it. |
| D2 → Foundry objective → Commons recovery/save → return to D2 → Arcade objective → Commons | Foundry-only variation, accessible free refuge before Arcade completion, remaining objective stays required; then both-complete guidance and legal Pumpworks gate. |
| D2 → Arcade objective → Commons recovery/save → return to D2 → Foundry objective → Commons | Mirror the preceding order with the Arcade-only variation; no dialogue-imposed order or stranded depleted duo. |
| Start either branch, retreat before its objective with low action uses or an incapacitated member | Board/recovery guidance remains usable, Quiet Landing return remains legal, no item fee, forced rematch or automatic healing; no false branch-complete line. |
| Both branch milestones → Commons → Pumpworks drainage → service return to D2 → return to D6 → Save/cold reload | Closed-before/open-after cues, both-way persisted access, short new return exchange, unchanged milestone ownership and no repeated introduction. |
| Same board state repeated; one optional quest/reward skipped; depleted inventory; optional Warrens skipped | Concise repeat cue, unchanged legal main route and recovery, no consumable gate or new scene reward. |
| Each scene/board/gate approach in the eventual native camera, including return from both branches | Readable labels and page breaks, landmark recognition, clear reviewed widths/interaction tiles, no NPC/duo staging obstruction or extra progression link. |

## Dependencies and ready next action

Reconciled against the full accepted plan, current content ledger and backlog on
the parent checkpoint. No existing authored Sluice scene was found; the D1/D2
stitched reference remains a concept awaiting its seam/native-layout gate.
This brief does not replace the historical D02 explosive-recipe entry.

Combat/resource foundation F1-C01, graph/ports/camera/widths F1-G02, and audited
state/migration/refuge design F1-S01 remain dependencies of native D2 production
F1-D02. Encounter/reward budgets, flags, save fields, coordinates and engine
binding await those reviews. No new engine files, executable tests, art generation
or district-completion claims accompany this documentation.

The missing ordinary Save and complete original reference stream continue to
block gameplay validation; the original legacy-input gate remains unavailable.
The accepted offline observer result stays separate. All historic attempts,
failures and controller records retain their status.

Next ready action: parent review of this brief's route/recovery cues and original
dialogue. A subsequent docs-only Foundry/Arcade-to-Commons handoff brief can build
on that review without assigning persistence or encounter budgets. Native
integration and runtime routes wait for their dependencies and authorization.
