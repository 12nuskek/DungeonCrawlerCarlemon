# C01 r2: retained Guard analysis, no new execution

Analysis starts at `56565c1ffdf24e025fe9d86d51e72fa9306149c4` on draft PR117.
Runtime source remains `978cbf03907c38ef24fb4008bfed04e1c69daea5`, game
`4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine tree
`0fedd142f43f136ceee189c54101b095fc88f495`. Existing verified build, recovered
tooling and observer identities remain in the immutable r2 checkpoint. No rebuild,
original-tool-identity claim, gameplay/claim/cold/export retry or balance change.

The [turn table](turn-table.md) and [processed observations](turn-analysis.json)
cover both actual encounters: five trial turns and six Guard turns. The new
[read-only parser](../../../../../scripts/analyze-f1-c01-retained-guard.py) checks
input files against the existing private retention manifest, then cross-checks
**15,382 TURN_METRIC rows against 17,784 battle packets**. It reports 40 executed
moves, 34 HP-removal events, 12 support effects, nine XP/level changes and three
player level-HP updates. All 15 observed Tackle hits fall inside source bounds;
two Tackle misses and two critical hits are observed. All 57 owned-menu input
records are retained as processed confirmations; player move confirmations and
Carl's selected targets agree with native chosen moves/PP decrements/attacks.
Neither raw data nor its stream/Save/ROM/ELF/owner/encryption identities are added
to this publication.

## What happened

Guide recovery is accepted before Guard: Carl33/33 and Donut28/28, status clear,
uses8/40/2/40. Guard's first opponent BRACEs once; Carl continues STRIKE against
its raised Defense. Donut SPARKs twice, then uses the existing native WEAKEN
fallback. Carl's support PP remains40 throughout. Both actors' own stat stages
remain neutral; enemy Attack reductions are real, as are subsequent KO resets.

Guard turn2/frame26594: enemy1's Tackle critical×2 calculates/removes15 HP,
Carl22→7, despite enemy Attack already reduced one stage. Turn4/frame29589:
enemy1 reaches zero; 81 XP each is awarded, Carl levels9→10, and native level
growth adds3 current/maxHP at29916. Enemy3 then removes3 HP, leaving Carl4.
Turn5/frame31258: enemy3's Tackle critical×2 calculates8 damage and removes
the remaining4 HP. Carl0/36, Donut16/28; enemy3 still has7 HP. Native outcome0
is unresolved. This remains STOP90, first incapacitation, not a resolved defeat
or a successful Guard/patrol/opening/Save/cold gate.

Trial's first opponent is SCUTTLER (native Zigzagoon), second is the authored
Wurmple placeholder; Guard's first is GUARD (native Spinda), second SCUTTLER.
Battler labels in the table avoid confusing native species IDs with game names.
Exact HP/PP/support targets and each KO/XP/level timestamp are in the table/JSON.
Enemy HP and native damage are observed RAM values, beyond the precision of the
ordinary HP bars; they are analysis evidence, not new player input authority.

## Damage bounds and first risks

These are integer-order **source-derived ranges**, conditional on a hit, not
observed extra outcomes. No Random(), RNG state, seed, alternative roll, replay
or policy sweep is used. Bounds use observed native stats/types/stages and the
authored, status/item/badge/screen-free matchup. New Game/accepted field flags
contain no badges; neither side has a screen move. They do not predict enemy
move/target choices, critical frequency or altered timing.

At Guard entry (Carl level9/Defense15; Donut level9/Defense13):

| Tackle attacker | Carl normal / critical | Donut normal / critical |
| --- | --- | --- |
| GUARD, level9/Attack15 | 5–7 / 12–15 | 7–9 / 15–18 |
| SCUTTLER, level8/Attack9 | 5–6 / 10–12 | 5–6 / 10–12 |

The table gives hypothetical neutral matchup damage, not legal target choices.
[Opponent source](../../../../../engine/src/battle_controller_opponent.c) fixes
GUARD's turn0 to BRACE, then TACKLE aimed at player-left Carl while both actors
are alive and that patterned move remains available. SCUTTLER uses ordinary AI
and can target either actor. GUARD's absent-Carl/fallback paths are outside this
first-incapacitation contract. Thus the **reachable** turn0 critical ceiling is12
for either actor; later, while both enemies live, it is27 for Carl and12 for
Donut. One critical plus a normal hit has a later Carl ceiling21. Donut's
hypothetical GUARD critical18/two-foe30 are not incoming threats in this scope.
The JSON marks each hypothetical matchup's target reachability. Healing can
delay KOs and consume limited supplies; a Potion rule is not a whole-fight
no-incapacitation proof.

| Risk definition | First observed relevant point |
| --- | --- |
| Trial full next-round two-critical envelope reaches both current HP | turn2 first metric13071: Carl21/30, Donut22/26; source ceiling22 each. No observed single-hit KO exposure. |
| Guard two-critical next-round envelope can KO Carl | turn2 first metric25672, Carl22 versus ceiling27. |
| Guard single remaining enemy critical can KO Carl | frame26594, Carl7; remaining SCUTTLER critical ceiling12. Next observed Carl action-menu A is27136 (turn3). |
| Guard ordinary remaining hit can already KO Carl | frame28017 (turn3), Carl4/33 while SCUTTLER still has its action: normal3–4, critical10–12. It actually targets Donut. Next Carl action-menu A28432 selects Fight. Exposure persists at level10/Carl4 after30396: normal3–4, critical7–9. |
| Guard single-hit exposure for Donut | None observed: reachable critical ceiling12, lowest observed HP16. GUARD's fixed Carl target must not be silently broadened. |

The proposed reachable-turn rule first identifies Carl22 at the next owned action
menu25684 (turn2). Donut never crosses its reachable12-HP threshold.

An envelope crossing mid-turn is not a newly available player action. The next
owned action-menu confirmation is given separately. Entire next-round envelopes
ignore attacks already spent in the current turn; the table does not recast them
as remaining-current-turn threats.

Source chain: [BattlePokemon layout](../../../../../engine/include/pokemon.h),
[CalculateBaseDamage and stage ratios](../../../../../engine/src/pokemon.c),
[critical/STAB/random damage commands](../../../../../engine/src/battle_script_commands.c),
[authored moves](../../../../../engine/src/data/battle_moves.h),
[trainer parties](../../../../../engine/src/data/trainer_parties.h) and
[trainers](../../../../../engine/src/data/trainers.h). Integer order is stage
scaling → power/level/Defense → /50 → physical minimum1 → +2 → critical×2 →
Normal STAB×15/10 →85–100% damage. Rounding matters; it is covered by
[new offline checks](../../../../../scripts/test-c01-retained-analysis-offline.py).

## Existing support and earned healing

BRACE raises its user's Defense one stage. At Guard entry, Carl's BRACE would
reduce GUARD's normal maximum7→6 and SCUTTLER's6→4, at the cost of Carl's turn;
that is a source bound, not a tested alternative. WEAKEN lowers both living
enemy Attack stages; Donut actually applies it four times in Guard. Its first
drop reduces GUARD's normal maximum against Carl7→6 and SCUTTLER's6→4.
Later observed hits3/4 demonstrate lower normal damage, but those individual
rolls do not establish a causal counterfactual. Neither move restores HP.
Criticals ignore lowered attacker Attack and raised defender Defense. At the
terminal native stages, even normal Tackle can remove Carl's remaining4 HP;
additional support does not eliminate the physical minimum/+2/STAB floor.
The authored Warden SLAM exception is scoped to that move/encounter, not Guard
Tackle; no Warden evaluation is launched here.

Carl still has STRIKE2/BRACE40 at STOP; his depleted STRIKE boundary was not
reached. The existing explicit STOP92 remains authoritative when STRIKE0 while
BRACE remains. Do not invent a BRACE/STRUGGLE fallback or claim its admission.
Donut's observed SPARK0→WEAKEN selection is the already defined native fallback.
Healing delays attacks and can prolong exposure; survival and offensive PP must
both be evaluated under any new policy.

The two earned Potions were available during trial. After trial, one was spent
on Donut24→28 (4 HP), immediately before the guide restored both actors for free.
This proves a native field Bag/target/heal demonstration; it was not necessary
for that observed intervening field leg. It proves neither the whole opening's
survival cost nor battle Bag readiness. It is a separate instructional/resource
waste concern: omit mandatory consumption from the proposed survival evaluation,
retain the original demonstration/failure, and review any game/tutorial change
separately. One Potion still remained unused in the failed Guard encounter.

Native battle-use source path:

```text
HandleInputChooseAction (Bag)
  OpenBagAndChooseItem → CB2_BagMenuFromBattle (battle location)
    ItemMenu_UseInBattle → ItemUseInBattle_Medicine
      ChooseMonForInBattleItem → ItemUseCB_Medicine
        ExecuteTableBasedItemEffect → native capped HP update + RemoveBagItem
      battle reshow → CompleteWhenChoseItem → one native item action
