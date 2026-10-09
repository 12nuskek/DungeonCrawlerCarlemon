# F1-G01e live opening migration

2026-10-07; base b694da17928b93ea579f55d905017aa9f7619422, sole Cloud task
01a10f4b-596b-700b-b8ba-241e3ca2c000, branch task/floor1-g01e-live-migration.
PR73 merged the complete five-map diagnostic contract:23/10541;94 exact pixels.

Outcome: append the reviewed five production identities without changing legacy
headers/layout IDs; preserve old gameplay/content once at new semantic anchors;
version0 ordinary saves migrate before header lookup through the local spawn path.
Version1 cold loads are idempotent. Unknown schema/unsupported current identities
reject Continue with readable text and no save write. Remap all owned saved warp
records, rebuild cache/player/templates/live objects and preserve party/items/state.
Fresh saves stamp version1 after event initialization. Far-side loop is persistent,
opens only at36,16 interacting west35,16, and remains optional.

Scope: crawler compatibility/load hooks, explicit membership, generated authored
maps/scripts/presentation, small host generation and read-only runtime tools/docs.
Exclude battle/resource balance, save ABI expansion, trainer count changes, native
art rollout, later districts, finalT, public release, parallel writers/schedulers.

Acceptance: fresh committed build; six old map controller cold/interaction/return/
manual save/second cold checks including mandatory I01 and corner originals; all
old flags/party/inventory preserved at migration, legal player/camera/object state;
controlled warp-index/stale-layout/invalid position/continue-warp/future-version/
stock-nonmember boundaries with no API-only substitute for ordinary controllers.
Recheck both patrol orders/travel ceilings and live loop save/reload; meaningful
win/one-down/both-down/local retry and repeats/craft/quest/stairs. Review diff,
push/draft PR, merge only verified scoped behavior; preserve failed attempts and
raw evidence. No production runtime pass claimed before it actually happens.

Warp policy: valid legacy warp indices first normalize through that legacy header's
coordinates. Corridor indices0/1 consequently choose Guard/Howler. Then all owned
records become declared safe semantic coordinates with WARP_ID_NONE. Current
ordinary saved position takes precedence over stale location x/y/warpId; active
continue-warp takes its normalized record destination. Dummy and stock records
remain byte-identical. Version1 rejects old current IDs rather than downgrading.

Next: implementation, clean compile and ordinary migrated controller matrix.
