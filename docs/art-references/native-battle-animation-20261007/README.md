# Native battle keypose candidates

Prepared 7 October 2026 for DungeonCrawlerCarlemon. Art preparation only. This is a reviewable native candidate package, not finished animation, an engine patch, a ROM, or evidence that the game displays these frames correctly.

## Contents and source identity

- Carl: STRIKE anticipation, contact and recovery; BRACE set and guarded hold. Three-quarter rear, right-facing; bare feet, brown hair, white/cream heart-print shorts.
- Donut: SPARK anticipation, cast and recovery; WEAKEN preparation and release; attention reaction. Fluffy tortoiseshell cat, gold collar and small teal jewel. No tiara.
- Warden: idle, windup, raised warning hold, slam contact and recovery. Approved armored front-facing adaptation; no rear view is invented.

The selected generated Carl v2, Donut v1 and Warden v1 masters are reused byte-for-byte by relative repository references in input-references.json. They were staged in [PR 58](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/58). The original approved native sprites are reused by relative repository references; nothing accepted was overwritten. Baseline provenance is recorded in provenance.json.

There was one built-in image-generation correction to Donut's two WEAKEN cells to harmonize their camera angle and scale with the SPARK reference. The corrected master remains unstaged while its platform upload is pending. Its exact prompt and source hashes are retained; the two derived WEAKEN PNGs can be validated independently. Only the corrected lower-left/lower-middle cells are used. Original SPARK and attention cells come from the original master. The resulting WEAKEN angle is visibly closer, but not mathematically identical to every SPARK pose.

## Native authoring and checks

Each pose is a distinct 64x64 PNG encoded as 4-bit indexed color. Index 0 alone is transparent; alpha is binary. Frames share their character's existing approved 16-entry RGB555-compatible palette, unchanged, with at most 15 opaque colors. Do not substitute a different character's palette or modify the shared palette.

Conversion is source-constrained native authoring: isolate the main alpha>=128 sprite component; ignore all RGB hidden under transparency; map opaque source pixels to the existing palette; vote source color clusters into a fixed per-character scale/anchor; set a binary silhouette and one-pixel contour; consolidate isolated dithery color pixels; restore source Carl eye/knuckle details and reshape interior existing heart motifs into native tiny red V marks. No new poses, in-betweens, magical effects or anatomy were painted. Exact feature edits and their rationale are recorded beside the script.

Each character uses one fixed scale throughout the sequence, rather than fitting every pose independently to 64x64. Pose-specific source foot/pelvis anchors register to Carl (27,61), Donut (42,61), Warden (32,61). Pose shape, crouching and extension still alter occupied bounds. The manifest records source hashes, crop bounds, anchors, palettes and final native bounds. The complete local source package passed252 checks before staging. This partial repository package passes250 native/input checks; corrected-source bytes are not present or verified here. verification.json distinguishes that limit.

Verify staged native assets:

    python verify_candidates.py
    python verify_staged.py

Full source regeneration with convert_candidates.py intentionally refuses before output because the corrected Donut master is absent. The source hash in pending-source.json is provenance, not proof that the missing bytes exist. Do not claim full source reproduction from this tree.

Dependencies: Python 3, Pillow, NumPy, SciPy. Scripts only read/write this art package. They contain no engine changes, repository operations, network calls or emulator commands.

## Placement contract, not gameplay acceptance

Source-ready candidate sprites end at y61 and leave rows 62–63 transparent. All sprites leave at least one transparent row/column around the canvas; no limb or tail is clipped. Carl's source bounds span x2–59 at maximum extension. Donut's widest pose spans x6–53. Warden's source raised hold occupies x11–53, y9–61.

The current opponent exporter requires the first eight rows empty and lifts each battle frame eight pixels for HUD clearance. All Warden source candidates satisfy this. The explicit prospective *-runtime-lift8.png variants apply that exact shift without scaling or recoloring: feet end at y53; raised hold top is y1. They are already shifted. Do not pass those variants through another eight-pixel lift. Current Carl/Donut exporter does not apply this lift.

This checks only canvas math. Battler screen coordinates, palette allocation, overlap with the duo panels, frame swaps, memory/compression budgets and camera behavior require the sole implementation writer's later engine/runtime review. No actual 240x160 battle capture was obtained or compared here.

The current binding audit is descriptive: Carl uses Machop front/back paths, Donut uses Meowth, Warden uses Loudred. Front animated art paths remain 64x128 static duplicates today. Trainer and icon consumers also reference these palettes. This package does not change any binding or declare these pose stacks drop-in replacements. Arbitrary multi-pose stacks require deliberate integration; the runtime will not gain battle-action animation merely by copying a PNG.

## Review and timing

Review images/HTML/GIFs are omitted from this small partial staging. build_local_preview.py can produce art-only previews locally from the staged native PNGs. These are local visual aids, explicitly not an emulator.

Timing-proposal.json suggests 60Hz holds: STRIKE 7/5/10 frames before rest; BRACE 8/24/6; SPARK 8/10/12; WEAKEN 8/10/10. Warden WIND UP suggests 6 idle / 10 windup / 24 warning hold. The warning hold may persist until the existing SLAM turn. SLAM suggests 8 held warning / 5 contact / 12 recovery / 24 idle. These are proposals, not implemented hit timing or new action rules. Repeated rest/hold poses are holds, not newly authored motion.

## Honest quality limits

- This is coarse keypose motion. No interpolated walk or attack frames, temporal pixel lock or smooth animation claim.
- Source anatomy and garment/fur markings vary slightly between poses. Consistent scaling/pivots prevent automatic scale jumps, but do not prove anatomical consistency at every pixel.
- Carl's tiny native heart print reads as red V/heart-like marks, with partial edge motifs retained. Skin shading is simplified by the accepted palette.
- Donut's corrected WEAKEN gesture remains subtler than SPARK; collar/jewel and paw silhouettes survive, while tiny whisker/digit detail is intentionally simplified at 64x64.
- Warden body art is narrower/smaller than the accepted static native baseline to fit its raised hands in the same frame with the existing eight-pixel HUD lift. Its hold/slam silhouettes are distinct; whether that scale feels right alongside the party requires live review.
- Existing approved palettes are preserved across the candidates. A future recolor or replacement of shared front/back/icon/trainer consumers needs its own integration audit.

This added-only reference package changes no game code, approved art, runtime binding or save format. Keep these candidates separate from accepted assets until the sole writer reviews and coordinates integration. Actual emulator screenshots: N/A for reference-only staging. No runtime acceptance is claimed.

## Repository staging

Exact base: d2c6a8545db4175718bfde87a272b515296d81a9. New directory only. Input paths are relative to this package and resolve in a normal repository checkout. Native-asset verification does not require Library files or private source paths. Full source regeneration remains unavailable for the missing corrected Donut image. package-inventory.json and verify_staged.py cover staged payload bytes and decoded native pixels. No ROMs, saves, build products or archives are included.

Partial staging: sources/donut-keypose-correction-v2.png is deliberately absent. No archive, re-encoding or substitute source is included. Existing master references, original SPARK/attention inputs and exact native palettes are preserved. All derived native PNGs retain their original byte and decoded-pixel identities.
