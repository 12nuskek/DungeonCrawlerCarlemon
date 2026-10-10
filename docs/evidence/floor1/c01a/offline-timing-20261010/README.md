# C01a offline timing audit: no game remedy established

STOP124 remains terminal. This increment inspected retained source/ELFs and
records and fixed host diagnostic retention offline. No gameplay process,
game rebuild, baseline/candidate replay, rendering/DMA change, stream waiver,
new execution claim or merge occurred. DraftPR115/issue116 remain blocked at
review of the [passive diagnostic proposal](passive-diagnostic-proposal.md).

[Contract](contract.md), [executable audit/count proof](../../../../../scripts/test-f1-c01a-offline-timing.py),
[processed results](offline-timing-proof.json), [terminal error/success tests](../../../../../scripts/test-f1-c01a-terminal-retention.py),
[host results](terminal-retention-proof.json), [ordinary offline attempt history](offline-attempts.json).

## Retained boundary and actual dispatch position

Last equal native B ordinal3149: visual3169/input5214, zero preceding B count in
its frame, emulator counter5213, requested keys1 (first Fight A). Original2560
snapshot SHA25607ccf4b3b0e0ab4ba0d6401faee51d3297003e3049555f8e4007f7b4135a4880.
Candidate's frozen native live comparison passed before the supplemental STOP;
there is no retained candidate actual B stream. Its `expected-...` file is the
original baseline copy, not a newly captured candidate record. Frames3170/3171
have no additional B boundary (summary boundary count0, anchor still3149).

| Physical visual frame | Baseline instruction position | Candidate instruction position |
| --- | --- | --- |
|3169|WaitForVBlank+32|WaitForVBlank+32|
|3170|BattlePutTextOnWindow+94|RequestDma3Copy+44|
|3171|ARM IRQ vector0x18, CPSR0x92; no ELF function|__umodsi3+48, Thumb system mode|

Both original summary hash chains verify. Per-frame record counts are64/48/36
at3169/3170/3171 respectively; the last two include zero new native B samples.
Raw passive detail hashes differ and include build-specific addresses/CPU paths;
they are not the strict normalized state oracle. Baseline retained detail covers
only7050 (17 records): this interval was rotated away. Candidate retains101
records across3169–3171, plus the terminal124 summary. Missing baseline detail
cannot be reconstructed from its summary digest.

Candidate3170/3171 share ReadKeys/dispatch5044, CB1 invocation3665 and CB2 count
5043. The same CB1 invocation spans those physical frames; a new CB2 did not run.
BattleMainCB1 at0x08039e94 first calls gBattleMainFunc (+6), then iterates
controllers0,1,2,3 through its indirect call (+36), returning at+40 each time.
The player command dispatch initializes names/cursor/PP-label/numbers/type-hint;
PlayerHandleChooseMove stores HandleChooseMoveAfterDma3 only after init returns.
Both compiled paths preserve this sequence. HandleChooseMoveAfterDma3 checks
the DMA manager on a subsequent controller call. Its changed stored callback is
not evidence that this DMA-wait function has already run.

At STOP124 exec9 versus11 differs in **opponent bit1**, not Carl bit0. Carl's
callback assignment has completed; opponent1's bit is clear, opponent3's remains
set. Candidate is in __umodsi3 at instruction0x082eb670 (raw pipeline PC
0x082eb672), called by GetSubstruct at0x0806a29a; LR0x0806a29f returns at
GetSubstruct+18. Earlier diagnosis used raw-PC offset50; actual instruction
offset is48. Source/compiled GetMonData2/GetBoxMonData2/GetSubstruct and both
opponent command handlers were audited. Source macro GetMonData is emitted as
GetMonData2/GetMonData3 aliases, not a standalone ELF symbol.

These observations place the candidate after Carl's init and opponent1's
completion within the continuing CB1 pass. **Current gActiveBattler, command
byte and caller stack above GetSubstruct were not recorded.** Do not label the
current work as observed battler3 AI or infer a longer candidate DMA wait.
The baseline3171 PC is an IRQ vector snapshot, not proof of a DMA defect.

Candidate frame ends record IE197/IF1/IME1, pending IRQ1 and an IRQ-root event.
Main/BIOS intr flags are5/5 at3170/3171. Existing CopyToVram queue count/bytes0,
armed0 at these ends refers to a separate queue, not `sDma3Requests`. DMA3 queue,
lock/cursor/busy mask, VCOUNT and baseline corresponding event context are absent.

## Source-bound printer counts, not recovered timing

Both panes use speed0, synchronous AddTextPrinter. Entry prints the same seven
windows (four names, label, numbers, type/hint), with unchanged cursor-copy path.
Movement/cursor-refresh branches have not run: no first Move-ready/input occurred.
The fixture executes extracted old/new printer functions, exact AddTextPrinter
and CopyWindowToVram on host stubs, using verified ELF encoded strings/type data.
Its RenderFont counts character/font operations against the unchanged RenderText
branches; it does not run GBA rendering, glyph pixels, interrupts or cycle timing.

