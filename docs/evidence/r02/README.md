# R02 achievements and deterministic loot

Handoff/test date: 2026-10-06. Issue #18; integration pending scoped PR.
Base `5a0fd8eaef6b4746c745e128bd9923f00afeeee0`.
Tested source `fbfb9e9cad1854b5b03e2a006d1ed1745348f365`.
Production ROM SHA256 `dec6f1db138ed1a622da477cf14495086fe5ea7c20ca9caaa6b5016a3f42ab32`.
Separate capacity fixture SHA256 `7fbcf9c7c4008ac17eaca206d36a3ec2831525f04bd335444e17f02bd2b23ed3`.

Implemented YES / isolated compilation PASS / runtime PASS / merge pending.
Run `bash scripts/test-r02.sh` with the [documented toolchain](../../testing.md).
The runner archives committed source, regenerates the pinned compiler and game,
and uses real mGBA 0.10.5 input-driven execution with read-only RAM assertions.
169 assertions passed; six error logs are empty. The 17 PNGs are actual emulator
framebuffers, visually reviewed. No ROM, executable, save or savestate is committed.
The local runner preserves production.gba before producing its explicit fixture;
the final snapshot engine ROM is the fixture, not the production game.

| Route | Assertions | Evidence |
| --- | ---: | --- |
| setup-rewards | 32 | Both boxes locked; note achievement, exact Potion2 award/repeat, save |
| victory-loot | 53 | Trial/XP, duo achievement/repeat, Scrap2 award/repeat, Potion2→1 healing, no-effect preserves1 |
| reload-reentry | 34 | Cold flags/items/XP/HP/PP, repeat both boxes across maps, guide recovery/save |
| reload-final | 13 | Second cold save retains all four persistent IDs, items, XP and restored resources |
| capacity (fixture) | 28 | All slots occupied/Potion98; real grant2 refuses atomically; toss1, retry grants2→99 |
| capacity-reload (fixture) | 9 | Cold flag/99 retained; repeat cannot duplicate |

132 production assertions and 37 explicit fixture assertions. The fixture changes
only isolated initialization, invoking actual inventory APIs; ordinary game input
then exercises the box, toss and save/reload paths. It is not a reachable debug menu.
Potion capacity failure is proven; other theoretical full-inventory branches are
not claimed individually replayed. Logs and routes accompany the screenshots;
screenshots alone do not establish persistence or atomicity.

Reader/duo achievement flags are 0x24/0x25; supply/workshop flags 0x26/0x27.
Rewards are optional and deterministic, with flags set only after successful grant.
Repeating after consuming a Potion retains Potion1 and Scrap2 rather than refilling.
Fresh saves required for this milestone; no save-layout migration is claimed.
SCRAP is reserved for D02 crafting, not yet usable. Stock box/item art, Pokémon
inventory wording and battle presentation remain explicit S02 placeholders.
Actual nonzero status curing and total action exhaustion remain later coverage.
No failed production fix or unresolved blocker. Replay timing was adjusted for
achievement pages and the full-stack toss confirmation; final isolated replay passed.
