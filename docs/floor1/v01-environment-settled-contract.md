# Separate source-diagnosed noncombat controller correction

The first V01 baseline claim2748afa8 stopped at3932 frames/25 assertions, exit14:
after the blocked right-input animation, the next up batch advanced to29,23 rather
than29,24. Candidate emulator never ran. Original STOP/claim/route/host/prepared
candidate and unchanged Save030b12fd remain immutable and separate.

Source diagnosis: field_player_avatar.c CheckMovementInputNotOnBike makes a turn
only when direction differs AND runningState!=MOVING. PlayerNotOnBikeCollide
uses a multi-frame walk-in-place animation; the custom blocked-input step omitted
the zero-input40-frame settle used after every ordinary directional batch in
live-route.py. Readiness of field callbacks does not imply completion of movement.
Immediate next input therefore bypasses the route generator's expected turn delay.
The preserved log proves a third up step/counter increment before the strict stop.

Under the parent's instruction to diagnose before another execution, apply ONE
source-diagnosed navigation correction: add the existing40-frame zero-input settle
after the blocked attempt. No timing/RNG search, new battle policy or assertion
change. New settled route keeps every original assertion/command byte-identical
otherwise. No engine/asset/host gate change; game remains frozen2748afa8/76dd6ae4.

Freeze separate wrapper/route before ONE separately claimed baseline and ONE
dependent candidate in runtime-settled;8188 frames each,720 native clip frames,
same existing ordinary input030b, zero battles/Save/actions. Retain original failed
root and first STOP rule; no further corrected execution if this separate pair
fails. Exact native resources, scene/map/palette/VRAM and budget assertions stay.
Historical gates, unavailable original legacy input, C01/human pacing remain.
