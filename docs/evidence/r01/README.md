# R01 XP and equipment verification — 2026-10-06

Integration update: merged PR #17 as `5a0fd8eaef6b4746c745e128bd9923f00afeeee0`. Earlier pending labels below describe the verification-time checkpoint.
Implemented YES / compiled PASS / runtime PASS. Integration is recorded in
[progress](../../progress.md) and [issue #16](https://github.com/12nuskek/DungeonCrawlerCarlemon/issues/16).
Base `4a27fc4b082b8d8b6dfa1840eb6d5f01ce554363` (B03 PR #15).
Tested commit `d9db8b3a61fa36035236cb5764f732ea20d88736`.
Production ROM SHA256 `aece986da533253d66fa77151d2972d81160002e5fbd17bd8374d50c400355d0`.
Actual mGBA0.10.5, normal inputs/flash saves, no host RAM writes or savestates.
Isolated run `artifacts/r01/run-jsToC1`. No ROM/save/executable is distributed.

## Reproduce

Use dependencies/environment variables from [B02 evidence](../b02/README.md) and
[testing](../../testing.md), replacing the command with `bash scripts/test-r01.sh`
at the tested commit. The runner exports the exact committed source, rebuilds
pinned compiler/game products, compiles the host harness with warnings as errors
and runs eight production routes in separate emulator processes. A separately
hashed fixture then runs two further routes. Local `production.gba` is preserved
before patching the isolated snapshot; its final engine ROM is the fixture.
Normal checkout/README build instructions always produce the production game.

Full raw setup/build/emulator logs are included with native whitespace preserved.
All ten emulator error logs are empty. Eighteen actual screenshots were visually
reviewed; they are lossless framebuffer conversions. No mock captures are used.

## Results

| Route | Assertions / result |
| --- | --- |
| setup | 16 PASS: fresh game, movement/interactions/maps and flash save |
| plain-victory | 25 PASS: win without acquiring/equipping the optional item; XP/level/stat growth; flag and bag remain empty |
| acquire-equip | 15 PASS: original crate dialogue, one grant/repeat, inventory Give to Carl, save |
| defeat-save | 23 PASS: one actor then both down, local recovery, gear/XP retained, save immediately after defeat |
| reload-defeat | 9 PASS: cold Continue retains gear/XP and restored resources; trial is retryable |
| equipped-victory | 24 PASS: gear affects combat, both level up, victory and deliberately depleted save |
| reload-take | 20 PASS: cold depleted HP/PP/XP/equipment persist, guide heals leveled stats, take/re-equip, save |
| reload-final | 12 PASS: second cold reload, XP/gear/health/resources and trial flag persist; repeat crate cannot duplicate item |
| fixture-setup | 19 PASS: fresh fixture, fixed-input real damage comparison and full-bag probe mask3 |
| capacity | 11 PASS: ordinary interaction refuses a full inventory without setting flag; toss one Potion, retry grants exactly one wrap; repeat remains resolved |

**174 assertions PASS; ten empty error logs.** Screenshots illustrate behavior;
route/log assertions provide the persistent-state proof. The fixture is explicitly
constructed test content, not a claim that a new production player naturally owns
30 consumables. Its source generator is `scripts/equipment-fixture.py`; no debug
entry or test grant is present in production.

## Observed progression and equipment effect

Carl starts level8/XP399, Donut level8/XP709, both20 XP before their next level.
The trial earns51 then45 XP each: final level9/XP495 and level9/XP805. Carl maxHP
30→33 and attack20→23; Donut maxHP26→28 and magic13→14. Existing growth/stat rules
are reused. Starting near a level is a documented compressed tutorial adaptation.

WRIST WRAP is item377, using the existing held-item slot. The stock normal-type
modifier scales attack input by20%, with integer rounding; final damage is not
promised to rise exactly20%. Same opening action route leaves the first foe at12HP
with the wrap versus14HP without it (second foe21HP in both). A controlled GBA
fixture calls the unchanged real damage function at identical inputs and gets
base damage10 without versus11 with the wrap. No separate combat model was added.

The depleted save reloads Carl/Donut HP29/14 and all four use counts4/40/0/38,
with final XP and held wrap intact. Guide recovery becomes33/28 HP and8/40/2/40
uses. Taking moves the item into inventory (held0/bag1); re-equipping restores
held377/bag0. Cold repeat interaction preserves that single total item. Defeat
likewise preserves the wrap and initial XP while restoring health/resources.

Full-inventory fixture: the normal crate script leaves item quantity0 and
FLAG_DCC_WRAP_TAKEN unset. After an ordinary Potion toss frees one slot, the same
interaction grants one wrap and sets the flag. Repeat gives no second item.

## Reviewed captures and limits

`wrap-found.png`, `wrap-bag.png`, `equipped.png`: authored grant, readable description
and normal equipment flow. `carl-level-growth.png`, `donut-level-growth.png` show
level-up stat increments. `equipped-turn-one.png` / `plain-turn-one.png` support
the paired damage assertions. `depleted-reloaded.png` is field context; numerical
persistence is proved by reload-take.log, not inferred from that image.
`wrap-taken.png`, `wrap-reequipped.png`, `repeat-after-reload.png` show the complete
item lifecycle. `retry-after-reload.png` illustrates accessible saved defeat.
`full-inventory-refusal.png` / `wrap-after-space.png` are explicitly fixture captures.

Fresh milestone save required; no save layout expansion or old-save migration.
The original scarf icon, species/stat presentation and battle/summary art are
tracked S02 placeholders. This adds one equipment item, not a complete loot or
achievement system. R02 is next after integration. Actual inflicted-status curing
and total action exhaustion remain S03 edges; depleted/immediate-defeat saves now
have concrete coverage. The complete Stage5 slice remains unfinished.
