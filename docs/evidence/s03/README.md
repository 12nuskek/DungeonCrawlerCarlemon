# S03 acceptance work — IN PROGRESS

Base d8f8ae62a3fba0dbe4c2c17fa2a4a1ce193bc530; issue29. This directory currently
contains routes under active validation, not a completed acceptance package.
Current diagnostic runs use production c9062da (same engine as merged S02) and
the read-only host helper committed in0c72f45; final evidence must come from an isolated
committed source snapshot. No S03 runtime or merge completion is claimed.

The battle pilot resolves actual player input callbacks from the linked ELF,
reads menus/turns/resources and sends normal A/directional pulses. It never writes
game RAM, changes outcomes, skips enemy actions or injects saves. A frame bound
rejects stalled battles; separate victory/defeat, flags, XP and persistence
assertions still determine success. Defensive policy uses two BRACE/three WEAKEN
opening turns; fortify uses three of each; offensive attacks until SPARK runs out,
then uses WEAKEN. These are replay strategies, not game AI or player assistance.

Trial checks restore turn damage, four battlers, resources, rejected empty SPARK
without lost turn/resources, WEAKEN attack reduction, level stats and pre-reward
state. Damage values are rebaselined from observed current frames; rules unchanged.
Both Donut scenes, actual Donut summary/action selector and real-time movement
recording are required. Current S02 still screenshots never proved smooth motion.

Pending final gates: fresh completion/declined quest/avoided trap; prepared boss;
all local defeats/retries and both incapacitations; empty actions; quest branches;
reward/crafting capacity and duplicates; collection restrictions; cold saves;
normal-speed pacing measurement with automated waits/reboots reported separately.
The 20–30 minute fresh-player target remains unproven. Preserve all stock/art
limitations in the final review package and await user playtest before Stage6.


Parent independently decoded the complete walking GIF: readable steps/directions,
no obvious flicker or broken gait. Initial/final Carl lower-body overlap is normal
foreground depth against the guide directly south (4,8 versus Carl4,7); guide
interaction/recovery and walking away/back are separately asserted. The GIF wrap
resets direction because the captured route restarts; no gameplay loop is claimed.
Donut adds a real stationary collision object at7,5. Routes intentionally go around
her; the original map tile collision bits alone never implied identical occupancy.
