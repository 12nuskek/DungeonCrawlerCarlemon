#!/usr/bin/env python3
"""Separate exclusive pair with only the native effective OAM flip read corrected."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
FROZEN='2a76829f2536e828c6ce5fb37f5150cfb89d5577'
source=subprocess.check_output(['git','show',FROZEN+':scripts/test-f1-v01-overworld.py'],cwd=ROOT,text=True)
needle="ROOT/'scripts/floor1/v01-overworld-host.py'";assert source.count(needle)==1
source=source.replace(needle,"ROOT/'scripts/floor1/v01-overworld-effective-flip-host.py'")
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'corrected_native_flip_runner'}
exec(compile(source,'<frozen character runner with effective native flip>', 'exec'),namespace)
if __name__=='__main__':namespace['main']()
