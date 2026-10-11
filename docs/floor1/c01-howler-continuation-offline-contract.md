# C01 Howler continuation — offline proposal, runtime CLOSED

Base main: `65bc4073d140b9d58bf1b83bd33235e28c972b23`. One writer, new draft
PR only; no merge or new runtime freeze/claim/process in this increment. This
proposal does not reopen any historical wrapper, failed attempt or STOP record.

The input is a separately named, hash-verified copy of the immutable Guard Save
`b88862308be4a5b58c7da79803106a29e9201d093d6e3be5307e226c556f63cf`.
Original operands and cold2 validator remain unchanged. Future review must admit
an exclusive continuation output and a conditional independent cold output before
execution; the current admission module rejects prepare/freeze/claim/execute/
Save/cold. No New Game, trial or Guard replay; no injected state, resource grant,
fake encounter count, RNG search, preparation, Warden or stairs.

The proposed ordinary route is Continue → Howler857 once → immediate resolved
repeat → guide → native same-file manual Save at Quiet Landing → conditional
new-Save cold. Both physical legs are17 steps/704 fixed frames; committed map
collision words, actor occupancy and reciprocal warp records are checked offline.
Original saved-party600 bytes/count2 remain the input snapshot through movement,
combat, repeat and recovery. Only the real new Save may replace that buffer.

Carl uses STRIKE on Howler, then Scuttler, with at most7 uses. Donut selects
SPARK on native turns0/1, then WEAKEN; a necessary native Potion can replace an
action. The stock bound is1. Native four-battler positions/species/party indexes,
both actual foe HP/presence bits and absent flags remain mandatory. Carl's danger
thresholds are16 with both foes,12 Howler only,9 Scuttler only; Donut's12 applies
only while Scuttler remains. Simultaneous danger, empty stock, impossible capped
healing, PP exhaustion, incapacity, full-state and medicine transaction failures
stop immediately. The budget retains one STRIKE PP at victory. MaxHP is source-
derived36→38 for Carl and28→30 for Donut, never inflated for survival.

Native trainer creation derives Howler30HP/14attack/9defense/9speed and
Scuttler25HP/9attack/12defense/16speed from cumulative encoded nameHash and nature.
Initial action order is Donut23 → Scuttler16 → Carl14 → Howler9. Howler selects
WEAKEN on turns0/3/6 and Tackle otherwise. Exact staged integer divisions,
critical multiplication, STAB, spread and85–100% damage rounding yield the
16/12/9/12 one-critical-plus-ordinary envelopes. Repeated WEAKEN has integer
plateaus. Neither simultaneous critical survival nor favorable outgoing criticals
is assumed. Conservative85% outgoing traces require a seven-STRIKE bound,
including the no-Potion case and either replaced early SPARK. Howler's64XP takes
Carl627→691, below the742XP level11 threshold: Carl remains level10/attack25
against surviving Scuttler. Scuttler's57XP then takes Carl to748/level11. Donut
937→1001 reaches level10 after Howler falls, producing the legal mixed maxHP
36/30 before Carl grows. No RNG state enumeration or critical-dependent planning.
The exact terminal range is Carl STRIKE1–7PP, with all other move/PP/full-state
constraints unchanged. A separate source-event critical-win fixture demonstrates
T0 spread SPARK10/8 plus one Carl STRIKE fainting Howler, then T1 single-target
SPARK18 fainting Scuttler17HP before Carl acts; Carl retains7PP. It establishes
validator coverage, not a favorable-critical runtime requirement.

Only earned Howler2137 is newly set. The expected recovered endpoint is
map35,1 `(4,5)`, section214, facing1; Carl/Donut levels11/10, XP748/1058,
friendship87/81, HP38/30, status clear, uses8/40/2/40; money4000, Scrap2,
Potion0or1 from actual use. Counter78→112 follows34 actual steps, with no128
walking-friendship boundary. Native growth derives the friendship change. All
preparation/boss/checkpoint/loop and forbidden flags remain unset. Repeat must
preserve every decoded field, XP, reward, resources and saved-party bytes.

Same-file Save enters the native first confirmation, releases A, waits for the
finished `gText_AlreadySavedFile` printer and `SaveOverwriteInputCallback` with
Yes0, then sends exactly one second fresh confirmation A. That text contains a
newline, no paragraph pause. Different-file overwrite is forbidden. Duplicate/
held/multi-frame A, an unfinished printer, wrong callback or No cursor fails.
The fourteen-sector disk validator compares complete live/disk party/count/
flags/vars/resources/counter/legal endpoint. The new Save already contains
TV_WATCH2193: new cold is idempotent, with no flag mask or allowance. Original
cold1 STOP96 and cold2 expectations/operands remain immutable.