| Changed pane | Baseline operations | Candidate operations |
| --- | --- | --- |
|PP/USES label|3 narrow glyphs (`PP `)|4 narrow glyphs (`USES`)|
|STRIKE type/hint|5 narrow +6 normal glyphs, one font control|7 narrow glyphs|
|BRACE type/hint|same old TYPE/NORMAL path|9 narrow glyphs|
|SPARK type/hint|same old TYPE/NORMAL path|9 narrow glyphs|
|WEAKEN type/hint|same old TYPE/NORMAL path|13 narrow glyphs|

Each pane makes one BattlePutTextOnWindow call, two GFX submissions and one MAP
submission in both builds. Label GFX256 bytes twice; type/hint GFX512 bytes twice.
Each MAP request is4096 bytes when the normal visible BG0 screen2 path accepts
it. These are source-bound submission shapes, not observed accepted queue state.
The full entry's other copies are unchanged; increased request volume is unsupported.
GetHint adds compiled work; shortened strings remove other work. Weighted CPU
cost, interruption placement and queue acceptance remain unmeasured. Compiler
size or glyph count alone cannot justify optimization/padding/DMA changes.

ProcessDma3Requests honors manager lock,40KiB limit and VCOUNT224 cutoff and
frees completed requests. VBlankIntr calls it after the native VBlank callback
and GPU-register copy. All these compiled/source paths were inspected; no defect
or justified game remedy was established. The proposed diagnostics record actual
controller dispatch, queue state and VBlank context without changing comparisons.

## Terminal host correction and verification

[Separately named generator](../../../../../scripts/floor1/c01a-ui-host-terminal.py)
keeps historical r4 sources unchanged. All four active immediate exits now close
the edge stream before exit. Complete buffered rows are retired as written so
later partial/bounded failures cannot duplicate the successful prefix. A healthy
terminal path writes tag11/result124 at the failing frame before close. I/O or
capacity failure reports retention125 and preserves the original STOP; a footer
cannot be promised when storage is exhausted. No CPU/game call, step, frame,
key, scheduling or emulated-memory write is added.

Eight host-only fake-memory cases pass:124 with pending rows; ordinary success;
preexisting recorder125; exhausted capacity; /dev/full; mid-buffer capacity
failure; STOP51; STOP109. Original success footer bytes match exactly. Reversing
only the scoped header/flush/four error-exit edits restores the complete historical
generated C byte-for-byte, including all15 key expressions and both strict streams.
Full host compile/link with pinned libmGBA0.10.5/USE_DEBUGGERS passes; binary never
launched. Original candidate5116 flushed records and missing tag11 remain exact.
No lost in-memory observations were recovered, and no historical acceptance was
retroactively changed.

## Exact identities and retention

- Starting checkpoint92d6f40fde2b7b5f9944d286a42ad2a6e897af4b; base mainbdff4e1acd117dc92aa6aa66bb687dc52cdfcbb7.
- Retained baseline source9c83611e8e9b61d55388c18496c361d3362e462e/engine8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a,
  ROM6b7a83f27ede2dac9a124c0e267f34c9d0747db4a68cff05425fb9966f5b2459,
  actual ELF1bc654d935e262489c3e073225394ebf99732b0452eb311025b9e5fee0059cdc.
- Candidate source807eeea457c973b097be9eab9e1556e20d0204aa/engine3ef0d46368e45c3e4a5b8084eeec2a81b50a688b,
  ROM3e6fa891385e38a900fa307660bc8916f8f0b9776098a76378f27e238d962248,
  ELFc5f7e26472f61831bf0166086ef86f42ccdedb615044b3a8e7e7bc9bc939d653.
- Actual retained observer C564c8b04c4ab6e8ef1efb9a5d846ff1934525f9b64e647b0c0db69b23ecf8732,
  binary39a6ad526bee8c3550ddfe2566bbdcc9c24b1307aedeeaa8c124593c07e79429.
  New compiled host identities are in [host proof](terminal-retention-proof.json);
  it has no runtime claim. Routef03cae6c47e866b49209f1a78f6fd2ca34e1653084422b5bab7c3c1e7175b3fa unchanged.
- All frozen tool-file hashes verified: GCC14.2.0; ARM binutils2.44-3+23+b1;
  agbcc sourceda598c1d918402c42c0c0d7128ba14567f3175e9;
  libmGBA0.10.5/a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63.
  Recovered compiler binaries differ from historical; no original-tool identity.
- Save53f62dc2e283d89236d5572f47c3e7449c0bc1c06de738b1427fc9664ae67eb6 and old
  STOPs/archives/strict streams retained. [Preservation hashes](preserved-identities.json).
  Actual prior [STOP screenshots/motion](../retained-baseline-candidate-20261010/README.md)
  remain bound to original tested identities; no new captures or hint visibility.

Private audit/build/disassembly artifacts are local under the64MiB offline cap.
Archive retention is reported separately in the receipt. Prior raw evidence,
builds/tools and Saves remain local, not independently backed up. Library five
upload failures plus one supported download failure, unknown cause/zero recovered
original bytes, are preserved; no retry. A user-selected private export with
destination hash verification remains an option, not a completed backup.

C01a counts remain4 baselines/1 candidate/5 processes. Historical V01 6/4 with
STOP117 before expectedB8402/requestedvisual8536, new accepted pair1/1 and ordinary
recovery5 are unchanged. No candidate runtime acceptance, legacy/original oracle
recovery, human/pacing acceptance or full-floor completion. Accepted bounded
nine-district Book1 plan and both orders/optional skips remain separate gates.
