# C01 native sampling audit — offline PASS, runtime unadmitted

Independent offline continuation from `66a07ff6ccd77f2f4a4c2889364c657bfae45cd1`
on draft PR117. The previous acknowledgement regression remains valid for its
synthetic states, but its grouped callback updates do not establish that native
frame observations always see those states. This increment audits that assumption
and blocks preparation before any freeze. It does not repair or admit native
medicine sampling. Screenshots N/A: this is a static binary/API and inert-fixture
audit; no emulator, gameplay, actual Save, cold verification or capture occurred.

## Exact observation boundary

The retained observer makes one `mCore.runFrame` call and then reads state without
draining a callback. The actual retained libmGBA binary installs function `f18b0`
at core offset `13d8`. That function loops on board video frame counter `14d8`,
with a time fallback, through `ARMRunLoop`. Instruction dispatch stops for native
events; neither return condition is a game callback completion barrier. The
[0.10.5 core source](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/core.c),
[video source](https://github.com/mgba-emu/mgba/blob/0.10.5/src/gba/video.c) and
[ARM loop](https://github.com/mgba-emu/mgba/blob/0.10.5/src/arm/arm.c) corroborate
the compiled instruction/offset checks. Installed-header host layout was measured
without creating an emulator. Upstream source is supporting evidence, not a claim
that the complete Debian shared library was rebuilt from that exact source.

The frame API does not exclude any of the following native instruction cuts.
**Their occurrence on the frozen route is not proven.** No worst-case callback
timing, cycle-phase or interrupt-context exclusion proof exists here. A synthetic
next-PC association is diagnostic only; the medicine guard does not consume it.
IRQ/event context can also leave a different PC, so PC alone cannot admit a cut.

| Native sequence in retained ELF | Split fixture result |
| --- | --- |
| `Task_DisplayHPRestoredMessage`: message call +`2a`, own function store +`44` | Created printer/wait task with old restoration function: 8 rejected, reason107 |
| `RunTextPrinters`: active-byte store +`6e`; `Task_PrintAndWaitForText`: cleanup +`2c`, destruction +`38` | Inactive printer before task destruction: 8 rejected, reason107 |
| `Task_ClosePartyMenu`: fade call +`16`, own function store +`26` | Active fade with old close-text task: 8 rejected, reason107 |
| `UpdatePartyToFieldOrder`: record-copy call +`32`; aligned `memcpy` single-word stores +`1c/20/24/28/36` | 1,248 full four-byte prefix states: 628 unchanged accepted, 468 source-correct permutations rejected106, 152 torn actor representations rejected82 |
| `Task_ClosePartyMenuAndSetCB2`: callback call +`2c`, sprite reset +`46`, pointer free +`4a`, task destruction +`50` | Published exit callback with cleanup pending: 8 rejected, reason107 |

All **1,280** fixtures span two native party orders, both recipients and Potion
quantities1/2. All600 party bytes match the exact progressive source copy; torn
actors remain checksum failures rather than being normalized. Restoration text
comes from the pinned ELF symbol, expands native nickname/actual capped HP gain,
and retains the `PAUSE_UNTIL_PRESS` suffix. The stable cleanup-complete exit also
passes with the native stale non-null global pointer: `FreePartyPointers` frees
the allocation without nulling that global. No freed pointer is dereferenced by
the exited-menu guard. Synthetic fixture memory is not game RAM injection.

## Verification and identities

[Sanitized audit receipt](offline-audit.json) records the final split results and
unchanged full aggregate regression. The full aggregate preserves74,124 policy
vectors, eight lifecycle cases plus two successive uses,65,760 snapshot byte
corruptions,210 readiness/lifecycle negatives,10 premature/10 duplicate no-input
cases,11 acknowledgement receipt negatives,49 ABI values/90 ELF bindings and all
inherited full-state/route/Save-cold/terminal/executable negatives. The original
aggregate artifacts are hashed again after isolated split fixtures; no synthetic
split fixture overwrites their namespace. One fresh A at native WAIT, Donut
ownership, exact HP/PP/inventory/permutation, per-use reset and all bounds remain
unchanged. No masks, party-validation skip or broad inconsistent-task allowance.

Compiled game `4a92a9de70848b9d7275f9f255bb0d2f53232ab8`, engine tree
`0fedd142f43f136ceee189c54101b095fc88f495`, main/base
`b51e27d96f7ea43667ed20c4ce7bc7ca113d1eae` remain unchanged; no game rebuild.
ROM SHA256 `79a0ed7621399bab8aa38ca00fbc3515fb69c4d84ade798a370bcc08d1c29246`;
ELF `7895d09e2d2f94e699ccd4f0d19e302e21d3d9d8991709abbfd4ba82e222536d`;
libmGBA0.10.5 `a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63`.
Generated observer `56c5f71914f2ecccb96d56eae2da0ae2e54b2769a80383a26bbd4dcbe897b153`;
compiled observer `0a9ed4fba40cd7978667be792faa5ae20cc7e1c02687931454f9a2828d604429`.
GCC14.2.0, ARM binutils2.44-3+23+b1 and agbcc source
`da598c1d918402c42c0c0d7128ba14567f3175e9`/retained manifests checked again.
Recovered compiler binaries differ from historical binaries.

The two diagnosed symbol-scope preparation failures remain private. A preliminary
audit used simplified printer text and shared fixture output; both limitations
were identified and corrected in the final isolated, full-text audit. Preliminary
artifacts/logs remain retained. These are offline preparation corrections, not
gameplay retries. Native medicine, host, state, ABI, policy, route and existing
inert sources are byte-unchanged from66a; only the wrapper's early preparation
gate and separately named independent audit files are new.

## Storage, preservation and next dependency

[Measured storage status](storage-status.json): full reservation remains
**10,000,408,128 bytes**, with no reduced ceilings or assumed compression savings.
Storage remains blocked. Kurt approved local lossless preservation of two
recordings' uncompressed RGB copies at **2026-10-10 13:28:29UTC**, conditional on
every decoded frame verifying. That is authority for the **next separately
frozen preservation increment**; this increment performs no compression, deletion,
consolidation or upload. Independent private backup remains unverified; Library
uploads are not approved. Prior five failed uploads/one supported failed backup
download, unknown cause and zero recovered original bytes remain unchanged.

Next: finish/review this offline checkpoint, then separately freeze the approved
local preservation operation with complete frame readback before any raw-copy
replacement. Before gameplay, a reviewed narrowly bound PC/task/full source-byte
transaction treatment, or valid observation exclusion proof, is additionally
required. Free storage alone cannot admit a run. No runtime freeze/output/claim
or process exists here; C01 opening3/3 and cold0/0 remain unchanged.

DraftPR117 stays open/draft/unmerged. Preserve STOP82/STOP90/STOP104, all archives,
main and every other branch; V01 six baseline/four candidate, STOP117 requested
visual8536 beforeB8402, later accepted1/1, ordinary recovery5, C01a actual5/3/1
and claims6/3/1 unchanged. Original runtime oracle/legacy inputs remain missing;
C01/G02/prepared/human/full-floor gates stay open. The accepted nine-district
Floor1 plan, T1449/8–12× area, widths5–7/3–4/junctions8–12, permanent duo,
accessible recovery, stock Emerald/GBA and Book1 spoiler ceiling are unchanged.
