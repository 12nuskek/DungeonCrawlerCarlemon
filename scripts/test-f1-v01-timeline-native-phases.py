"""Actual retained Wait instructions, synthetic IRQ body; no game/Save/reset.

Keep the older mechanism fixture immutable. A private generated variant wraps
only instruction-ready ARMRun calls with passive observations; due-event calls
remain exactly original. Production event-drain parity is tested separately.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, struct, subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--official-video',type=Path,required=True);a=p.parse_args()
    out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    private=out/'private-fixture-output';private.mkdir(mode=0o700)
    spec=importlib.util.spec_from_file_location('old_mechanism',ROOT/'scripts/floor1/v01-timing-audit.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    old.prepare(private,a.official_video)
    helper=r'''
#include "v01-native-timeline.h"
static struct BvTimeline phaseTimeline;
static void phaseEnable(const char *name)
{
    struct GBA *g=core->board;
    struct BvTimelineConfig cfg={.mainAddress=0x030022c0,.copyCount=0x03004000,
        .copyArmed=0x03004001,.copies=0x03004100,.seen=15};
    for(unsigned i=0;i<BV_TL_POINTS;i++){
        unsigned pc=0x08000600+2*i;
        cfg.point[i]=(struct BvTimelinePoint){pc,pc,0x46c0,MODE_THUMB,15};
    }
    const unsigned indices[]={BV_TL_WAIT,BV_TL_WAIT_CLEAR,BV_TL_WAIT_EXIT};
    const unsigned addresses[]={0x080008ac,0x080008b8,0x080008d2};
    const unsigned opcodes[]={0xb500,0x8390,0x4700};
    for(unsigned i=0;i<3;i++)cfg.point[indices[i]]=(struct BvTimelinePoint){addresses[i],addresses[i],opcodes[i],MODE_THUMB,15};
    cfg.point[BV_TL_IRQ]=(struct BvTimelinePoint){0x03007000,0x08000028,0xe1c010b0,MODE_ARM,15};
    g->memory.rom=code;g->memory.romSize=4096;
    char path[160];assert(snprintf(path,sizeof path,"%s-private.bin",name)>0);
    assert(!bv_tl_open(&phaseTimeline,core,&cfg,path));
    /* Fixture-only synthetic service store, explicitly distinct from the
     * production IntrMain entry/main VBlankIntr flag-store pins. */
    phaseTimeline.config.point[BV_TL_IRQ].pc=0x28;
}
static void phaseRun(struct ARMCore *c)
{
    unsigned ready=c->cycles<c->nextEvent;
    if(ready){
        struct ARMCore cpu=*c;struct GBA gba=*(struct GBA*)core->board;
        assert(!bv_tl_before(&phaseTimeline));
        assert(!memcmp(&cpu,c,sizeof cpu)&&!memcmp(&gba,core->board,sizeof gba));
    }
    ARMRun(c); /* Exactly one original call; no event/input/order substitution. */
    if(ready){
        struct ARMCore cpu=*c;struct GBA gba=*(struct GBA*)core->board;
        assert(!bv_tl_after(&phaseTimeline));
        assert(!memcmp(&cpu,c,sizeof cpu)&&!memcmp(&gba,core->board,sizeof gba));
    }
}
static void phaseClose(void)
{
    assert(!bv_tl_flush(&phaseTimeline,0,1));assert(!bv_tl_close(&phaseTimeline));
    ((struct GBA*)core->board)->memory.rom=NULL;
}
'''
    src=(ROOT/'scripts/floor1/v01-timing-audit-fixture.c').read_text()
    assert src.count('        ARMRun(c);')==1
    src=src.replace('static void run(',helper+'\nstatic void run(',1)
    src=src.replace('    trace("synthetic-callback-complete");','    phaseEnable(name);\n    trace("synthetic-callback-complete");',1)
    src=src.replace('        ARMRun(c);','        phaseRun(c);',1)
    src=src.replace('    core->deinit(core);\n}', '    phaseClose();\n    core->deinit(core);\n}',1)
    generated=private/'phase-fixture.c';generated.write_text(src)
    subprocess.run(['cc','-std=gnu11','-O2','-Wall','-Wextra','-Werror','-I'+str(private),
        '-I'+str(ROOT/'scripts/floor1'),str(generated),'-lmgba','-o',str(out/'phase-fixture')],check=True)
    completed=subprocess.run([str(out/'phase-fixture'),str(private/'before-wait.bin')],cwd=private,capture_output=True,text=True,check=True)
    assert completed.stdout==(private/'before-trace.jsonl').read_text()
    (out/'fixture.log').write_text('PASS three native Wait mechanisms: original stdout/event/frame/flag ordering identical; every observation whole CPU/GBA byte neutral\n')
    cases=[]
    for f in sorted(private.glob('*-private.bin')):
        assert f.stat().st_mode&0o777==0o600
        b=f.read_bytes();assert b[:8]==b'BVTIME01' and (len(b)-16)%184==0
        rows=[struct.unpack_from('<46I',b,i) for i in range(16,len(b),184)]
        clear=[r for r in rows if r[41]&(1<<8)];irq=[r for r in rows if r[41]&(1<<20)]
        assert len(clear)==2 and clear[0][0]==1 and clear[1][0]==2 and clear[1][19]==0
        assert clear[0][19]==(1 if f.name.startswith('serviced-') else 0)
        assert irq and len(irq)%2==0
        for before,after in zip(irq[::2],irq[1::2]):
            assert before[0]==1 and after[0]==2 and after[19]==before[19]|1
        assert len([r for r in rows if r[41]&(1<<7)])==2
        assert len([r for r in rows if r[41]&(1<<9)])==2
        cases.append({'case':f.name.removesuffix('-private.bin'),'records':len(rows),'trace_SHA256':sha(f),'native_clear_before':clear[0][19],'native_clear_after':0})
    assert len(cases)==3
    result={'result':'PASS three exact native Wait clear/exit phase observations and synthetic IRQ-store phases, original ordering unchanged',
        'cases':cases,'observations_whole_CPU_GBA_byte_neutral':True,'original_stdout_exact':True,
        'source_SHA256':{str(f.relative_to(ROOT)):sha(f) for f in [ROOT/'scripts/test-f1-v01-timeline-native-phases.py',ROOT/'scripts/floor1/v01-native-timeline.h',ROOT/'scripts/floor1/v01-timing-audit-fixture.c']},
        'generated_fixture_SHA256':sha(generated),'fixture_binary_SHA256':sha(out/'phase-fixture'),
        'native_Wait_SHA256':sha(private/'before-wait.bin'),'gameplay_host_invocations':0,'ROMs_loaded':0,'Saves_loaded':0,'new_execution_claims':0,
        'limits':'Native Wait only; synthetic service body/bus/callback costs. Due ARMRun calls unchanged and uninstrumented here; production event-drain parity has separate synthetic tests. No historical timing recovered.'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
