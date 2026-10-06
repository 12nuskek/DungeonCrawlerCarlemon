#!/usr/bin/env python3
"""Verify this partial native kit without needing the absent main source PNG.

No network, game checkout or publication action. Packing diagnostics are created
only in a disposable temporary directory. No complete source reproduction claim.
"""
from pathlib import Path
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    checksums = (ROOT / "SHA256SUMS").read_text().splitlines()
    for line in checksums:
        expected, relative = line.split("  ", 1)
        assert sha((ROOT / relative).read_bytes()) == expected, relative
    status = json.loads((ROOT / "package-status.json").read_text())
    for omitted in status["omitted_pending_publication"]:
        assert not (ROOT / omitted["path"]).exists(), omitted["path"]
    report = json.loads((ROOT / "independent-validation-report.json").read_text())
    actual = sorted(p.relative_to(ROOT).as_posix()
                    for p in (ROOT / "native").rglob("*.png"))
    assert actual == sorted(a["path"] for a in report["decoded_assets"])
    for asset in report["decoded_assets"]:
        path = ROOT / asset["path"]
        data = path.read_bytes()
        assert sha(data) == asset["file_sha256"], asset["path"]
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        chunks, offset = {}, 8
        while offset < len(data):
            length = struct.unpack_from(">I", data, offset)[0]
            kind = data[offset + 4:offset + 8].decode("ascii")
            chunks[kind] = data[offset + 8:offset + 8 + length]
            offset += length + 12
        assert offset == len(data)
        assert chunks["IHDR"][8:10] == bytes([4, 3])
        assert len(chunks["PLTE"]) == 48 and chunks["tRNS"] == b"\x00"
        assert set(chunks) <= {"IHDR", "PLTE", "tRNS", "IDAT", "IEND"}
        with Image.open(path) as image:
            assert image.mode == "P" and list(image.size) == asset["dimensions"]
            assert sha(image.tobytes()) == asset["indexed_pixels_sha256"]
            assert sha(bytes(image.getpalette()[:48])) == asset["palette_sha256"]
            assert sha(image.convert("RGBA").tobytes()) == asset["decoded_rgba_sha256"]
    assert len(actual) == 91
    with tempfile.TemporaryDirectory(prefix="dcc-native-static-") as td:
        work = Path(td)
        shutil.copytree(ROOT / "native", work / "native")
        for name in ("pack_validate.py", "manifest.json", "architecture-manifest.json"):
            shutil.copyfile(ROOT / name, work / name)
        subprocess.run([sys.executable, "pack_validate.py"], cwd=work,
                       check=True, capture_output=True, text=True)
        validation = json.loads((work / "validation-report.json").read_text())
        assert validation["checks_passed"] == 721
        for name in ("tile-pack.json", "validation-report.json",
                     "native/background-tiles-8x8.png"):
            assert (ROOT / name).read_bytes() == (work / name).read_bytes(), name
    print(f"PASS: {len(checksums)} staged checksums; 91 native decoded PNG identities; "
          "721 static checks. Full source reproduction unavailable: main source PNG absent.")


if __name__ == "__main__":
    main()
