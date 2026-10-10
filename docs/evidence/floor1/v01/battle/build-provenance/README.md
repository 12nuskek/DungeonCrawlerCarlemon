# Pre-mask ROM parity and active static budget

2026-10-09. Parent accepted offline implementation checkpoint `d5b2a784` / source `9c83611e`. This increment performs one isolated unchanged pre-mask engine compile and static inspection. Game/engine code, policy, route, observer and behavioral assertions are unchanged. Existing draft PR114 remains unmerged. **Zero emulator execution, gameplay preparation, Save access, reference reconstruction or upload retries. Counts remain six baseline/four candidate executions.**

## One-build provenance result

Exact pre-mask engine tree `baac7fee52e2133fa6192799ef3851f629f188d7` was exported from Git into a new isolated build directory in this same selected workspace. It is also the engine tree of source `2feadf56764c0d89c3dde9ef4622ea6d43b32f69`. The three required upstream multiboot blobs were copied from the existing build after checking their recorded Git blob identities. Existing recovered tool binaries were installed locally into the isolated tree, then **one** full `make -j2` invocation completed. No compiler variant search or game rebuild/retry occurred.

Rebuilt ROM SHA256 is exactly the historical pin:

`a022b2a5030214f8cbeb0621af47e6cb9a47208424aa86f56b67862b5028f8d4`

This establishes byte parity for this engine with these recovered tools and source/assets. It does not establish original compiler binary identity, historical execution equivalence or private-input recovery. New rebuilt ELF SHA256 is `f1dc95e4efcd16afd65dce33b4f85af88975077e3545eccf3fdb39c38fe074ec`; the original ELF bytes are unavailable for a section-level comparison, so no cause of their differing hashes is asserted.

Compiler source remains `da598c1d918402c42c0c0d7128ba14567f3175e9`; GCC14.2.0 and binutils2.44-3+23+b1. Rebuilt agbcc SHA256 remains `58078c3fe54c564bf23496d355f498a394fd5bb2b3a933e35cc835cc9bb14e0e`, differing from historical `6347d07ec65fb1a5df58f4fa79a807db11ac7bef32ffb6162ffb79bc68512684`. Both auxiliary compiler binary hashes also differ. [Provenance](provenance.json) records all exact hashes, the single compile, verified hydration and build-log identity. Identical emitted ROM bytes do not imply identical compiler executable files.

## Active ELF static headroom

Inspected the existing active ELF with exact SHA256 `98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d`, engine tree `8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a`. No active game rebuild or execution occurred.

| Region | Capacity | Active linked bytes | Static unallocated bytes | Growth from rebuilt pre-mask |
| --- | ---: | ---: | ---: | ---: |
| EWRAM | 262144 | 249732 | 12412 | 4 |
| IWRAM | 32768 | 30892 | 1876 | 0 |

EWRAM ends at `0x0203cf84`; IWRAM ends at `0x030078ac`. The sixteen-byte pose state remains at `0x0203cf68`; the two one-byte masks occupy `0x0203cf78` and `0x0203cf79`. Total linked EWRAM growth is four bytes after alignment. The existing `gHeap` reservation is 114688 bytes (`0x1c000`) at `0x02000000`, already included in EWRAM usage.

The compiled startup stack words are SYSTEM `0x03007e40` and IRQ `0x03007fa0`, matching unchanged `crt0.s`; the interrupt vector is `0x03007ffc`. The static gap below initial SYSTEM SP is 1428 bytes. The 1876-byte raw IWRAM remainder includes stack/top reservations and is not an allocation budget. No runtime stack high-water mark, heap allocation peak or dynamic free-heap acceptance was measured or transferred.

## Native boundary and observer ABI pins

The unchanged exact-ELF resolver verified unique scoped STT_FUNC identities, the one direct AgbMain Wait call, its preceding PlayTimeCounter_Update/MapMusicMain call order and eight relevant native function hashes. Eleven observer lifecycle identities resolve uniquely. [Native boundary record](native-boundary.json) pins:

- WaitForVBlank entry: `0x080008ac`.
- AgbMain BL: `0x080004ba`; caller LR: `0x080004bf`.
- Entry instruction: `0xb500` (`push {lr}`).
- Three-call bytes: `83f005fca2f0f9fa00f0f7f9`.

These values match the unchanged host/runtime hard pins. This static check does not establish live CPU mode, prefetch, event timing, breakpoint authority or boundary-stream acceptance.

The unchanged thirteen native layout assertions compiled against actual ARM headers. Additional compiled constants match observer requirements: Pokemon 100/BoxPokemon 80/BattlePokemon 88 bytes, HP offset 40, SaveBlock1 `0x3d88`/SaveBlock2 `0xf2c`, flags offset `0x1270`/300 bytes, resource span `0x490..0x988`/1272 bytes and battle-turn offset `0x13`. Sprite-copy requests have stride 12, destination offset 4 and size offset 8; allocator headers have size 16, magic offset 2, size offset 4 and next offset 12. Source-local request/allocator declarations were copied verbatim from native C for inspection; game sources were not edited.

Native compiler constant objects also verify sprite inUse byte 62/mask 1, invisible 62/4, animBeginning 63/4, usingSheet 63/64, Main inBattle byte `0x439`/mask 2 and fade active 7/128. The original sprite/main/task/graphics offsets and sixteen-byte pose state remain intact. Objects were inspected, never executed. [Static audit](static-audit.json) records exact results and compiled-object/source hashes.

## Reproduction and review scope

The single game compile used the same tool environment as the accepted active build:

```sh
git archive --format=tar --prefix=engine/ baac7fee52e2133fa6192799ef3851f629f188d7
# Extract into an empty isolated directory; verify/copy the three recorded upstream blobs.
# Install the existing recorded agbcc binaries into that isolated engine tree.
PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/bin:$PATH PKG_CONFIG_SYSROOT_DIR=/workspace/scratch/v01-active-pose-tooling/root PKG_CONFIG_LIBDIR=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu/pkgconfig CPATH=/workspace/scratch/v01-active-pose-tooling/root/usr/include LIBRARY_PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu LD_LIBRARY_PATH=/workspace/scratch/v01-active-pose-tooling/root/usr/lib/x86_64-linux-gnu make -C /workspace/scratch/v01-pre-mask-provenance/engine -j2
python3 scripts/floor1/v01-static-build-audit.py --active-engine /workspace/scratch/v01-active-pose-build/engine --pre-mask-engine /workspace/scratch/v01-pre-mask-provenance/engine --tool-root /workspace/scratch/v01-active-pose-tooling/root --output /workspace/scratch/v01-pre-mask-provenance/static-audit
```

The audit script hashes already built files, reads ELF data and compiles a constant ABI unit; it does not compile the game, load a ROM/Save into an emulator or execute CPU instructions. Its final inspection also checks the compiled stack words. No further old synthetic lifecycle/cost checks were rerun. Review confirmed that this scoped diff contains only the diagnostic script and safe provenance/budget evidence; engine code and all existing behavioral assertions remain unchanged. ROMs, ELF/object files, private inputs and raw historical datasets stay outside publication. Denied private history/status material remains excluded.

Stop at documented ROM parity and verified static pins. Parent review of this evidence is dependency-ready now. Runtime validation remains blocked until the original private complete reference and other required inputs are available and exactly verified, followed by separate authorization. No new oracle, baseline restart, lost-iteration inference, victory/cleanup/Save acceptance or visual rollout claim. All prior failures, controller/strategy records and original legacy/C01/human-pacing/full-floor limitations remain.
