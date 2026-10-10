"""New-input pair: compile unchanged observer and bind the actual selected ELF.

This entry point never calls the gameplay runner, executes the generated host,
loads a ROM/Save, or creates a runtime expected stream. Native ABI objects are
inspected; the optional age fixture is ordinary host C with synthetic memory.
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

ROOT = Path(__file__).resolve().parents[1]
ELF = "98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d"
HOST = "1647352d92b3fa6f0135cf80f4c48df1c2a8a3818b711fd94651390a6334977f"
HOST_BINARY = "a17ea5134e700efd77552d9a279fd4d6dd94294d443683b8e9fbfe142361ccbd"
GAME = "9c83611e8e9b61d55388c18496c361d3362e462e"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/floor1" / filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", type=Path, required=True)
    parser.add_argument("--tool-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true", help="Resume completed offline artifacts after a diagnosed tooling failure")
    parser.add_argument("--game", required=True)
    parser.add_argument("--host-artifacts", type=Path, help="Reuse byte-exact already compiled unchanged host")
    args = parser.parse_args()
    global ELF, HOST_BINARY, GAME
    GAME = args.game
    ELF = sha(args.engine / "pokeemerald.elf")
    engine, tool, out = args.engine.resolve(), args.tool_root.resolve(), args.output.resolve()
    assert sha(engine / "pokeemerald.elf") == ELF
    if GAME == "9c83611e8e9b61d55388c18496c361d3362e462e":
        assert (engine / "src/dcc_battle_pose.c").read_bytes() == (ROOT / "engine/src/dcc_battle_pose.c").read_bytes()
    assert git("rev-parse", GAME + ":engine") in ("76001ee128785714b7c15aef6d9c95630587d0a9", "8d8c7761f4878bb9a8d7e2bffe36ed38da08aa6a")
    if args.resume:
        assert out.is_dir() and sha(out / "observer.c") == HOST
        assert sha(out / "observer-compile-only") == HOST_BINARY
    else:
        out.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    env["PATH"] = str(tool / "usr/bin") + ":" + env["PATH"]
    # Imported exporters also launch objdump; use the selected tools there.
    os.environ["PATH"] = env["PATH"]
    commands = []

    def run(command, cwd=ROOT, **kwargs):
        commands.append(command)
        return subprocess.run(command, cwd=cwd, env=env, check=True,
                              capture_output=True, **kwargs).stdout

    # No seed_snapshot, fixtures, runner main, Save copy, or reference verifier.
    if args.resume:
        code = (out / "observer.c").read_text()
    else:
        code, _ = module("offline_host", "v01-battle-host.py").generate(git)
        (out / "observer.c").write_text(code)
    assert sha(out / "observer.c") == HOST
    assert "busWrite" not in code and "core->runFrame(core);" not in code
    assert code.count("bv_native_frame(&native,") == 1
    libdir = tool / "usr/lib/x86_64-linux-gnu"
    library = libdir / "libmgba.so.0.10.5"
    assert sha(library) == "a1d7713cc89e3a4e4eeaf2bc7a523115356ebe14e057805c06f5e9d4a328be63"
    compiler = ["cc", "-DUSE_DEBUGGERS", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                "-I" + str(tool / "usr/include")]
    if args.host_artifacts:
        import shutil
        assert sha(args.host_artifacts / "observer.c") == sha(out / "observer.c") == HOST
        shutil.copyfile(args.host_artifacts / "observer-compile-only", out / "observer-compile-only")
        (out / "observer-compile-only").chmod(0o755)
        assert sha(out / "observer-compile-only") == sha(args.host_artifacts / "observer-compile-only")
    elif not args.resume:
        run(compiler + [str(out / "observer.c"), "-L" + str(libdir), "-lmgba",
                        "-o", str(out / "observer-compile-only")])
    HOST_BINARY = sha(out / "observer-compile-only")
    # Generated host is deliberately never invoked, including --help.
    native = module("offline_native", "v01-native-boundary-symbols.py")
    symbols = native.symbols
    if args.resume and (out / "native-boundary.json").exists():
        boundary = json.loads((out / "native-boundary.json").read_text())
        assert boundary["ELF_SHA256"] == ELF
        assert boundary == native.resolve(engine / "pokeemerald.elf")
    else:
        boundary = native.write(engine / "pokeemerald.elf", out / "native-boundary.json")
    assert (boundary["entry"], boundary["caller_BL"], boundary["caller_LR"], boundary["entry_opcode"]) == (
        0x080008AC, 0x080004BA, 0x080004BF, 0xB500)
    text = run(["arm-none-eabi-nm", "--defined-only", str(engine / "pokeemerald.elf")], text=True)
    text += run(["python3", str(ROOT / "scripts/battle-input-symbols.py"), str(engine)], text=True)
    if args.resume and (out / "verified-functions.json").exists():
        verified = json.loads((out / "verified-functions.json").read_text())
        assert verified == symbols.functions(symbols.elf_symbols(engine / "pokeemerald.elf"))
        text += ''.join(f'{r["address"]:08x} F {r["token"]}\n' for r in verified) + symbols.lifecycle_symbols(verified)
    else:
        text += symbols.export(engine / "pokeemerald.elf", out / "verified-functions.json")
    for name, key in [("Entry", "entry"), ("Caller", "caller_LR"), ("Opcode", "entry_opcode")]:
        text += f"{boundary[key]:08x} A bv_native{name}\n"
    text += module("offline_timeline", "v01-native-timeline-symbols.py").export(
        engine / "pokeemerald.elf", out / "native-timeline-points.json")
    (out / "game.sym").write_text(text)
    rows = [line.split() for line in text.splitlines()]
    required = sorted(set(re.findall(r'strcmp\(symbol,\s*"([^"]+)"\)', code)))
    bindings = {}
    optional_absent = {"gDccCollectionProbe", "gDccEquipmentProbe", "gDccMembershipProbe", "gDccRewardProbe"}
    route = (ROOT / "scripts/contracts/f1-v01-battle.route").read_text()
    assert not any(line.startswith("policy ") for line in route.splitlines())
    if GAME == "c6d647a815ffce44a2419a2cf83b6c2c094359f0":
        optional_absent.add("sDccBattlePoses")
    legacy_bindings = {}
    verified_rows = json.loads((out / "verified-functions.json").read_text())
    for name in required:
        ordered = [int(address, 16) for address, kind, label in rows if label == name]
        hits = set(ordered)
        if name in optional_absent:
            assert not hits  # Inherited policy command fails closed; frozen route never calls it.
            legacy_bindings[name] = {"present": False, "route_uses_policy_command": False}
            continue
        if name == "Task_DisplayHPRestoredMessage":
            # Preserve the inherited parser's last-row assignment. Verify its
            # effective target by scoped STT_FUNC, without silently rerouting it.
            candidates = [r for r in verified_rows if any(a.endswith(":" + name) for a in r["aliases"])]
            assert len(hits) == len(candidates) == 2
            target = [r for r in candidates if "L:party_menu.o:" + name in r["aliases"]]
            assert len(target) == 1 and ordered[-1] == target[0]["address"]
            legacy_bindings[name] = {"raw_addresses": ordered, "effective_address": ordered[-1],
                                     "effective_identity": target[0]["identity"], "globally_unique": False}
        else:
            assert len(hits) == 1, (name, "missing or ambiguous observer binding")
        bindings[name] = ordered[-1]
    functions = json.loads((out / "verified-functions.json").read_text())
    for field, identity in symbols.LIFECYCLE_FUNCTIONS.items():
        hits = [row for row in functions if identity in row["aliases"]]
        assert len(hits) == 1 and bindings["bv_" + field] == hits[0]["address"]
    # Fail-closed symbol negatives, without changing any native files.
    rejected = 0
    for identity in symbols.LIFECYCLE_FUNCTIONS.values():
        try:
            symbols.lifecycle_symbols([r for r in functions if identity not in r["aliases"]])
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("Missing lifecycle identity accepted")
    assert rejected == 11

    audit = module("offline_sections", "v01-static-build-audit.py")
    evidence = json.loads((ROOT / "docs/evidence/floor1/v01/battle/build-provenance/static-audit.json").read_text())
    abi = ROOT / "scripts/floor1/v01-observer-binding-abi.c"
    assert sha(abi) == evidence["native_ABI_source_sha256"]
    assert abi.read_text().startswith((ROOT / "scripts/floor1/v01-battle-layout.c").read_text())
    for filename, name in [("sprite.c", "SpriteCopyRequest"), ("malloc.c", "MemBlock")]:
        declaration = re.search(r"^struct " + name + r"\s*\{.*?^\};",
                                (engine / "src" / filename).read_text(), re.M | re.S)[0]
        assert declaration in abi.read_text()
    pp = run(["gcc", "-E", "-iquote", "include", "-iquote", "src", "-Wno-trigraphs", "-DMODERN=0",
              "-I", "tools/agbcc/include", "-I", "tools/agbcc", "-nostdinc", "-undef", "-std=gnu89", str(abi)],
             cwd=engine)
    assembly = run(["tools/agbcc/bin/agbcc", "-mthumb-interwork", "-Wimplicit", "-Wparentheses", "-Werror",
                    "-O2", "-fhex-asm", "-o", "-", "-"], cwd=engine, input=pp)
    (out / "native-abi.s").write_bytes(assembly + b"\n.text\n\t.align\t2, 0\n")
    obj = out / "native-abi.o"
    run(["arm-none-eabi-as", "-mcpu=arm7tdmi", "--defsym", "MODERN=0", "-o", str(obj), str(out / "native-abi.s")])
    data = audit.sections(obj)[".rodata"]["bytes"]
    objects = symbols.elf_symbols(obj)

    def constant(name):
        hits = [r for r in objects if r["name"] == name]
        assert len(hits) == 1
        r = hits[0]
        return data[r["value"]:r["value"] + r["size"]]

    values = struct.unpack("<18I", constant("observerLayout"))
    assert list(values) == list(evidence["observer_layout"].values())
    for bit in evidence["observer_bitfields"]:
        value = constant(bit["name"])
        assert value[bit["offset"]] == sum(value) == bit["value"]
    observer = (ROOT / "scripts/floor1/v01-battle-observer.h").read_text()
    snapshot = observer.split("static unsigned bv_snapshot(", 1)[1].split("static void bv_snapshot_mismatch", 1)[0]
    assert "poseState" not in snapshot  # Existing strict 2560-byte definition stays intact.
    assert "core->busRead8(core,v->a.poseState+5)>=18" in observer
    assert "for(unsigned i=0;i<16;i++)if(core->busRead8(core,v->a.poseState+i))" in observer
    result = {
        "scope": "Offline host compile and exact active ELF bindings; no generated-host invocation or emulator execution",
        "source_checkpoint": git("rev-parse", "HEAD"), "active_game_source": GAME,
        "engine_tree": git("rev-parse", GAME + ":engine"), "ELF_SHA256": ELF,
        "host_source_SHA256": sha(out / "observer.c"), "host_binary_SHA256": sha(out / "observer-compile-only"),
        "library_SHA256": sha(library), "symbols_SHA256": sha(out / "game.sym"),
        "verified_functions_SHA256": sha(out / "verified-functions.json"),
        "native_boundary_SHA256": sha(out / "native-boundary.json"),
        "native_timeline_SHA256": sha(out / "native-timeline-points.json"),
        "native_ABI_source_SHA256": sha(abi), "native_ABI_object_SHA256": sha(obj),
        "observer_binding_count": len(bindings), "bindings": bindings, "inherited_parser_limits": legacy_bindings,
        "canonical_function_count": len(functions), "unique_lifecycle_functions": 11,
        "missing_lifecycle_rejections": rejected, "native_timeline_points": 21,
        "native_layout_assertions": 13, "compiled_ABI_constants": 18, "compiled_bitfields": 6,
        "generated_host_invocations": 0, "emulator_executions": 0, "Save_accesses": 0,
        "new_runtime_expected_streams": 0, "baseline_executions": 6, "candidate_executions": 4,
        "gameplay_prepared": False, "runtime_verified": False, "merged": False,
        "new_pair_baseline_executions": 0, "new_pair_candidate_executions": 0,
        "limitations": ["Ordinary Save bytes unavailable after one failed supported download; no retry.",
                        "Complete original raw reference/expected-boundary stream unavailable.",
                        "Original legacy inputs unavailable; no replacement acceptance.",
                        "Offline binding cannot prove game cadence, visual acceptance, cleanup, rewards or Save persistence."],
        "commands": commands, "PASS": True,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("commands", "bindings", "limitations")}))


if __name__ == "__main__":
    main()
