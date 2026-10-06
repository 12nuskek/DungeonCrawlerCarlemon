# D02 explosive crafting and optional cache

Date: 2026-10-06. Issue #22; scoped integration pending.
Base `c42d444b8c2ae1b665105baad133094859bf8fa5`.
Tested `b53b8e6a2c64fe3e9e22d37bca5277c97ac46b02`.
Production SHA256 `a4c542bae88f85f8e537c4590bdafb2830b386844bc4806a783b5825b2793972`.
Explicit fixture SHA256 `76ef23a5851b33c1bc7c6be8334fa5203bd86f056b84e0439fea13c3ec5b9ecf`.
Implemented YES / isolated compile PASS / runtime PASS / merge pending.

Run `bash scripts/test-d02.sh` with [documented dependencies](../../testing.md).
Clean committed archive regenerates pinned compiler and products. Real mGBA0.10.5,
ordinary button input, host read-only assertions. 111 assertions PASS:
67 production and44 explicit fixture, seven empty errors,19 actual framebuffer
PNGs visually reviewed. No ROM/save/executable committed. Local production.gba is
preserved before fixture generation; the final engine ROM in the runner snapshot
is the fixture. A normal checkout build produces the production game.

| Route | Checks | Result |
| --- | ---: | --- |
| materials | 16 | Empty recipe/cancel/cache refusal, Mara quest supplies Scrap2, save |
| craft | 13 | Cold materials, cancel preserves2, craft2→Charge1, repeat missing, inert menu use, save |
| blast-use | 17 | Cold Charge1, cancel, spend1→SuperPotion1 once, repeat, medicine restores Carl26→30, save |
| reload-recover | 13 | Cold blasted/consumed state, repeat no refill, return/guide clears paralysis, save |
| reload-final | 8 | Final cold flags/resources/items agree |
| capacity fixture | 33 | R02 workshop full-stack refusal/retry, craft output refusal/two successful crafts, cache output refusal/retry |
| capacity-reload fixture | 11 | Cold final quantities, repeat cache and workshop cannot duplicate |

The fixture deliberately starts with all item slots occupied, Scrap98, Charge99,
SuperPotion99 and the R02 duo achievement flag set. It does not simulate earning
those materials or winning the trial. Real field scripts then reject capacity
without consuming inputs or setting reward flags; normal inventory toss frees
room and retry succeeds. Workshop98→toss1→grant2→99; crafting with output99
refuses, then after output toss two crafts each consume2 (Scrap99→97→95).
Cache output99 refusal retainsCharge99; after medicine toss, retry gives99 and
consumesCharge99→98. Cold quantities95/98/99 persist. This closes the separately
identified R02 Scrap-box capacity edge. No debug path exists in production source.

Optional cache flag0x2E persists. Its future S01 boss preparation effect is not
implemented yet; the current benefit is usable recovery medicine. Empty materials
never close the return route. Crafting conservatively requires output room before
consuming inputs, even if input consumption could free a slot; refusal explains it.
No new save layout. Fresh milestone saves required for new objects.

Original recipe/dialogue; stock crate/icon/explosion sound and inherited refusal
text (including DAD advice on menu use) are explicit S02 placeholders. New writing
and final presentation audit remain scheduled. No failed production fix or blocker;
exploratory navigation was adjusted around an existing sign. Screenshots alone
are not persistence proof: exact routes and RAM assertions are included.
