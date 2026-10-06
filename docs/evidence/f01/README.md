# F01 foundation evidence — 2026-10-06

Result: **matching build and real emulator boot pass**. No gameplay adaptation.
PR: https://github.com/12nuskek/DungeonCrawlerCarlemon/pull/2
Base: `8ac45a70f39bddf5fd50de7b3a40f436784ee3b8` (empty-repo docs bootstrap).
Engine/build tested commit: `ef471fc90335bacce3e23aa6349fd7eea80e958e`.
Final harness/route commit: `e9c8df785c4ed438a8d8938118c69c65349f4ec9`.
Later F01 commits change evidence/documentation only, not engine or harness.
Upstream and compiler pins: [provenance](../../upstream/provenance.md).

## Build identity

| Check | Observed result |
| --- | --- |
| Build | `bash scripts/build-baseline.sh`, exit 0 |
| Upstream comparison | `make -C engine compare`: `pokeemerald.gba: OK` |
| ROM size | 16,777,216 bytes |
| SHA-1 | `f3ae088181bf583e55daf962a92bb46f4f1d07b7` (upstream expected) |
| SHA-256 | `a9dec84dfe7f62ab2220bafaef7479da0929d066ece16a6885f6226db19085af` |
| Import audit | Every retained upstream tracked file byte-identical; no missing retained file in Git index |
| Source artifact audit | No tracked `.gba`, `.elf`, `.o`, `.a` or `.sav` files |

Full [build log](build.log), [compare log](compare.log), and
[second clean checkout comparison](reproduction-compare.log) are retained.
Build-log SHA-256: `4cb2f6180752750340a1d8203d1a23045328ddfbfc5b59163c7898bc9eb73c2d`.
Upstream formatting warnings in `git diff --check` were preserved; newly authored
files pass. The engine source has no functional or save-layout modifications.

## Toolchain and actual environment

Debian 13 amd64; GCC 14.2.0 (Debian 14.2.0-19), Make 4.4.1;
ARM binutils 2.44 (`2.44-3+23+b1`); libpng 1.6.48 (`1.6.48-1+deb13u5`);
mGBA 0.10.5 (`0.10.5+dfsg-1`), linked actual GBA emulation core.
agbcc built with `PATH=/workspace/toolchain/root/usr/bin:$PATH bash ./build.sh`
then `./install.sh /workspace/DungeonCrawlerCarlemon/engine`.

Packages were downloaded from Debian trixie main using isolated apt lists and
extracted with `dpkg-deb -x` into `/workspace/toolchain/root`, with no system writes.
Package checksums are in [packages.sha256](packages.sha256).
Build environment:

```sh
export PATH=/workspace/toolchain/root/usr/bin:$PATH
export PKG_CONFIG_SYSROOT_DIR=/workspace/toolchain/root
export PKG_CONFIG_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu/pkgconfig
export LIBRARY_PATH=/workspace/toolchain/root/usr/lib/x86_64-linux-gnu
bash scripts/build-baseline.sh
```

The extracted PNG development package's shared-library target was initially
missing, causing static-link math-symbol errors. Extracting the matching PNG
runtime package fixed it; no engine workaround. Empty initial apt lists were
resolved with workspace-local package lists. mGBA headers require GNU C mode
(`-std=gnu11`), as now documented. These setup issues are resolved, not blockers.

## Runtime route and observations

Compiled `scripts/boot-baseline.c` with GCC `-std=gnu11 -Wall -Wextra -Werror`,
using the extracted mGBA include/library paths and rpath. Ran the real core:

```sh
cd artifacts/boot
/workspace/toolchain/boot-baseline ../../engine/pokeemerald.gba \
  < ../../docs/evidence/f01/route.txt > boot.log 2> mgba.log
```

Exit 0. Built-in BIOS, no save loaded, 240×160 software rendering. [Route](route.txt)
and [execution trace](boot.log) contain exact frame counts and GBA key masks.
Initial exploratory captures calibrated title-animation timing; the recorded route
is the successful route, without RAM patching or debug game commands.

| Frame | Observation | Evidence |
| --- | --- | --- |
| 1262 | Emerald title, animated background and Press Start visible | [Title](title.png) |
| 1443 | New Game and Option menu after A from title | [Menu](menu.png) |
| 2044 | Birch rendered and introduction dialogue begins after New Game | [Introduction](new-game.png) |

Captures were visually inspected, in addition to checking emulator execution and
input-driven state transitions. Full diagnostic log remains locally under ignored
`artifacts/boot/mgba.log` (SHA-256
`1d6281f6698fe54784137ac0a5edebb679cf86e3409f4e1a7d47e10a2e9ef89f`).
mGBA emits BIOS/DMA/register diagnostic messages for this matching retail baseline;
these did not prevent the observed title/menu/introduction route. Boot validation
does not claim a complete new-game playthrough, save test, audio review or hardware
GBA validation.

## Reproduction and integration boundary

Cloned the committed source into `/workspace/f01-reproduction` using
`git clone --no-hardlinks`; ran its `scripts/setup-foundation.sh` with a new empty
`.cache` to fetch both exact upstream pins and build agbcc again. Then ran its
`scripts/build-baseline.sh`. Setup and build both exit 0; second ROM byte-identical
to first, including SHA-256 above. No build outputs copied from first checkout.
This proves clean-checkout reproduction on the same provisioned host, not a second
fresh OS environment. F02 should automate/prove fresh-environment provisioning.

The baseline retains all stock Pokémon mechanics intentionally. No catching,
duo combat, crawler maps, original art/dialogue or recovery adaptation is claimed
yet. Those belong to dependency-ordered Stages 1–5. No ROM is committed or released.
