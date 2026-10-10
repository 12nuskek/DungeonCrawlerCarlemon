# Opening4 retained review: conserve medicine under a declared risk envelope

Reviewed from clean `4cff72680be2256fd35531eb4ed2a643fb45da1e`. This increment only
reads retained evidence and source. **No game process, freeze, claim, Save, cold
process, ROM change or retry.** Opening4's STOP101 remains terminal. The proposal
below needs independent review and a separate authorized contract before use.

## Exact observed Guard sequence

The bounded [analysis](analysis.json) independently rehashes its original input
files against the immutable private manifest and decodes the retained battle
packets. [Read-only analyzer](../../../../../scripts/analyze-f1-c01-opening4-retained.py)
has no emulator/replay entry point. Actor order in HP columns is explicit below;
the next row is the previous turn's resulting state, not a simulated continuation.

| Turn / native decision frame | Carl / Donut HP | Guard / Scuttler HP | Carl STRIKE / Donut SPARK PP | Potions before | Actual actions, in execution order |
| --- | --- | --- | --- | --- | --- |
| 0 / 22919 | 33 / 28 | 29 / 24 | 8 / 2 | 2 | Donut SPARK: 3 to each foe; Guard BRACE: Defense stage6→7; Carl STRIKE: 5 to Guard; Scuttler TACKLE: 5 to Donut |
| 1 / 24105 | 33 / 23 | 21 / 21 | 7 / 1 | 2 | Donut SPARK: 3 to each; Guard TACKLE: 6 to Carl; Carl STRIKE: 5 to Guard; Scuttler TACKLE: 5 to Carl |
| 2 / 25052 | 22 / 23 | 13 / 18 | 6 / 0 | 2 | Donut Potion on Carl: 22→33; Guard TACKLE: 6 to Carl; Carl STRIKE: 5 to Guard; Scuttler TACKLE: 5 to Donut |
| 3 / 26113 | 27 / 18 | 8 / 18 | 5 / 0 | 1 | Donut Potion on Carl: 27→33; Guard TACKLE: 6 to Carl; Carl STRIKE: 5 to Guard; Scuttler TACKLE: 5 to Carl |
| 4 / 27144 | 22 / 18 | 3 / 18 | 4 / 0 | 0 | STOP101 before turn4 actions: fixed Carl≤27 policy requires unavailable medicine |

All observed damaging hits in these four completed turns are normal hits;
metadata, PP changes and target HP changes agree. No WEAKEN was executed in this
Guard encounter. Carl BRACE / Donut WEAKEN remain40PP. Guard Attack remains stage6
and Defense remains stage7 after turn0. Event frames and full allowed battle
fields appear in analysis.json. Persisting metadata during menu/heal animations
does not establish a new attack; only actual PP, HP or stage transitions are used.
Trial is a separate earlier encounter, not part of this Guard table.

## Two actual medicine closures; transient coverage limits

| Use | Confirm / full-heal / fresh-A / native-return frame | HP restored / unused cap | Stock |
| --- | --- | --- | --- |
| 1, Donut-owned, Carl slot0 | 25251 / 25264 / 25419 / 25502 | 11 / 9 | 2→1 |
| 2, Donut-owned, Carl slot0 | 26295 / 26303 / 26451 / 26534 | 6 / 14 | 1→0 |

The existing native audit was independently rerun on retained snapshots: field
to native Bag compaction, complete UI permutation, capped20HP heal and removal of
exactly one item at the actual inventory position, reverse party permutation,
all600 party bytes and all other decoded state, and single fresh-A ordered before
native return PASS for both uses. No snapshot/state validator was weakened. The
actual logs report key release, printer completion, printer-task destruction,
party fade, field order, exit, setup and reshow for each return. Full snapshot
capture occurs after the earlier battle-cache HP transition at25252/26296; these
timestamps describe different observation points in the same native heal.

`gc_lifecycle` calls the bound `gt_transition` before ordinary checks. Actual
closure flags and the two returns establish successful use of that integrated
observer, but **do not identify each transient instruction cut exercised**.
The retained battle stream has party/mons/control/chosen-move fields, not
per-frame CPU registers, callbacks, tasks, printer state or heap headers. The only
CPU capture is terminal STOP101. Across the two fresh-A-to-return windows there
are zero checksum-invalid actor samples. Four such Guard samples elsewhere
(22917,24099,25046,26251) cannot identify an Update/memcpy/Free path. Identity UI
order also makes many copy writes observationally identical. Specific creation,
printer destruction, outer Update offsets, progressive memcpy, skipped-copy
observations, Free/coalescing and cleanup instruction cuts retain **offline-only
coverage**, not new actual runtime coverage. Prior offline results/proofs are
preserved and were not rerun in this increment.

