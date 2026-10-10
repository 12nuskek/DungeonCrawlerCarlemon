# Proposed C01 uninterrupted ordinary unprepared opening/resource evaluation

**Review proposal only: not frozen, compiled or executed.** PR115 Journal
integration closes its scoped optional-notes acceptance, not C01 or G02. This
next task measures a complete ordinary unprepared D1 run before the prescribed
prepared route. No gameplay or execution claim is admitted by this document.

## One continuous ordinary run

Start an empty Save through native New Game and stay in one emulator process
through opening checkpoint/manual Save. No intermediate Continue, reset, Save
import, savestate, injected party/resources, RNG inspection/search, retiming or
automatic retry. Ordinary manual Saves may occur at existing save opportunities,
but neither stopping nor reloading them may bridge the run. A later cold process
is a separately claimed persistence check, never part of continuous gameplay.

Freeze these decisions before execution:

1. Inspect the opening note, claim the one-time ordinary two-Potion supply, and
   follow the authored path to Quiet Landing. Meet the guide and take normal
   free recovery. Skip optional equipment, quest/trap/secret/cache/crafting and
   the return loop; keep preparation46 unset. The existing Journal remains
   available; do not replay its already accepted isolated notes tests here.
2. Complete trial855 with the existing offensive controller and its fixed
   readiness-aware12-frame button cadence. Claim the existing two-Scrap rack
   reward, use exactly one earned Potion on Donut via native Bag/party controls,
   then recover at the guide. Preserve the source-supported item-use assertions;
   do not substitute invented post-battle wounded HP/PP.
3. Guard856 first, then Howler857, with the reviewed offensive decisions and
   ordinary guide recovery after each. Follow the existing legal anchors and
   measured recovery legs. No extra encounter, item intervention or optional
   resource expenditure. Assert no rematch/repeated XP/money on resolved talks.
4. Approach Warden room35,3 at(8,7); actual facing recorded. Require trial/patrol
   wins and no preparation/boss/checkpoint. Engage unprepared858 exactly once;
   the native flag46 branch must not select prepared859. Use the prescribed
   fortify decisions: BRACE/WEAKEN for turns0–2, then existing offence and Donut's
   native depleted-SPARK fallback. Keep target choices and12-frame cadence;
   do not tune them to historical HP, turns, random outcomes or Save bytes.
5. Require actual victory/no incapacitation under the reviewed one-attempt
   contract; record real wounded HP/status/PP. Verify earned rewards and resolved
   repeat without another battle. Take actual staircase No then Yes, acknowledge
   the opening checkpoint, and manually Save at the legal35,4 review location.
   No post-victory guide heal or supplied resources. A failure stops the run and
   blocks any dependent cold or prepared attempt.

Existing decisions come from `scripts/test-f1-ordinary-recovery.py`, its committed
fresh-trial route and ordinary setup generator, unchanged
`scripts/contracts/f1-g01e-guard-first-current.route`, and
`docs/floor1/g01e-warden-first-clear-contract.md`. Their prior staged/cold boot,
process exits and input imports cannot simply be concatenated into acceptance;
a new source-bound continuous host/route must explicitly replace those handoffs
while preserving all gameplay decisions and gates. This is a new ordinary input
trajectory; historical RNG/Save/HP equivalence is not an expectation.

## Resource and action measurements

Record before/after each encounter, item use, reward, recovery and Warden approach:
full six-slot party/count, all six checksums and native reencoding, HP/maxHP,
status, level/XP, each action's PP, friendship under the native walking/level
model, exact counter, all flags, every bag/PC slot and money/coins. Preserve the
actual encryption context privately; compare logical quantities and exact party
bytes outside declared native mutations. Do not allow blanket friendship masks
or read SaveBlocks during relocation/rekey phases.

At each turn log actor, selected move/target, actual PP use, damage, support stage
before/after, fainting, and any ineffective support turn at the native stage cap.
Measure Donut's turns without offensive PP, STRIKE/BRACE versus SPARK/WEAKEN
choices, recovery count/travel, actual active movement frames, combat/text/menu
frames, and usable resources at each recovery interval. Separate technical frame
durations from player decision time; scripted success does not establish engaging
choices, ordinary-speed human comprehension or a mistake margin. Report actual
costs and remaining margin; no numerical balance change is preauthorised.

