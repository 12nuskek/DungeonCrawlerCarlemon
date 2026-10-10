# C01 r2 retained turn analysis

Native turns are zero based. Enemy1/enemy3 denote battler slots, not party positions. All values below are observations unless explicitly marked as source bounds. `turn-analysis.json` contains each input confirmation, PP decrement, damage/stage event and XP timestamp. Player Attack/Defense/Sp. Attack/Sp. Defense stages remain neutral throughout; Carl never uses BRACE. Status is clear.

## Trial

HP cells show start→end/maxHP. End PP lists STRIKE/BRACE and SPARK/WEAKEN. Enemy HP is the observed end of the turn; native stage 6 is shown as 0. A critical lists nominal damage and, if capped by remaining HP, actual HP removed.

| Turn; frame interval | Carl HP | Donut HP | End PP C; D | Carl / Donut actions | Enemy actions in execution order | End enemy HP | Enemy Attack / Defense stages |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0; 10487–12125 | 30→26/30 | 26→26/26 | 7/40; 1/40 | STRIKE→enemy1 / SPARK→enemy1,enemy3 | enemy1 TACKLE→Carl MISS; enemy3 TACKLE→Carl 4 | 12, 21 | enemy1: 0/0; enemy3: 0/0 |
| 1; 12126–13070 | 26→21/30 | 26→22/26 | 6/40; 0/40 | STRIKE→enemy1 / SPARK→enemy1,enemy3 | enemy1 TACKLE→Carl 5; enemy3 TACKLE→Donut 4 | 1, 17 | enemy1: 0/0; enemy3: 0/0 |
| 2; 13071–15137 | 21→19/33 (max increased) | 22→24/28 (max increased) | 5/40; 0/39 | STRIKE→enemy1 / WEAKEN→enemy1,enemy3 | enemy1 TACKLE→Carl 3; enemy3 TACKLE→Carl 2 | 0, 17 | enemy1: 0/0 (KO reset); enemy3: -1/0 |
| 3; 15138–15957 | 19→17/33 | 24→24/28 | 4/40; 0/38 | STRIKE→enemy3 / WEAKEN→enemy3 | enemy3 TACKLE→Carl 2 | 0, 6 | enemy1: 0/0 (KO reset); enemy3: -2/0 |
| 4; 15958–17595 | 17→17/33 | 24→24/28 | 3/40; 0/37 | STRIKE→enemy3 / WEAKEN→enemy3 |  | 0, 0 | enemy1: 0/0 (KO reset); enemy3: 0/0 (KO reset) |


## Guard

HP cells show start→end/maxHP. End PP lists STRIKE/BRACE and SPARK/WEAKEN. Enemy HP is the observed end of the turn; native stage 6 is shown as 0. A critical lists nominal damage and, if capped by remaining HP, actual HP removed.

| Turn; frame interval | Carl HP | Donut HP | End PP C; D | Carl / Donut actions | Enemy actions in execution order | End enemy HP | Enemy Attack / Defense stages |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0; 22984–24724 | 33→33/33 | 28→23/28 | 7/40; 1/40 | STRIKE→enemy1 / SPARK→enemy1,enemy3 | enemy1 BRACE→enemy1; enemy3 TACKLE→Donut 5 | 21, 21 | enemy1: 0/1; enemy3: 0/0 |
| 1; 24725–25671 | 33→22/33 | 23→23/28 | 6/40; 0/40 | STRIKE→enemy1 / SPARK→enemy1,enemy3 | enemy1 TACKLE→Carl 6; enemy3 TACKLE→Carl 5 | 13, 17 | enemy1: 0/1; enemy3: 0/0 |
| 2; 25672–27121 | 22→7/33 | 23→20/28 | 5/40; 0/39 | STRIKE→enemy1 / WEAKEN→enemy1,enemy3 | enemy1 TACKLE→Carl 15 CRIT×2; enemy3 TACKLE→Donut 3 | 8, 17 | enemy1: -1/1; enemy3: -1/0 |
| 3; 27122–28422 | 7→4/33 | 20→16/28 | 4/40; 0/38 | STRIKE→enemy1 / WEAKEN→enemy1,enemy3 | enemy1 TACKLE→Carl 3; enemy3 TACKLE→Donut 4 | 3, 17 | enemy1: -2/1; enemy3: -2/0 |
| 4; 28423–30411 | 4→4/36 (max increased) | 16→16/28 | 3/40; 0/37 | STRIKE→enemy1 / WEAKEN→enemy1,enemy3 | enemy1 TACKLE→Carl MISS; enemy3 TACKLE→Carl 3 | 0, 17 | enemy1: 0/0 (KO reset); enemy3: -3/0 |
| 5; 30412–31258 | 4→0/36 | 16→16/28 | 2/40; 0/36 | STRIKE→enemy3 / WEAKEN→enemy3 | enemy3 TACKLE→Carl 8 CRIT×2 (4 HP removed) | 0, 7 | enemy1: 0/0 (KO reset); enemy3: -4/0 |

## Observed KO, XP and level timing

| Event | Native frame | Observed party/battle transition |
| --- | --- | --- |
| trial enemy1 reaches zero | 14153 | 1 HP removed; nominal damage 7 |
| trial Carl XP/level | 14466 | XP 399→419; level 8→9 |
| trial Carl level HP applied | 14491 | HP 18→21; maxHP 30→33 |
| trial Carl XP/level | 14635 | XP 419→450; level 9→9 |
| trial Donut XP/level | 14754 | XP 709→729; level 8→9 |
| trial Donut level HP applied | 14779 | HP 22→24; maxHP 26→28 |
| trial Donut XP/level | 14923 | XP 729→760; level 9→9 |
| trial enemy3 reaches zero | 16571 | 6 HP removed; nominal damage 11 |
| trial Carl XP/level | 16878 | XP 450→495; level 9→9 |
| trial Donut XP/level | 16998 | XP 760→805; level 9→9 |
| guard enemy1 reaches zero | 29589 | 3 HP removed; nominal damage 5 |
| guard Carl XP/level | 29891 | XP 495→560; level 9→10 |
| guard Carl level HP applied | 29916 | HP 4→7; maxHP 33→36 |
| guard Carl XP/level | 30060 | XP 560→576; level 10→10 |
| guard Donut XP/level | 30179 | XP 805→886; level 9→9 |
| guard Carl reaches zero | 31258 | 4 HP removed; nominal damage 8 |

Trial awards 96 XP each (51+45), raises both actors to level9 and adds 320 money. Guard enemy1 awards 81 XP each before STOP; Carl levels to10, increasing HP/maxHP by3, then loses3 HP. Enemy3 remains at7 HP. Full Guard XP/reward/win flag is not observed. Carl ends XP576, Donut886; Guard outcome0 remains unresolved.

Inventory: trial Potion2/Scrap0; after earned rack Scrap2. The field demonstration consumes one Potion on Donut, 24→28 HP. Free guide recovery then makes Carl33/33 and Donut28/28 with full8/40/2/40 PP. Guard therefore has Potion1/Scrap2 available throughout, with no Bag action selected. Money is3320 before Guard. Stable decoded field endpoints and per-turn inventory basis are in the JSON.
