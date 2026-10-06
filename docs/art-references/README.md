# Carl and Donut source references

Generated on 2026-10-06 with the built-in OpenAI image generator. These proposed
reference sheets preserve the approved character direction for the S02 native
sprite pass. They are not gameplay screenshots, indexed GBA-ready sprites, or
proof of visual acceptance. No underlying character-IP clearance is asserted.

## Package

- `carl-donut-proposed-replacement-reference-v2.png`: battle identity and front/back
  references, original 1254×1254 RGBA output (947,534 bytes).
- `carl-donut-overworld-proposed-reference-v2.png`: exploration direction and
  movement references, original 1086×1448 RGBA output (968,151 bytes).
- `INTEGRATION_HANDOFF.md` and `OVERWORLD_INTEGRATION_HANDOFF.md`: provenance,
  source extraction bounds, engine contracts, known defects and native-art tasks.
- `generation-prompts.txt` and `overworld-generation-prompts.txt`: exact prompt
  intent for both two-pass generation workflows. Generation is nondeterministic.
- `SHA256SUMS`: hashes of the seven files above, for byte-exact verification.

The battle composition was prompted without third-party image inputs; exploration
used that generated battle sheet as its identity/style reference. The reference
PNGs are preserved byte-for-byte. Both require deliberate native-resolution
redrawing/cleanup and palette conversion. In particular, exploration row 3 column
3 faces right and must be corrected for the left walk cycle; Donut's back view
meets the bottom boundary; proportions, alpha and color budgets require correction.

## Scope and verification

Base: `2c082b499b138ec936eab8bc9f51f318faf49be9`, the inspected head of
[S02 draft PR #27](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/27).
Task: [S02 issue #26](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/26).

This package adds only files under `docs/art-references/`. It changes no engine
assets, generators, code, palettes, save formats, workflows or gameplay evidence.
Both PNGs were opened for visual review and validated as readable RGBA PNGs with
expected dimensions and hashes. Run `sha256sum -c SHA256SUMS` from this directory.

Build and runtime tests: not run for this docs/reference-only package. Emulator
screenshots: N/A; no runtime change or acceptance claim is made. The existing
[S02 runtime report](../evidence/s02/README.md) documents the prototype and its
failed visual acceptance; it is not evidence for these replacement references.
Implemented: reference package only. Compiled: N/A. Runtime verified: NO.
Native replacement and S02 visual acceptance: PENDING. Merged: NO at staging.

Next action: the sole S02 integrator obtains this commit, checks the hashes and
actual pixels, authors coherent native battle and overworld masters, wires the
reproducible generators and palettes, and runs the required isolated build/runtime
suite. Record the exact tested implementation commit and actual battle, summary,
walking and Donut-scene captures before claiming visual acceptance. Keep S02
unmerged and dependent S03 gated until the required review is satisfied.
