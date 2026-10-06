#!/usr/bin/env python3
"""Resolve only player-controller input functions for read-only emulator routing.

The pinned agbcc object has one .text section. Link its local offsets using the
exported SetControllerToPlayer anchor, then verify each result exists in the ELF.
No ROM or game state is modified. Append output to the normal global nm symbols.
"""
from pathlib import Path
import subprocess, sys
engine = Path(sys.argv[1])
nm = sys.argv[2] if len(sys.argv) > 2 else 'arm-none-eabi-nm'
def symbols(path):
    rows = subprocess.check_output([nm, '--defined-only', str(path)], text=True)
    return [(int(a,16),kind,name) for a,kind,name in (line.split() for line in rows.splitlines())]
local = {name: address for address,kind,name in symbols(engine/'build/emerald/src/battle_controller_player.o')}
linked = symbols(engine/'pokeemerald.elf')
anchor = next(address for address,kind,name in linked if name == 'SetControllerToPlayer')
base = anchor-local['SetControllerToPlayer']
for suffix in ['Action','Move','Target']:
    name = 'HandleInputChoose'+suffix
    address = base+local[name]
    assert any(a == address and n == name for a,k,n in linked), (name,'link mismatch')
    print(f'{address:08x} T DccTestInput{suffix}')
