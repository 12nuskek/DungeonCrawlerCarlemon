# Prescribed candidate — static gate before emulator

Contract commit4034311c58c76a9a9d7ed68b6188bfd1264a6a3b precedes implementation.
Base PR97 ed519a05e34f47bf45fa150aa5e456b9e1028926. Exact ordinary seed026c16fe…23220a.
The original Warden loss1/1 and all earlier failures remain separate/unchanged.

Only enemy Loudred SLAM in normal authored858/859 uses effective power45 and
critical multiplier1. Shared move data remains65; the complete stock crit body
is byte-identical behind the local guard. Helper Whismur TACKLE targets Donut
on turns0/4/8,… and otherwise advances the native action queue with no move,
damage, status, PP cost or stat effect. No new move or altered party/save state.
Legacy/current unprepared/prepared native cues all explain the same cadence.

Exact-header C checks cover all65,536 trainer identities, member/player/wild/
link/frontier/species/move exclusions and all256 turn values. The stock critical
body, shared move tables, parties, duo initializer and save structs are verified
unchanged. The host compiles with warnings as errors and wraps every emulator
frame through the existing whole-battle30,000 limiter. Read-only telemetry can
stop on a violation but never changes the frozen inherited policy choices.

[Exact envelopes](envelopes.json) validate the reviewer estimates rather than
assuming them. Ordinary offensive SLAM maxima16+12 leave Carl at least10HP;
fortify6+4+4+4 leaves at least20. Normal player hits clear Warden on turns3–4
offensive or6–7 fortify; two further STRIKEs finish helper by6 or9. Carl needs
at most7 of his8 STRIKE uses. Donut uses both owned SPARKs, then WEAKEN.
No benefit from victory level gains is needed for these conservative bounds.

Helper ordinary damage is at most7+4 offensive or6+4+4 fortify, leaving Donut
at least19 or16HP through cleanup. Physical base damage's minimum1 before+2
means the last heavily weakened TACKLE still has maximum4, not3; the offline
calculation corrected that expectation before the gate passed. Stock helper
criticals remain12–15 and ignore negative Attack stages. Two maximum helper
criticals can exhaust30HP; no universal RNG guarantee is claimed or searched.
Authored SLAM alone suppresses criticals. Any actual route failure must STOP.

Prepared859 preserves levels10/8 and HP36/28, gives exact192XP each/money320,
and lower ordinary offensive SLAM maxima15+10. Ordinary craft/cache route
consumes owned2 SCRAP and one crafted Charge, grants one unused Super Potion;
duo stats/uses stay intact. Prepared is independent evidence, not unprepared
acceptance. Frozen exclusive route/host/source/build/ROM identities will be
recorded before execution. No emulator has run at this static gate.
