# Full Floor 1 execution

Execution authorised by Kurt on **2026-10-07 03:42:58 UTC**:
> ok plan limits are reset are we ready to begin? I dont want to have to confirm with you anymore for blobs etc just keep going til its done

This supersedes the prior playtest/Stage6 pause, planning-only restrictions and
fixed overnight window. Complete the bounded nine-district Floor1, with the
opening spoiler ceiling, GBA/pinned Emerald, permanent duo, no collection,
accessible recovery and private delivery unchanged. No later floors, public
release, new scheduler, purchases or incompatible save reset. Routine reversible
implementation, asset work, builds and verified scoped PR merges are authorised.

The [complete accepted plan](accepted-plan.md) is copied from
https://chatgpt.com/space/page_299ca9888dcc81919db9c00b90ca1e97 on2026-10-07,
including the parent's execution-authorisation update. Original Page Markdown is
preserved verbatim. The initial handoff named sequence9; the refreshed read exposed
no sequence field, so no later sequence number is invented. Repository docs now
carry the working checkpoint; subsequent plan changes require deliberate reconciliation.

Delivered baseline main3f1c851cce076b51cf4eb174925d9a2e41777a1f, game testeaf073d,
ROM8e7e8c20c8dde66488d9374ec90e80391a02c255ad4a0a422e7392f04f1ccfb6,
private ZIP34b4e0694a1f78236fa3c7a74d3f0001591d4c845455159dae2b493a69e92826.
Both readable local artifacts were rehashed successfully; original sources, saves,
90-session/1531-check evidence and private Library history remain preserved.
No import or baseline build repeated. Executor has Bash/Git/GCC/ARM binutils,
pinned agbcc and mGBA0.10.5;9.5GiB free at launch. No open PR/issues before issue53,
no workflow files, no returned PR-triggered CI runs, no .agents/skills directory.
Historical branches remain intact. Parent owns continuation; no schedule added.

[Baseline register](baseline-register.json) records all six old map headers,
layout IDs, exact map words/collision edges, object local IDs, warps and events.
It is an inventory, not a finished relocation map. Destination anchors and migration
remain pending reviewed D1 geometry. Regenerate using
`python3 scripts/floor1/audit-baseline.py`; it reads the immutable delivered commit.

The current map buffer holds10240 u16 cells (20480 bytes), including padding
(width+15)*(height+14). D1 64×48 needs4898 cells;72×56 needs6090. This arithmetic
permits investigation, not runtime acceptance.16 active objects include the player;
64 saved object templates,512 primary+512 secondary tiles and13 BG palette banks
remain allocation limits. Connections/camera/event and graphics peaks must be measured.

Before new maps/encounters, replace implicit group/range membership with explicit
crawler-map and encounter classification. Presentation/markers currently key on
mapNum and must use full map identity to prevent cross-group collisions. Migration
must cover mapLayoutId, player/object/template positions and IDs, saved warps and
idempotent save/cold reload. Numeric UNUSED aliases at0x23–0x30 are already owned
by DCC and cannot be treated as free. The old completion flag retains its meaning.

Library references resolved successfully, but consumer materialization is blocked:
first supported invocation lacked a bundled companion; the companion was obtained
unchanged, then the current downloader failed `hosted apps tools/list request
failed: network` before any file transfer. No art bytes inspected/accepted yet.
No guessed URLs, manual download or workaround publication. Preserve this blocker;
continue source/graybox work. If parent stages assets, first commit/push and explicitly
pause repository writes for that handoff. Generated concepts are never collision
or runtime evidence. No human playtime/comprehension is claimed from automated input.
