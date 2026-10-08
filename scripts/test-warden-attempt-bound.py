#!/usr/bin/env python3
"""Whole-battle bounds include entry/exit; zero-frame cold process is permitted."""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
CODE=r'''
#include <assert.h>
#include <stdio.h>
#include "warden-attempt-bound.h"
int main(void) {
    assert(warden_before_frame(0,0));
    assert(warden_before_frame(0,1));
    assert(warden_before_frame(29999,1));
    assert(!warden_before_frame(30000,1));
    assert(!warden_before_frame(30001,1));
    assert(warden_after_frame(29999,1));
    assert(!warden_after_frame(30000,1));
    assert(!warden_after_frame(30001,1));
    assert(warden_after_frame(30000,0));
    assert(warden_before_frame(30000,0));
    unsigned frames=0;
    /* One entering frame, 29998 interior frames, one exiting frame = 30000. */
    for (unsigned i=0;i<30000;i++) {
        unsigned before=i!=0,after=i!=29999;
        assert(warden_before_frame(frames,before));
        if (before || after) frames++;
        assert(warden_after_frame(frames,after));
    }
    assert(frames==30000);
    puts("PASS whole-battle boundary checks=11 plus30000-frame entry/interior/exit vector");
}
'''
with tempfile.TemporaryDirectory(prefix='dcc-warden-bound-') as path:
    d=Path(path);(d/'test.c').write_text(CODE)
    subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-fsanitize=undefined',
        '-I',str(ROOT/'scripts/floor1'),str(d/'test.c'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
