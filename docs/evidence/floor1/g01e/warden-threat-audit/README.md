# Warden 858 threat/action audit — read-only, no second attempt

Parent review of PR95 confirmed one genuine loss and authorised this bounded
source/retained-trace audit. Base `e0d75cc339548a9d57a5ecc9b2e80036deda6f50`;
branch `task/floor1-g01e-warden-threat-audit`. **Current reconstructed-input Warden
attempts/failures remain 1/1.** The three historical patrol strategy failures and
two initial replacement recovery failures remain separate records. No emulator
process, new battle, timing/seed/RNG search, policy search or balance change.

Decision: **do not prescribe a second unprepared execution yet.** The documented
strike-fast response is conditionally viable, but ordinary opening helper
targeting can exhaust its entire survival margin before its first possible
noncritical Warden kill. Three support turns improve ordinary-hit survival but
delay that kill by three turns and do not protect against critical SLAM. This is
a narrow unresolved threat-budget/two-response design gap, not proof that every
unprepared strategy is impossible. Parent design review is the next dependency.

## Frozen identities and method

- Game source `c643f01c11ec68119b0347b107ee20115131debc`.
- Exact ROM SHA256 `b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a`.
- Reviewed ordinary Save SHA256 `026c16feccd0a1741ff0c3ec077e7272fc6ee43bf0e4fa12ab8953c50523220a`.
- Retained PR95 trace SHA256 `598e6f5e7f3675e3d65d7a775e56af61671a7e0827463925800e7d9900046ba2`.
- Runtime contract/host remains `7197e785a704e216c9f4a5429ae6cb4fb9302703`.

[Reproducible offline audit](../../../../../scripts/audit-f1-g01e-warden-threat.py)
reads only the exact local save, pinned ROM metadata, symbols and retained trace.
It checks newest complete save-slot headers, the two relevant sector checksums,
plaintext party stats and badge flags, without decrypting secure save fields or
printing keys/OT IDs. Enemy stats come from the compiled trainer/name/nature/
species tables and pinned `CreateNPCTrainerParty`/`CalculateMonStats`. All 18
source files read are byte-equal to the pinned game commit. The output is a safe
derived summary, not a replacement save or a synthetic runtime result.

The damage calculation uses source integer truncation, critical stage rules,
spread reduction, STAB and the 85–100% damage endpoints. It never calls an RNG,
reads a seed, selects a roll or replays an alternative trajectory. Every one of
the retained **17 actual HP transitions** falls inside the source envelope.
Stages/PP inferred from source and completed choices are labelled separately
from observed HP/damage and sampled Warden Attack stages in [analysis.json](analysis.json).
An initial offline ABI-stride guard and a mistaken expected-hit-count guard
stopped during authoring; correcting those guards caused no game execution or
additional battle failure. No prior gameplay assertion was changed.

Reproduce with the already retained private inputs:

```sh
python3 scripts/audit-f1-g01e-warden-threat.py \
  --save artifacts/floor1/new-save-recovery/runtime/patrol.sav \
  --rom artifacts/floor1/recovery/current-build/source/engine/pokeemerald.gba \
  --symbols artifacts/floor1/warden-first-clear/runtime/game.sym \
  --trace artifacts/floor1/warden-first-clear/runtime/first-clear/replay.log
```

## Exact matchup and action order

| Actor | Level | HP | Attack | Defense | Speed | Sp. Attack | Sp. Defense |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Carl / Machop | 11 | 38 | 26 | 18 | 14 | 12 | 14 |
| Donut / Meowth | 10 | 30 | 16 | 14 | 25 | 15 | 15 |
| Warden / Loudred | 12 | 42 | 22 | 15 | 16 | 22 | 15 |
| Helper / Whismur | 9 | 30 | 14 | 9 | 10 | 14 | 9 |

