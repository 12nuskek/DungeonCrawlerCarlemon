"""Synthetic source-level pose/observer age integration; no runtime inputs.

Reuse the existing native-event stubs and observer memory harness verbatim,
then connect current pose bytes and authored pixels to the unchanged observer.
No emulator is linked or invoked; capture is the original no-output unit stub.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ELF = "98fc1accd7516fb54baf15ba76cb954ca24a30051dfea63704a0efcf2882c53d"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal(filename, marker):
    values = [n.value for n in ast.walk(ast.parse((ROOT / "scripts" / filename).read_text()))
              if isinstance(n, ast.Constant) and isinstance(n.value, str) and marker in n.value]
    assert len(values) == 1
    return values[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--engine", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    engine, out = args.engine.resolve(), args.output.resolve()
    assert sha(engine / "pokeemerald.elf") == ELF
    assert (engine / "src/dcc_battle_pose.c").read_bytes() == (ROOT / "engine/src/dcc_battle_pose.c").read_bytes()
    out.mkdir(parents=True, exist_ok=False)
    headers = out / "headers"
    headers.mkdir()
    (headers / "constants").mkdir()
    (headers / "global.h").write_text(literal("test-f1-v01-battle-hook.py", "#ifndef MOCK_GLOBAL"))
    for name in ["battle.h", "battle_anim.h", "battle_setup.h", "battle_util.h", "sprite.h", "util.h"]:
        (headers / name).write_text('#include "global.h"\n')
    for name in ["moves.h", "species.h", "trainers.h"]:
        (headers / "constants" / name).write_bytes((engine / "include/constants" / name).read_bytes())
    spec = importlib.util.spec_from_file_location("age_native", ROOT / "scripts/floor1/v01-native-boundary-symbols.py")
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    symbols = native.symbols.elf_symbols(engine / "pokeemerald.elf")
    arrays, assets = [], []
    paths = re.findall(r'INCGFX_U32\("([^"]+)"', (engine / "src/data/dcc_battle_pose_graphics.h").read_text())
    assert len(paths) == 17
    for i, path in enumerate(paths):
        image = Image.open(engine / path)
        assert image.size == (64, 64) and image.mode == "P"
        pixels = list(image.get_flattened_data())
        assert max(pixels) < 16
        data = bytearray()
        for ty in range(0, 64, 8):
            for tx in range(0, 64, 8):
                for y in range(8):
                    for x in range(0, 8, 2):
                        n = (ty + y) * 64 + tx + x
                        data.append(pixels[n] | pixels[n + 1] << 4)
        row = [r for r in symbols if r["name"] == "sDccPose" + str(i) and r["index"]]
        assert len(row) == 1 and row[0]["size"] == 2048
        assert native.rom_bytes(engine / "pokeemerald.elf", row[0]["value"], 2048) == data
        arrays.append(f"static const u32 sDccPose{i}[512]={{" +
                      ",".join(hex(int.from_bytes(data[j:j + 4], "little")) for j in range(0, 2048, 4)) + "};")
        assets.append({"path": path, "compiled_pixels_sha256": hashlib.sha256(data).hexdigest()})
    arrays.append("static const u32 *const sDccPosePictures[]={" + ",".join(f"sDccPose{i}" for i in range(17)) + "};")
    (out / "assets.h").write_text("\n".join(arrays) + "\n")
    (out / "module.c").write_text((engine / "src/dcc_battle_pose.c").read_text().replace(
        '#include "data/dcc_battle_pose_graphics.h"', '#include "assets.h"'))
    event_harness = (ROOT / "scripts/floor1/v01-active-pose-equivalence.c").read_text().split("int main(void)", 1)[0]
    observer_harness = literal("test-f1-v01-battle-observer.py", "static unsigned fixture_trace(")
    observer_harness = observer_harness.split('#include "stop105-projection.h"', 1)[0]
    first = observer_harness.index("/* Diagnostic regression harness only:")
    last = observer_harness.index("static struct mCore core=")
    observer_harness = observer_harness[:first] + observer_harness[last:]
    # No original test body is changed or executed. Only setup/stubs are reused.
    fixture = "#define setup native_setup\n" + event_harness + "\n#undef setup\n" + observer_harness
    fixture += (ROOT / "scripts/floor1/v01-observer-age-fixture.c").read_text()
    (out / "age-integration.c").write_text(fixture)
    command = ["cc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror", "-Wno-unused-function",
               "-I" + str(out), "-I" + str(headers), "-I" + str(ROOT / "scripts/floor1"),
               "-idirafter", str(engine / "include"), str(out / "age-integration.c"), "-o", str(out / "age-integration")]
    compiled = subprocess.run(command, capture_output=True, text=True)
    (out / "compile.log").write_text(compiled.stdout + compiled.stderr)
    compiled.check_returncode()
    run = subprocess.run([str(out / "age-integration")], cwd=out, check=True, capture_output=True, text=True)
    (out / "fixture.log").write_text(run.stdout)
    record(engine, out, assets)


def record(engine, out, assets):
    """Record already-completed unit execution without recompiling or rerunning it."""
    stdout = (out / "fixture.log").read_text()
    assert "PASS source/observer age integration: 14 cases; no emulator, Save, reference stream or captures" in stdout
    assert not list(out.glob("*.bin")) and not list(out.glob("*.ppm")) and not list(out.glob("*.sav"))
    result = {"scope": "SYNTHETIC host C integration of current pose source and unchanged observer, not recovered state",
              "ELF_SHA256": ELF, "pose_source_SHA256": sha(engine / "src/dcc_battle_pose.c"),
              "observer_source_SHA256": sha(ROOT / "scripts/floor1/v01-battle-observer.h"),
              "fixture_source_SHA256": sha(out / "age-integration.c"), "fixture_binary_SHA256": sha(out / "age-integration"),
              "fixture_log_SHA256": sha(out / "fixture.log"), "cases": 14,
              "coverage": ["Both trainer IDs 858/859: native WINDUP reaches >=18 before sleep",
                           "Successful settled warning age freezes; native notification wakes and preserves warning",
                           "Unchanged observer accepts held warning during another actor's animation",
                           "Unchanged observer STOP108 on wrong warning pixels at >=18",
                           "Successful REST settles and freezes unused age without warning eligibility",
                           "Unchanged observer STOP105 on stale retirement age; actual reset then permits retirement/field"],
              "emulator_executions": 0, "generated_host_invocations": 0, "Save_accesses": 0,
              "new_runtime_expected_streams": 0, "actual_captures": 0,
              "baseline_executions": 6, "candidate_executions": 4, "assets": assets, "PASS": True}
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "assets"}))


if __name__ == "__main__":
    main()
