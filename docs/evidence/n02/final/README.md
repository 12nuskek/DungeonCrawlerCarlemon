# N02 room outlines and preserved routes

Base c71636ac213147181eb28ab968ffd15e718501fc (verified N01).
Tested source dec2c5e479cdceedf8b358d00448358640561b91.
Production SHA256421d812a9a18ac1b1432dc5b831a5ba281c6e034249215364f3a99fd598d33b1.

The six rooms now have bounded alcoves, clipped corners and small patrol/gate
supports. Exactly26 map cells change:14 become walkable alcoves and12 become
small supports/corners. All1150 remaining map/border collision/elevation/behavior
values, six event/warp contracts and49 approved character/opponent assets remain
unchanged. The renderer follows actual boundaries. No added encounter, long
corridor, required interaction, reward or persistent variable. Native budget:
158 used8x8 tiles/160 allocated,172 metatiles, BG banks6–9.

Two earlier runs caught useful direct routes obstructed despite static overall
reachability. First111fd5c blocked Service6–8,3; second0fc144f blocked13,3 during
crafting fixture reload. The final candidate removes all four obstructions. It
preserves the original routes rather than adding detours. Raw failures live in
../diagnostics; an evidence-derived path contract now checks every previously
observed same-map straight segment as well as global object/warp connectivity.

With the pinned toolchain documented in docs/testing.md:

```sh
DCC_LEGACY_RUN=/path/to/completed/I01/run \
DCC_CORNER_SAVE=/path/to/ordinary/N01-corner-save.sav bash scripts/test-n02.sh
```

The corner input was produced through5 normal-input assertions on N01 ROM
17e97672a2a3a6b6f7b670d3d901f4e6be21425a8eb92407a4c91be874cec637 at Exit13,9.
Its input route/logs are in legacy-corner-input; its hash is legacy-input.sha256.
The three other legacy saves are the actual I01 motion/craft/completion inputs
identified in legacy-inputs.sha256. No save editing or RAM/state injection.

Accepted runtime results belong to the exact tested source above:

-73 emulator processes/1210 assertions, including193 explicitly labeled diagnostic
 fixture assertions and1017 production assertions;73 empty error logs.
-Original1053/62 retained, all five newer Journal/alternate-patrol routes43 retained,
 three old-save routes41 retained, six-room18, boundary/alcove47, old-corner escape8.
-Fresh uninterrupted prepared completion and cold reload; both segmented boss
 strategies; quest/craft/trap/reward/collection-policy and capacity failure checks.
-Nine exact opponent frame matches plus eight native prop matches.
-Two complete isolated source exports preserve8807 tracked asset files; only
 palette line endings normalized. export-validation.json records this separately.

Fresh forward no-dialogue arrivals are setup-room/setup-landing/gates-service/
gates-gauntlet/forward-boss-arrival/continuous-complete. The last is the same
Exit4,6 arrival position after closing completion dialogue and manually saving;
forward-exit-arrival separately preserves the automatic completion message. All
come from the
continuous-prepared route; only capture names differ from its original controls
and assertions. Reverse rooms and focused shape-probes supplement these views.
Before: ../../n01/rooms at cd6946e. All images are real240x160 mGBA output.

The Service wire remains too subtle and still looks live after use; gate/cache/
secret/defeated-state visuals are planned separately. No claim that these are fixed
here. Source native kit remains partial; omitted artifacts were not recreated.
Existing limits remain: six retry routes prove re-entry, not wins in those exact
recovered saves; prepared continuous completion passed, while unprepared wins are
segmented. Automated fixed waits do not establish human20–30minute completion.
No ROM/save/executable is included in source evidence.
