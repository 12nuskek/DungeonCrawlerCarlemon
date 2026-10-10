# Superseded Carl-heals proposal — historical review record

The separately authorized Donut-heals experiment is specified in
[c01-guard-choice-r1-contract.md](c01-guard-choice-r1-contract.md).
The original proposal below remains unchanged as superseded history.

# Proposed C01 Guard player-choice evaluation — review only

Analysis base `56565c1ffdf24e025fe9d86d51e72fa9306149c4`; actual r2 tested helper
`978cbf03907c38ef24fb4008bfed04e1c69daea5`. This is a new proposed contract,
not an amendment/admission/execution of either frozen C01 opening contract.
No runtime claim or policy is executed. See the
[retained analysis](../evidence/floor1/c01/retained-guard-analysis-20261010/README.md)
and [complete turn table](../evidence/floor1/c01/retained-guard-analysis-20261010/turn-table.md).

## Recommendation and predeclared choice

Evaluate ordinary earned healing first. Keep game stats/moves/critical rules,
Carl's target choice, Donut's depleted-SPARK fallback and readiness-aware12-frame
cadence. The observed unused Potion and continued Fight at Carl7/4 HP demonstrate
an untested player choice, not a demonstrated need for lower enemy stats.
BRACE/WEAKEN have source-supported normal-hit usefulness and a critical limit;
do not replace them or change balance on this single failed trajectory.

One readable Guard-specific rule, fixed before any new source/runtime freeze:

> At the start of each Guard turn, heal an actor whose current HP cannot cover
> the next turn's reachable enemy attacks: Carl27 HP while GUARD lives, Carl12
> after GUARD falls, Donut12 throughout. Heal at or below those thresholds.
> If both qualify, stop before input: this scoped rule admits one Carl item
> action per turn, not a second simultaneous healing actor.
> Carl selects Bag → earned Potion → that actor instead of STRIKE. Donut keeps
> its ordinary SPARK, then WEAKEN fallback. Otherwise use the existing offence.

Thresholds derive from source/observed entry stats and **native legal targets**:
GUARD BRACEs on turn0, then targets Carl with Tackle; its critical maximum15
plus SCUTTLER's12 yields27. SCUTTLER alone can hit Donut, maximum12. Use the
conservative27 threshold even on turn0, and retain the entry SCUTTLER ceiling12
after Carl's level growth (actual level10 ceiling9). This predefined foe-KO
branch is not a retune to a desired frame, roll or successful policy search.
Confirm that the ordinary authored
party construction supplies these entry stats in offline admission; an unexpected
native stat/type/ability/state is a terminal contract failure, never a resource
grant or forced stat. Do not read RNG, add timing padding, align historical
frames or predict that the recorded criticals will recur after different inputs.

Require an available earned Potion and a living injured target. If the threshold
calls for healing but inventory is exhausted, or capped20-HP recovery cannot put
that actor above its declared threshold, stop with an explicit resource/
turn-buffer failure before further input. A native incapacitation at any
frame still stops immediately. No revive, rescue, menu cancellation loop, mid-turn
decision revision or automatic retry. Record actual gain/waste, actor's replaced
move, unchanged PP for that item action, and increased encounter duration.

This is a conservative **next-turn** buffer rule, not a whole-fight survival
proof. Repeated focused criticals, limited20-HP gains/supplies and delayed
damage/PP can exhaust that buffer; the explicit resource stop is retained.
Donut is not exposed to GUARD's hypothetical18-HP critical while Carl lives.
Applied analytically to the immutable r2 trace, it first calls for Carl healing
at turn2's menu (observed frame25684, Carl22; native capped gain would be11).
Donut never crosses its reachable12-HP threshold in that trace. These are
diagnostics only: no claim that a
changed-input trajectory reaches those states, spends those exact Potions or wins.

