# Read-only G01e inventory — 2026-10-09

[Draft PR #108](https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/108) / existing [issue #106](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/106), stacked on unchanged PR107; open/draft/unmerged. Inventory source `ba2237c8f2a9b5e338528000293d1332ff26f7de`.

Parent PR107 review passed. Bounded prepared persistence is complete270+132;
historical failed cold25 remains failure evidence. Base/source checkpoint
1663abb05000374b03d0c0db3c78a974c87b3852. No game edits, build, emulator process,
route rerun, Save write or new combat claim. Screenshots N/A for this source/docs
increment; prior exact actual views stay linked in the requirement matrix.

[Concise acceptance matrix, smallest current check, integration and V01 path](../../../../floor1/g01e-acceptance-inventory.md).
[Actual count/ELF budget output](geometry-budget.json), [remote/PR/source reconciliation](reconciliation.json),
[source/asset command results](checks.log). No raw buffers, legacy saves, denied
dataset/ancestry or keys are added to this package.

```
live T = Field982 + Quiet115 + Workshop116 + Warden118 + Checkpoint118 =1449
closed =1440; opening9 gate cells adds9; provisional→live delta=0
8–12T =11592–17388; 10T=14490
25 actual-source occupancy-aware width probes pass
5084 ELF: EWRAM249704 (12440static remaining); IWRAM30892 (1876remaining)
```

Count reads actual collision/elevation bits and source-defined presentation,
subtracts fixed actor/prop cells consistently, floods every map, checks object
approaches and each declared width. All gates open; each map counted once,
no player subtraction or border padding. Unchanged geometry/binding-normalized
actors compared to99243073; exact engine diff to5084 is empty. Current ROM/ELF
rehash matches approved build23c77/cafc512. No current scene-peak relabelling:
G01d diagnostic observed peaks remain identified as such; V01 measures its
affected scene/battle allocation. Existing game compile reused, not rebuilt.

Reproduce only this read-only source/build inventory:

```sh
python3 scripts/inventory-f1-g01e.py \
  --build artifacts/floor1/warden-fairness/build/source/engine \
  --output docs/evidence/floor1/g01e/acceptance-inventory
```

Staged battle250native/180package checks, full-floor231, environment123checksums/
91native PNG identities/721static pass. Original Donut corrected source and main
environment prop source remain unavailable; independently verified native PNGs
remain available for integration. No new image generation or workaround.

Next only: parent-scoped current Guard-first order/travel/Save/cold from retained
ordinary reconstructedc11c Save, then reviewed protected merge-commit integration
including CP72e through PR91's explicitly reviewed bridge, then staged V01 pilot.
C01 uninterrupted/human pacing remains later. Original16legacy inputs/deleted raw
logs/original patrol-complete Save not recovered; fresh inputs never replace that
gate. No broader acceptance or merge here. Existing private saves/logs already
retained; this read-only increment creates no new private runtime dataset.
