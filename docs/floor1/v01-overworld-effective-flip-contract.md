# Separate source-proven effective flip adapter

First character baseline2a76829f STOP97 at7924 frames/61 assertions. All9 Carl
frames and3 Donut frames matched actual OBJ VRAM/palettes/pivots; four existing
conversations, five scene/overlay/VRAM checks, field controls and resources passed.
Coverage masks incorrectly reported0 mirrored frames for both actors. Candidate
never prepared/executed. Original claim/host/route/STOP/log/raw frames and full
stop-clock/accepted/live buffers remain separate; unchanged ordinary Save030b.

Diagnosis: new character observer read Sprite.hFlip atbyte63bit0, the optional
sprite-level override. Actual native SetSpriteOamFlipBits XORs that with each
animation command's hFlip and writes OAM.matrixNum bit3, hence hardware attr1bit12.
Existing right-facing AnimCmds set hFlip=TRUE, while override remains0. Actual
first baseline right-facing screenshots show the correct mirror, but the faulty
observer classified them as unmirrored. No game/gait/route/controller defect is
established. Four compiled actual-native XOR cases prove the effective bitfield.

Under parent's stop-and-diagnose-before-another-execution instruction, freeze ONE
separate adapter correction reading already captured attr1bit12. All original
visual coverage, strict state/gameplay/frame bounds and reaction24 assertions
remain unchanged. No tolerance, re-anchor, new route/cadence or assertion removal.
Game/assets/build remain2a76829f / ROM4cfc89f8 / engine963d2b06. Historical original
host and first failure stay unchanged; no retroactive baseline acceptance.

New separate runtime-effective-flip root permits ONE new baseline and ONE
dependent candidate, original153-line route/input/cadence byte-identical. If this
pair fails, stop/preserve/diagnose; no automatic retry. Original legacy/C01 limits,
private necessary logs/saves/frames and denied-context upload exclusions stay.