Player stats are read from the exact saved party tail; enemy stats are source
derived, with zero IVs/EVs and neutral Hardy/Bashful natures. No held items,
status, badge boosts, weather, screens or type advantages enter this matchup.
Reviewed PP is Carl8/40 and Donut2/40; Potion0, SCRAP2. Trial/both patrols are
cleared, preparation/boss/checkpoint unset. Recovery/save identity stays the PR93
claim; this audit adds no runtime persistence claim.

All actions have priority0. Source order is **Donut → Warden → Carl → helper**,
with no speed tie. Consequently BRACE selected on a SLAM turn acts after SLAM;
BRACE on the preceding WIND UP turn applies before the next attack. WEAKEN acts
before both foes and lowers each Attack one stage; WIND UP subsequently raises
the Warden one stage. BRACE raises Carl Defense one stage and is not a block.

Warden alternates WIND UP on even turns and SLAM on odd turns, targets Carl
while active and switches to Donut after Carl is absent. Helper TACKLE uses
ordinary doubles AI. The double-battle script discourages hitting its ally;
healthy neutral player targets retain equal scores and tie selection uses RNG.
The helper target is not controlled by the player or inherited across policies.

STRIKE is Normal40/100%-accuracy, **without STAB on Fighting Carl**. SPARK is
Psychic50/always-hit, without STAB on Normal Donut, and hits both live foes at
half base damage before the final +2. WEAKEN is100%-accuracy/both foes; BRACE is
self-target. SLAM is Normal65/100%-accuracy with Warden STAB. TACKLE is
Normal35/95%-accuracy with helper STAB. A TACKLE miss is possible; relying on one
is not a fixed threat response. Ordinary damaging moves can critically hit
(base critical denominator16); no critical-blocking ability applies here.

