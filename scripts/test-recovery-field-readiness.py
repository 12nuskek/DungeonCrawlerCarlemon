#!/usr/bin/env python3
"""Reject the diagnosed task-created-before-menu-running state without an emulator."""
from pathlib import Path
import ast, subprocess, tempfile
ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / 'scripts/test-potion-menu-readiness.py').read_text())
base = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'CODE' for t in n.targets))
base = base.replace('int main(void)', 'static int original_gate_checks(void)')
code = base + r'''
#include "recovery-field-readiness.h"
int main(void) {
    original_gate_checks();
    struct mCore core={read8,read32};
    unsigned tasks=32,fade=800,mainstate=900,running=0x401,input=0x501;
    memset(memory,0,sizeof memory);
    host32(tasks,input);memory[tasks+4]=1;
    host32(mainstate+4,0x601); /* Bag setup: input task exists, fade still inactive. */
    assert(menu_ready(&core,tasks,fade,input));
    assert(!recovery_field_ready(&core,mainstate,running,tasks,fade,input));
    host32(mainstate+4,running);memory[fade+7]=128;
    assert(!recovery_field_ready(&core,mainstate,running,tasks,fade,input));
    memory[fade+7]=0;
    assert(recovery_field_ready(&core,mainstate,running,tasks,fade,input));
    assert(!recovery_field_ready(&core,mainstate,0,tasks,fade,input));
    assert(!recovery_field_ready(&core,0,running,tasks,fade,input));
    memory[tasks+4]=0;
    assert(!recovery_field_ready(&core,mainstate,running,tasks,fade,input));
    puts("PASS field menu setup/fade/callback/missing-task checks=7");
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='dcc-recovery-field-') as directory:
    d = Path(directory)
    (d / 'test.c').write_text(code)
    subprocess.run(['cc', '-std=gnu11', '-Wall', '-Wextra', '-Werror', '-I', str(ROOT / 'scripts/floor1'),
                    str(d / 'test.c'), '-o', str(d / 'test')], check=True)
    subprocess.run([str(d / 'test')], check=True)
