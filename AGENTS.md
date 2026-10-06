# DungeonCrawlerCarlemon working contract

Read docs/progress.md and current remote branches/PRs before changing anything.
One implementation writer and one dependency-ready task at a time. Preserve work.
Scope: Stages 0–5, then at most five evidence-led improvement cycles; await Kurt's
playtest before Stage 6. Parent owns continuation; never add a scheduler here.

Foundation gate: exact stock pret/pokeemerald pin, matching clean build, ROM
identity and real emulator boot must pass before gameplay edits. Compilation
never proves runtime. Record implemented, compiled, runtime verified and merged
separately. Use pinned INSTALL.md and docs/testing.md for build commands.

Keep engine internals named as upstream where renaming creates churn. Reuse
src/battle*, src/pokemon.c and the held-item slot through small crawler interfaces;
field code handles exploration, data/maps scripts content, save code persistence.
Separate high-risk engine changes from content changes. No capture, breeding,
storage, capture tutorial, shops or rewards may expose creature collection in
the eventual slice; audit both interface and battle-rule paths.

Both Carl and Donut remain permanent. Accessible defeat recovery; original Book 1
opening adaptation dialogue only, no later spoilers. Mark uncertain chronology
and intentional departures in docs/content-ledger.md, never invent canon.

Manual saves outside battles. Declare compatibility per milestone; no unreviewed
save-layout changes. Persistent unique reward IDs, idempotent awards, atomic
crafting capacity/material checks. Optional items must not block progression.

For each task record base, tested commit, commands/results, runtime route/evidence,
PR/merge state, blockers and exact next action. Review diff before commit/push/PR;
merge runtime-sensitive changes only after relevant runtime checks. Honour
protections. Stop a blocker after three materially different unsuccessful fixes.
Continue genuinely independent documentation/content when a gate is blocked.

Never commit ROMs, build products, saves or private credentials; never force-push,
wipe history, alter visibility/billing, bypass protections or publish a playable
public release. Provenance and remaining placeholders must be explicit.