Source-derived XP/reward checkpoints: trial495/805 (levels9/9); Guard adds132XP
each and320money; Howler adds121XP each and360money; preboss748/1058 (11/10).
Guide recovery restores full health/status/PP8/40/2/40 only through its native
script. With the prescribed one Potion use, preboss Potion1/Scrap2 follows earned
rewards; other inventory must remain exact. Unprepared Warden awards226XP each
and360money, giving974/1284 and levels12/10, with unprepared trainer2138 and
boss47 set, prepared2139/preparation46 unset. Confirm these against merged source
when freezing; post-victory HP/status/PP and actual counter/friendship are observed,
not copied from a prior Save. Checkpoint48 changes only on native staircase Yes;
no full-floor completion or later milestone is granted.

## Source-proven handoffs needed before freezing

Bind symbols and scoped function ownership to the actual tested ELF. Battle
inputs belong to `HandleInputChooseAction`, `HandleInputChooseMove` and
`HandleInputChooseTarget`, with the native actor/cursor/PP/turn/outcome gates.
Retain whole-battle entry/interior/exit counting and a single absolute guarded
frame driver, including text, walking, menu returns and Save frames. Warden's
30,000-frame whole-battle ceiling remains; earlier offensive bounds remain
36,000 each. Proposed whole-process ceiling100,000 frames is an independent
first-failure bound, not permission to relax any encounter limit.

Native Bag task creation is insufficient: require running `CB2_BagMenuRun`,
setup/fade completion and exact item context, then the running scoped party
callback before targeting/healing. Retain Summary ownership where used.
Field SaveBlock reads require `CB1_Overworld`, `CB2_Overworld`, `VBlankCB_Field`
and no battle; preserve anchors and defer during copy/rekey. Native text uses
compiled message identity plus printer readiness. Yes/No uses the actual task
and source-defined input delay, followed by native acknowledged result and
field-control return. Manual Save requires native completion, sector checksums,
full saved/live decoded equivalence and legal field location before exit.

Reuse verified source/build/tooling and existing native ABI/phase/menu/friendship
helpers; no repeated engine import or game rebuild if exact identities still
match. The currently tested game is4a92a9de70848b9d7275f9f255bb0d2f53232ab8,
engine tree0fedd142f43f136ceee189c54101b095fc88f495. ROM/ELF pins are in the
Journal build receipt. The integration commit and new host/route/observer binaries,
all source/tool/dependency hashes, offline negative guards and complete route
assertions must be pinned before the new claim. Existing exclusive runners and
claims remain untouched; never call them to obtain this run.

Proposed separate private output `c01-uninterrupted-unprepared-r1`; exactly one
exclusive opening-run claim, not another C01a baseline/candidate/field probe.
No claim or directory has been created. Bound storage before launch:12GiB total,
2GiB per file and32MiB logs; full trace/state measurements, named native240×160
captures, streamed motion at native frame timing in bounded chunks. Choose and
freeze the capture cadence/retention plan and verify its worst-case estimate
against available storage. Prefer tested lossless streaming over retaining
100,000 individual PPMs. Never drop captured frames or weaken trace/state gates
to fit; fail admission if the bound/tooling cannot be proved. No backup upload
until separately approved and verified.

After all continuous-run and manual Save checks pass, a separately frozen cold
contract may verify the actual new Save without battle/heal/new Save. The later
prepared route retains the prescribed earned workshop craft/cache
decline→accept→repeat, prepared859 offensive decisions,30,000 whole-battle bound,
192XP each/320money, actual stairs/Save and independent native-phase cold checks
from `docs/floor1/g01e-prepared-persistence-contract.md` and
`g01e-prepared-cold-phase-contract.md`; it requires its own reviewed start and
continuity scope, not an automatic launch from this proposal. Both patrol orders,
optional skips, original legacy inputs/oracle and normal-speed human/full-floor
gates remain open. C01 acceptance and G02 readiness require their remaining gates.