```

[Item data/effect](../../../../../engine/src/data/pokemon/item_effects.h) restores
20 HP, capped at maxHP, and cannot revive. [Party code](../../../../../engine/src/party_menu.c)
maps battle UI slots back to party/battler ownership, updates the live battler
when healing is confirmed, and consumes one item on successful effect.
[Battle action order](../../../../../engine/src/battle_main.c) puts item/switch
actions before move actions; the item replaces its actor's move. The HP setter
already runs during the target UI, so do not double-count a second heal when
the later item action executes. Donut has an independent move selection in this
ordinary double battle. No battle Potion action is observed in r2.

Existing readiness binds running Bag/party callbacks, active tasks and fade
completion for **CO_POTION field demonstration**. That does not admit the battle
controller owner, battle Bag location, battle party type/order/target identity,
return/reshow callbacks, or in-battle heal/consume transition. Their exact source/
ELF/ABI binding and positive/negative offline vectors are dependencies for the
[proposed player-choice contract](../../../../floor1/c01-guard-player-choice-proposal.md).
Task existence alone is insufficient, as preserved historical setup failures show.

## Verification limits and retention

Battle fields and logs are sampled at native frame boundaries, not atomic game
transactions. Four actor samples with invalid decoded checksums during native
secure-record updates are excluded from XP reporting; adjacent stable records
restore the prior XP. This is not a new corruption/failure classification and
does not weaken any original assertion. XP setter and later maxHP updates are
reported at their independently observed frames. CPU evidence proves valid
r0–r15/CPSR reads at STOP, SPSR unavailable; raw register values remain private.
It does not prove complete banked context, atomic party writes, rendered KO
animation, or an engine crash. No post-STOP state/Save/cold exists.

Readiness for battle medicine, changed-policy outcome, a human pacing judgment,
and complete FFV1 roundtrip remain unverified. [Export diagnosis/plan](export-plan.md)
uses existing logs/size/receipts only; no encoder or replay is started. Old raw,
partial FFV1 and complete lossy MP4 remain intact. All103 r2 retained entries
and35 r1 preservation pins are rehashed unchanged for this analysis. Existing
retention receipt is immutable; new analysis has a separate local receipt.
Local scratch readback is verified, **independent private backup is not**.
A separately approved private destination with full manifest/readback verification,
or a user-managed copy verified independently, could provide durable retention;
neither is completed. No Library/private upload or attachment backup claim.

R2 remains1 opening process/claim; cumulative C01 opening2/2; cold0/0. Prepared
route unlaunched. Historical C01a actual5/3/1=9/claims6/3/1=10, original V01 six
baseline/four candidate (STOP117 visual8536 beforeB8402), later separately accepted
pair1/1, ordinary recovery5 and exhausted Library five failed uploads/one failed
supported backup download stay unchanged; cause unknown, zero original bytes.
Original oracle/legacy inputs remain missing. C01/G02/human/full-floor gates remain
open. Accepted nine-district plan, engine, old contracts/STOPs and other branches
are unchanged. Draft PR117 review only; no merge, issue116 write or second writer.
