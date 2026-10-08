# Authored Warden fairness candidate — two unprepared passes, prepared stop

Implemented and freshly compiled; both frozen unprepared first-clear/Save/cold
pairs passed. Prepared combat won, but its post-victory exact-duo gate failed
after actual staircase NO. **Global STOP remains active. Prepared YES, manual
Save and cold are unverified.** No retry, assertion relaxation or further emulator
execution followed the stop. This increment is unmerged and awaits parent review.

The [prespecified contract](../../../../floor1/g01e-warden-fairness-contract.md)
was committed at `4034311c58c76a9a9d7ed68b6188bfd1264a6a3b` before implementation.
Base is draft PR97, `ed519a05e34f47bf45fa150aa5e456b9e1028926`.
Only normal authored trainer858/859 enemy Loudred SLAM uses effective power45
and critical multiplier1. The shared move remains65 and the complete stock
critical body is unchanged behind the guard. Authored helper TACKLE targets
Donut on turns0/4/8,…; other turns advance the action queue without a move,
PP cost, damage, status or buff. Native cues explain cadence/support. Duo,
enemy party levels/HP, preparation advantage, rewards, flags and save ABI stay
unchanged. No new art, geometry, generated concepts or visual rollout.

## Exact identities and static/build gate

Game source: `5084a1814904f1a43fd999fddf770b221bb53653`.
ROM SHA256: `23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167`.
ELF SHA256: `cafc512d915d01ff1b598b1a7050261f5990bc50fc0faed533b0ec6d7309336b`.
Frozen host/runner source: `a31355a22267e1e8b309adde7e59206cd3e43f3a`.
Generated host SHA256: `b2030b4da242f14d9993cbb00493dd9bb02c746fc12ce75cd994b11b760f0c71`.
All three compiled hosts/routes/claims were frozen before the first emulator.
[Build pins and log hashes](build-identity.json), [all route identities and actual trace review](runtime-evidence.json).

Fresh isolated git archive, pinned Emerald731ad5/agbccda598 and verified installed
toolchain; all engine objects rebuilt. Initial e503283 compile stopped on a missing
`battle_setup.h` declaration before any emulator; fixed in5084a1 and preserved
separately. Final build exit0. Host compiled with Wall/Wextra/Werror.
Exact-header C checks cover65,536 trainers and256 cadence turns, member/nonmember,
side/species/move and wild/link/frontier exclusions. Shared moves, original stock
crit body, parties/duo/save definitions are byte-identical to the prior game.
[Static results](guard-envelope-tests.log), [full envelopes](envelopes.json),
[pre-execution interpretation](pre-execution.md).

Ordinary offensive SLAM maxima16+12 and fortify6+4+4+4 include full cleanup:
latest ordinary cleanup turns6/9, at most7 owned STRIKEs, two owned SPARKs.
Helper normal totals11/14 leave Donut at least19/16HP. Stock helper/player
criticals remain; the envelope explicitly preserves their risk rather than
claiming all possible RNG trajectories. No seed/roll/timing/policy search.

## Actual executions

Every case used a separate byte-identical copy of the reviewed ordinary Save
`026c16feccd0a1741ff0c3ec077e7272fc6ee43bf0e4fa12ab8953c50523220a`:
Field37,31; Carl/Donut11/10, XP748/1058, restored38/30HP, PP8/40/2/40,
Potion0/SCRAP2, patrols won, boss/preparation/checkpoint unset. Normal routes and
readiness-aware native inputs only, inherited12-frame controller cadence.
One exclusive battle per frozen response, every battle frame wrapped by30,000
limit; no frame30,001. Read-only sampling added no emulator frames or decisions.

| Case | Battle frames / attempts | First-clear assertions | Cold assertions | Observed result |
| --- | --- | --- | --- | --- |
| Unprepared offensive858 | 8,669 / 1 | 204 pass | 132 pass | Complete victory/repeat/NO/YES/Save/cold |
| Unprepared fortify858 | 13,733 / 1 | 204 pass | 132 pass | Complete victory/repeat/NO/YES/Save/cold |
| Prepared offensive859 | 6,952 / 1 | 193 completed, exit53 | Not executed | Victory/repeat/NO passed; exact-duo comparison stopped |

Both members dealt real damage in all three battles: Carl/Donut45/27,
51/21 and36/28 actual enemy HP respectively. Offensive SLAM13+10;
fortify5+3+4, with Carl Defense rising6→7→8→9 during the prescribed three
BRACE turns; prepared SLAM12. All observed SLAM critical multipliers1.
Stock Donut SPARK critical multiplier2 occurred in offensive/prepared, demonstrating
that the local guard does not suppress player criticals. Helper hit Donut on
turn0 (6), fortify turns0/4 (5/3), prepared turn0 (6); rest PP unchanged and
no incidental positive stat buffs were checked by the host. Fortify helper was
knocked out before its turn8 action; source/static cadence covers later turns.

