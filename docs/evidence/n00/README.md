# N00: progress-aware guidance

Base: bf27e2692025eb4291ffbf992a3b6412340d32cd.
Tested source: f3514caa05d99ff60c0c666d017fced8274e11e9.
Production ROM SHA256: 1a9d4b248b86880d74769e4b66a2f8e1d2319be8cff2579c4587132dbf999573.

The Journal names the landing trial, post-trial guide and service-room advice
identify the correct exits, and Donut acknowledges reaching the final stairs.
Original adaptation dialogue; no encounter, reward, collision or save changes.

Run `bash scripts/test-n00.sh` with the toolchain in ../../testing.md. It builds
an isolated committed archive and runs 18 unchanged production routes, retaining
all 373 assertions. A supplementary normal-input guide conversation used the
same production ROM and host, and a copy of the ordinary manual rest save:
`playtest production.gba guide-directions.sav game.sym < guide-directions/input.route`.
That route adds seven assertions. It ran before the runner's final log collection,
so validation-summary.json correctly records 19 sessions / 380 assertions.
The script alone runs 18 / 373; the supplementary route is separately archived.
All 19 emulator error logs are empty. Nine exact opponent framebuffer checks also
pass. No fixture ROM, save editing, RAM writes or fabricated capture was used.

Actual 240×160 captures were visually inspected: Journal objective, guide exit
and save advice, Mara's repeated resolved quest dialogue, Lev's exit advice and
Donut's ending. All revised text fits. Before images are I01 captures from
81b232ae41647b5e456e45ed73d51a170f17fb58 on the same routes; other images are N00.
Raw logs, every input route and build logs are archived with checksums. Generated
ROMs, executables and saves stay outside source control.

This focused check does not extend earlier claims: the six recovery routes prove
battle re-entry, not subsequent wins in those exact attempts; prior continuous
completion was prepared, and automated elapsed time is not human playtime.
