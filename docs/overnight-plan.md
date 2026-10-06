# Dungeon refinement: overnight audit and backlog

Authorised2026-10-06 13:19:10UTC through approximately21:19UTC. Base
bf27e2692025eb4291ffbf992a3b6412340d32cd. Sole writer; existing parent-owned
continuation only. Earlier playtest stop superseded within this window; Stage6
and new systems remain excluded. Preserve private I01 baseline for comparison.

## Actual-room audit

Six16×12 maps share the same12×7 walkable rectangle, same top-wall lamp pattern,
nine simple tile motifs and identical blue-gray palette. Repetitive one-tile
floor borders compete with characters; walls lack depth and material variation.
Stairs look like narrow ladders. Safe and review rooms repeat the same rug and
Donut exchange. Entrances/exits have weak framing; props rarely tell a story.
The approved protagonists/opponents are significantly more developed than rooms.

Baseline evidence: I01 tested81b232a; ROMf46643a4…e43948; full1053/62 checks and
nine native-image matches. All systems work, but automated timing is not human
pacing and retry re-entry checks do not prove victories in those exact saves.
No active PRs or implementation processes at audit; main clean, all prior PRs
merged. No .agents/skills directory is present; root AGENTS.md applies.

## Dependency-ready priorities

| ID | Scope | Acceptance |
|---|---|---|
| N01 (issue35) | Original environment materials, wall depth, floor scale, light/palette identity for six rooms | Preserve collision/elevation/behaviors and event coordinates; native budgets; actual six-room comparison; affected runtime routes |
| N02 | Entrance and quiet landing composition: purposeful zones, safe-area furnishing, stronger arrival and recovery staging | Bounded geometry/props; four-direction collisions; all interactions/recovery/save; no blocked routes |
| N03 | Service/gauntlet exploration: meaningful branching, readable trap/secret and patrol spaces | Optional quest/crafting/secret branches, backtracking and encounters persist; preserve assertions |
| N04 | Boss/stair staging and environmental story/dialogue clarity | Both boss responses, preparation, staircase/re-entry; no canon invention/later spoilers |
| N05 | Evidence-led pacing/presentation defects and final regression | Same-save retry-to-win where practical; continuous routes; private comparison package; honest remaining limits |

Sequence may adapt to actual defects and design-review feedback. One bounded
implementation task at a time. No corridor padding, scripted waits or speculative
mechanics to fill time. New major systems, campaign expansion and platform changes
require a user decision and are not part of this window.

## N01 contract

Replace the thin grid material pass with authored native pixel tiles: large worn
flagstones, deep wall bases/caps, readable stair mouths and material-specific
decals. Give each room a distinct lighting/material palette and focal floor
composition without moving objects, changing scripts or walkability. Shared OBJ
palette and approved character/enemy bytes remain unchanged. Runtime proof must
cover all six rooms, palette/UI returns, interactions, transitions and saving.
Keep code that changes native assets separate from subsequent layout edits.

No open blocker attempts. Deadline is a review boundary, not permission to merge
unverified changes. Preserve baseline ROM/private ZIP and all failed traces.

## Reconciled outcomes

The initial priority labels above were planning hypotheses. Actual focused tasks:
N00/N00b guidance and Journal; N01 native rooms/props and legacy save-cache recovery;
N02 bounded26-cell geometry; N03 persistent environment states and matching text;
N04 exact recovered-save wins; N05 one-page repeat recovery and final full regression;
N06 private visual/playable package. N05 merged PR50 at f2edec3, tested eaf073d with
90 sessions/1531 assertions across full and recovery runs. No Stage6/new systems.
The visual review and exact qualification of pacing remain the final deliverable.
