# Offline native battle retirement contract

Parent paused live execution after retained STOP35, STOP107 and STOP105 and
authorised this observer-only increment. Implement and compile the lifecycle
contract, test offline fixtures, review the complete native return path, preserve
the evidence and publish the existing draft PR114 checkpoint for parent review.
**No baseline, candidate, replay, emulator frames, new execution claim or failure
count reset is authorised here.** Parent decides any subsequent live scope.

Game engine, poses, palettes, mechanics, Save ABI, rewards, resource gates, route,
controller policy/cadence, 30,000 battle and 36,000 visual bounds stay fixed.
Full frame trace/capture remains enabled; existing pose masks, repeat/swap,
warning, faint, palette, exact state/control and complete budget gates remain.

The read-only observer distinguishes pre-entry from three qualified states:

1. **ACTIVE** starts only at the verified native first-turn phase with four
   registered battler owners and completed first picture copies. Pin the saved
   ordinary trainer-return callback, original graphics registry and four 8,192
   byte picture source ranges. Live HP actors retain strict registered ownership;
   Carl/Donut/Warden retain the original known-pixel, shape and palette checks.
   A cleanup phase with graphics still allocated remains ACTIVE.
2. **RETIRING** requires the verified native FreeReset, TryEvolve or ReturnFrom
   cleanup phase, cleared graphics/battle-resource registries, cleared candidate
   16-byte pose state and no queued copy overlapping any retained picture source
   range. Cleanup phases cannot regress. Never dereference retired memory or
   apply live picture ownership to it. Native fade may still retain sprites and
   the battle flag. Queue checks apply even when processing is unarmed, and
   continue during field reconstruction; reused address ranges get no exemption.
3. **FIELD** requires post-retirement !inBattle, retained ReturnFrom phase and
   saved trainer callback, the script/music wrapper followed by local rebuild
   states0,1,2,3 in order (repeated current states allowed), then native
   CB1_Overworld/CB2_Overworld. Require unlocked controls, script shutdown2,
   cleared field hooks, inactive native palette fade, no continuation-fade task,
   and continued retired-registry/pose/queue cleanup. Readiness must remain valid
   through finish. Ordinary field sprites are recreated by native code; they
   are not expected to be empty or preserve battler images.

Native CallCallbacks runs CB1 then the currently selected CB2. ReturnFromBattle
is called by BattleMainCB1 and selects the saved CB2_EndTrainerBattle; that CB2
can execute immediately and select the script/music wrapper before sampling.
Pin savedCallback at readiness and throughout the lifecycle. Do not require a
full-frame EndTrainer observation; record whether it was actually observed.
The verbatim native scheduler/setter are exercised in the offline fixture.

Source-pinned scoped ELF STT_FUNC identities route all11 lifecycle/readiness
functions. Compiler/NOTYPE labels and unscoped nm function names cannot select
these predicates. Missing/ambiguous identities and unresolved phases stop.
Evolution scenes/link/other return paths are not admitted: this game has
DCC_ALLOW_COLLECTION FALSE and native evolution returns SPECIES_NONE.

Pre-entry !inBattle retains the existing candidate reset assertion but contributes
**zero exitClean frames**. Finish requires qualified ACTIVE, RETIRING and FIELD,
all four local states and a postbattle exit sample; old pre-entry counters cannot
satisfy it. Lifecycle failures use114; existing ownership/pose105, unknown
pixels107, readiness110, identity112 and queue113 failures stay active.

Use retained STOP105 actor/sprite/phase/copy metadata in a distinct offline
projection. Registry/resource NULL values are modeled overlays because the old
execution did not serialize those values separately. The fixture is not a replay,
recovered input, retroactive PASS or actual field-return evidence. Preserve all
three actual failures, exclusive claims, counters, controllers and unchanged
ordinary Saves. Original legacy saves/raw logs/patrol-complete input stay missing;
ordinary reconstructed inputs never substitute for the legacy acceptance gate.

See [offline evidence and source review](../evidence/floor1/v01/battle/observer-lifecycle/README.md).
