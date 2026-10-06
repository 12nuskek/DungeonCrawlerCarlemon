# B03 permanent crawler and collection boundary — 2026-10-06

Implemented YES / compiled PASS / runtime PASS / integration tracked in
[progress](../../progress.md), [issue #14](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/14).
Base `4c76d692b37a2fa934e89e4b057e0b83568e64f0` (B02 PR #13).
Tested commit `769196afc57635b98aa2de8b9ddc43ed1847a4ef`.
Production ROM SHA256 `8ffe93dde477e54c9d23a52532e73b1ca7087595250afc3b8b0ed16384256f2d`.
Actual mGBA 0.10.5, 240×160 framebuffer, normal inputs and real flash saves.
Final isolated run: `artifacts/b03/run-OR5Jqi`. No binaries/saves distributed.

## Reproduce

Use the environment variables/dependencies from [B02 evidence](../b02/README.md)
and [testing](../../testing.md), but run `bash scripts/test-b03.sh` at this tested
commit. The runner archives the committed source, rebuilds the pinned toolchain
and all game products, builds the host harness with warnings as errors, then runs
seven production routes in separate emulator processes. The eighth route uses a
separately patched, separately hashed GBA fixture. Full raw logs are retained;
native trailing whitespace has not been edited. All eight emulator error logs
are empty. Screenshots are lossless conversions of actual framebuffer captures.

The snapshot's final engine ROM is the **test fixture**, not the production game.
Build the normal checkout using README commands to play. A manually preserved
local `artifacts/b03/run-OR5Jqi/production.gba` has the recorded production hash;
it is ignored and is not included in source or public release artifacts.

## Results

| Route | Assertions and result |
| --- | --- |
| setup | 16 PASS: fresh game, authored movement/interactions, reciprocal maps, save |
| menus | 14 PASS: fixed-order roster, Summary/Item actions, field inventory 0→2→3→4→0 and reverse, unchanged duo/resources |
| battle-menu | 10 PASS: battle inventory skips capture pocket 0→2→0; returns with battle/PP unchanged |
| guide-before-trial | 10 PASS: guide dialogue, healthy party and all four resource slots |
| support-defeat | 19 PASS: both support effects; Donut 0 HP while Carl acts (BRACE 33→32, Donut WEAKEN remains33); both down, local recovery of HP/all uses, movement and retry |
| depletion-victory | 28 PASS: direct actions, empty SPARK refusal/alternate WEAKEN, victory, guide restoration, return route and save |
| reload | 10 PASS: cold Continue retains victory/guide flags and all restored party resources |
| fixture | 3 PASS: policy mask127, healthy unchanged duo, unchanged 8/40/2/40 uses |

**110 assertions PASS.** Logs and routes provide behavioral proof beyond images.
`roster` and `uses` read actual party data, not stale battle PP.

Fixture mask127 covers seven groups: all capture item grants rejected; creature
gift rejected; scripted egg rejected; daycare deposit/egg leave exact party bytes
unchanged; otherwise eligible evolution/learnset blocked; actual capture opcode
rejects wild/trainer/Wally/Safari flags with controller idle and waits unchanged
when busy; ordinary Potion grant/remove still succeeds. The fixture runs compiled
GBA functions and deliberately supplies test state from game code. The host never
writes RAM. It is not a claim of naturally reaching capture in production or of
rendering the unreachable refusal message. See [audit](../../collection-audit.md).

## Reviewed captures

`start-menu.png`, `crawler-actions.png`: readable Crawlers/Inventory, no party
reorder or collection navigation. `battle-items.png` and `battle-skills.png` show
the 0→2 pocket transition, backed by pocket assertions. `carl-menu.png` shows the
new battle labels. `donut-down.png`, `carl-alone.png`, `both-down.png`, `recovery.png`
and `retry.png` illustrate the complete accessible loss route. Stock art, summary
species/type text, TM/HM/berry labels and bag graphics are explicit S02 placeholders.

First attempt at `a763280` correctly failed the old B02 exact-HP loss checkpoint:
this build's sequence incapacitated Donut first. The new route records the observed
sequence without weakening the permanent-duo/recovery checks. An exploratory
fixture link failed because upstream discards unused libc memcmp; explicit byte
comparison fixed it. Final committed isolated run passes all checks. Failed local
logs remain at `artifacts/b03/run-BsM18n`; no failed run is presented as acceptance.

Fresh milestone save required, no save-layout change or old-save migration.
Neither this task nor zero-status assertions prove nonzero-status curing. Remaining
S03 edges include total action exhaustion and depleted/immediate-defeat saves.
The Stage5 slice is still incomplete; R01 XP/equipment is next after B03 integration.
