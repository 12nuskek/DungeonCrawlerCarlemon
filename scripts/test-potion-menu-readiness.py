#!/usr/bin/env python3
"""Host gate tests: false readiness must never send input or acknowledge selection."""
from pathlib import Path
import json, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
# Small host mock, not a ROM, save or emulator; exercise the exact shared gate.
CODE=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
struct mCore {
    unsigned (*busRead8)(struct mCore *,unsigned);
    unsigned (*busRead32)(struct mCore *,unsigned);
};
static unsigned char memory[1024];
static unsigned read8(struct mCore *c,unsigned a) {(void)c;assert(a<sizeof memory);return memory[a];}
static unsigned read32(struct mCore *c,unsigned a) {
    (void)c;assert(a+3<sizeof memory);return memory[a]|memory[a+1]<<8|memory[a+2]<<16|memory[a+3]<<24;
}
static void host32(unsigned a,unsigned v) {
    for (unsigned i=0;i<4;i++) memory[a+i]=(v>>(8*i))&255;
}
#include "potion-menu-readiness.h"
int main(void) {
    struct mCore core={read8,read32};
    unsigned tasks=32,fade=800,bag=0x101,context=0x201,recipient=0x301, checks=0;
#define CHECK(x) do {assert(x);checks++;} while(0)
    host32(tasks,bag);memory[tasks+4]=1;
    CHECK(menu_ready(&core,tasks,fade,bag));
    memory[fade+7]=128;
    CHECK(!menu_ready(&core,tasks,fade,bag)); /* Original premature-fade bug. */
    CHECK(!menu_ready(&core,tasks,fade,context));
    memory[fade+7]=127;
    CHECK(menu_ready(&core,tasks,fade,bag)); /* Other flag bits cannot block indefinitely. */
    memory[tasks+4]=0;
    CHECK(!menu_ready(&core,tasks,fade,bag));
    memory[tasks+4]=1;host32(tasks,context);
    CHECK(!menu_ready(&core,tasks,fade,bag));
    CHECK(menu_ready(&core,tasks,fade,context));
    CHECK(!menu_ready(&core,0,fade,bag));
    CHECK(!menu_ready(&core,tasks,0,bag));
    CHECK(!menu_ready(&core,tasks,fade,0));
    memory[tasks+4]=0;host32(tasks+40*15,bag);memory[tasks+40*15+4]=1;
    CHECK(menu_ready(&core,tasks,fade,bag)); /* All task slots, Thumb-bit normalization. */
    memory[fade+7]=128;
    CHECK(!menu_ready(&core,tasks,fade,bag));
    CHECK(acknowledged_stage(2,0,1,0,13,0)==2); /* No sent input, no advancement. */
    CHECK(acknowledged_stage(2,1,0,0,13,0)==2); /* A alone, not context acknowledgment. */
    CHECK(acknowledged_stage(2,1,1,0,14,0)==2); /* Wrong selected item. */
    CHECK(acknowledged_stage(2,1,1,0,13,0)==3);
    CHECK(acknowledged_stage(3,0,0,1,13,0)==3);
    CHECK(acknowledged_stage(3,1,1,0,13,0)==3); /* Old context cannot acknowledge recipient. */
    CHECK(acknowledged_stage(3,1,0,1,13,1)==3); /* Wrong recipient. */
    CHECK(acknowledged_stage(3,1,0,1,14,0)==3);
    CHECK(acknowledged_stage(3,1,0,1,13,0)==4);
    CHECK(acknowledged_stage(4,1,1,1,13,0)==4);
    /* Sequential readiness: fade -> Bag A -> wait -> context -> Use -> wait -> Carl. */
    unsigned stage=2,pending=0,keys=0;
    CHECK(!menu_ready(&core,tasks,fade,bag) && keys==0);
    memory[fade+7]=0;
    if (menu_ready(&core,tasks,fade,bag)) {keys=1;pending=1;}
    CHECK(keys==1 && stage==2);
    keys=0;stage=acknowledged_stage(stage,pending,0,0,13,0);
    CHECK(keys==0 && stage==2);
    host32(tasks+40*15,context);
    stage=acknowledged_stage(stage,pending,menu_ready(&core,tasks,fade,context),0,13,0);
    CHECK(stage==3);
    pending=1;stage=acknowledged_stage(stage,pending,1,0,13,0);
    CHECK(stage==3);
    host32(tasks+40*15,recipient);memory[fade+7]=128;
    stage=acknowledged_stage(stage,pending,0,menu_ready(&core,tasks,fade,recipient),13,0);
    CHECK(stage==3);
    memory[fade+7]=0;
    stage=acknowledged_stage(stage,pending,0,menu_ready(&core,tasks,fade,recipient),13,0);
    CHECK(stage==4);
    printf("PASS Potion menu readiness negative/positive/acknowledgement checks=%u\n",checks);
    return 0;
}
'''
with tempfile.TemporaryDirectory(prefix='dcc-potion-gate-') as d:
    d=Path(d);(d/'test.c').write_text(CODE)
    subprocess.run(['cc','-std=gnu11','-Wall','-Wextra','-Werror','-I',str(ROOT/'scripts/floor1'),str(d/'test.c'),'-o',str(d/'test')],check=True)
    subprocess.run([str(d/'test')],check=True)