Unprepared rewards exactly226XP each/money360; Carl12/974, Donut10/1284,
money4360, full inventory unchanged. Boss47/trainer2138 set, preparation46/
trainer2139 unset. Resolved repeat awarded nothing and started no battle.
Actual staircase NO returned0, retained35.3/12,10/checkpoint unset; YES returned1,
set checkpoint48, transitioned to35.4/4,4. Native checkpoint review, manual
Save and separate cold repeated real staircase/reward/resource checks. No heal.

| Persisted unprepared case | Actual HP / PP | Exact Save SHA256, identical after cold |
| --- | --- | --- |
| Offensive | 18/41,24/30; 3/40/0/37 | `6ab1357be75bcf4f41fe8064e8df590876348e28fe78e557f28ff90648246386` |
| Fortify | 29/41,22/30; 2/37/0/33 | `7092ce7704a94158046195581e6b9e72dfb640005c46dea20efc83ff3638badf` |

Final saved position35.4/8,6; statuses0, held items0, all observed resources
and exact save bytes persisted. Prepared ordinary owned2SCRAP→Charge craft,
cache decline/accept and repeat passed; preparation46 set, Charge consumed,
one unused Super Potion. Actual foes36/28HP, levels10/8; XP192 each andmoney320
passed (Carl11/940, Donut10/1250, money4320, trainer2139 set/2138 unset).
It won with26/38,24/30HP andPP4/40/0/38. The disk input remains unchanged026…:
**that file is an input copy, not a post-prepared Save.**

## Prepared stop diagnosis and next dependency

Error: `Post-victory duo/inventory changed; STOP`, exit53,41 error bytes.
[Preserved stop](prepared-STOP.json). The full inventory check passed; the failure
is the subsequent exact200-byte party comparison in the inherited preservation
observer. Its first resolved-repeat comparison passed, then the comparison after
staircase NO failed. Logged HP/status/PP/levels/XP/equipment stayed identical.
The failure is therefore after genuine victory/reward and actual NO, not a
combat loss or preparation-resource substitution.

The stock walking path calls `UpdateFriendshipStepCounter` every ordinary step
and may adjust friendship every128 steps; this updates encrypted party data and
checksum even without a battle or resource change. Seed counter24 and the longer
prepared route make this a plausible source explanation. It is **not proven**:
the frozen observer did not log mismatch offsets or both200-byte buffers, and
the failed process ended before Save. The retained trace cannot identify the
changed field retrospectively. No assertion was relaxed and no logger/policy/
route was changed after failure. Parent review must decide a separately scoped
diagnostic that records exact mismatched fields while preserving the gate and
this failed claim before any further execution. Prepared persistence remains open.

## Actual native before/after and motion evidence

Before remains the separately labelled [original c643 critical-loss capture](../warden-first-clear/pilot-carl-down.png);
it is historical evidence, not a candidate execution. Candidate after:
[offensive victory](offensive-warden-result.png), [fortify support turn3](fortify-turn-03.png),
[offensive manual-save position](offensive-saved.png),
[prepared cache](prepared-cache-blasted-00-00.png),
[prepared real NO before stop](prepared-stairs-no-cancelled-00-00.png).
Native cues: [helper cadence](offensive-cue-006.png), [rest/support](offensive-cue-008.png).
Actual motion: [WIND UP](offensive-wind-up.gif), [SLAM](offensive-slam.gif).
Clips assemble consecutive native frames sampled every4 actual frames at70ms
per captured image; no generated/interpolated/replaced frames. This is sampled
battle motion, not a human-paced walkthrough. [All321 native capture identities
and two clip source lists](captures.json) bind source, ROM and frame hashes.

## History, retention and limits

All56 prior remote branch heads are unchanged; main remainsb694da1, PR97 remains
open/draft/unmerged. [Reconciliation](reconciliation.json). Original c643/b025
Warden loss1/1, three historical patrol strategy failures, two initial replacement
recovery failures and their controllers remain distinct and unaltered. Candidate
counts: three battles, three combat victories, zero combat losses, two completed
first-clear/cold pairs, one post-victory route stop. Successful pairs672 emulator
assertions; failed prepared193 completed assertions,865 total across five processes.

Complete new claims/routes/observer/build logs/traces/captures/STOP and necessary
real saves are retained privately in Library; no saves, ROMs, executables or keys
are committed. The private package excludes ROMs, executables, keys and old
denied raw datasets.
Original legacy saves/raw logs remain missing; original legacy-input gate is
unrestored. Fresh ordinary inputs never substitute for legacy acceptance.
No merge, wholeFloor1/finalT/human-pacing/reverse-order/V01 acceptance. Parent
review of the exact prepared stop is the next dependency; no additional execution.
