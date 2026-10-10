# C01 r2 actual opening2 — terminal Guard STOP90

The sole r2 opening process (opening2 overall) stopped at absolute native frame
**31258**, Guard856 turn5, **STOP90: first Carl incapacitation**. Carl HP4→0 on
remaining enemy battler3's Tackle33, power35, critical multiplier2, damage8;
Donut HP16. Outcome0/in-battle1: stop precedes resolved battle loss/faint handling.
All six party checksums/reencoding are valid, exact unused400 bytes preserved,
Pokerus0 in both party-member records. This is supported native combat failure,
not corruption or unsupported Pokerus. No assertion/controller/route/balance
correction or runtime retry. Howler/Warden/stairs/manual Save were not reached.

[Sanitized actual verdict](runtime-STOP90.json). Main/base
`b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`; increment start
`605f64777807ad8724500470e450d12b5cdab306`; committed/pushed-before-runtime and
tested helper `978cbf03907c38ef24fb4008bfed04e1c69daea5`. Draft
[PR117](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/117) stays unmerged.
Compiled game `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine
`0fedd142f43f136ceee189c54101b095fc88f495`; actual ROM/ELF pins below unchanged.
Prepare rehashed11734 source entries, actual game/tools/observer/native ABI/72 ELF
bindings/routes/storage; no game rebuild. Freeze SHA256
`aa0787949c09d60b887e4dcc74352887fea4212730386f041729f49b8c8470a8`;
observer `f77473d393b10e89354c1ad10dba38584b0bd635f25b98fd54547cee35eae1c3`.
Recovered compiler binaries remain distinct from historical binaries.

Eight complete source-native phases passed: boot2886, note4438, supply5046,
guide-initial8306, trial18497, scrap19133, potion19758, guide-posttrial20522.
Trial855 win earned+96XP each/+320 money, with native Carl/Donut Lv9/9,
XP495/805. At actual Potion demonstration Donut missed4HP, native gain4, one
Potion spent; following guide restored duoHP33/28, PP8/40/2/40. This does not
establish full-opening survival costs. Native menus/callbacks and phase-end
party/resources/flags/variables were checked, with no fabricated wound/resource.

Last accepted field: map35,0(37,31), facing1, walking counter72, count2/saved0,
money3320, Potion1/Scrap2, trial win set; Guard/Howler/Warden wins and preparation/
boss/checkpoint/loop unset. Last accepted party Lv9/9 XP495/805 HP33/28 clear,
friendship75/75, full uses. At the battle stop Carl Lv10 XP576 HP0/36, PP2/40,
friendship81; Donut Lv9 XP886 HP16/28, PP0/36, friendship75, both status clear.
These partial battle XP/levels include the first defeated Guard enemy, not a
completed Guard reward or accepted field endpoint. Current legal field state is
not claimed while still in battle.11187 field and17784 battle packets retained.

Read-only CPU context retained96 bytes at the same stop clock: r0–r15 valid,
CPSR valid, SPSR read unavailable (validity false). Raw registers remain private.
This does not establish physical-frame atomicity of native getter/setter/healing.
No extra frame, Continue, recovery or new Save after STOP. PID153748 exited90;
no observer remains. Native131072-byte Save still allFF. Native manual Save,
14-sector disk equivalence and cold were not performed; cold is unadmitted.
R2 opening processes/claims1/1; cumulative C01 opening2/2; cold0/0.

Actual [note3496](note.png), [supplies5004](supply.png), [trial start10487](battle-start.png),
[trial result18195](battle-result.png), [Potion menu19493](field-potion.png),
[posttrial guide20480](guide-posttrial.png), [Guard start22984](guard-start.png),
[first-failure31258](first-failure.png), and [whole actual review motion](actual-opening-review.mp4).
Potion capture is inside the native party message callback; full field return/
phase-end acceptance is later19758. The inherited opening capture filename
`cold.ppm` at2044 is only a New Game page label, never an independent cold run.
Native240x160,31258 frames/523.343513seconds at16777216/280896fps. All12 PPM/PNG
captures equal the corresponding indexed raw RGB frame; sequence1..31258 complete,
including the first violating frame. All3600921600 raw bytes are private and
locally readback hashed. [Capture identities](captures.json) bind published files.
Whole MP4 is a complete lossy review export; no replay or human pacing acceptance.

**Export limitation:** FFV1 encoding exited nonzero at its480MiB file cap. Its
incomplete503316480-byte artifact and error logs remain private, no export retry.
Exact encoder signal was not retained. No complete actual FFV1 decode/roundtrip
is claimed. The whole MP4 completed independently,31258 frames/3707653 bytes;
raw lossless RGB remains intact. Export directory stayed within512MiB total.
The earlier3-frame inert FFV1 test PASS remains offline evidence only.

[Local retention receipt](local-retention-receipt.json) verifies all source/execution
manifest entries by complete readback, including raw chunks/index/traces/phase
snapshots/blank Save/CPU context/freeze/claim/STOP/observer/source/logs, all offline
history, small source archive, complete MP4 and failed FFV1 artifact. All35 r1
private files rehashed unchanged; all r1 tracked source/evidence/contract history
preserved. Local retention is not independent backup: unapproved/unverified,
no Library/private upload, ROM/ELF/Save/raw recovery payload publication or issue116
write. Hosted CI is absent, not passing; no merge.

C01a actual5/3/1=9, claims6/3/1=10; originalV016/4 STOP117 visual8536 beforeB8402,
later separately accepted1/1, ordinary5, Library five failed uploads/one supported
failed existing-backup download, unknown cause/zero original bytes unchanged.
Original oracle/legacy inputs still missing; no acceptance inferred from this
ordinary run. Engine/accepted nine-district plan unchanged. C01/G02/human/legacy/
full-floor gates remain open.

Next dependency: review this native Guard critical/incapacitation and bounded
export limitation on draft PR117. Further gameplay requires a separately
reviewed/authorized contract; no automatic retry, cadence/RNG search, prepared
route, engine/balance change or merge in this increment.

---

The following source checkpoint is historical, retained verbatim:

# C01 r2 native empty-party repair — final offline source checkpoint

Independent review authorizes this increment from
`605f64777807ad8724500470e450d12b5cdab306`, against main/base
`b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae`, on draft PR117. Source checkpoint
must be committed/pushed before r2 preparation or gameplay. R1 opening1 STOP82,
freeze/claim/blank Save/first-failure state/screenshots/motion remain untouched.
[Separately named r2 contract](../../../../floor1/c01-uninterrupted-unprepared-r2-contract.md).

C co_read and Python snapshot now recognize exact native100-byte empty Pokemon:
zero except mail85=MAIL_NONE0xFF. Compile-only native ABI binds100/85/255 alongside
all previous17 constants. All six checksums/reencoding and exact unused400 bytes
remain required. Occupied/empty fixtures retain native mail. Before Save, native
SaveBlock1 remains count0/zero600, distinct from the live empty-party template.
Native disk count is checked as the full source u32. No engine/game/balance/build,
normal route/strategy/cadence/bounds change. Old standalone recovery wrappers, r1
contract/claims remain unchanged; r1 shared observer source is preserved at c3db41b2.

[Final aggregate admission](source-admission.json) PASS:288 literal-source decision
vectors; previous24 battle positive/corruption checks (not all phases);14 native
sector corruption negatives; exact3-frame native-timing FFV1 roundtrip. Existing
callback/fade/menu/pointer/phase, walking/poison, whole-battle30000 and11 terminal
bounded-driver mocks also pass, including actual underlying advance counts and
read-only first-failure CPU-register capture. Five executable admission negatives,
72 actual ELF function/literal/local-callback bindings and native20-value ABI pass.

The retained actual frame1538 bytes pass corrected Python snapshot and generated-C
co_read offline, without relabeling r1 as runtime success. Reject412 unused-slot
byte/zero/wrong-mail mutations and checksum damage in all six records. Full
source-derived chain passes all18 phases through snapshot() and both validators:
boot, note/supply, five guides, trial/Guard/Howler/Warden, scrap/Potion, resolved
repeat, both staircase choices, Save and native disk/cold.108 phase negatives are
rejected at Python endpoints; C rejects107 and intentionally accepts the one
intermediate Save-buffer case.273 walking transitions include full counter wrap,
native friendship event/skip and poison modulo4;19 map/TEMP_1 lifecycle transitions;
54 encryption-key-independent resource comparisons;30 Save/disk/cold cases,
including valid-checksum full-count negatives and the exact cold CLI. Source
trainer parties/yields/XP rounding/EVs/money table/growth/flags/healing/move PP/
map scripts derive fixtures. They are inert offline evidence, never game inputs.

Non-link battle return may acquire/spread Pokerus and change later EVs: eight
strict acquisition/EV negatives remain unsupported native state, not corruption,
defeat or RNG-search authority. Authored ABILITY_NONE excludes Pickup. Partial
native healing/setter states stay strict; callback identity does not establish
physical-frame atomicity. CO_SAVE intermediate saved buffer is exempt; full
endpoint/disk/cold equality remains mandatory. No unknown-field masks added.

Generated host SHA256
`77c49580d1323e12073b4e742eb6f6e09435401ad2a47383e84b1f53a48da9d0`.
Compile-only ABI assembly/object hashes and values are in the receipt. Reuse
compiled game `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine
`0fedd142f43f136ceee189c54101b095fc88f495`; ROM
`79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246`, ELF
`7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d`.
Final prepare must rehash actual outputs/source/tools and verify the own-compiled
observer before freeze/claim. Recovered GCC14.2.0/ARM2.44-3+23+b1/agbcc source
`da598c1d918402c42c0c0d7128ba14567f3175e9`/libmGBA0.10.5 remain manifest-bound;
recovered compiler binaries differ from historical binaries. Zero game rebuilds.

