# Exact-field diagnosis — one noncombat resource-encoding stop

**One probe stopped; intended staircase NO and friendship boundary were not
reached.** Added raw-resource guard stopped at frame2236 during a normal warp.
All600 party bytes stayed exact, both native member checksums/re-encoding valid.
Friendship deltas0, counter66→72. Original prepared changed field remains
unidentified. No retry, further emulator frame, prepared replay, battle, Save,
preservation relaxation or friendship exception followed this stop.

Parent accepted PR99's two bounded unprepared pairs and encounter-local guards.
This increment implemented/compiled a separate read-only exact-field observer
and offline decoder, then executed one exclusive24,000-frame probe. Its intended
mechanism question remains unresolved. [Prespecified contract](../../../../floor1/g01e-party-preservation-diagnosis-contract.md),
[frozen pre-execution identities](pre-execution.md), [safe exact findings](findings.json),
[actual stop summary](summary.json), [preserved STOP](STOP.json).

## Inspect first, preserve the missing original field

Retained private PR99 package SHAce1fed73…e0878 and local prepared observer/log
were inspected before implementation. No original before/after party buffers,
state capture or mismatch offsets exist. The strict historical200-byte block,
prepared claim/STOP/trace and all prior controllers/evidence are unchanged.
Even a future new walking delta would demonstrate a mechanism, not identify
the missing original buffers. No original legacy-input acceptance is restored.

## Actual new probe and its exact-field findings

Completed controller-authored offensive unprepared Save
`6ab1357be75bcf4f41fe8064e8df590876348e28fe78e557f28ff90648246386`,
cold checkpoint35.4/8,6, Carl12/Donut10, HP18/24, XP974/1284, PP3/40/0/37,
statuses/equipment0, money4360, Potion0/SCRAP2, boss/checkpoint won and preparation
unset. Native Save sector/party checksums, recorded state and exact encoding
validate offline. The save choice was fixed before the route; no seed screening.

At frame2044, ready controls and exact state passed; private buffers anchored,
historical preservation gate retained verbatim, same strict200 bytes additionally
compared every armed frame. Remaining400 party bytes, owned-resource region and
flags were also compared. Frozen normal route: checkpoint arrival warp back to
boss room, actual stairsNO, four short legal row round trips. At frame2236, first
warp map35.3/4,3, the added resource comparison stopped before the next frame.
Exit57,21 completed emulator assertions,192 armed per-frame checks, six natural
counter transitions66→72, zero battle frames/attempts. The saved input copy is
byte-identical; no Save was performed. These counts are separate from the original
Warden loss1/1, candidate three victories/two accepted Save-cold pairs/one prepared
route stop, historical patrol/recovery failures and the offline decoding checks.

Private captures include anchor, last stable frame2235 and stop frame2236:
600 party bytes each, owned region1272 bytes each, flags300 bytes each, party
counts, position and exact counter observations. Complete private decoding covers
identity/header/flags, all four native substructs, padding, XP/items/moves/PP,
friendship/EVs/origin/IVs/ribbons and unencrypted status/level/HP/stats. Public
findings expose only bounded field changes and validity/invariance booleans.

| Field group | Actual before/after finding |
| --- | --- |
| Strict duo200 / complete party600 | Byte-identical; no decoded field differences |
| Native member checksums / XOR round-trip | Both valid before, stable and after |
| Carl / Donut friendship | Both delta0; no mechanism demonstrated |
| Remaining400 party bytes / party count / flags | Exact, count2 |
| Natural friendship counter | Six single-step increments66→72; no127→0 boundary |
| Raw owned-resource region | 378 changed bytes confined to encoded money, coins and186 bag quantity words |
| Unencoded owned-region bytes / all bag item IDs | Exact |
| Source encoding pattern | All186 quantities and coins share one XOR difference; money low16 agrees |
| Independently decoded resource invariance | Unproved: old/new resource encoding context was not retained |
| Actual staircase NO / friendship boundary | Unreached |

The added raw-resource guard was too broad for map transitions. Pinned
`overworld.c:LoadMapInStepsLocal` calls `ResetMirageTowerAndSaveBlockPtrs`, which
calls `MoveSaveBlocks_ResetHeap`. That moves SaveBlocks and re-encodes encrypted
data under a fresh native key. `load_save.c`/`item.c` apply it to money/coins/all
bag quantities, precisely the changed field locations and common XOR pattern.
This explains the source-observer mismatch pattern without altering the strict
party gate. The actual old/new resource keys were not captured; assuming unchanged
balances to infer them would be circular. No such inference is used as acceptance,
and no full decoded resource-invariance claim is made. [Offline verification](offline-analysis.log).

## Source/build, actual native captures and review

Game source unchanged: `5084a1814904f1a43fd999fddf770b221bb53653`.
Same accepted isolated ROM SHA256:
`23c77a0c3eb86bac74aee25b189c147f172601d29403cbd485f665aec705b167`.
This increment recompiles host tooling only; no new game-build claim.
Frozen host source `a9e730744fe8505ae53b6c4dae2a62032c27a8ba`, generated host
SHA256`5fb1277ec61c000eccf901fb029871c62f6415f88d3fe685d0e8e5f984dc6354`.
Actual execution source `5bc8b2b203638c9a65290bb9e57ea4e49cabfe81`.
Route SHA256`efad1580ea49f49bd215868aec53f4f9313face05ef6d563bf32856d779a0f69`.
Initial host compilee2944c stopped on inherited variable-name collision before
any emulator; corrected separately, full compiler/source logs retained.
Corrected host compiled Wall/Wextra/Werror, exit0. Decoder tests use only real
retained offensive/fortify saves; all14 native sector checksums, actual members,
source-derived24 permutations and exact party round-trip pass, no synthetic saves.

Actual native anchor frame2044, hosta9e7307/execution5bc8b2b; exact-state assertions:

![Actual noncombat ready checkpoint anchor](probe-anchor.png)

Actual native frame2236 at strict resource stop,21 assertions; black map-load
transition frame is preserved exactly, not a staircase screenshot or art candidate:

![Actual native map transition at diagnostic stop](probe-stop.png)

[All three actual PNG identities](captures.json). No generated concepts, image
editing, new art or visual rollout. Reviewed complete tooling diff: game/accepted
plan/historical observers/contracts/evidence unchanged; all frame sites funnel
through one noncombat24,000 guard; no memory writes/RNG calls/input adaptation.
Gate remains strict, first mismatch dumps then exits; no subsequent frame.
Offline decode/source checks passed; compilation never substitutes for runtime.

## Durable checkpoint and next dependency

Complete new safe logs, route/claim/STOP, private raw buffers/full decoding,
native captures and unchanged ordinary input copy retained privately in Library.
Git contains safe bounded findings/hashes/captures only. No raw buffers, decoded
identities, keys, saves, ROMs, executables or old denied datasets are committed;
private upload excludes ROMs/executables/credentials/old denied raw data.
All57 earlier remote heads/mainb694 remain unchanged. No merge or CI pass claim.

**Next: parent review of this preserved observer stop.** Any separately authorised
new probe needs native logical resource comparison that accounts for re-encoding
without weakening the exact200-byte party gate, plus enough private read-only
observations to verify derived encoding independently. This increment does not
change those checks or retry. No legitimate friendship delta was proven, so
no friendship-allowing preservation contract is recommended yet. Only after
separate bounded evidence proves that delta may a separate contract consider it,
with every other party/resource field exact and valid derived encoding/checksums.
Original prepared field, prepared persistence, legacy inputs and broader Floor1/
human-pacing/finalT/V01 gates remain open. No prepared replay or battle authorised.
