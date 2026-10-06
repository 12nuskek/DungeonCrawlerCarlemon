# S01 checkpoint — partial exploratory verification

Source `f784d58fe9692ef696224742cfa279cf3211ead4`; incremental build passes.
This is NOT the final S01 acceptance package. New-content isolated build, complete
boss outcomes and staircase cold saves remain pending. No S01 merge yet.

Reused input routes from R02 pass on current source: setup-rewards32,
victory-loot53, reload-reentry34. Then gates17, guard19, guard-rest12 and howler
opening5 pass with normal mGBA input/read-only RAM. New `pattern` diagnostics
verify actual trainer/turn, enemy PP/stages/level and Carl attack stage.

The branch checkpoint retains these routes to resume; full raw logs and reviewed
screenshots will accompany final isolated acceptance. Current local exploratory
artifacts are under artifacts/s01. Save snapshots before guard/howler are generated
by normal saves and ignored; no RAM injection or committed binary.

Next: finish howler victory/recovery, test local defeat/retry, branch real saves for
prepared/unprepared boss strategies, verify staircase/cold persistence; then run
isolated committed suite, archive evidence and create scoped PR.
