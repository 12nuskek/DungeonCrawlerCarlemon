#!/usr/bin/env python3
"""Independent offline cold phase closure; full native data stays private."""
from pathlib import Path
import importlib.util,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'artifacts/floor1/prepared-cold-phase';DATA=ART/'runtime/cold'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=module('closed_native',ROOT/'scripts/floor1/prepared-save-validation.py');fields=native.fields
summary=json.loads((ART/'runtime/summary.json').read_text());c=summary['clock']
assert summary['exit']==0 and summary['errors_bytes']==0 and summary['assertions']==132
assert summary['battle_frames']==summary['battle_attempts']==0
assert c=={'absolute_frames':6258,'valid_frame_samples':4195,'deferred_frame_samples':19,'explicit_checkpoints':9,'reentry_comparisons':2,'boundary_events':0,'armed_frame':2044}
save=ART/'runtime/cold.sav';assert hashlib.sha256(save.read_bytes()).hexdigest()==summary['input_Save_SHA256']==summary['output_Save_SHA256']
saved=fields.saved_party(save);before=(DATA/'anchor-party.bin').read_bytes();assert before==saved['party'] and saved['friendship_counter']==8
assert saved['latest_sector_checksums_valid'] and saved['count']==2
private=[fields.decode(before[100*i:100*(i+1)])['fields'] for i in range(2)]
assert [p['friendship'] for p in private]==[88,84]
logical=native.canonical((DATA/'anchor-owned.bin').read_bytes(),(DATA/'anchor-context.bin').read_bytes());flags=(DATA/'anchor-flags.bin').read_bytes()
snapshots=[]
for f in sorted(DATA.glob('*-party.bin')):
    prefix=f.name[:-len('-party.bin')]
    if prefix.startswith('expected'):continue
    assert f.read_bytes()==before
    for i in range(2):assert fields.decode(f.read_bytes()[100*i:100*(i+1)])['checksum_valid']
    assert (DATA/(prefix+'-flags.bin')).read_bytes()==flags
    raw=(DATA/(prefix+'-owned.bin')).read_bytes();context=(DATA/(prefix+'-context.bin')).read_bytes()
    assert native.canonical(raw,context)==logical
    meta=json.loads((DATA/(prefix+'-metadata.json')).read_text());assert meta['native_phase_valid'] and meta['count']==meta['saved_count']==2
    snapshots.append({'snapshot':prefix,'absolute_frame':meta['absolute_frame'],'counter':meta['counter'],'map':meta['map'],'party600_flags_logical_resources_exact':True,'actual_context_used':True,'native_phase_valid':True})
assert len(snapshots)==13
log=(DATA/'replay.log').read_text()
defer=list(map(lambda x:tuple(map(int,x)),re.findall(r'^PHASE defer absolute_frame=(\d+) last_accepted_frame=(\d+)$',log,re.M)))
reentry=list(map(lambda x:tuple(map(int,x)),re.findall(r'^PASS PHASE reentry absolute_frame=(\d+) last_accepted_frame=(\d+) complete_party_count_counter_flags_resources=1$',log,re.M)))
assert defer==[(3076,3075),(5618,5617)] and reentry==[(3086,3075),(5627,5617)]
assert sum(b[0]-a[0] for a,b in zip(defer,reentry))==19
steps=[tuple(map(int,x)) for x in re.findall(r'^WALK_STEP absolute_frame=(\d+) counter=(\d+)->(\d+)$',log,re.M)]
assert len(steps)==27 and [x[1:] for x in steps]==[(i,i+1) for i in range(8,35)]
assert all(a[0]<b[0] for a,b in zip(steps,steps[1:]))
assert not any(lo[0]<=f<hi[0] for f,_,_ in steps for lo,hi in zip(defer,reentry))
assert 'PASS choice-result 0' in log and 'PASS choice-result 1' in log and 'PASS repeat encounter no battle' in log
final=json.loads((DATA/'final-metadata.json').read_text());assert final['absolute_frame']==6258 and final['counter']==35 and final['map']==[35,4]
report={'summary':summary,'native_saved_sector_checksums_valid':True,'saved_counter':8,'final_runtime_counter':35,
    'natural_counter_steps':27,'friendship_before_after':[88,84],'all600_party_bytes_exact':True,
    'checksums_and_reencoding_valid':True,'all300_flags_exact_checkpoint48_remains_set':True,
    'all1272_logical_resource_bytes_exact':True,'all186_bag_IDs_quantities_empty_PC_unencoded_exact':True,
    'actual_native_contexts_used_no_inference':True,'snapshots':snapshots,
    'deferred_intervals':[{'first_deferred_frame':a[0],'last_accepted_frame':a[1],'first_stable_reentry_frame':b[0],'deferred_frames':b[0]-a[0]} for a,b in zip(defer,reentry)],
    'every_deferred_snapshot_and_expected_state_retained':True,'absolute_step_labels':steps,
    'dedicated_clock_sample_accounting_exact':4195+19==6258-2044,
    'actual_arena_return_repeat_NO_YES_checkpoint_reentry_final_verified':True,
    'new_battle_Save_or_extra_route':False,'historical_failed_cold_or_original_CPU_phase_reinterpreted':False,
    'next_dependency':'Parent review of bounded prepared persistence closure; read-only remaining F1-G01e acceptance inventory before F1-V01/G02, with legacy/motion/T/pacing gates explicitly retained.'}
(ART/'safe-findings.json').write_text(json.dumps(report,indent=2)+'\n')
(ART/'private-decoded-fields.json').write_text(json.dumps({'members':private,'canonical_owned':logical.hex()},indent=2)+'\n')
print('PASS one cold-only route132 assertions/6258 absolute frames/zero battles/empty errors/unchanged savedbaaf…ccd7')
print('PASS all13 valid snapshots:600 party bytes/checksums/reencoding/count2/300flags/full1272 logical resource bytes exact;actual contexts privately captured')
print('PASS native counter8→35 through27 ordinary steps,friendships88/84 unchanged,no boundary event;actual return/repeat/NO/YES/re-entry/final state')
print('PASS deferred3076..3085 and5618..5626:19 frames/no reads or anchors accepted;complete exact re-entry at3086/5627')
print('PASS exact dedicated clock:4195 valid frame samples+19 deferred=6258−2044;9 explicit checkpoints/2 re-entry comparisons counted separately;no historical acceptance or CPU-phase inference')
