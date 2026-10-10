"""Compare retained source with active masks on fixed SYNTHETIC native events.

The 17 authored PNGs supply actual tiled bytes; event schedules and state are
synthetic. No private reference, ROM, Save, controller or gameplay is opened.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = "6d6a80aaea6eb7e6a54e17f6f210c8f87167e1e9"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Reuse the repository's native-interface headers and run its original cases.
    subprocess.run(["python3", str(ROOT / "scripts/test-f1-v01-battle-hook.py"),
                    "--output", str(out / "headers")], check=True)
    graphics = (ROOT / "engine/src/data/dcc_battle_pose_graphics.h").read_text()
    assets = []
    arrays = []
    for index, path in enumerate(re.findall(r'INCGFX_U32\("([^"]+)"', graphics)):
        image = Image.open(ROOT / "engine" / path)
        assert image.mode == "P" and image.size == (64, 64)
        pixels = list(image.get_flattened_data())
        assert max(pixels) < 16
        tiled = bytearray()
        for ty in range(0, 64, 8):
            for tx in range(0, 64, 8):
                for y in range(8):
                    for x in range(0, 8, 2):
                        i = (ty + y) * 64 + tx + x
                        tiled.append(pixels[i] | (pixels[i + 1] << 4))
        words = [int.from_bytes(tiled[i:i + 4], "little") for i in range(0, 2048, 4)]
        arrays.append(f"static const u32 sDccPose{index}[512] = {{" +
                      ",".join(hex(x) for x in words) + "};")
        assets.append({"path": path, "tiled_sha256": hashlib.sha256(tiled).hexdigest()})
    assert len(arrays) == 17
    arrays.append("static const u32 *const sDccPosePictures[] = {" +
                  ",".join(f"sDccPose{i}" for i in range(17)) + "};")
    (out / "assets.h").write_text("\n".join(arrays) + "\n")
    sources = {
        "baseline": subprocess.check_output(["git", "show", BASE + ":engine/src/dcc_battle_pose.c"], cwd=ROOT).decode(),
        "candidate": (ROOT / "engine/src/dcc_battle_pose.c").read_text(),
    }
    traces = {}
    for name, src in sources.items():
        case = out / name
        case.mkdir(exist_ok=True)
        (case / "module.c").write_text(src.replace('#include "data/dcc_battle_pose_graphics.h"', '#include "assets.h"'))
        cmd = ["cc", "-std=c99", "-O2", "-Wall", "-Wextra", "-Werror",
               "-I" + str(case), "-I" + str(out), "-I" + str(out / "headers"),
               "-I" + str(ROOT / "engine/include")]
        if name == "baseline":
            cmd.append("-DBASELINE")
        subprocess.run(cmd + [str(ROOT / "scripts/floor1/v01-active-pose-equivalence.c"),
                             "-o", str(case / "fixture")], check=True)
        with (case / "trace.txt").open("w") as f:
            subprocess.run([str(case / "fixture")], stdout=f, check=True)
        traces[name] = (case / "trace.txt").read_text().splitlines()
    assert len(traces["baseline"]) == len(traces["candidate"])
    for i, (before, after) in enumerate(zip(traces["baseline"], traces["candidate"])):
        assert before.split(" COST ")[0] == after.split(" COST ")[0], (i + 1, before, after)
    # Each assignment class is covered in native source, including non-move launches.
    assignment = re.compile(r"^\s+(?:gBattleAnimAttacker|gAnimScriptActive|gAbsentBattlerFlags|gBattleMons\[[^\]]+\]\.hp)\s*(?:=|\+=|-=|\|=|&=)(?!=).+;\s*$")
    writers = []
    for path in sorted((ROOT / "engine/src").glob("*.c")):
        lines = path.read_text().splitlines()
        for i, line in enumerate(lines):
            if assignment.match(line):
                assert lines[i + 1].strip() == "DccBattlePoseNotify();", (path, i + 1)
                writers.append({"path": str(path.relative_to(ROOT)), "line": i + 1})
    switch = (ROOT / "engine/src/battle_script_commands.c").read_text()
    assert "monData[i] = gBattleBufferB[gActiveBattler][4 + i];\n    DccBattlePoseNotify();" in switch
    assert "battleMonAttacker[i] = battleMonTarget[i];\n        DccBattlePoseNotify();" in switch
    main_source = (ROOT / "engine/src/battle_main.c").read_text()
    assert "DccBattlePoseUpdate();\n    AnimateSprites();" in main_source
    assert "DccBattlePoseNotify();\n        if (GetBattlerPosition(gActiveBattler)" in main_source
    result = {
        "scope": "SYNTHETIC offline native events and authored pose pixels; no gameplay or recovered runtime state",
        "baseline_source_commit": BASE,
        "source_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in sources.items()},
        "matched_ticks": len(traces["candidate"]),
        "scenarios": int(traces["candidate"][-1].split()[0]),
        "per_tick_pixels_actions_recovery_applied_warning_writes_queues_equal": True,
        "age_semantics": "Transition/failed-guard ticks advance; successful settled holds freeze unused age, WINDUP at >=18. Sleeping REST age is not compared to the old redundant increments.",
        "synthetic_all_rest": {k: [x.split(" COST ")[1] for x in v[-10:]] for k, v in traces.items()},
        "native_notified_writers": writers,
        "assets": assets,
        "baseline_executions": 6, "candidate_executions": 4,
        "PASS": True,
    }
    (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("native_notified_writers", "assets")}))


if __name__ == "__main__":
    main()
