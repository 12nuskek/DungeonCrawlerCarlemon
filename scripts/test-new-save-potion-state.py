#!/usr/bin/env python3
"""Capped healing and fresh-save precondition negative checks, without gameplay."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CODE=r'''
#include <assert.h>
#include <stdio.h>
#include "new-save-potion-state.h"
int main(void) {
    assert(new_save_potion_hp(20,36)==36);
    assert(new_save_potion_hp(3,36)==23);
    assert(new_save_potion_hp(35,36)==36);
    assert(new_save_potion_hp(1,36)==21);
    assert(new_save_potion_decision(856,4,0,20,36,16,1));
    assert(!new_save_potion_decision(857,4,0,20,36,16,1));
    assert(!new_save_potion_decision(856,3,0,20,36,16,1));
    assert(!new_save_potion_decision(856,4,2,20,36,16,1));
    assert(!new_save_potion_decision(856,4,0,0,36,16,1));
    assert(!new_save_potion_decision(856,4,0,36,36,16,1));
    assert(!new_save_potion_decision(856,4,0,20,36,0,1));
    assert(!new_save_potion_decision(856,4,0,20,36,16,0));
    assert(!new_save_potion_decision(856,4,0,20,36,16,2));
    puts("PASS capped healing/fresh decision checks=13");
}
'''
with tempfile.TemporaryDirectory(prefix='dcc-new-save-potion-') as path:
    d=Path(path);(d/'test.c').write_text(CODE)
    subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-fsanitize=undefined',
        '-I',str(ROOT/'scripts/floor1'),str(d/'test.c'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
