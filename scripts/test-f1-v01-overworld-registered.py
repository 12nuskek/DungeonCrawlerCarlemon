#!/usr/bin/env python3
"""One separately claimed registered candidate against the already passed baseline."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'artifacts/floor1/v01-overworld/runtime-effective-flip/before'
FROZEN='2a76829f2536e828c6ce5fb37f5150cfb89d5577'
summary=json.loads((BASELINE/'summary.json').read_text());identity=json.loads((BASELINE/'identity.json').read_text())
assert summary['execution_source']=='640be7827e2cf302ed88b202836beafd68953e90' and summary['native_exit']==0 and summary['errors_bytes']==0 and summary['assertions']==64
source=subprocess.check_output(['git','show',FROZEN+':scripts/test-f1-v01-overworld.py'],cwd=ROOT,text=True)
for old,new in [("choices=['before','after']","choices=['after']"),("ROOT/'scripts/floor1/v01-overworld-host.py'","ROOT/'scripts/floor1/v01-overworld-effective-flip-host.py'"),("a.output.resolve()/'before/summary.json'","ROOT/'artifacts/floor1/v01-overworld/runtime-effective-flip/before/summary.json'")]:
    assert source.count(old)==1;source=source.replace(old,new)
namespace={'__file__':str(Path(__file__).resolve()),'__name__':'registered_native_candidate'}
exec(compile(source,'<frozen candidate runner with retained accepted baseline>', 'exec'),namespace)
assert identity['route_SHA256']==namespace['sha'](ROOT/'scripts/contracts/f1-v01-overworld.route')
if __name__=='__main__':namespace['main']()
