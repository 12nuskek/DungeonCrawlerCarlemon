#!/usr/bin/env python3
"""Separate claimed route with one source-diagnosed settle; old runner preserved."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
FROZEN='2748afa8bca3e3f405c8da3342c9938fd1e5d3df'
source=subprocess.check_output(['git','show',FROZEN+':scripts/test-f1-v01-environment.py'],cwd=ROOT,text=True)
needle="route=ROOT/'scripts/contracts/f1-v01-environment.route'"
assert source.count(needle)==1
source=source.replace(needle,"route=ROOT/'scripts/contracts/f1-v01-environment-settled.route'")
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'v01_settled_frozen_runner'}
exec(compile(source,'<frozen V01 runner with source-diagnosed route>', 'exec'),namespace)
if __name__=='__main__':namespace['main']()