The initial estimate was69425 =5825fixed +36000encounter +3600engage +13200dialogue
+10800threeSavewaits, with a proposed70000 ceiling. The exact generated route
retains the1200-frame battle-start wait: fixed7025, whole conservative70625.
Proposed final ceilings are72000 continuation/6000 cold,600 seconds per process.
The read-only resolved-text check consumes no frames or paragraph inputs. No
extra unbudgeted `pages` controller is used. The future process supervisor must
also enforce whole output/per-file/per-log ceilings before any claim.

Reservation remains the complete unchanged72k+6k ledger: continuation8837820160,
cold894152512 plus268435456 headroom =10000408128 bytes. This includes every
115200-byte native RGB frame, complete3340-byte field and1040-byte battle records,
16-byte indexes,64MiB logs per process,256 PPM+PNG capture pairs per process,
32/16MiB review motion,32MiB source/Save/manifest per process and32MiB continuation
medicine audits. It is not reduced to match current free space. Runtime is CLOSED.

Exact planned named captures: continuation `cold.ppm`, `howler-start.ppm`,
`howler-victory.ppm`, `howler-resolved.ppm`, `guide-howler.ppm`,
`saved-success.ppm`, `saved.ppm`; cold `cold.ppm`. At most one Potion adds
`medicine-01-bag.ppm`, `medicine-01-recipient.ppm`, `medicine-01-healed.ppm`.
First failure preserves `first-failure.ppm` and native CPU/last-state context;
field-menu/pilot-down captures are defensive failure paths. Complete motion
remains native RGB at every frame. No new actual screenshots or motion exist.

Offline fixtures are explicitly synthetic, including the native-format sector
fixture. They are never gameplay Saves, recovered oracle bytes or runtime
acceptance. Full aggregate covers the new Continue/phase/route/reward/repeat/
recovery/Save/cold handoffs, native medicine instruction/IRQ closure, production
pre-init negatives, complete dependency and executable identity gates.

Game remains `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine tree
`0fedd142f43f136ceee189c54101b095fc88f495`; retained ROM
`79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246`, ELF
`7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d`.
Recovered GCC14.2.0/ARM binutils2.44-3+23+b1/agbcc source
`da598c1d918402c42c0c0d7128ba14567f3175e9`/libmGBA0.10.5 retain their checked
manifests; recovered compiler binaries are not the historical originals. No
engine rebuild or edit. New observer identities belong to this offline proposal.

Opening claims/processes5/5 and cold2/2 remain unchanged; opening STOP82/90/104/101
and cold1 STOP96 remain failures. Historical V01 six baseline/four candidate and
STOP117 before expectedB8402, later separate1/1 pair, ordinary recovery5 and C01a
actual5/3/1 versus claims6/3/1 remain separate. The later scoped V011/1 runtime
pair and PR114's merged accepted active poses retain their [technical closure](../evidence/floor1/v01/new-input-pair-20261010/closure.md).
PR114 merged atbdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7; this accepted scope does
not recover the original six/four oracle or imply broader human motion/full-floor
acceptance. Withdrawn live hints/STOP124 remain failed, separately from accepted
PR115 optional Journal notes: [battle regression](../evidence/floor1/c01a/journal-admission-r3-20261010/README.md)
and [field probe](../evidence/floor1/c01a/journal-field-r1-20261010/README.md), merged
atb51e27d96f7ea43667ed20c4ce7bc7ca113d1eae. PR114/PR115 heads and issue116 remain untouched.
The original runtime oracle/legacy inputs remain missing. FullC01/patrol/opening,
both orders/optional skips/human/full-floor gates remain open; G02 is not ready.
The accepted nine-district Floor1 plan remains authoritative and unchanged.

Local retention is not independent backup. Library's five failed uploads and one
failed supported existing-backup download, unknown cause and zero original bytes,
remain unchanged; no retry or transfer. A separately authorized private object
store or user-controlled download requires verified readback before any backup
claim. No ROM/ELF/Save/raw trace/full symbol publication, compression or deletion.

Next dependency: review this exact offline proposal, the70625/72000 route bound
and source/state/Save guards; separately approve and verify retention/capacity,
then prepare a reviewed runtime supervisor/freeze/claim. No execution is admitted
by this document, fixture receipt, draft PR or storage measurement.
