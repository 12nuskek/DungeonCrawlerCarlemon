"""Offline-prepared terminal retention revision; no execution claim or runner.

Keep the historical r4 generator/header intact. Success stepping, keys, strict
comparisons and normal footer are identical. Only host writes/error exits change.
"""
from pathlib import Path
import importlib.util,re
ROOT=Path(__file__).resolve().parents[2]

FLUSH=r'''static unsigned c01_edge_flush(void)
{
    if(!edge.file)return 0;
    unsigned char bytes[C01_EDGE_WORDS*4];unsigned written=0,reason=0;
    /* Never retry a partially written record after a stream error. Retire every
     * complete record even when a later write fails, avoiding duplicate rows. */
    if(ferror(edge.file))return edge.reason=125;
    for(;written<edge.used;written++){
        bv_ts_pack(bytes,edge.buffer[written],C01_EDGE_WORDS);
        if(edge.rows>=C01_EDGE_MAX_ROWS || fwrite(bytes,1,sizeof bytes,edge.file)!=sizeof bytes){reason=125;break;}
        edge.rows++;
    }
    edge.used-=written;
    if(edge.used&&written)memmove(edge.buffer,edge.buffer+written,edge.used*sizeof edge.buffer[0]);
    if(fflush(edge.file)||ferror(edge.file))reason=125;
    if(reason)edge.reason=reason;
    return reason;
}'''
TERMINAL=r'''static void c01_edge_terminal_exit(unsigned result)
{
    unsigned retention=c01_edge_close(result);
    if(retention)fprintf(stderr,"Terminal edge retention failed=%u; original STOP=%u preserved\n",retention,result);
    exit(result);
}'''

def edge_header():
    code=(ROOT/'scripts/floor1/c01a-ui-edge-r4.h').read_text()
    start=code.index('static unsigned c01_edge_flush(void)\n{')
    end=code.index('static unsigned c01_edge_record',start)
    return code[:start]+FLUSH+'\n'+code[end:]+'\n'+TERMINAL+'\n'

def generate(git):
    spec=importlib.util.spec_from_file_location('c01_terminal_prior',ROOT/'scripts/floor1/c01a-ui-host-r4.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    code=prior.generate(git);old=(ROOT/'scripts/floor1/c01a-ui-edge-r4.h').read_text()
    assert code.count(old)==1
    code=code.replace(old,edge_header())
    # Startup symbol-parser exit112 precedes edge-open and has no edge file.
    # All four potentially active immediate exits close without advancing CPU.
    assert code.count('exit(51);')==1 and code.count('exit(109);')==1 and code.count('exit(vr);')==2
    for expression in ['51','109','vr']:
        code=code.replace('exit('+expression+');','c01_edge_terminal_exit('+expression+');')
    original=prior.generate(git)
    assert re.findall(r'core->setKeys\(core,([^;]+)\);',code)==re.findall(r'core->setKeys\(core,([^;]+)\);',original)
    assert code.count('bv_native_frame(&native,')==original.count('bv_native_frame(&native,')==1
    assert code.count('ARMRun(cpu);')==original.count('ARMRun(cpu);')
    assert 'busWrite' not in code
    return code
