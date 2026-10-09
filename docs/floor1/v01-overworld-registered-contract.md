# Separate native animation-table registration correction

Effective-flip baseline640be782 PASSED64 assertions/7924 frames, zero errors,
Carl9 frames and right2/7/8, Donut3 standing/mirrored2, five scenes/four existing
conversations. Input/outputSave030b unchanged. Accepted baseline remains that
exclusive execution; it is not repeated or copied into a new execution claim.

Candidate640be782 on game2a76829f/4cfc ROM STOP97/61 assertions at7924. Both side
attention holds were exactly24 actual OBJ VRAM frames; four conversations/field
controls/resources and all5 scenes passed. Carl masks511/391; Donut masks13/12
omit standing north1. Actual north screenshot retains down art despite native
facingNorth. Candidate has full actual stop-clock/live/last accepted buffers;
no success/final snapshot/heap peak footer claim. Preserve this failure and the
earlier wrong-effective-flip baseline STOP97 separately.

Source diagnosis: new sAnimTable_DccDonut retained Standard's20 animation pointers,
but was not added to sStepAnimTables. Native GetStepAnimTable matches pointer
identity; SetStepAnim updates animNum but skips SeekSpriteAnim if unregistered.
Paused facing therefore leaves the previous VRAM picture. Actual compiled native
lookup/SetStepAnim reproduces that defect offline. This is the implementation's
graphics-table registration omission, not a timing/input/observer exception.

Add ONE sStepAnimTables entry with the exact existing Standard1/3/0/2 metadata.
No other game code/assets, dialogue script, native movement/controller/cadence,
save ABI, environment, palette or assertions change. Offline actual source cases
verify four starting indices/standard metadata/inanimate guard before freeze.

Freeze/compile separate new committed candidate; ONE exclusively claimed ordinary
candidate execution in runtime-registered/after against the existing accepted
640be782 before. Original153-line route and all gameplay/visual gates are exact,
including all3 standing directions and24 actual west/east reaction frames. Same
030b normal save and24000 absolute/zero battle bound. No baseline repetition,
RNG/timing search, automatic retry or broad replay. Stop any further divergence.
Retain all failed claims and private necessary logs/saves/frames, keys/diagnostic
buffers outside uploads; old legacy/C01/human pacing/battle-stage gates remain.
Draft checkpoint then parent visual review, no merge/rollout of this stage.
