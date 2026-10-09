# Current Guard-first order and travel contract

Parent PR108 inventory review passed and explicitly authorises ONE separate
Guard→guide→Howler→guide route plus its dependent exact native cold check.
Base3e0ace22ce82fcee61a6e945be219dd8849e6ea3; unchanged game5084a1814904f1a43fd999fddf770b221bb53653
/ ROM23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167.
Input is the ordinary pending PR91 Savec11c64559f38680dd21afe693327e703fd4b452776ace69f8e7f1e0b1f3bc67f:
Field37,31, Carl/Donut9/9 XP495/805, full health33/28, PP8/40/2/40,
Potion1/SCRAP2, trial2135 won, patrol2136/2137 pending, friendship counter72.
Native sectors/complete party/count/flags/logical resources must match on boot.

Freeze the complete [route](../../scripts/contracts/f1-g01e-guard-first-current.route),
[cold cadence](../../scripts/contracts/f1-g01e-guard-first-current-cold.route), host,
validator and input before execution. Reuse the historical Guard-first
`pilot offensive 36000` decision code and12-frame readiness-aware cadence twice:
FIGHT, Carl first action; Donut first action until empty then second; engine
STRUGGLE handles exhausted pairs. No new choice, timing/RNG search or retry.
Two permitted trainer identities856 then857, no other battle,100000 total frame
bound and36000 actual battle-bit frames per patrol. Victory/no-incapacity required.

Validate at prescribed stable native milestones. Complete native party identity,
checksum/reencoding,600 bytes/count2, exact300 flags, exact1272 canonical owned
bytes and actual native encoding contexts participate. Source-native callback1,
callback2 and field VBlank gate precedes every actual SaveBlock observer read;
retain accepted state across invalid phases. Field35.0 and Quiet35.1 are the
route domains; arena35.3 is permitted only for the preboss approach/final cold,
never checkpoint35.4. Battle/recovery mutations suspend unchanged-party sampling
until the declared milestone; they cannot replace the walking gate.

Guard reward is132XP each/320money, flag2136 before2137, levels10/9 XP627/937;
Howler adds121XP each/360money, levels11/10 XP748/1058. Source EV yields and
level friendship/stat changes are derived exactly; native HP/PP expenditure is
recorded as actual combat output within legal ranges, with every other byte
reconstructed exactly. Guide must restore full health/zero statuses and exact
PP8/40/2/40 while preserving all other party/resources. Real repeat dialogue at
each patrol proves no battle or repeated XP/money. All optional/preparation/boss/
checkpoint/loop flags remain input-exact, Potion1/SCRAP2 unchanged. No item use.

Measure six EXACT names: guard-out/back, howler-out/back, preboss-out/back.
Keep the historical active-motion latch; phase-gate its native reads before
sampling. Never derive frames as16×steps. Reject missing/duplicate/unknown names
and missing legs. Guard total≤28steps/448activeframes; Howler≤38/608;
Howler→guide→Warden approach≤46/735, preserving original approach endpoint8,7
on35.3 without interacting with Warden. No extra exploration or optional walking.
All stable positions must match route expectations and native legal collision.

Manual Save once at that approach, validate latest14 native sector checksums and
exact saved600 party/count/counter/flags/full logical resources/map/position
against live output; then ONE dependent cold boot with exact native identity
and unchanged disk Save. Stop on FIRST divergence/failure; preserve claim/logs/
captures/private input and snapshots; no dependent cold after failure.

No fresh start, optional content, Warden combat, stairs, deliberate loss, game
changes, integration or broad claim. This closes only CURRENT order/travel if it
passes, never original unavailable legacy acceptance, C01 or full-floor pacing.
Preserve all historical failures/controller records. Back up only this new
private input/log/snapshot/Save package through supported private Library;
exclude ROMs/executables/credentials/denied original datasets from all uploads.
Next dependency: parent review → explicit stack integration authority → stagedV01.
