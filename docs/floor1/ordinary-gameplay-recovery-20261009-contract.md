# Ordinary gameplay recovery — replacement workspace contract

Status: **terminal preparation STOP before host compilation/gameplay**. The new
source verifier failed at engine/asmdiff.ps1 because it compared raw Git bytes
with the pinned CRLF archive representation. Read-only diagnosis found only
explicit attribute-driven CRLF transformations. No retry or executable freeze.
[Exact build/stop/diagnosis](../evidence/floor1/ordinary-recovery-20261009/build-r4/README.md).
A separately reviewed archive-attribute-aware source check and new prepare claim
are the next dependency; the successful single game build should be reused.
This prospective contract replaces only its previously blocked draft. Historical contracts and executions remain
unchanged. Kurt authorized the replacement on 9 October 2026 at 23:29 UTC;
accepted tooling-r3 identities permit this explicitly new ordinary recovery.
First unexpected failure is terminal; checkpoint before dependent gameplay.

Gameplay source is integrated main c6d647a815ffce44a2419a2cf83b6c2c094359f0,
engine tree 76001ee128785714b7c15aef6d9c95630587d0a9. Publication starts from
PR114 head 5b1c108557ecdb2704dea94c61aff1fb28845acd, retaining its active-pose
engine 8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a. No engine edits or merge.
Actual new ROM SHA256 ae1e9d36a94ed2eaa9d8fc79d790a2dc47173b932551891d889c657e12ca8461;
actual new ELF SHA256 6e56b32192e1a861b39c70e62bb5c43e762b9f5cc8ce0389d3cb494c3ee6dde6.
The ROM equals the recorded integrated gameplay ROM; the ELF differs. Neither
fact establishes original compiler binary identity or transfers acceptance.

The single build used GCC 14.2.0, ARM binutils 2.44-3+23+b1, agbcc source
da598c1d918402c42c0c0d7128ba14567f3175e9 and recovered compiler binaries:

- agbcc: 0eb17d598f1e7318a1ad7aa9864480fcc8d30d29c3a855d7f43c01909277158f
- old_agbcc: e3dc2daec27cf4bd23172905631c3937e0eba0c7cb2bcfdce2264559e7535f24
- agbcc_arm: 20c9d2f83f43a67c44eb6b16240a1702d5eb6d8fe1d1feebc3e04373b7d32f19

libmGBA 0.10.5 library SHA256 is
a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63.
[Tooling-r3 manifest and qualifications](../evidence/floor1/ordinary-recovery-20261009/tooling-r3/README.md)
records verified package/source hashes, dependencies and existing inih 59-1
library provenance. Historic extracted inih-library identity is unavailable;
its installed owner/version/current hash are frozen. This does not block this
new ordinary run. Historical binaries, inputs and oracle remain unavailable.

Archive the entire main source for native source-dependent validators. Hydrate
only the three recorded multiboot blobs from official pret/pokeemerald commit
731ad5bfd6e6f265508d0efcca0ba42f9dcf5881, checking exact Git blob IDs before use.
Freeze generated host/binary, actual ELF symbols, native compiler ABI constants
and bitfields, four routes, tooling/dependencies and encoder before execution.
Every tracked archived engine file is compared with main except those exact
hydrated blobs. Native friendship must use main pokemon.c SHA256
df008d2d381b70f30998e476ed1f7183871580ea037d0fc5832bea11beb9c064.

Use the separately named test-f1-ordinary-recovery.py and ordinary-recovery-host.py.
The reviewed historical host transformations supply input policy and gates;
no historical GAME/BASE/SEED pins, wrappers, claims, STOPs or routes change.
The main archived validators enforce complete native walking, friendship,
party/count, flags and logical resources for the reviewed patrol. Bag and party
inputs retain running CB2_BagMenuRun/CB2_UpdatePartyMenu readiness with actual
native task/fade checks. Preserve the inherited ordered duplicate task binding:
verify its final assignment is party_menu.o Task_DisplayHPRestoredMessage.
Four absent unused policy probes remain fail-closed. No assertion is narrowed.

One exclusive execution each, in dependency order:

