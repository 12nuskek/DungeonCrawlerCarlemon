"""Compile actual old/new modules and measure bounded synthetic ARM paths.

No ROM is loaded; only module instruction/data segments and native bit masks.
The existing interpreter fixture supplies controlled RAM and counted stubs.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = "6d6a80aaea6eb7e6a54e17f6f210c8f87167e1e9"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--engine", type=Path, required=True)
    p.add_argument("--tool-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    base, tool, out = a.engine.resolve(), a.tool_root.resolve(), a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PATH"] = str(tool / "usr/bin") + ":" + env["PATH"]
    env["LD_LIBRARY_PATH"] = str(tool / "usr/lib/x86_64-linux-gnu")
    spec = importlib.util.spec_from_file_location("pose_symbols", ROOT / "scripts/floor1/v01-native-boundary-symbols.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    native = m.symbols.elf_symbols(base / "pokeemerald.elf")
    defs = {x["name"]: x["value"] for x in native if x["bind"] == 1 and x["index"]}
    commands = []

    def run(cmd, **kw):
        commands.append(cmd)
        return subprocess.run(cmd, env=env, check=True, capture_output=True, **kw).stdout

    def compile_c(path):
        pp = run(["gcc", "-E", "-iquote", "include", "-iquote", "src", "-Wno-trigraphs",
                  "-DMODERN=0", "-I", "tools/agbcc/include", "-I", "tools/agbcc", "-nostdinc",
                  "-undef", "-std=gnu89", str(path)], cwd=base)
        pp = run(["tools/preproc/preproc", "-i", "-g", "build/assets", str(path), "charmap.txt"], input=pp, cwd=base)
        asm = run(["tools/agbcc/bin/agbcc", "-mthumb-interwork", "-Wimplicit", "-Wparentheses", "-Werror",
                   "-O2", "-fhex-asm", "-g", "-o", "-", "-"], input=pp, cwd=base)
        path.with_suffix(".s").write_bytes(asm + b"\n.text\n\t.align\t2, 0\n")
        run(["arm-none-eabi-as", "-mcpu=arm7tdmi", "--defsym", "MODERN=0", "-o", str(path.with_suffix(".o")), str(path.with_suffix(".s"))], cwd=base)
        return path.with_suffix(".o")

    def section(path, name):
        data = path.read_bytes()
        h = struct.unpack_from("<16sHHIIIIIHHHHHH", data)
        rows = [struct.unpack_from("<10I", data, h[6] + i * h[11]) for i in range(h[12])]
        strings = rows[h[13]]
        table = data[strings[4]:strings[4] + strings[5]]
        for r in rows:
            if table[r[0]:table.index(0, r[0])].decode() == name:
                return r[3], data[r[4]:r[4] + r[5]]
        raise ValueError(name)

    layout = out / "layout.c"
    layout.write_text('#include "global.h"\n#include "battle.h"\n'
                      'const u32 poseLayout[] = {sizeof(struct BattlePokemon), (u32)&((struct BattlePokemon *)0)->hp};\n')
    mon_size, hp_offset = struct.unpack("<II", section(compile_c(layout), ".rodata")[1])
    native_layout = out / "native-layout.c"
    native_layout.write_bytes((ROOT / "scripts/floor1/v01-battle-layout.c").read_bytes())
    compile_c(native_layout)  # Existing native ABI assertions, unchanged.
    (out / "audit.ld").write_text("SECTIONS { .text 0x08010000 : { *(.text) } .rodata 0x08100000 : { *(.rodata) } ewram_data 0x02038000 : { *(ewram_data) } }\n")
    sources = {
        "baseline": subprocess.check_output(["git", "show", BASE + ":engine/src/dcc_battle_pose.c"], cwd=ROOT).decode(),
        "candidate": (ROOT / "engine/src/dcc_battle_pose.c").read_text(),
    }
    identities = {}
    for name, text in sources.items():
        path = out / (name + ".c")
        path.write_text(text)
        obj = compile_c(path)
        if name == "candidate":
            assert section(obj, ".text")[1] == section(base / "build/emerald/src/dcc_battle_pose.o", ".text")[1]
        unresolved = [line.split()[-1] for line in run(["arm-none-eabi-nm", "-u", str(obj)], text=True).splitlines()]
        elf = out / (name + ".elf")
        assert all(n in defs for n in unresolved)
        run(["arm-none-eabi-ld", "-T", str(out / "audit.ld"), "-o", str(elf), str(obj)] +
            ["--defsym=" + n + "=" + hex(defs[n]) for n in unresolved])
        syms = m.symbols.elf_symbols(elf)
        state = [x for x in syms if x["name"] == "sDccBattlePoses"]
        assert len(state) == 1 and state[0]["size"] == 16
        values = {x["name"]: x["value"] for x in syms if x["index"]}
        names = ["DccBattlePoseUpdate", "Apply", "DccBattlePoseNotify", "gBattleTypeFlags", "gTrainerBattleOpponent_A",
                 "gBattleAnimAttacker", "gAnimScriptActive", "gBattlersCount", "gAbsentBattlerFlags", "gBattlerSpriteIds",
                 "gBattleMons", "gSprites", "gMonSpritesGfxPtr", "gBitTable", "sDccBattlePoses", "sDccPoseActive",
                 "sDccPosePending", "GetBattlerSide", "GetBattlerPosition", "CpuSet", "RequestSpriteCopy", "memset", "sDccPosePictures"]
        # Baseline lacks notifications; use its Update for the two notification
        # slots, and exclude those slots from before/after semantic comparisons.
        values.setdefault("DccBattlePoseNotify", values["DccBattlePoseUpdate"])
        values.setdefault("sDccPoseActive", 0)
        values.setdefault("sDccPosePending", 0)
        bindings = [values[n] & ~1 if n in names[:3] + names[17:22] else values[n] for n in names] + [mon_size, hp_offset]
        segments = [section(elf, ".text"), section(elf, ".rodata"),
                    (defs["gBitTable"], m.rom_bytes(base / "pokeemerald.elf", defs["gBitTable"], 16))]
        with (out / (name + ".bin")).open("wb") as f:
            f.write(struct.pack("<25I", *bindings)); f.write(struct.pack("<I", len(segments)))
            for address, data in segments:
                f.write(struct.pack("<II", address, len(data))); f.write(data)
        identities[name] = {"source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                            "object_text_sha256": hashlib.sha256(section(obj, ".text")[1]).hexdigest(),
                            "module_text_bytes": len(section(obj, ".text")[1])}
    run(["gcc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror", "-I" + str(tool / "usr/include"),
         str(ROOT / "scripts/floor1/v01-active-pose-cost.c"), "-L" + str(tool / "usr/lib/x86_64-linux-gnu"),
         "-lmgba", "-o", str(out / "fixture")])
    traces = {}
    for name in sources:
        r = subprocess.run([str(out / "fixture"), str(out / (name + ".bin"))], env=env, capture_output=True, text=True)
        (out / (name + "-trace.jsonl")).write_text(r.stdout)
        (out / (name + "-stderr.txt")).write_text(r.stderr)
        r.check_returncode()
        traces[name] = [json.loads(x) for x in r.stdout.splitlines()]
        assert len(traces[name]) == 28
    for i, (b, c) in enumerate(zip(traces["baseline"], traces["candidate"])):
        if i in (12, 13):
            continue
        for key in ("action", "recovering", "applied", "copies", "requests"):
            assert b[key] == c[key], (i, key, b, c)
    result = {
        "scope": "SYNTHETIC bounded module interpreter costs; unit ROM bus; native stubs excluded; no ROM/Save/gameplay",
        "actual_frame8536_state_retained": False,
        "frame8536_case": "Synthetic all-REST pattern only; no recovered state or historical timing claim",
        "candidate_matches_compiled_game_module_text": True,
        "existing_native_layout_assertions_compile": True,
        "pose_state_bytes": 16,
        "cases": 56, "identities": identities, "traces": traces,
        "agbcc_sha256": hashlib.sha256((base / "tools/agbcc/bin/agbcc").read_bytes()).hexdigest(),
        "libmgba_sha256": hashlib.sha256((tool / "usr/lib/x86_64-linux-gnu/libmgba.so.0.10.5").read_bytes()).hexdigest(),
        "commands": commands, "PASS": True,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("commands", "traces")}))


if __name__ == "__main__":
    main()
