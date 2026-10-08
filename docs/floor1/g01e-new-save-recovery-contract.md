# Separate fresh-save recovery contract — parent review continuation

Prescribed before execution on 8 October 2026. Parent reviewed draft PR91 and
explicitly authorised one fresh-input patrol replay. Its inherited historical
HP equality was a fixture mismatch, not Guard defeat, failed healing or a
demonstrated game regression. Base `b36f750c689029e4fcc9f0a43b73c0c3dca7dccf`,
branch `task/floor1-g01e-new-save-recovery`, sole replacement writer. Original
task remains terminal. No new task/schedule, merge or Warden execution.

## Exact inputs and preserved history

Use only the already manually saved ordinary pending file SHA256
`c11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f`.
Field37,31, healthy levels9/9, XP495/805, PP8/40/2/40, Potion1, SCRAP2,
trial won, patrols/preparation/boss/checkpoint unset. Require the current isolated
game `c643f01c11ec68119b0347b107ee20115131debc`, ROM SHA256
`b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a`.
Hash before and after. Reuse its unchanged compiled ELF/symbols and pin libmGBA
0.10.5/tooling image `4aafe586a8b5c8e5ec720843a42e3afd63f03e62663965d06c1492702c579a54`.

Historical runners/contracts/evidence, all three strategy failures/controller
records and both new recovery failures/STOP files stay byte-identical. New host
starts from the exact repaired observer SHA256
`743ee603601c131046a1c270fe8240e84bd8f9d9aeda99d86d51d3781544163f`.
No game, balance, resources, save ABI, battle strategy, timing or RNG changes.
No state writes or synthetic save. The legacy-input gate is still unavailable;
fresh success never substitutes for original inputs/acceptance.

## Retained trace inspection

The stopped run contains turn HP, player action/target choices, PP, trainers and
owned item values. Howler turns0–6: Carl33→30→24→24→24→21→18, Donut28→28→25→13→10→10→10.
Howler wins at9,220 pilot frames with no incapacitation, awards121 XP per crawler,
and guide recovery restores PP8/40/2/40. Guard turns0–4: Carl36→36→31→23→20,
Donut28→23→18→18→16; foes29/24→19/17→10/14→4/14→0/14. The turn4 decision
has Carl20/36, Donut16/30, PP4/40/0/38 and one Potion. The player target cursor
chooses foe1 until defeated, then foe3. There was no Potion or Guard victory.
The old trace contains no per-hit damage/critical events: attribution of its
larger HP drops to a critical hit or specific enemy target is unverified.

New read-only telemetry records per-frame battle HP transitions with attacker,
target, move, critical multiplier and pending damage. These are observations,
not timing predicates. Complete detailed new logs remain private. No claim that
the original missing save/RNG state has been recovered.

## Single replay and exact intervention

One execution from the pinned new file: unchanged boot/walking/text cadence,
Howler `weaken-first` (single first-turn Donut WEAKEN), guide recovery, then Guard
offence with the same Carl turn4 owned-Potion intervention. Each pilot remains
bounded36,000 frames; no search or repeated combat. Require actual victory
outcome1 and no incapacitation for both. No additional gameplay frame/input
before the prescribed decision; added assertions/telemetry only observe.

At Carl actor0, trainer856, turn4, action menu, require living injured Carl,
living Donut, exactly one owned Potion, action cursor0, maxHP36/30, exact
PP4/40/0/38, first foe defeated and remaining foe alive. Historical current HP
and remaining-foe HP equality are deliberately replaced only in this separate
contract. Capture actual HP/PP before selecting Bag. Same readiness helper,
task/fade checks and receiving item-context/Carl-recipient acknowledgements.

Expected healing is `min(20, maximumHP-currentHP)`: capture expected finalHP
before inputs. If the observed decision is20/36, require36/36 and16HP gain.
Verify healed party state, unchanged Donut HP and PP, exactly one consumption
1→0, then actual return to battle with both party/battle Carl HP at expected
value and unchanged PP. Resume the identical original offence policy.

Require Howler first, flag2137 set/2136 unset, levels10/9 and XP616/926,
Potion1/SCRAP2 and money reward360. After Guard, require flag2136/2137 set,
levels11/10, XP748/1058 (another132 each), Potion0/SCRAP2 and money reward680
total. Preparation/boss/checkpoint remain unset throughout these milestones.
Guide recovery restores HP/status/PP. Guard repeat must not start battle or
change XP/money/resources. Preserve all prior combat/reward/save assertions;
additional exact reward checks do not change input cadence.

Manual Save at Field37,31. Separate cold process from its copied file must
verify the full target state, resolved Guard and Howler repeats with no battle,
duplicate XP/money/rewards or resource changes, then return37,31. Cold repeat
does not Save and its file must remain byte-identical. Native actual captures
bind source/host/route identities. Claims/output directories forbid reuse.

Stop immediately on assertion/input/readiness/budget failure or emulator error;
retain the STOP/claim/logs and do not execute cold or another replay. Diagnosis
and parent direction are needed after a failure. Back up new saves/complete
logs privately through supported Library storage; no ROM, old denied datasets,
keys, missing original saves or raw logs in Git. Publish bounded real captures,
source and verdicts in one focused issue/draft PR on PR91. No broad merge,
visual rollout, full-floor or legacy equivalence claim. Next dependency after
success is parent review before the separately prescribed Warden contract.
