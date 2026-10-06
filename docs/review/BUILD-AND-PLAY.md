# DungeonCrawlerCarlemon — private overnight review

Open `REVIEW.html` first for actual before/after views. Open
`DungeonCrawlerCarlemon-N05.gba` in a GBA emulator to play. The tested core is
mGBA 0.10.5. This is the requested private review, not a public playable release.

Tested source: `eaf073d434a9347dfc2ed921f5f44d163563964b`.
Merged: `f2edec341fe1a1900f82740cbef25563b08f7532` via PR50.
ROM SHA256: `8e7e8c20c8dde66488d9374ec90e80391a02c255ad4a0a422e7392f04f1ccfb6`.
Repository: https://github.com/12nuskek/DungeonCrawlerCarlemon

## Play

Start a fresh save; keep old development saves separately. D-pad moves, A
interacts/confirms, B cancels, START opens the menu. Save outside battle using
START → Save. Emulator savestates are not needed. See PLAYTEST.md for the route.

Read the entrance note, meet the Quiet Landing guide and complete the trial.
Carl uses STRIKE/BRACE; Donut uses SPARK/WEAKEN. The guide freely restores HP,
status and action uses. Repeat recovery now takes one contextual page. Both
defeated recovers locally; you can retry or backtrack without permanent death.

The Service Room southwest ladder leads to two patrols and the gate warden.
After winning the required fights, examine the northeast stairs. The quest,
trap, equipment and cache preparation are optional. Try defense/debuffs or
cache preparation if the warden is difficult. The ending permits save and return.

## Build the same production ROM

On Linux install build-essential, binutils-arm-none-eabi, git, libpng-dev and
pkg-config. Then:

```sh
git clone https://github.com/12nuskek/DungeonCrawlerCarlemon.git
cd DungeonCrawlerCarlemon
git checkout eaf073d434a9347dfc2ed921f5f44d163563964b
bash scripts/setup-foundation.sh
make -C engine -j2
sha256sum engine/pokeemerald.gba
```

Expected SHA256 is above. The custom game does not match stock Emerald; do not
use baseline `make compare` as a custom-game acceptance check. Setup uses the exact
pret/pokeemerald `731ad5bfd6e6f265508d0efcca0ba42f9dcf5881` and pret/agbcc
`da598c1d918402c42c0c0d7128ba14567f3175e9` provenance/toolchain pins.
The repository's docs/testing.md has environment and historical baseline evidence.

Full regression additionally needs libmgba-dev, Python3, Pillow and NumPy, and the
ordinary I01 legacy saves plus the N01 corner save. They are not bundled; their
normal-input creation routes and hashes are documented in N02 evidence. Set both
inputs explicitly; missing inputs stop before building and cannot produce a
misleading full-pass result:

```sh
DCC_LEGACY_RUN=/path/to/completed/I01/run \
DCC_CORNER_SAVE=/path/to/ordinary/N01-corner.sav bash scripts/test-n05.sh
DCC_RECOVERY_BASE_RUN=/path/to/accepted/N05/run python3 scripts/test-n04.py
```

The first command builds an isolated committed snapshot. It also creates labeled
diagnostic ROMs for capacity/exhaustion checks. Only its immutable `production.gba`
is this game's deliverable; fixture builds must never be substituted for it.

## Evidence and remaining limits

90 actual emulator sessions / 1,531 assertions: 1,338 production and 193 labeled
fixture checks; 90 empty emulator error logs; 38 exact rendered comparisons.
The six exact recovered saves all win, pass resolved-repeat XP checks and retain
HP/status/action uses/XP/equipment and progression through manual save/cold reload.
Full raw N05 logs are bundled under evidence/n05. Images are actual unedited
240×160 mGBA output; REVIEW.html only scales them. The capture manifest identifies
source paths, tested commits and hashes. The authoritative source evidence is:
https://github.com/12nuskek/DungeonCrawlerCarlemon/tree/005154eef04e24318d48b6435087e1c6954cff42/docs/evidence/n05

Prepared uninterrupted fresh completion passes. Unprepared wins and recovered-save
wins are separately verified; they are not an uninterrupted unprepared campaign.
Two historical uninterrupted unprepared routes lost, including a repeated loss
within the second route. Their traces remain preserved. No balance change is
claimed by the overnight presentation/recovery work.

The automated prepared route is 90,586 frames (25m16.655s), including 53,700 fixed
idle frames. This is not human reading/decision time or proof of the 20–30 minute
design target. Please report your actual playtime and confusing interactions.

Original Book 1 opening adaptation dialogue uses compressed chronology and no
later-book spoilers. Tutorial enemies are adaptation choices, not canon claims.
Static poses, stationary Donut, inherited audio/attack/send-out effects and some
UI elements remain. The accepted environment kit has documented source-sheet and
packed-output omissions; native masters reproduce the game assets, but full
source-sheet reproduction is not claimed. See CONTENT-LEDGER.md and PROVENANCE.md.
Stage 6 remains awaiting the user's playtest. No public ROM release is authorised.
