# N01 native kit: partial publication

Supports [N01 issue #35](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/35).
Only new files under `docs/art-references/environment-native-candidates/` are staged.

- Target: `task/n01-dungeon-materials`.
- Exact base: `24eef764e51d7bd6f70ba99e21744161dd92e302`.
- Original art/research baseline: `bf27e2692025eb4291ffbf992a3b6412340d32cd`.
- Original ZIP SHA256: `2995d794e4821d4c00c04a23d392eb47f46e473506d886635445f1dfabc49347`.
- All 119 original checksum entries and 120 decoded ZIP entries passed locally.
- The complete local delivery reproduced 109 outputs in two fresh runs, each
  passing 721 static checks. This is historical local evidence, not a claim that
  this partial published tree can perform complete source-sheet reproduction.

## Present and absent

All 91 native PNGs are present: 56 architecture tiles, 14 shared-palette props,
20 BG prop variants, and the packed PNG atlas. Exclude the two pressure-plate
alternatives in each prop family: 12 shared props and 18 BG variants are recommended.
All palettes, six previews, native manifests, exact prompts and three original
generation scripts are present. Shared OBJ and original BG palette values match
`scripts/content/slice_art.py` at the staging base.

Two files remain absent pending publication:

- `native/background-tiles.4bpp`: optional 7,360-byte packed diagnostic tile output.
- `source/environment-props-reference.png`: original 1,424,228-byte main prop source.

Their hashes and roles are in `package-status.json`. Neither absent file is
included through another encoding or archive. The accepted native PNGs can be
used independently. Complete source-sheet reproduction is unavailable until the
main source PNG is supplied; the historical reports are labelled accordingly.
Copied research snapshots and regenerable crop intermediates are also omitted.

## Current-tree checks

With Python 3.12.14 and Pillow 12.3.0, run from this directory:

```sh
sha256sum -c SHA256SUMS
python3 verify_staged.py
```

The verifier checks staged checksums and actual 4-bit PNG encoding, 16-color
palettes, alpha and all 91 decoded identities. It then runs the original 721
static checks using copies of the native files in a temporary directory. Generated
diagnostic outputs stay temporary and are never uploaded by the verifier.
No game checkout or network is required. It does not replace missing source data.

Screenshots: N/A for this reference-only change. Previews are not emulator captures.
Engine compilation: N/A. Integrated: NO. Runtime verified: NO. No existing engine
assets, maps, state, palettes, protagonist/opponent art or files are changed.

## Integration acceptance

Inspect selected native pixels, establish one authoritative export pipeline,
preserve approved OBJ art/palettes, and run N01's map/event/behavior/art invariants.
Then verify a clean committed build with matched real room/menu/battle/transition
and cold-reload captures. New state bindings or collision/layout changes require
separate gameplay acceptance. Keep N01 open until verified integration.
Source provenance does not establish clearance for the underlying adapted IP.
