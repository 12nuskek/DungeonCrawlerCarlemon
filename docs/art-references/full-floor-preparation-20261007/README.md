# Full Floor1 art preparation references

Selected source art prepared 7 October 2026, staged as reference-only input for the authorised nine-district Floor1. All image bytes are unchanged. These are generated concept/keypose masters, not runtime assets, collision plans, finished animations or emulator evidence.

## Selected material

- environment/: Service Room and Quiet Landing material/light concepts, exact prompts, and two genuine earlier 240x160 room reference captures.
- characters/: Carl selected v2 (STRIKE/BRACE), Donut v1 (SPARK/WEAKEN/reaction), Warden v1 (idle/windup/warning/slam/recovery), exact prompts and approved source PNG identity anchors.
- connected-layout/: selected opening-sector overview v2, included as a source dependency of the full-floor and district concepts.
- full-floor/: overview v1, orientation only.
- district-stitch-pilot/: D1 selected v2, D2 v1 and the unretouched 1:1 D2-north/D1-south stitched proof.

Source identities and exact checksums are in source-identities.json and manifest.json. Preparation-provenance.json retains historical generation/review records with private transfer metadata removed. The inventory is manifest.json. Historical prompt references to rejected drafts describe generation lineage; those drafts are deliberately absent.

## Omissions

Rejected Carl v1, Quiet Landing draft, opening-sector v1 and D1 v1 are omitted. The unused full-floor v2 prompt is omitted. Optional camera close views, duplicate references, base64 duplicates, archives and transfer receipts are omitted. No ROMs, saves, host executables, raw generated 4bpp or engine files are included. No new district-generation batch was commissioned.

## Verification

Run python3 verify_staged.py from this directory with Pillow installed. It checks every payload checksum and Git blob identity, PNG decoding/dimensions/modes, eight approved source identities, absence of private transfer metadata, and exact decoded pixels of both panels within the stitch. This is source-package validation only. Gameplay compilation/runtime checks are N/A; no runtime acceptance is claimed.

Base: 50bf6d99fdfc4cb3d1ce6799a327a9974e8b786f (PR56 task/floor1-t01-state-text). No existing repository files are changed. Native integration is a later implementation step.
