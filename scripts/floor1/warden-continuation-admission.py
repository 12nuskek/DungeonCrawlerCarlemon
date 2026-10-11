"""Inert reservation and exclusive-claim proposal. Execution is always closed."""
MiB=1024**2
BLOCK=4096
def allocated(size):
    assert isinstance(size,int) and size>=0
    return ((size+BLOCK-1)//BLOCK)*BLOCK
def storage(continuation_frames,cold_frames):
    assert (continuation_frames,cold_frames)==(134360,2044),'unchanged complete route bounds'
    rows={}
    for mode,frames in (('continuation',continuation_frames),('cold',cold_frames)):
        # Complete RGB/index plus worst-case complete field AND battle records,
        # two bounded logs, all five 32-page captures plus fixed/terminal
        # captures, Save/source/snapshot work and allocation rounding.
        captures=176 if mode=='continuation' else 4
        chunks,remainder=divmod(frames,2000)
        files=[dict(name='full_RGB_chunks',count=chunks,per_file_bytes=2000*115200),
               dict(name='last_RGB_chunk',count=int(bool(remainder)),per_file_bytes=remainder*115200),
               dict(name='frame_index',count=1,per_file_bytes=frames*16),
               dict(name='complete_field_trace',count=1,per_file_bytes=frames*3340),
               dict(name='complete_battle_trace',count=1,per_file_bytes=frames*1040),
               dict(name='bounded_logs',count=2,per_file_bytes=64*MiB),
               dict(name='native_PPM_captures',count=captures,per_file_bytes=115264),
               dict(name='optional_PNG_derivatives',count=captures,per_file_bytes=256*1024),
               dict(name='later_review_derivatives',count=8 if mode=='continuation' else 2,per_file_bytes=64*MiB),
               dict(name='Save_copies',count=2,per_file_bytes=131088),
               dict(name='complete_snapshots',count=32,per_file_bytes=3324),
               dict(name='bounded_metadata_work',count=64,per_file_bytes=256*1024),
               dict(name='source_checkpoint',count=1,per_file_bytes=32*MiB),
               dict(name='observer_binary',count=1,per_file_bytes=MiB),
               dict(name='symbols',count=1,per_file_bytes=512*1024)]
        for f in files:f['allocated_bytes']=f['count']*allocated(f['per_file_bytes'])
        rows[mode]=dict(frames=frames,files=files,bytes=sum(f['allocated_bytes'] for f in files),
                        logical_bytes=sum(f['count']*f['per_file_bytes'] for f in files),
                        per_log_bytes=64*MiB,capture_limit=captures,chunk_frames=2000,
                        per_file_limit_bytes=512*MiB)
    return dict(processes=rows,allocation_block_bytes=BLOCK,headroom_bytes=256*MiB,
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
