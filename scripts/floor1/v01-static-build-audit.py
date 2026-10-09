"""Offline ELF/ABI inspection only: no ROM/Save loading or CPU execution.

The pre-mask ROM is hashed after one separately completed isolated compile.
Native headers and source-local structs are compiled to constant data; the
resulting ARM object is inspected, never executed. Game sources stay unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
ACTIVE_ELF = "98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d"
HISTORICAL_ROM = "a022b2a5030214f8cbeb0621af47e6cb9a47208424aa86f56b67862b5028f8d4"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sections(path):
    data = Path(path).read_bytes()
    h = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
    assert h[0][:7] == b"\x7fELF\x01\x01\x01" and h[2] == 40
    rows = [struct.unpack_from("<10I", data, h[6] + i * h[11]) for i in range(h[12])]
    s = rows[h[13]]
    names = data[s[4]:s[4] + s[5]]
    return {names[r[0]:names.index(0, r[0])].decode(): {
        "type": r[1], "address": r[3], "size": r[5],
        "bytes": data[r[4]:r[4] + r[5]] if r[1] != 8 else b"",
    } for r in rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--active-engine", type=Path, required=True)
    p.add_argument("--pre-mask-engine", type=Path, required=True)
    p.add_argument("--tool-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    active, old = args.active_engine.resolve(), args.pre_mask_engine.resolve()
    out, tool = args.output.resolve(), args.tool_root.resolve()
    out.mkdir(parents=True, exist_ok=True)
    assert sha(active / "pokeemerald.elf") == ACTIVE_ELF
    parity = sha(old / "pokeemerald.gba") == HISTORICAL_ROM
    assert parity, "STOP first concrete pre-mask ROM mismatch; no compiler search/rebuild"
    spec = importlib.util.spec_from_file_location("native_symbols", ROOT / "scripts/floor1/v01-native-boundary-symbols.py")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    boundary = native.resolve(active / "pokeemerald.elf")
    assert (boundary["entry"], boundary["caller_LR"], boundary["entry_opcode"]) == (0x080008AC, 0x080004BF, 0xB500)
    host = (ROOT / "scripts/floor1/v01-battle-host.py").read_text()
    runtime = (ROOT / "scripts/floor1/v01-native-boundary-runtime.h").read_text()
    assert "nativeEntry!=0x080008ac || nativeCaller!=0x080004bf || nativeOpcode!=0xb500" in host
    assert "entry!=0x080008ac || callerLR!=0x080004bf" in runtime
    funcs = native.symbols.functions(native.symbols.elf_symbols(active / "pokeemerald.elf"))
    lifecycle = native.symbols.lifecycle_symbols(funcs)  # Unique scoped STT_FUNC identities.
    (out / "native-boundary.json").write_text(json.dumps(boundary, indent=2) + "\n")
    budget = {}
    for name, base, capacity in [("ewram", 0x02000000, 0x40000), ("iwram", 0x03000000, 0x8000)]:
        now, before = sections(active / "pokeemerald.elf")[name], sections(old / "pokeemerald.elf")[name]
        assert now["type"] == before["type"] == 8 and now["address"] == before["address"] == base
        assert 0 <= now["size"] <= capacity
        budget[name] = {"origin": base, "capacity": capacity, "used": now["size"],
                        "linked_end": base + now["size"], "unallocated_static_bytes": capacity - now["size"],
                        "pre_mask_used": before["size"], "growth_bytes": now["size"] - before["size"]}
    assert "sp_sys: .word IWRAM_END - 0x1c0" in (ROOT / "engine/src/crt0.s").read_text()
    assert "sp_irq: .word IWRAM_END - 0x60" in (ROOT / "engine/src/crt0.s").read_text()
    sys_sp, irq_sp = 0x03008000 - 0x1C0, 0x03008000 - 0x60
    assert budget["iwram"]["linked_end"] < sys_sp < irq_sp < 0x03007FFC
    budget["stack"] = {"initial_system_sp": sys_sp, "initial_irq_sp": irq_sp,
                       "interrupt_vector": 0x03007FFC,
                       "static_gap_below_initial_system_sp": sys_sp - budget["iwram"]["linked_end"],
                       "runtime_stack_depth_measured": False}
    all_symbols = native.symbols.elf_symbols(active / "pokeemerald.elf")
    compiled_stack = {}
    for name, expected in [("sp_sys", sys_sp), ("sp_irq", irq_sp)]:
        hits = [x for x in all_symbols if x["name"] == name and x["index"]]
        assert len(hits) == 1
        address = hits[0]["value"]
        value = struct.unpack("<I", native.rom_bytes(active / "pokeemerald.elf", address, 4))[0]
        assert value == expected
        compiled_stack[name] = {"literal_address": address, "value": value}
    budget["stack"]["compiled_initial_stack_words"] = compiled_stack
    relevant = {}
    for name in ["gHeap", "sHeapStart", "sHeapSize", "sDccBattlePoses", "sDccPoseActive", "sDccPosePending"]:
        matches = [x for x in all_symbols if x["name"] == name and x["index"]]
        assert len(matches) == 1
        relevant[name] = {k: matches[0][k] for k in ["value", "size", "type"]}
    assert relevant["gHeap"] == {"value": 0x02000000, "size": 0x1C000, "type": 1}
    assert relevant["sDccBattlePoses"]["size"] == 16
    assert relevant["sDccPoseActive"]["size"] == relevant["sDccPosePending"]["size"] == 1
    budget["symbols"] = relevant
    budget["heap"] = {"reserved_bytes": 0x1C000, "included_in_ewram_used": True,
                      "runtime_allocations_or_free_heap_measured": False}
    # Compile the unchanged repository ABI assertions plus observer-specific
    # constants against native ARM headers and exact source-local declarations.
    layout = (ROOT / "scripts/floor1/v01-battle-layout.c").read_text()
    local_structs = []
    for filename, name in [("sprite.c", "SpriteCopyRequest"), ("malloc.c", "MemBlock")]:
        text = (active / "src" / filename).read_text()
        found = re.search(r"^struct " + name + r"\s*\{.*?^\};", text, re.M | re.S)
        assert found
        local_structs.append(found[0])
    fields = [
        ("pokemon_bytes", "sizeof(struct Pokemon)", 100),
        ("box_bytes", "sizeof(struct BoxPokemon)", 80),
        ("battle_mon_bytes", "sizeof(struct BattlePokemon)", 88),
        ("battle_hp_offset", "BV_OFFSET(struct BattlePokemon, hp)", 40),
        ("save1_bytes", "sizeof(struct SaveBlock1)", 0x3D88),
        ("save2_bytes", "sizeof(struct SaveBlock2)", 0xF2C),
        ("flags_offset", "BV_OFFSET(struct SaveBlock1, flags)", 0x1270),
        ("flags_bytes", "sizeof(((struct SaveBlock1 *)0)->flags)", 300),
        ("resource_start", "BV_OFFSET(struct SaveBlock1, money)", 0x490),
        ("resource_end", "BV_OFFSET(struct SaveBlock1, seen1)", 0x988),
        ("battle_turn_offset", "BV_OFFSET(struct BattleResults, battleTurnCounter)", 0x13),
        ("copy_request_bytes", "sizeof(struct SpriteCopyRequest)", 12),
        ("copy_dest_offset", "BV_OFFSET(struct SpriteCopyRequest, dest)", 4),
        ("copy_size_offset", "BV_OFFSET(struct SpriteCopyRequest, size)", 8),
        ("allocator_header_bytes", "sizeof(struct MemBlock)", 16),
        ("allocator_magic_offset", "BV_OFFSET(struct MemBlock, magic)", 2),
        ("allocator_size_offset", "BV_OFFSET(struct MemBlock, size)", 4),
        ("allocator_next_offset", "BV_OFFSET(struct MemBlock, next)", 12),
    ]
    extra = '\n#include "pokemon.h"\n' + "\n".join(local_structs) + "\n"
    extra += "const u32 observerLayout[] = {" + ",".join(x[1] for x in fields) + "};\n"
    extra += "const struct Sprite observerInUse = {.inUse = TRUE};\n"
    extra += "const struct Sprite observerInvisible = {.invisible = TRUE};\n"
    extra += "const struct Sprite observerAnimBeginning = {.animBeginning = TRUE};\n"
    extra += "const struct Sprite observerUsingSheet = {.usingSheet = TRUE};\n"
    extra += "const struct Main observerInBattle = {.inBattle = TRUE};\n"
    extra += "const struct PaletteFadeControl observerFadeActive = {.active = TRUE};\n"
    path = out / "native-abi.c"
    path.write_text(layout + extra)
    env = dict(os.environ)
    env["PATH"] = str(tool / "usr/bin") + ":" + env["PATH"]
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.run(cmd, cwd=active, env=env, check=True, capture_output=True, **kw).stdout

    pp = run(["gcc", "-E", "-iquote", "include", "-iquote", "src", "-Wno-trigraphs", "-DMODERN=0",
              "-I", "tools/agbcc/include", "-I", "tools/agbcc", "-nostdinc", "-undef", "-std=gnu89", str(path)])
    asm = run(["tools/agbcc/bin/agbcc", "-mthumb-interwork", "-Wimplicit", "-Wparentheses", "-Werror", "-O2",
               "-fhex-asm", "-g", "-o", "-", "-"], input=pp)
    path.with_suffix(".s").write_bytes(asm + b"\n.text\n\t.align\t2, 0\n")
    obj = path.with_suffix(".o")
    run(["arm-none-eabi-as", "-mcpu=arm7tdmi", "--defsym", "MODERN=0", "-o", str(obj), str(path.with_suffix(".s"))])
    const_data = sections(obj)[".rodata"]["bytes"]
    rows = native.symbols.elf_symbols(obj)

    def constant(name):
        hits = [x for x in rows if x["name"] == name]
        assert len(hits) == 1
        row = hits[0]
        return const_data[row["value"]:row["value"] + row["size"]]

    values = struct.unpack("<" + "I" * len(fields), constant("observerLayout"))
    assert list(values) == [x[2] for x in fields], "STOP first observer ABI mismatch"
    bitfields = [("observerInUse", 62, 1), ("observerInvisible", 62, 4),
                 ("observerAnimBeginning", 63, 4), ("observerUsingSheet", 63, 64),
                 ("observerInBattle", 0x439, 2), ("observerFadeActive", 7, 128)]
    for name, offset, expected in bitfields:
        data = constant(name)
        assert data[offset] == expected and sum(data) == expected, (name, offset)
    result = {"scope": "Static ELF and compiled native ABI inspection only; zero emulator/Save/runtime execution",
              "pre_mask_ROM_parity": parity, "active_ELF_sha256": ACTIVE_ELF,
              "memory": budget, "native_boundary_pins_verified": True,
              "unique_lifecycle_function_count": len(lifecycle.splitlines()),
              "existing_layout_assertions_compiled": True,
              "observer_layout": {row[0]: value for row, value in zip(fields, values)},
              "observer_bitfields": [{"name": n, "offset": o, "value": v} for n, o, v in bitfields],
              "native_ABI_source_sha256": sha(path), "native_ABI_object_sha256": sha(obj),
              "commands": commands, "baseline_executions": 6, "candidate_executions": 4, "PASS": True}
    (out / "static-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("commands", "observer_bitfields", "observer_layout")}))


if __name__ == "__main__":
    main()
