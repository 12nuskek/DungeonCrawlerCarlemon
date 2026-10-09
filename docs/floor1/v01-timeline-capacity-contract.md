# Offline recorder capacity correction

Parent review accepts publication 4c1a2800 as a recorder total-capacity STOP119:
999,932 records left 68 slots against a 70-slot reserve, while maximum observed
frame flush used 104 of 4096. Kurt reaffirmed overnight continuation at 12:48 UTC
on 2026-10-09. This increment authorises only a conservative route-derived
capacity correction, matching header/parser, offline streaming/stress tests,
host compilation, review and publication to existing draft PR114.

The frozen route has 2044 boot frame calls. The generated host guards the next
36000 visual frame calls before executing a frame. Its sole frame driver flushes
the fixed 4096-record buffer each frame. Add the largest instruction reserve70
and one separate terminal record: `(2044 + 36000) * 4096 + 70 + 1 = 155828295`.
This ceiling is independent of the observed maximum104. It covers global
reservation headroom but does not relax per-frame overflow or any acceptance.

Version2 header retains the 16-byte envelope and 46-word/184-byte records;
historical version1 is decoded under its exact old million-record bound. Writer
allocation remains753664 bytes. Maximum file envelope28672406296 bytes exceeds
current free storage; actual writes remain streamed and disk/I/O failure remains
fatal119. No disk/platform change or worst-case preallocation is authorised.

Implemented source6217e6e6; generated host64a924e8/binary6a23c9bf compiled only.
Offline PASS352 writer/counter/short-write/terminal/precedence cases, all38044
maximum4096-record frame flushes,216 parser cases, and999932 actual retained
records decoded/payload-identical after rewriting only the versioned header.
Zero CPU instructions/events, ROMs/Saves loaded, gameplay host calls, new
preparation/execution claims or Library transfer attempts in this increment.

Preserve all original failures/controller/strategy records, prior outputs,
verified local archive and actual captures. Raw trace/reference/keys/binaries/
ROMs/Saves stay outside Git/uploads. The five failed private Library transfers
must not be retried or bypassed; no durable fresh-backup claim. Totals remain
six baselines/three candidates. Legacy inputs and historical timing remain
missing; no historical cause/remedy or full gameplay acceptance is established.

Parent offline review is next. The proposed later validation is one candidate
against independently reverified retained historical complete PASS reference;
the latest failed baseline supplies matching partial timeline evidence only
through requested frame13956. If the complete reference is unavailable, stop
dependent work; never reconstruct it or restart a baseline. The existing
runner's fresh-baseline PASS gate remains unchanged: any retained-reference
execution contract/binding requires separate review before preparation.

No candidate or baseline execution, game change, retry, continuation, waiver,
realignment, merge, rollout or scope expansion is authorised here. Nine-district
Floor1, accessible recovery, permanent duo, Emerald/GBA and Book1 opening ceiling
remain unchanged. Full candidate actions/motion/cleanup/equivalence, legacy/C01,
human pacing and full-floor gates remain pending.

[Offline evidence](../evidence/floor1/v01/battle/timeline-capacity/README.md).