## Source bounds and the terminal KO branch

Frozen game source is `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine tree
`0fedd142f43f136ceee189c54101b095fc88f495`, identical to this review's engine.
Native integer truncation gives the following neutral Normal TACKLE bounds at
Carl level9, Defense15; no status, held item, badge, screen or damage-boosting
ability applies on this authored route:

| Incoming hit | Normal | Critical |
| --- | --- | --- |
| Guard→Carl | 5–7 | 12–15 |
| Scuttler→Carl | 5–6 | 10–12 |
| Scuttler→Donut | 5–6 | 10–12 |

Guard follows BRACE on turn0 then TACKLE at player-left Carl while that patterned
action is available; Scuttler can target either protagonist. Native speed order
for ordinary moves is Donut23 > Guard15 > Carl13 > Scuttler12, priorities0.
STRIKE has100 accuracy against the observed neutral accuracy/evasion stages;
Carl has GUTS rather than HUSTLE, Guard OWN TEMPO rather than an evasion ability,
and neither actor has a held item or status. Guard's authored moves supply no
Protect, invulnerability, accuracy/evasion change or priority interruption.

At the **actual terminal state**, Carl's normal STRIKE is5–6 despite Guard's +1
Defense, enough to KO Guard3HP before Scuttler. Guard XP is
`floor(floor(85×9/7)/2)×150/100 =81`: Carl495→576 crosses medium-slow level10
threshold560. Native faint handling runs between actions; the level-up updates
current HP by maxHP difference33→36 and updates Defense15→**17** before Scuttler.
The source-derived level10 stats are36/25/17/14/12/14
(maxHP/Attack/Defense/Speed/SpAttack/SpDefense). The initial analyzer used an
incorrect Defense16 expectation and failed an assertion; read-only diagnosis
corrected it to17. No game run or evidence mutation followed that analysis failure.
The level10 Scuttler critical ceiling remains9. Thus even both critical ceilings
on Carl give `22−15+3−9 =1HP`. The bound also allows Guard choosing BRACE or a
miss and Scuttler targeting Donut; those do not worsen Carl's bound. Donut18
survives her reachable12-damage critical ceiling.

This is a conditional source proof for **one terminal turn**, not an observed
turn4, remaining-fight victory, altered-input replay prediction or permission to
resume. Earlier retained r2 turn4 independently observed Guard KO, Carl9→10,
33→36 maxHP/+3 currentHP, then Scuttler acting; its eventual STOP90 stays preserved.
Neither that history nor this arithmetic recovers the missing original oracle.

Source anchors: [move definitions](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/data/battle_moves.h#L4619),
[authored move/target pattern](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/battle_controller_opponent.c#L1577),
[speed order](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/battle_main.c#L4599),
[damage and critical stage rules](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/pokemon.c#L3243),
[accuracy](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/battle_script_commands.c#L1094),
[XP/level update](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/battle_script_commands.c#L3331),
[between-action faint processing](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/battle_util.c#L651),
[native HP increment](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/4cff72680be2256fd35531eb4ed2a643fb45da1e/engine/src/pokemon.c#L2886).

## One practical proposal, for later review

**Use one declared medicine-conservation strategy: assess one critical plus the
other foe's ordinary hit, preserving Donut's SPARK→WEAKEN support turns.** Do not
change enemy stats, critical rules, action PP, rewards or the game ROM. This is
an ordinary combat decision with an explicitly accepted risk, not a special
state-check exemption for this trace. Source ceilings before Guard's KO are
`max(15+6,7+12)=21` on Carl with both foes,15 with Guard alone,12 with Scuttler
alone. Donut's reachable ceiling is12 while Scuttler remains; Guard alone targets
Carl while both protagonists live. Keep the solo-Scuttler Carl threshold12
conservative even after level10 makes the actual ceiling9. Fixed thresholds
do not take credit for a future successful WEAKEN or a predicted KO.

For a separately reviewed strategy contract, risk means Carl HP≤21/15/12 for
those foe sets, and Donut HP≤12 with Scuttler present. Donut heals the single
at-risk recipient through native Bag while Carl continues STRIKE on Guard, then
Scuttler; otherwise Donut spends available SPARK and then WEAKEN. With no foes,
leave battle resolution to native callbacks. Every native readiness, full-state,
resource, incapacitation, frame/time/storage and first-failure requirement stays
strict. Both recipients at risk still stop100; no medicine when healing is
required still stops101; capped healing unable to exceed the envelope still
stops102. No undeclared fallback, resources or retry.

At the **observed**22/27HP boundaries this strategy would decline those wasteful
Potions and permit the existing WEAKEN support decision. It does not assert that
changed inputs reproduce those HP states or enemy rolls. The general envelope
does **not** cover simultaneous criticals: at level9 two critical ceilings total27
and can incapacitate Carl22. Native criticals ignore Attack reductions and
positive Defense stages; neither WEAKEN nor BRACE guarantees protection against
that case. The terminal KO branch is a separately verified narrower exception,
not a universal safety threshold. No probability or lucky retry is promised.

Acceptance cases for later review and authorization:

- Boundary/source checks: both foes Carl21 versus22, Guard-alone15 versus16,
  Scuttler-alone12 versus13, Donut12 versus13; unchanged stock0/no-risk ordinary
  choice, both-risk100, required-heal/no-stock101 and capped-heal102 stops.
- Verify native targets, order, available patterned moves, accuracy, critical
  bypass and full state. Prove the actual Guard3HP/STRIKE4PP/XP495 terminal
  arithmetic separately; reject unsupported assumptions rather than allowing
  the favorable branch to mask a changed source/state.
- Any later actual opening requires its own frozen source/observer/route/claim
  and storage admission. Record real SPARK/WEAKEN or healing decisions and actual
  damage, capped waste, PP, targets and failures; never substitute these retained
  calculations for execution. Stop on the first failure, including incapacitation.
- Guard victory, guide recovery, manual Save/full live-disk validation and an
  independent cold process remain conditional later goals. Human explanation
  must show why Donut chose support or medicine and why Carl chose that target;
  continued useful duo contribution and recovery-trip burden need observation.

The two offensive SPARKs removed12HP across four targets here, then Donut spent
two turns restoring17HP from40 nominal healing, wasting23. That trade displaced
two fast WEAKEN turns and left foes' Attack unchanged. Native support can reduce
ordinary incoming damage before slower foes act, but its effect is discrete and
criticals bypass it. This makes medicine conservation a meaningful player choice
to assess, not evidence that two SPARK uses or enemy balance already pass the
accepted plan's player-experience gates. Carl retained4STRIKEPP at STOP; his
remaining offensive budget and post-KO survival still require actual verification.
Free guide recovery remains accessible and restores all uses. A concise later
player-facing note could explain the20HP cap, Donut healing while Carl attacks,
and WEAKEN's ordinary-damage benefit after the strategy is verified; no text or
ROM change is included here. Both branch orders/optional skips, nine authored
districts and all remaining full-floor acceptance requirements stay open.

## Identities, preservation and next dependency

Base/main remains `b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`; executed helper
`ff6f5180fdeca60380b782da61998cb1fe77ff87`, wiring tested
`fd24d3e76e370a9ab2c15bab0fbededba0ea2391`, reviewed transaction
`32a25769c5427656a010287bed6cf03c5f62b45c`. Existing ROM and ELF were rehashed:
`79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246` /
`7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d`.
Observer `8a7c91422d418d6b5e5b54938c0a4e0a4daa24f0110c55643ffa8b83832449ea`,
validator `89501c5e2090a44d59ab880e5b1e36be5b47264cbdf3ce6389faee53a2790a78`,
libmGBA0.10.5 `a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`.
Recorded GCC14.2.0, ARM binutils2.44-3+23+b1, agbcc source
`da598c1d918402c42c0c0d7128ba14567f3175e9`; recovered compiler binaries differ
from historical binaries. This review neither rebuilt nor claims original-tool identity.

Original opening4 manifest102entries/3190319959B was freshly rehashed exact,
including all27144 native frames in14 raw chunks. Existing local retention is
verified; **independent backup is unverified**, not an attachment backup claim.
No compression, deletion or upload occurred. Five failed Library uploads plus
one supported existing-backup download failure remain unknown-cause/zero original
bytes and are not retried. A separately approved private storage destination
with verified upload and independent download/hash check would be needed to
claim backup. Public material contains only sanitized analysis and previously
approved screenshots/motion, never ROMs, Saves or raw private streams.

C01 opening4/4 and cold0/0 remain unchanged, STOP82/90/104/101 preserved.
Historical V01six baseline/four candidate executions, STOP117requestedvisual8536
beforeB8402, later separate1/1, ordinary recovery5 and C01aactual5/3/1 with
claims6/3/1 remain unchanged. Main/all69 other heads/issue116, historical pins,
failed controllers/strategies and STOP records are preserved. PR117 stays draft
and unmerged. Original oracle/legacy input acceptance, uninterrupted C01,
G02/prepared/human/full-floor gates are unmet. Next dependency is independent
read-only review of this one strategy and its risk declaration; no execution
authority is added by this publication.
