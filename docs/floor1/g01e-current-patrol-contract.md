# F1-G01e-CP: one current-candidate patrol check

2026-10-08, same Cloud task `01a10f4b-596b-700b-b8ba-241e3ca2c000`.
Base `f8178113b42cdf14f5540ecd50268df5da8a947f`, PR89 reconciled draft/unmerged.
Parent reviewed PR89's bounded historical claim and explicitly authorises this
one focused current-candidate validation. Older drafts75–89/main unchanged;
GitHub reports0 workflow runs and no tracked workflow/skill directory. One writer;
parent owns continuation. Preserve historical failures and private diagnostics.

## Identity and differences, before execution

Current compiled game `c643f01c11ec68119b0347b107ee20115131debc`, ROM SHA256
`b0251d46f4d102cfbd91df961bb7aa98bd3e711d8598e9f690ec45abc5e64b1a`.
Reuse the retained isolated compile; no new game build or compilation claim.
Archive `2dd7aa66942a3d13604ae4ce81a1a3d978a2c73551c23a3ed83d7208c3b051b7`
and ROM rehashed. Recover only ROM/ELF/map/player-controller object for symbols;
all original artifacts stay intact. Compared with historical99243073/6c447159,
eight engine files differ: event-script include, four live map event bindings,
new live navigation scripts, spent secret feedback and Journal dispatch/text.
Battle engine, trainer/move/species data, save ABI, party/item structures and map
geometry remain unchanged. Live narration can change elapsed frames and RNG;
historical outcomes and timing are not transferred to this candidate.

Ordinary pending input remains the original controller-authored
`artifacts/floor1/a01/run-I7PJq0/both-pending.sav`, SHA256
`ea719ffb76f510eabac88cbd345c87d7e21ce009dde0bfca9418ca0a1d3babc8`.
No save differences from PR89; no synthetic save or resource injection. Candidate
migrates the same legacy save normally. Its initial flags2136/2137 must be unset,
and it must own exactly one Potion. Historical read-only struct observer and
route inputs remain private inputs pinned by their recorded hashes; current
addresses are freshly resolved from the current ELF/object, never old symbols.

## Prespecified route and decision

Cold Continue; Field37,31→51,27 Howler. Same normal `weaken-first` choices, then
flag2137 must set. Walk to Quiet guide4,5; actual recovery; return to51,27, then
walk to Guard37,31. Same normal offensive choices until Carl's turn4 action.
Expected semantic decision is unchanged: Carl3/36HP, Donut30/30HP, PP4/40 and
0/38, Guard0/29HP, Scuttler18/24HP, one owned Potion and Carl action cursor0.
Do not carry historical frame24673 as a current-ROM identity or timing assertion.
Record the actual frame, and stop before Potion on any semantic divergence.
No search for another turn, alternate strategy or arbitrary retiming.

If the exact decision matches, normal Bag/Potion/Carl uses actual fade/task
readiness and observed receiving-menu acknowledgements. Zero-input waiting only
for real readiness; same12-frame input cadence. Assert3→23HP, exactly1→0Potion,
unchanged four action PP, then resume the original offensive choices.

Guard flag2136 must follow Howler2137; actual victory/map return and guide rest.
Repeat the resolved Guard interaction: no new battle/XP reward. Preserve existing
position/flags/recovery/XP assertions and original manual Save buttons. Cold
Continue must restore both wins, Potion0, XP and37,31; repeat must remain resolved.
Check XP121+132 per crawler, stock money360+320 and other inventory unchanged.
Document candidate input/state coverage separately from historical59-input proof.

## Stop and publication

One exclusive current-candidate execution. On divergent decision state or any
failed execution, stop and diagnose read-only; no alternate policy, injected
items/stats/PP, RNG fishing, retimed replay or attempt-count reset. Preserve errors
and all outputs. Publish only scoped host source, bounded verdicts and actual
native frames in a focused draft PR. Raw denied datasets/keys/saves/ROMs/ancestry
stay local. No broad merge, V01/full-route claim, new writer/task/scheduler/quota
calls. Return exact tested commit/checkpoint and next dependency-ready action.
