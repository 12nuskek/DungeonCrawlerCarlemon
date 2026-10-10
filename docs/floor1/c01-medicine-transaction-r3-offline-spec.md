# C01 medicine transaction r3 — offline source specification

This increment is an offline correction only. No emulator initialization, game
build, input-policy/cadence change, runtime freeze/claim, Save or cold process.
Preparation remains closed; user-requested checkpoint/idle supersedes continued
verification at this boundary. Historical helpers/contracts/STOPs are immutable.

`scripts/floor1/medicine-transaction-proof.py` verifies the pinned ELF/library,
scoped function bytes and valid instruction starts, startup IRQ stack, native
568-byte internal allocation, host CPU ABI and fresh IRQ bank transfers.
`scripts/floor1/medicine-transaction.h` admits only narrowly supported source
states after verified healing. Call-site stacks bind RunTasks → party callback →
owned task and the specific UpdatePartyToFieldOrder memcpy. Constrained copy registers,
NZCV, actual source buffer and copy prefix must match the compiled aligned loop;
all600 party bytes and the remainder of the3324-byte snapshot stay exact.
Ordinary complete-record checksum/reencoding and native empty-slot checks remain.
Freed allocation payloads are never followed; cleanup must finish before exitSeen.
Unknown nested helper/interrupt states fail closed. This does not prove all
possible native cuts are supported or that historical frame returns used them.

The separate r3 generator retains the old r2 fresh-WAIT A edge, two-use cap,
per-recipient reset, ownership, HP/PP/Bag resources, full return and bounds.
The separate inert adapter exercises both orders/recipients and successive uses.
Its opcode interpreter derives copy registers/writes independently of the
validator descriptor table. Bad context/caller/task/flags/buffer/position,
noncompiled byte images, unrelated mutations and early cleanup are rejected.
Identical native words cannot disclose invisible redundant/skipped writes from
observed bytes; this remains a review limitation, never an acceptance claim.

The r3 preparation wrapper contains no execution path. A future reviewed record
must bind exact helper/generator/generated source/compiled observer/ELF/library/
proof/bindings/full-aggregate hashes; a boolean cannot transfer admission.
At this checkpoint that final record and aggregate are unavailable. Keep closed.
Private offline output is bounded128MiB and retained locally, including failures.
Do not alter or reprocess prior RGB recordings; no independently verified backup.
Full opening+cold reservation stays10000408128 bytes, irrelevant to admission
until review. No merge or issue116 edit. See the [checkpoint evidence](../evidence/floor1/c01/medicine-transaction-r3-20261010/README.md).
