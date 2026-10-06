# B03 collection boundary

Handoff 2026-10-06. Issue #14, base `4c76d692b37a2fa934e89e4b057e0b83568e64f0`.
`DCC_ALLOW_COLLECTION` is deliberately FALSE for this game, not a user option.
No save structure changes. Use fresh milestone saves; imported Emerald saves and
older map/object caches are unsupported, never silently migrated.

| Entry | Production boundary | Verification |
| --- | --- | --- |
| Ball rewards, shops, scripts | AddBagItem rejects every ball pocket item before capacity/quantity mutation | GBA fixture loops Master through Premier; ordinary Potion add/remove still works |
| Bag field/battle | Ball pocket normalized on entry and skipped in both directions, including wrap | Actual field menu route, pocket IDs 0/2/3/4; battle regression |
| Item handler | PokeBall handler displays original refusal before removal/action submission | Source review; no ball is obtainable in production |
| Capture opcode | Rejects before trainer, Wally, Safari, wild odds or successful catch paths; waits for controller idle | GBA fixture calls unchanged opcode for all four flags, idle and busy; no caught outcome |
| Gifts/scripted eggs | GiveMonToPlayer returns MON_CANT_GIVE before party/storage writes; ScriptGiveEgg funnels through it | GBA fixture checks both and exact unchanged party bytes |
| Daycare deposit/egg | Public entry functions return without touching roster | GBA fixture invokes both, exact unchanged party bytes |
| Storage PC | Public menu special resumes field/script without constructing storage task | Source review; no PC exists on reachable maps |
| Party reorder/release | Field actions are Summary/Item/Cancel; fallback summary action also has no Switch; release belongs to inaccessible storage | Actual roster/action capture and unchanged duo checks |
| Species evolution/learning | No evolution or automatic placeholder-species learned moves | GBA fixture uses an otherwise eligible level-28 Machop evolution and level-13 learnset |
| Capture tutorial/link/collection worlds | New-game route goes straight to authored entrance; no Wally, link or stock-world exit | Fresh-game and reciprocal-map routes; map audit |

The only reachable maps are group 34 DCC_Entrance and DCC_Vestibule. Their only
warps lead to each other. Scripts inspect props, give original dialogue, restore
the duo, set introduction/guide flags and run the deterministic trainer trial.
Neither map has a wild encounter entry, shop, PC, daycare, capture tutorial or
creature reward. The authored four skills have no field transport effects. No
running/escape/cycling map route is enabled. Normal start menu ignores collection
feature flags and exposes Crawlers, Inventory, Save, Option and Exit only.

Retained upstream code/data is not a claim of supported gameplay: stock Safari,
link, trades, Pokédex, storage screens, daycare maps and capture scripts remain
unreachable. New content must use these boundaries and repeat this audit rather
than enabling old maps or calling lower-level party/storage writers directly.
Story allies, alternate party sizes and new skill progression need deliberate
future interfaces. Both protagonists remain permanent; defeated actors recover
through the already verified trial/guide paths.

The fixture is a separate local ROM built after the production runtime routes.
`scripts/collection-fixture.py` appends GBA-side probes only to an isolated source
snapshot. It invokes actual compiled production functions, deliberately varies
capture mode/controller inputs, and publishes a 127 success bitmask. No emulator
RAM injection, fixture switch, debug grant or test hook ships in production.
The fixture does not prove the unreachable refusal dialogue renders; production
menu screenshots and B02 routes supply visible/runtime evidence separately.

Remaining S02 presentation placeholders include species summary data/art, bag
TM/HM and berry labels/graphics, old pocket indicator spacing, battle sprites and
animation assets. None grants capture, storage or breeding. Summary skill ordering
remains a normal presentation preference; Carl/Donut roster order cannot change.
Nonzero inflicted-status recovery remains pending; these tests do not add a status
source or claim to verify that separate behavior.