Development logs retained: two diagnosed fixture errors (Save intermediate
exemption, unchanged Donut HP after Potion), affected PASS, earlier full aggregate
PASS and final full-count audit/admission. These are offline preparation, not
runtime attempts. New r2 opening processes/claims0/0 and cold0/0; existing r1 is1/1.
No r2 execution output/claim yet. No synthetic imagery presented as gameplay.

After source publication, freeze exact dependencies/actual observer/build/tool/
route/storage in `/workspace/scratch/c01-uninterrupted-unprepared-r2-20261010`,
reserve13GiB, then launch opening2 once. Only complete live/manual Save/native14-
sector equivalence admits cold1 once. First runtime failure terminal; no automatic
retry, timing/RNG search or prepared route. Publish actual result/captures here on
draft PR117 and stop at review, no merge or issue116 write.

Preserve C01a actual5/3/1=9, claims6/3/1=10; originalV016/4 STOP117 visual8536
beforeB8402, later separately accepted1/1, ordinary5, Library5 failed uploads/one
failed supported existing-backup download, unknown cause/zero original bytes.
No Library transfer or private upload. Private retention locally checked;
independent backup unapproved/unverified. C01/G02/original oracle/legacy/human/
full-floor gates remain open; all historical evidence and accepted plan unchanged.
