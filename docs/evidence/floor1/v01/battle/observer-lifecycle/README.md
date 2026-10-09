# Offline lifecycle checkpoint for PR114

**Implemented, offline tested and host compiled; zero emulator frames; draft
unmerged.** Parent review of this contract is the next dependency. No fresh
execution pair or automatic retry is authorised by this checkpoint.

The observer now qualifies ACTIVE → RETIRING → FIELD, keeps live ownership and
pixels strict, rejects copies sourcing retained retired picture ranges, requires
cleared native registries/candidate pose state, and proves subsequent native
field callback/rebuild/readiness cleanup. Pre-entry !inBattle supplies no exit
proof. Engine/route/controller/assets/bounds remain unchanged.

[Contract](../../../../../floor1/v01-battle-observer-lifecycle-contract.md) ·
[Native source references/hashes](native-source-review.json) ·
[11 scoped lifecycle functions in both pinned ELF builds](lifecycle-functions.json) ·
[Offline result](offline-result.json) · [Complete fixture log](offline-observer.log) ·
[Host and build identities](compile-identity.json) ·
[Actual history preservation](preservation.json).

The full native path was reviewed from trainer savedCallback through fast fade,
graphics/resources free, native no-evolution loop, ReturnFromBattle, trainer end,
script/music wrapper, local field states0..3, heap/graphics/sprite/task reset,
continuation fade task and script shutdown/unlock. CallCallbacks executes CB1
then current CB2 in one iteration: EndTrainer can select the wrapper before a
frame sample. The observer therefore proves the pinned saved trainer callback
and observed wrapper/rebuild, and separately records EndTrainer observation.
Verbatim native CallCallbacks/SetMainCallback2 are compiled in the offline case.

Offline fixtures exercise original readiness/symbol/pixel negatives, strict
live ownership during cleanup, all four live owners, registry loss outside
cleanup, cleared/uncleared pose and resource state, stale queued sources from
every retained buffer including boundary overlaps, phase regression/unknown
phases/callbacks, changed saved callback, native scheduler dispatch, skipped
rebuild, incomplete field return, locks/scripts/hooks/fade/fade-task readiness,
pre-entry false exit, and continued FIELD readiness. Baseline and candidate
retirement fixtures pass. Pinned agbcc native ABI compile also verifies
Main0/4/8/0x438, Task40/active4 and palette active byte7 bit7; see
[native accessor assembly](native-layout.s). Full host compiles with
`-std=gnu11 -Wall -Wextra -Werror -lmgba`, empty build log.

STOP105's actual actor/sprite/phase/copy projection is checked against its exact
diagnostic and baseline ELF identities. Cleared registry/resource pointers and
retained initial buffer ranges are explicitly modeled fixture values; they were
not separately serialized by the original run. Original actual STOP105 remains
a failure; no actual complete field return or candidate visual acceptance exists.

One initial offline fixture expectation failed: a source crossing adjacent
buffers correctly reported the earlier overlapping actor rather than the later
one. Its source/log remain local and in the private offline package. The test
expectation was corrected; no game execution or gate relaxation resulted. Other
offline outputs are retained under separate local roots. Final complete fixture
source is scripts/test-f1-v01-battle-observer.py; fresh-root offline invocation
uses `--output` and contains no runFrame interface.

| Retained actual execution | Partial assertions | Absolute / visual frames | Attempts / moves | Result |
| --- | --- | --- | --- | --- |
| d1dc4792, original north entry | 22 | 5685 / 3641 | 0 / 0 | STOP35 |
| cf726350, south entry | 27 | 4720 / 2676 | 1 / 0 | STOP107 |
| 8ee05954, native-ready baseline | 27 | 17032 / 14988 | 1 / turns0–8, six intended moves | STOP105 |

Each original claim/STOP/ordinary Save remains unchanged, candidate claim count
zero. STOP105's readiness3155, actor0/sprite9, empty queue, known baseline VRAM,
partial peaks and private actual clip remain in [original evidence](../observer-phase/README.md).
All original strategy failures/controllers, older visual failures and missing
legacy-input limitation remain distinct. The previously confirmed private
5999176-byte/15174-entry runtime archive already retains the ordinary Save and
actual logs/captures; this increment introduces no new Save or runtime capture.
Denied raw datasets/keys/.bin/complete symbols/executables/ROM/ELF stay outside
uploads. No candidate pose/HUD/warning/budget/matched-control/field-return,
first-clear, C01/human-pacing, legacy or full-floor acceptance is claimed.
