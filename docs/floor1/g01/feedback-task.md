# F1-G01e-SF — relocated pickup feedback

Resumed 2026-10-08 (Australia/Brisbane) after the user's continuation instruction.
Base: `16d7012bcff5de4ce04ad691fa81543bb3047ff7`, draft PR75.
One writer; no scheduler, new Cloud task, strategy reset or broad art rollout.

The live Field pickup calls the existing once-only reward script, but its flag
does not select a live presentation tile. Add an available floor-panel state and
a disturbed-floor state using existing authored native tiles. Preserve the cell's
collision/elevation and effective movement behavior. Keep all archived maps,
reward scripts, save structures, flags, anchors and reachable area unchanged.

Acceptance: reproduce the missing feedback on the exact previous binary; build
the committed candidate in an isolated snapshot; use ordinary controller input
and an untouched copied original save for pickup, repeat, movement across the
cell, map exit/re-entry, manual Save and cold reload. Inspect native screenshots
and verify reward count/flag, complete tile words and movement. Regenerate source
and review the diff. Compilation is separate from runtime verification.

Excluded: battle/resource balancing, a fourth blind combat strategy, navigation
copy, other art, save migration changes, V01, whole-floor acceptance or PR75 merge.
Full logs/saves remain local; publish only scoped source, bounded results and
actual screenshots. Preserve unpublished diagnostic ancestry in its existing
local branch/archive; this branch starts directly from the remote PR75 head.
