# Build and runtime validation

## Matching baseline build

Use Linux with `build-essential binutils-arm-none-eabi git libpng-dev pkg-config`.
The selected matching compiler is pret/agbcc, not the modern target; pins and
source exceptions are in [provenance](upstream/provenance.md).
From a clean repository checkout:

```sh
bash scripts/setup-foundation.sh
bash scripts/build-baseline.sh
```

Setup fetches exact pins, hydrates three ignored upstream multiboot inputs and
builds/installs agbcc into `engine/tools/agbcc`. Build runs `make -j2`,
`make compare` and SHA-256 recording. Logs go to ignored `artifacts/`.
`JOBS` controls build parallelism. `DCC_CACHE` optionally chooses the checkout
cache (default `.cache/`). Do not point it at unrelated user repositories.
Never commit ROMs, ELF, maps, saves or compiled tools.

## Emulator boot and interactive play

For interactive play, open the locally built `engine/pokeemerald.gba` in mGBA.
Set GBA buttons in the emulator's input settings. Begin with no save file; baseline
is unchanged Emerald, not yet DungeonCrawlerCarlemon. No downloadable ROM is
provided here.

For repeatable headless execution install `libmgba-dev` and compile:

```sh
mkdir -p artifacts/boot
cc -std=gnu11 -Wall -Wextra -Werror scripts/boot-baseline.c -lmgba -o artifacts/boot-baseline
cd artifacts/boot
../boot-baseline ../../engine/pokeemerald.gba < ../../docs/evidence/f01/route.txt > boot.log
```

The harness runs the actual mGBA core with built-in BIOS and no loaded save, steps
GBA frames with recorded button masks, and writes PPM captures. Convert captures
to PNG for inspection if desired. Record the source commit and ROM checksum with
the route. It is not a mocked game or a screenshot-only test.

Runtime gate: load the matching ROM in a real GBA emulator with a clean save,
observe boot/title, press Start and reach New Game, then enter the introduction.
Record emulator version, exact input/frame route and screenshots against the
tested source commit and ROM checksum. A screenshot alone is not full validation.

Future runtime matrix: fresh-save completion; all movement/collision/transitions;
duo actions, incapacitation, victory/defeat/escape; reward repetition and reload;
inventory empty/full, recipe failure/success; optional quest branches; boss alternate
strategy; staircase; capture/storage/breeding audit; text/palette/sprite limits.
Those checks are pending until their stages exist. Stock baseline saves are not
promised compatible with future crawler milestones. No save layout changes yet.