Omit the mandatory field Potion consumption immediately before free guide
recovery from this **new evaluation route**, retaining the original demonstration
and its4-HP cost unchanged. This keeps both legitimately earned supply Potions
available. It is a separate efficiency/instructional recommendation, not a grant,
balance edit, or claim that zero items suffice for survival. Any later tutorial
text/code change requires its own scope/review. The omission naturally changes
ordinary input duration; add no delay to preserve/search an old random trajectory.

## Proposed scope and dependency order

1. Author separately named Guard-choice helper/model/route/contract/output root;
   leave both old wrappers/contracts/source archives/STOPs/claims intact. Reuse
   the unchanged integrated game/build only after manifest revalidation; do not
   rebuild or merge PR117. The proposed route is normal New Game → note/supply →
   guide → original offensive trial → earned Scrap → guide → Guard → guide.
   No Howler, Warden, prepared route, stairs, optional equipment or later floor.
2. Bind native battle action controller owner, Bag location/running callback,
   task/fade/context Use readiness, battle party type/action/layout/order/target
   and actual native Carl/Donut identity, successful capped heal/consume and
   reshow/return/next independent Donut selection to exact source/ELF/compile-only
   ABI. Existing field Potion readiness is insufficient. Do not assume target
   UI slot0/1 is party0/1 without the native battle-order mapping. Reject task
   existence during setup, wrong actor/target/item/menu/fade, premature return,
   no-effect/fainted/full-HP target, duplicate consume/heal and unsupported state.
   Derive last-Potion removal, native zero-quantity slot handling/compaction and
   any rekey from item/menu source; the old field2→1 fixture does not admit1→0.
3. Admit the policy with source-derived exact threshold/two-actor-risk/empty-inventory/
   capped-heal/PP-boundary vectors and the actual retained-state cases offline,
   without replay. Preserve Carl STRIKE0/BRACE>0 STOP92; do not invent a fallback.
   Donut SPARK0→WEAKEN remains exact. Bind the native item action cost/priority;
   the HP update occurs in target UI, not a second heal during item-action text.
   Keep all six decoded checksum/reencoding/unused400 checks, full flags/vars/
   resources and native friendship/counter/poison/EV handling. Extend only declared
   earned Potion/HP mutations with complete byte-derived expectations, not masks.
4. Freeze legal routes and new guide/Save endpoint from source, all source/build/
   observer/ABI/input identities, strict resource/action/phase model, first-failure
   capture (including CPU), bounded all-frame storage, and exclusive claim. Review
   the published source/contract/offline admission before authorizing one opening.
   The [export plan](../evidence/floor1/c01/retained-guard-analysis-20261010/export-plan.md)
   needs separate capacity/admission; current storage cannot reserve its combined
   100,000-frame capture/full-cap export plan. No unsupported storage promise.
5. Only after that separate authorization, one opening could evaluate the rule.
   If native Guard victory and guide recovery succeed, manually Save at the legal
   Quiet Landing field endpoint35,1 at(4,5), recording actual facing and checking
   source/legal field readiness. No acceptance of guessed HP/Save bytes. Expected
   earned totals, conditional on both actors surviving the same two KOs: levels
   10/9, XP627/937, money3640, Scrap2, trial/Guard wins set; Howler/preparation/
   boss/checkpoint/loop unset. Guide HP/PP restore is derived natively, not injected.
   Potion remainder derives exactly from observed item actions (0–2), not a
   required desired consumption. Native friendship/walking are modeled exactly.
6. Admit one independently claimed cold process only after actual manual Save
   and complete14-sector/latest-generation/full-u32-count/party/flags/vars/
   resources/counter/legal-field equivalence. Use normal Continue, no reload to
   bridge gameplay or extend the route. First failure blocks cold/dependent work.
   Stop for review before Howler/Warden; this Guard-only evaluation would not
   close the continuous C01, prepared, both-orders/optional-skips or full-floor gate.

The immediate next dependency-ready work is offline source/model/contract admission
of battle medicine and this fixed rule, plus a reviewed capacity choice. Runtime
launch is not authorized by this proposal. No narrow balance patch is recommended
from the present evidence; any demonstrated future inability to manage ordinary
risk should identify its exact move/stat/resource problem before proposing one.