1. Ordinary New Game; note, two earned Potions, guide recovery and trial using
   unchanged offensive policy. Manually Save. Expected trial result Carl/Donut
   9/9, XP 495/805, uses 3/40/0/37; trial set, patrol/boss flags unset.
2. Independent Continue; earned Scrap 2, actual owned field Potion on injured
   Donut, native menu return and guide recovery. Potion 1, uses 8/40/2/40,
   levels/XP unchanged. Move to guard approach (35,0)/(37,31), manually Save.
3. Reviewed Guard-first route, wins, repeat checks, earned rewards and full
   guide recoveries. Six exact measured travel legs retain existing ceilings.
   Manually overwrite Save at the reference endpoint.
4. Separate cold process loads the ordinary final Save, compares complete
   state and leaves its Save bytes unchanged; no battle or further gameplay.

Reviewed patrol route SHA256:
8de593f9f8c95fb52a1a63e4b104ee75d627670c2568a1dd6c41213c1ad175b5.
Reviewed cold route SHA256:
b042379c0f70dbba87e3f25f5fe66ce6384752ac9cafdea07d73d9de2823aa67.
Fresh/setup route bytes and hashes are frozen in identity.json before any run.
The source-derived XP transitions remain 627/937 after Guard, 748/1058 after
Howler; earned money +320/+360. No Potion rescue policy, grants, injections,
RNG/timing search, fabricated state or historical-byte forcing.

Reference endpoint is map 35,3 at (8,7), actual facing recorded. Source names
map 35,3 DCC_F1D1Warden; this is the approach position before any Warden action,
not the separately named workshop map. Carl/Donut 11/10, XP 748/1058, HP 38/30,
status clear, uses 8/40/2/40, Potion 1 and Scrap 2. Trial 2135 and patrol 2136/2137
set; preparation 46, boss 47, checkpoint 48, loop 49 and Warden 2138/2139 unset.
No Warden interaction, boss execution, later floors or candidate pair.

Before execution freeze output root
/workspace/scratch/ordinary-recovery-r4-20261010/runtime. Require empty output,
create-only execution claims, fixed dependencies and terminal STOP.json. Each
stage is at most 100000 native frames and 600 wall seconds. Fresh permits only
trainer855 once, patrol only trainers856/857 once each, each battle at most
36000 frames; setup/cold permit zero battles. No stage can be repeated.
Fresh free space check requires 7GB before each stage. Output bound is 13GB.

Capture actual route screenshots at existing route labels, plus stop frame on
failure. Passively sample RGB240x160 every four actual emulator frames, up to
25000 samples/2.88GB per stage. Encode lossless FFV1 at native speed
(16777216/1123584 sampled frames per second) without emulator replay. Freeze
encoder hash. Screenshots/motion are attributable to this new tested source,
ROM/ELF, generated observer, route, claim, actual Save and logs. They never
represent missing original captures. Raw RGB, ROM/ELF, Saves, full party/flags/
resource snapshots and private context stay workspace-local and unpublished.

Each actual manual Save must pass all latest14 native sector checksums and
complete live/disk equality of 600 party bytes, counts, 300 flags, 1272 canonical
owned-resource bytes, counter, map and position, with decoded member integrity,
no eggs/status problems and legal native field tile. Exact independent cold
compares the same full decoded state, records actual facing and verifies no
Save modification. Expected fixtures are offline comparison data only.

Preserve six historical baseline/four candidate executions, latest STOP117 at
requested visual8536 before expected B8402, exhausted controller/strategy
history and missing original runtime-reference/legacy inputs. Reconstruction
is not recovery of that oracle or legacy-save acceptance. Active-pose source
9c83611e8e9b61d55388c18496c361d3362e462e remains compiled/offline-only without
runtime acceptance. No full-floor claim or PR114 merge. Stop at this checkpoint
for review; a later separate baseline/candidate contract needs its own review.

Five failed Library uploads and one failed supported existing-backup download
recovered zero bytes; cause unknown. Do not retry them. Local bundles and new
private evidence are not verified independent backups. Preserve raw evidence
and offer a local verified archive; do not claim attachment backup.
