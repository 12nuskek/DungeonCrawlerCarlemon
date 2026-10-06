# Build and runtime validation

F01 setup is in progress. Use the exact pinned upstream installation guide once
imported. The selected matching compiler is pret/agbcc, not the modern target.
Baseline commands: `make -j2`, `make compare`, `sha256sum pokeemerald.gba`.
Run these from the imported engine directory with the recorded toolchain on PATH.
Never commit the resulting ROM, ELF, maps, saves or compiled tools.

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