Source anchors: [party/init](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/crawler.c#L18),
[trainer party](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/data/trainer_parties.h#L13),
[enemy creation](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_main.c#L1960),
[speed order](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_main.c#L4595),
[authored target/pattern](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_controller_opponent.c#L1571),
[doubles target scoring](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_ai_script_commands.c#L450),
[move data](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/data/battle_moves.h#L4619).

## Retained single fortify attempt

Turns are zero-based. End stages below are source inferred (0 means neutral).
The HP pairs and damaging-hit targets are actual retained observations.

| Turn | Duo selections | Warden action; helper target | End Carl DEF / Warden ATK / helper ATK | End observed Carl/Donut HP | End observed Warden/helper HP |
| --- | --- | --- | --- | --- | --- |
| 0 | BRACE / WEAKEN | WIND UP; Donut | +1 / 0 / −1 | 38/24 | 42/30 |
| 1 | BRACE / WEAKEN | SLAM Carl7; Carl3 | +2 / −1 / −2 | 28/24 | 42/30 |
| 2 | BRACE / WEAKEN | WIND UP; Donut3 | +3 / −1 / −3 | 28/21 | 42/30 |
| 3 | STRIKE / SPARK | SLAM Carl5; Donut3 | +3 / −1 / −3 | 23/18 | 30/24 |
| 4 | STRIKE / SPARK | WIND UP; Donut3 | +3 / 0 / −3 | 23/15 | 17/18 |
| 5 | STRIKE selected, not executed / WEAKEN | critical SLAM Carl28; Donut3 | +3 / −1 / −4 | 0/12 | 17/18 |
| 6 | Carl absent / WEAKEN | WIND UP; Donut3 | +3 / −1 / −5 | 0/9 | 17/18 |
| 7 | Carl absent / WEAKEN | SLAM Donut11; helper never acts | +3 / −2 / −6 | 0/0 | 17/18 |

Source-inferred executed costs: Carl2 STRIKE/3 BRACE → PP6/37; Donut2 SPARK/
6 WEAKEN → PP0/34; Warden4 WIND UP/4 SLAM → PP36/36; helper7 TACKLE → PP28.
The unexecuted turn5 STRIKE costs no PP, and the helper's final action is
cancelled after both protagonists faint. The final PP vector is an inference
from this trace/source, not a new final RAM assertion. The existing image at
the next Donut menu independently shows SPARK exhausted and WEAKEN36 before
the last two WEAKEN executions. No manual Save followed the loss.

At frame13923, multiplier2/pending28 took Carl23→0 before his chosen STRIKE.
Source critical damage ignores negative attacker Attack and positive defender
Defense stages. With neutral effective Attack22/Defense18 the resulting SLAM
envelope is28–33, encompassing28. This is the previously reviewed actual cause.
No reinterpreted selection, extra resource or hypothetical favourable roll
changes that loss. Actual outcome2; whole-battle12,875 frames; STOP retained.

## Damage and kill-turn comparison

All envelopes assume the displayed neutral matchup and successful normal hit;
critical rows explicitly say so. Kill-turn estimates assume both protagonists
remain active, actions resolve, both foes remain alive during the two SPARKs,
and no player critical hit. They are algebraic bounds, not executed battles.

| Action / state | Damage |
| --- | ---: |
| Carl STRIKE → Warden | 8–10 |
| Carl STRIKE → Warden, critical | 17–20 |
| Carl STRIKE → helper | 12–15 |
| Donut SPARK → Warden / helper, two live foes | 4–5 / 5–7 |
| Donut SPARK → Warden, critical / two live foes | 8–10 |
| Fortify turn1 SLAM, Warden−1 / Carl+1 DEF | 7–9 |
| Fortify turn3/5 ordinary SLAM, Warden−1 / Carl+3 DEF | 5–6 |
| Fortify critical SLAM, same raised/lowered stages ignored | 28–33 |
| Strike-fast turn1 SLAM, Warden+1 / Carl0 DEF | 20–24 |
| Strike-fast turn1 critical SLAM, positive Attack retained | 40–48 |
| Strike-fast turn3 SLAM after PP-aware WEAKEN, Warden0 / Carl0 DEF | 13–16 |
| Strike-fast turn3 critical SLAM | 28–33 |
| Unweakened helper TACKLE → Carl | 5–6 |

The calculation follows [base/stage/spread order](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/pokemon.c#L3237),
[critical calculation and multiplier](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_script_commands.c#L1253),
[STAB](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_script_commands.c#L1356),
and [damage endpoints](https://github.com/12nuskek/DungeonCrawlerCarlemon/blob/c643f01c11ec68119b0347b107ee20115131debc/engine/src/battle_script_commands.c#L1639).

**Strike-fast comparison:** existing offensive choices mean Carl STRIKE at
Warden each turn; Donut SPARK twice, then WEAKEN each turn. The fallback matters:
it lowers Warden Attack before its second SLAM rather than leaving it at+2.
Warden cumulative damage through turns0…4 is12–15,24–30,32–40,40–50,48–60.
The Warden's42HP exceeds the maximum40 through turn2. First possible ordinary
kill is Carl's turn3 STRIKE, guaranteed by turn4 only if Carl remains active.
Warden speed16 beats Carl14, so both turn1 and turn3 SLAM occur first.

Even with no enemy criticals, those SLAMs total33–40. One successful helper
TACKLE on Carl in turn0 or1 contributes at least5: **33+5≥38**, guaranteeing
Carl's incapacitation before that fourth STRIKE when no player critical kills
earlier. The source allows either protagonist to be the helper's target. Even
if both opening TACKLEs hit Donut, the damage/target margin remains small; later
helper hits can close it. A first critical SLAM40–48 is independently lethal
from Carl's full38HP. Player criticals, helper misses and favourable targets can
permit wins, but no such trajectory is selected, simulated or counted here.
This is why another seed-dependent offensive attempt is not well supported as
the next fair/no-incapacity acceptance contract.

**Three support turns:** the same offensive kill envelope moves to turns3…7,
so ordinary Warden clear is earliest turn6/latest turn7, with SLAMs on1/3/5
and potentially7. BRACE/WEAKEN plainly lower ordinary damage. Actual two early
helper hits and two SLAMs left Carl23HP at turn5; the critical envelope28–33 then
exceeded that remaining health regardless of its precise damage endpoint.
The observed loss is preserved. This does not invalidate historical segmented
fortify wins or establish that every support variant fails; those inputs and
executions cannot be transferred to this fresh save.

If Warden is removed and Carl survives, helper cleanup would need two ordinary
STRIKEs after the two SPARKs (helper16–20HP, STRIKE12–15). PP8 can cover that:
strike-fast4–5 Warden hits plus2 helper hits; fortify4–5 plus2 as well. Thus
Carl's stock of offensive PP is not the demonstrated primary blocker. Donut's
two SPARKs provide useful damage but force an early support fallback; her
remaining40 WEAKEN uses are not replacement offensive damage. Post-clear level
growth and rewards are deliberately not simulated or accepted here.

## Narrow design gap and evidence-led next action

The accepted plan requires an achievable optional-preparation skip, two
reasonable boss responses and understandable useful support: [combat section](../../../../floor1/accepted-plan.md#preparation-should-change-the-fight-without-becoming-a-hidden-requirement)
and [fairness gate](../../../../floor1/accepted-plan.md#how-to-judge-the-second-iteration).
The actual prompt promises “BRACE softens the hit. WEAKEN offsets its rising
attack. Or strike fast.” Normal damage supports the first two statements;
critical bypass is an uncommunicated exception. Strike-fast's ordinary
kill-before-survival deadline depends on helper targeting outside that cue.

**Design inference:** the exact unprepared Warden threat/action budget does not
yet support the advertised two-response acceptance with a reasonable ordinary
mistake margin. This finding is confined to trainer858, this duo/save and these
two documented responses. It is not a universal impossibility or a broad
balance verdict. There is no new fixed second response, executable route or
permission to run one in this package.

Next dependency: parent review/authorisation of a narrow Warden design increment
that resolves (1) the offensive kill deadline versus ordinary helper pressure
and (2) the support cue versus critical bypass. Before any implementation,
prespecify the resulting one-variable change, both fixed response sequences,
an ordinary-hit survival/resource budget and treatment of critical SLAM.
Do not remove criticals or inflate stats silently, make preparation mandatory,
or let a prepared victory close unprepared acceptance. Runtime contracts must
still require exact trainer/input identity, genuine victory, no incapacitation,
the whole-battle30,000-frame bound, first-clear reward/flag idempotence and real
stairs/Save/cold checks; any state/error/budget/victory failure must STOP with no
retiming, RNG search or automatic retry. Those are future gates, not audit passes.

## Preserved evidence, publication and limits

Nonvisual audit: new screenshots **N/A**. Relevant existing actual captures are
linked unchanged with their original source7197e785/gamec643/ROMb025 identities:
[pre-attempt cold](../warden-first-clear/cold.png),
[trainer858 intro](../warden-first-clear/warden-start.png),
[Carl fainted/Donut menu](../warden-first-clear/pilot-carl-down.png).
[Original capture register](../warden-first-clear/captures.json) and
[private trace/save retention](../warden-first-clear/private-retention.json)
remain authoritative; no new ROM/save/raw trace upload is needed.

All55 prior remote branch heads and PR95/PR93 stack identities reconciled;
mainb694 and patrol72e08 stay unchanged. PR95 remains draft/open/unmerged at
e0d75cc3, based on PR93/1263d8b9. CI returned zero PR-triggered runs at PR95's
head, not a CI pass. Previous evidence/controller/STOP files and accepted plan
are preserved. [Reconciliation](reconciliation.json) records the scoped check.

Implemented and executed offline audit; no new game/host compilation or emulator
test is necessary for these documentation/arithmetic changes. Unprepared clear,
prepared route, two accepted responses, repeat/rewards/stairs/persistence, human
pacing, full opening/Floor1/V01 and original legacy equivalence remain open.
Reconstructed save and complete prior trace are retained privately as before;
the original deleted-workspace legacy inputs remain missing. Nothing merged.
