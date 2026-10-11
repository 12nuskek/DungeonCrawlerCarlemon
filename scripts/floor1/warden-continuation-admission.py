"""Inert reservation and exclusive-claim proposal. Execution is always closed."""
import math
MiB=1024**2
def storage(continuation_frames,cold_frames):
    assert continuation_frames>30000 and cold_frames>0
    rows={}
    for mode,frames in (('continuation',continuation_frames),('cold',cold_frames)):
        # Complete RGB/index plus worst-case complete field AND battle records,
        # two bounded logs, all five 32-page captures plus fixed/terminal
        # captures, Save/source/snapshot work and allocation rounding.
        captures=176 if mode=='continuation' else 4
        logical=frames*(240*160*3+16+3340+1040)+2*64*MiB+captures*(240*160*3+64)+32*MiB
        rows[mode]=dict(frames=frames,bytes=math.ceil(logical/4096)*4096,
                        per_log_bytes=64*MiB,capture_limit=captures,chunk_frames=2000)
    return dict(processes=rows,headroom_bytes=256*MiB,
                reservation_bytes=sum(r['bytes'] for r in rows.values())+256*MiB,
                fresh_full_reservation_before_each_process=True,prepared_credit=False)

def capacity(free,reservation):
    if free<reservation:raise RuntimeError('STOP: full route/cold reservation plus headroom unavailable')
    return True

def runtime_action(*args,**kwargs):
    raise RuntimeError('CLOSED: offline review only; no runtime authority, freeze, claim, emulator, Save or cold')

def proposal():
    return dict(runtime_admission=False,claims_per_mode=1,exclusive=True,first_failure_terminal=True,
                first_incapacitation_terminal=True,resource_divergence_terminal=True,retry=False,
                cold_requires_actual_complete_successful_manual_Save=True,
                refusal_consumes_no_runtime_claim=True,compression=False)
