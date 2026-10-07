# Native integration handoff

The accepted written plan in docs/floor1 governs exact geography, widths, gates, permissions and mechanics. Images only communicate art direction. Keep gameplay, save compatibility and progression changes in their dependency-ready tasks. Finish F1-T01 evidence, then explicit map/encounter membership F1-A01 before new-map work.

## Environment and layout

Author modular native floor/wall/edge/corner tiles and existing prop-state variants; do not flatten the room paintings into game backgrounds. Preserve exact exits, collision and interaction anchors until a reviewed graybox/migration deliberately changes them. Live/spent wire art must communicate actual state without adding a raised physical barrier.

D1 upper maintenance-bay passage and entry stairs remain too narrow relative to the intended width hierarchy. D2 has finer tile pitch, narrower bridges/service necks and visible wall/tile seam differences. Widen main routes and normalize native scale before implementation. Connection-register.json records illustrative D1.N-D2.S alignment only. The unchanged stitched panels prove source-pixel preservation, not traversal/collision correctness.

Full-floor overview is 1672x941, not the ideal 3072x1728. Approximately 10x explorable area is a design intent, not a measured result. Illustrated cistern/wheel/refuge details drift from the written plan; the plan controls. Local player camera remains unchanged by the panoramic concept.

## Character conversion

Redraw deliberately on aligned native 64x64 cells; keep consistent body scale, ground contacts, pivots and facing. Preserve Carl white red-heart boxers/bare feet/brown hair and Donut tortoiseshell coat/gold collar/teal jewel. Donut WEAKEN poses drift toward the front and need harmonizing. Warden is front-only; no rear view is supplied.

Generated sheets contain many colours and semi-transparent fringe. Carl alpha peaks at254, so do not require source alpha==255 when identifying the body. Hidden background RGB can make some viewers display brown haze even where alpha is zero. Native assets need indexed palettes, transparent index0/binary alpha and15 opaque RGB555 colours per character under the current4bpp contract. Preserve these masters; clean during native authoring.

Audit sprite templates, animation tables, compressed budgets, palette banks and peak allocation before frame counts are fixed. Author timing/in-betweens and bind poses to real actions; repeated stills are holds. Warden warning must match its real WIND UP state without inventing reaction-time mechanics.

## Acceptance still needed

Native240x160 clips/stills, actual playback/timing, HUD/clipping/silhouette/palette tests, scene headroom, clean committed build and affected battle/exploration/save/reload/recovery regressions. No such runtime checks were performed for this source package. Existing gameplay and prior accepted source anchors are unchanged. No character-IP clearance claim is made.
