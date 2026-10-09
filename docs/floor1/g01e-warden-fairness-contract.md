# Authored Warden fairness candidate — prespecified contract

Parent review of PR97 accepts the narrow two-response design gap and authorises
this candidate on 8 October2026. Base ed519a05e34f47bf45fa150aa5e456b9e1028926;
branch task/floor1-g01e-warden-fairness, sole writer. No broad merge/new task.
All56 earlier remote heads, accepted plan, prior contracts/controllers/evidence
and private inputs are preserved. Original reconstructed-input Warden loss1/1
stays separate from new candidate attempts, three patrol strategies and two
initial recovery failures. PR97 is open/draft/unmerged; mainb694 unchanged.

## Candidate scope, frozen before implementation

Only actual authored trainer encounters858/859, enemy-side Loudred SLAM:
effective power65→45 and noncritical. Shared MOVE_DCC_SLAM remains power65;
stock/global critical behavior and other attackers/moves/encounters unchanged.
Only the authored enemy helper Whismur in858/859: TACKLE targets Donut on
turn0 and every second subsequent WIND UP, meaning turns0,4,8,… (zero-based).
On all other turns it rests, spending no PP, applying no damage/status/buff.
Do not substitute WIND UP/BRACE/a different move as a fake rest. A clean
encounter-local action skip is allowed; otherwise checkpoint infeasibility.
Warden WIND UP/SLAM cadence and Carl-first targeting otherwise stay unchanged.
Native cues must communicate alternating attacks, helper cadence and dependable
BRACE/WEAKEN for SLAM. No duo stats/HP/PP, enemy levels/HP, preparation advantage,
held items, resources/rewards, progression/flags, maps/art or save ABI changes.

Before any emulator battle: implement pure membership/side/species/move guards,
test actual member and nonmember combinations plus critical/cadence isolation;
verify full damage and cleanup envelopes for BOTH fixed responses from the
reviewed save, including ordinary maxima, critical SLAM suppression and retained
stock helper/player critical risk. Parent's16+12 offensive SLAM and6+4+4+4
fortify estimates are hypotheses until calculated. No roll/seed/timing search.
Commit exact source, regenerate a fresh isolated engine build with pinned
toolchain, keep full logs, record ROM/ELF/host/route hashes before execution.

## Frozen executions, exact ordinary inputs and stop rules

Seed SHA256026c16feccd0a1741ff0c3ec077e7272fc6ee43bf0e4fa12ab8953c50523220a.
Each route uses its own byte-identical copy and exclusive claim/directory.
Cold Field37,31: Carl/Donut11/10, XP748/1058, HP38/30 restored/status0,
PP8/40/2/40, held items0, Potion0/SCRAP2, trial/patrol2135/2136/2137 set,
preparation46/boss47/checkpoint48/loop49 and trainer2138/2139 unset. Require
same state at Warden arrival8,7 after ordinary authored path and normal native
interaction; no earlier battle. Preserve exact reviewed12-frame ordinary action
cadence, readiness-aware menus/text, no input dependent on damage telemetry.

Unprepared offensive: Carl STRIKE at living Warden then living helper; Donut
SPARK for both owned uses, then WEAKEN. Use inherited default target behavior
when a foe is absent, not an adaptive heal/attack policy. Unprepared fortify:
Carl BRACE/Donut WEAKEN for turns0/1/2, then identical offensive choices/PP
fallback. Exactly one attempt per frozen route, bound30,000 frames entering,
inside and leaving battle; never frame30,001. Require trainer858, levels12/9,
HP42/30, four battlers, genuine outcome1, no incapacitation, both contributions,
actual support stages and helper cadence/target/no-buff/no-PP-cost rest evidence.

Execute offensive first, then its persistence; fortify second then persistence.
If any route fails, preserve trace/STOP/claim/captures and do not execute that
route's dependent cold/repeat. Diagnose before any further execution; no retry,
retiming, seed search, assertion relaxation, policy/resource/balance change.
Complete independent static/documentation work; additional combat awaits parent
direction if failure invalidates the candidate hypothesis.

Require unprepared first-clear XP226 each (Carl974/level12, Donut1284/level10),
money+360, boss47/trainer2138 newly set, preparation46/trainer2139 unset; full
inventory unchanged. Capture actual wounded HP/status/PP, no guide heal after
victory. Resolved repeat must award/change nothing and begin no battle.
Actual staircaseNO: acknowledged0, remain35.3/12,10, checkpoint48 unset.
Actual YES: acknowledged1, checkpoint48 newly set, real35.4/4,4 transition;
read opening-checkpoint text at8,6, ordinary manual Save, all observed resources
unchanged. Separate cold process from real Save verifies exact observed wounded
duo/resources/XP/money/flags, resolved repeat/stairs re-entry and unchanged save
bytes. Keep first-clear/save/repeat/cold assertions from PR95 contract.

Prepared859 is a separate ordinary preparation route from the same seed: walk
to workshop, craft one Charge from owned2 SCRAP, decline then accept its cache
blast, consume Charge and gain one Super Potion/preparation46, verify repeat
idempotence; do not use Super Potion. Ordinary route back to Warden; require
trainer859/foe levels10,8 and source-derived exact HP, same duo/PP. Use fixed
offensive response, own exclusive claim30,000-frame bound and victory checks.
Verify optional advantage through reduced party stats, exact prepared XP/money,
prepared trainer2139 versus unprepared2138, preparation/resource preservation,
resolved repeat and actual stairs/Save/cold. Prepared success never substitutes
for either unprepared result. No additional patrol/recovery combat.

## Durable evidence and reporting

Focused member/nonmember tests plus real emulator assertions/native before and
after captures bind full source/build/host/route/save identities. Record actual
WIND UP/SLAM and helper rest/attack motion/cadence frames, not generated concepts
or native art candidates. Reuse unchanged original loss image only as labelled
before; capture new actual candidate after. No visual rollout/fullFloor1 claim.
Back up complete new safe build/runtime logs, claims, saves, traces, captures and
STOP if needed through supported private Library, never Git saves/ROMs/keys or
old denied datasets. Missing original legacy input acceptance remains missing.
Publish reviewed focused issue/draft PR stacked on PR97, commit/push; no merge.
Report implemented/compiled/runtime-tested/merged separately, counts separated,
precise source/ROM and dependency-ready checkpoint with remaining gates.
