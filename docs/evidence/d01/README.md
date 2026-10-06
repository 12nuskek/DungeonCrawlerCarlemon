# D01 optional quest, trap and secret

Integration update: merged PR #21 as `c42d444b8c2ae1b665105baad133094859bf8fa5`. Earlier pending labels below describe the verification-time checkpoint.
Test date: 2026-10-06. Issue #20; scoped PR integration pending.
Base `ae4679e2e19a94fd60ac879c9dd18e89f7de2c41`.
Tested `060864caa9aecfa48c38c810fe2a7f87895b308e`.
Production SHA256 `427c16b312869f2dd575bac6f0b736953c524bf96753273a88d2429444b0cfec`.
Explicit fixture SHA256 `9388b52f7b658eaf83843efd16179ffd6e393f2c638cd8d4f7c3f3dc02d07090`.
Implemented YES / isolated compilation PASS / runtime PASS / merged pending.

Run `bash scripts/test-d01.sh` with [toolchain variables](../../testing.md).
Committed-source archive, regenerated pinned compiler/products, mGBA0.10.5,
normal button input and read-only host assertions. 114 assertions passed:
84 production and30 explicit fixture. Seven empty error logs. Nineteen actual
framebuffer PNGs visually reviewed. No ROM/save/executable committed. The runner
preserves local production.gba before fixture generation; its final engine ROM is
the fixture. Build normal source for play, never mistake the fixture for gameplay.

| Route | Checks | Observed behavior |
| --- | ---: | --- |
| decline | 13 | Fresh entry, safe bypass, reserved tag, optional decline/save |
| accept-trap | 16 | Cold decline, ladder return/re-entry, accept later, warning, real shock, spent tile/save |
| tag-secret | 15 | Cold accepted/status/spent flags, secret once, tag once/save |
| complete-recover | 22 | Cold tag, Lev clue, turn-in/repeat, return, actual guide cure/save |
| reload-final | 18 | Cold completed state/items/cure, repeat quest/secret, no second trap damage |
| capacity fixture | 21 | HP1 trap boundary; full bag/Scrap98 refusal retains tag; toss1/retry grants2→99 |
| capacity-reload fixture | 9 | Cold completion/99/no tag; repeat preserves quantity |

Carl's HP30→26 and paralysis64 survive cold saves; guide restores30 and clears
status to0. Donut remains26HP. All four action resources remain intact. Quest
accepted/completed, found tag, secret and spent trap persist. Declining leaves
ladder access open. Completing adds exactly Scrap2 and removes key-item tag379;
repeats never add more. Secret adds one Parlyz Heal18. Full-capacity fixture uses
actual inventory APIs and normal quest/toss input; no production debug route or
host RAM writes. Other theoretical inventory-full branches are not all replayed.

Exploratory defect: coordinate events kept restarting on a spent trap, intercepting
START on that tile. First fix disables the temporary trigger immediately and seeds
it from the persistent spent flag on map load. The final cold routes prove the save
really occurs and the trigger stays spent. Earlier in-memory checks alone missed it.
No unresolved blocker. Fresh milestone saves required; no save-layout migration.

Original Mara/Lev scenes are neutral adaptation characters, not book-canon claims.
Cave/NPC/box/item graphics remain explicitly scheduled S02 placeholders. New map
and metatile .bin files are authored source assets. No crafting/boss or expanded
campaign is claimed here. Total action exhaustion remains later S03 coverage;
actual nonzero status curing is now covered by this production route.
