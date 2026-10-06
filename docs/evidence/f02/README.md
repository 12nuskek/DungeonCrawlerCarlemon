# F02 fresh-environment evidence — 2026-10-06

Implemented, compiled and runtime verified: **PASS**. Integration tracked in
[progress](../../progress.md). PR: https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/3
Base: `1af617261881fcc26c6bb0fbd924d4c8a3c56d9a` (merged F01).
Tested implementation: `fcf3bd049e5369b8fcc3015244fe53c2f557e744`.
Following commits in this task add documentation/evidence only.

Ran `DCC_PROXY_HOST_MAPPING=proxy:172.31.6.29 bash scripts/verify-container.sh`
in the saved Cloud environment. This address was the observed host resolution for
this run only; resolve the actual proxy afresh in future environments. Command
exited 0. The source commit was captured before image building and reused for
both archives, so later branch movement cannot change the tested inputs.

Fresh Debian 13.6 root filesystem, pinned image digest in [image.json](image.json).
No host compiler cache, engine build products or repository mounted in the test
container. Image contains tools only. Source streamed from `git archive`; setup
fetched exact upstream/compiler commits into an empty container cache, rebuilt
agbcc, hydrated the three verified upstream inputs, built and compared the ROM.
The disposable test container was removed after extracting scoped evidence.

Build: [full log](build.log), [comparison](compare.log), [ROM SHA-256](rom.sha256).
Result is the same 16 MiB matching ROM as F01:
`a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af`.
Complete dependency versions: [packages.tsv](packages.tsv). Container libpng is
1.6.48-1+deb13u6 versus the initial host's deb13u5; the expected ROM remains exact.
Dependencies receive Debian security updates; no byte-identical container-layer
or offline build claim is made.

Runtime: real mGBA 0.10.5, built-in BIOS, no loaded save. The unchanged
[F01 button/frame route](../f01/route.txt) reaches title, New Game menu and Birch
introduction. [Boot trace](boot.log) records three passing RGB fingerprints at
frames 1262, 1443 and 2044. [Title](title.png), [menu](menu.png) and
[introduction](new-game.png) screenshots were also visually inspected.

The harness now rejects malformed/empty/truncated routes, missing checkpoints,
wrong inputs and zero-length steps. Required fingerprints derive from the F01
visually inspected software-rendered RGB frames. They are baseline-specific
regression assertions, not general gameplay acceptance or a substitute for later
playthroughs. [Ten test cases](negative-tests.log) pass, including both dirty
tracked and dirty untracked compiler-cache rejection before network/import work,
with source contents preserved. New files pass shell syntax and diff checks.

## Resolved setup failures

1. Docker client tried a read-only home path: redirected its cache to the workspace.
2. Default container networking lacked the managed proxy: passed standard proxy
   variables and the host public trust bundle, keeping TLS verification enabled.
3. Proxy hostname did not resolve inside Docker: passed its observed host mapping;
   network connection then succeeded. No further attempts at that blocker needed.
4. The copied public CA bundle inherited owner-only permissions: made it 0644 so
   apt's unprivileged downloader could read it. Dependency installation succeeded.

After the first successful fresh OS build/boot, the parent review findings were
fixed and the entire final committed implementation was rebuilt and run in a new
container. Both fresh runs produced the same ROM. Final evidence checksums are
listed in [evidence.sha256](evidence.sha256). Raw setup/image/emulator diagnostics
remain in the ignored local `artifacts/container/run-MwwsEI` directory.

No engine or gameplay changes; `git diff 1af6172 -- engine` is empty. No ROM,
compiled binary, workflow or scheduler added. Stages 1–5 remain pending.
