# Derived Donut native source master

Publication clarification — 2026-10-09: routine source/documentation/art Git blobs are authorised and the original offline checkpoint0d9e93f5 is published through existing draft PR114. The local-only wording below records its initial offline authority, superseded for this publication only. ROMs/playable releases/secrets/private raw diagnostics remain excluded; runtime binding and gameplay remain unstarted. Offline source, tests and derived pixels are unchanged. See docs/evidence/floor1/v01/battle/native-boundary/publication.json.

This local source package is derived from ten verified native indexed PNGs at
checkpoint a86ceca9a3e642e87d3319e7072d35fd9adea21a. It is not the original
illustration, a new generated concept, newly authored art or new approval.
`master.json` records each exact source/hash, pinned Git blob verification,
dimensions, indexed-pixel hash, palette and recipe identity. Six source PNGs
(battle rest plus five actions) also match the frozen V01 battle asset manifest.

Dot means transparent palette index0; hexadecimal1–f preserves the original
index. The text files preserve every native pixel, including duplicate animation
frames and atlas layout. `palette.json` preserves all48 RGB bytes and index0
transparency. No drawing, resampling, recoloring or integrated asset write occurs.

Reproduce into separate new directories:

```sh
python scripts/content/donut_source_master.py derive --output /tmp/donut-master-copy
python scripts/content/donut_source_master.py rebuild --master /tmp/donut-master-copy --output /tmp/donut-native-copy
```

Two derivations'12 definition files are byte identical. All ten PNG exports
roundtrip exactly: original PNG file bytes, every indexed pixel, full palette,
transparency, dimensions and RGBA bytes. Results are in `roundtrip.json` and
`reproducibility.json`. No emulator was run. Existing candidate battle visuals
remain unverified because the candidate stopped before poses/readiness/actions.

The normal.pal checkout uses CRLF by .gitattributes; its pinned Git blob uses LF.
Both source hashes and that text-only provenance distinction are recorded.
RGB palette values and all native PNG blobs are exact, without normalization of
any pixel/palette byte. The initial strict file-hash assertion caught this EOL
distinction; that offline diagnosis is retained in the native-boundary package.

This package and checkpoint remain local under the no-public-upload instruction.
The exporter refuses integrated engine output directories. No generated PNG,
ROM, Save or denied raw runtime dataset is committed in this package.
