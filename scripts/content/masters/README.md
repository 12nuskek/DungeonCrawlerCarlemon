# Native exploration pixel masters

2026-10-06: derived from the user-approved generated exploration reference in
`docs/art-references/carl-donut-overworld-proposed-reference-v2.png`, then manually
cleaned at 16×32 (Carl) / 16×16 (Donut). Each character is a palette index: dot is
transparent; hexadecimal 1–f selects its independent approved battle palette.
`../protagonist_art.py` exports these authoritative pixels without resampling.

Reference normalization used its documented component crops (idle down/up/left),
BOX sampling and nearest palette matching. Native edits restore readable eyes,
hair, shorts/heart accents, Donut's face/ruff and clipped back paws. Carl contact
frames were authored from normalized idle poses with alternating feet and arms;
head/torso anchors remain fixed. The flawed right-facing reference contact is
not imported. Engine mirrors the three left-facing frames for right movement.
Donut's three directional standing frames are stationary scene art; no follower
or walking cycle is claimed. Native frames retain transparent outer margins.

Generated source and conversion are not hand-drawn source illustration. These
text masters include authored native cleanup; they remain subject to emulator
movement/palette review. See the content ledger and S02 evidence for status.
