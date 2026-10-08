#!/usr/bin/env python3
"""Offline prepared success/cold STOP; raw fields and contexts remain private."""
from pathlib import Path
import importlib.util,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'artifacts/floor1/prepared-persistence';DATA=ART/'runtime/prepared'
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
native=module('prepared_native',ROOT/'scripts/floor1/prepared-save-validation.py');fields=native.fields
first=DATA/'first-clear';cold=DATA/'cold';summary=json.loads((DATA/'summary.json').read_text())
assert [(x['exit'],x['assertions'],x['battle_frames']) for x in summary]==[(0,270,6952),(57,25,0)]
assert summary[0]['attempts']==1 and summary[1]['attempts']==0
save=native.validate(DATA/'first-clear.sav',first);assert (DATA/'first-clear.sav').read_bytes()==(DATA/'cold.sav').read_bytes()
assert hashlib.sha256((DATA/'first-clear.sav').read_bytes()).hexdigest()=='dbaaf7312ed6100b780811cd9b71c627ba42c6100bf318071b8cd1616a62ccd7'
assert (first/'anchor-party.bin').read_bytes()==(first/'walking-event-00-before-party.bin').read_bytes()
before=(first/'walking-event-00-before-party.bin').read_bytes();after=(first/'walking-event-00-after-party.bin').read_bytes()
safe,private=fields.compare(before,after)
assert [m['friendship_delta'] for m in safe['members']]==[1,1]
for member in safe['members']:
    assert member['checksums_valid_before_after'] and member['reencoding_exact']
    assert member['all_other_canonical_bytes_exact'] and member['derived_checksum_delta_exact'] and member['only_derived_ciphertext_bytes_changed']
assert safe['remaining400_party_bytes_exact'] and after==(first/'final-party.bin').read_bytes()
assert [fields.decode(before[100*i:100*(i+1)])['fields']['friendship'] for i in range(2)]==[87,83]
source=(ROOT/'engine/src/pokemon.c').read_text();assert '[FRIENDSHIP_EVENT_WALKING]         = { 1,  1,  1}' in source
for i in range(2):
    d=fields.decode(before[100*i:100*(i+1)]);misc=bytes.fromhex(d['fields']['origin_IV_ribbons'])
    assert d['fields']['held_item']==0 and ((int.from_bytes(misc[2:4],'little')>>11)&15)!=11 and misc[1]!=217
anchor=native.canonical((first/'anchor-owned.bin').read_bytes(),(first/'anchor-context.bin').read_bytes())
checks=[]
for f in sorted(first.glob('stable-*-owned.bin')):
    context=f.with_name(f.name.replace('-owned','-context'));assert native.canonical(f.read_bytes(),context.read_bytes())==anchor
    checks.append({'snapshot':f.stem,'logical_exact':True,'actual_context_used':True})
assert len(checks)==11
for prefix in ['anchor','stable-00']:
    assert (cold/(prefix+'-party.bin')).read_bytes()==after
    assert (cold/(prefix+'-flags.bin')).read_bytes()==(first/'final-flags.bin').read_bytes()
    assert native.canonical((cold/(prefix+'-owned.bin')).read_bytes(),(cold/(prefix+'-context.bin')).read_bytes())==anchor
assert json.loads((cold/'anchor-metadata.json').read_text())['counter']==8
assert (cold/'stop-party.bin').read_bytes()==(cold/'stop-last-party.bin').read_bytes()==after
flags=(cold/'stable-00-flags.bin').read_bytes();stopFlags=(cold/'stop-flags.bin').read_bytes()
assert flags[68:]==stopFlags[:232]
owned=(cold/'stable-00-owned.bin').read_bytes();stopOwned=(cold/'stop-owned.bin').read_bytes()
ownedOverlap=sum(a==b for a,b in zip(owned[68:],stopOwned[:1204]));assert ownedOverlap==1196
stopMeta=json.loads((cold/'stop-metadata.json').read_text());assert stopMeta['counter']==5953 and stopMeta['party_count']==2
load=(ROOT/'engine/src/load_save.c').read_text();assert load.index('SetSaveBlocksPointers(\n')<load.index('*gSaveBlock1Ptr = *saveBlock1Copy;')
log=(first/'replay.log').read_text();clog=(cold/'replay.log').read_text()
assert 'PASS choice-result 0' in log and 'PASS choice-result 1' in log
assert 'PASS checkpoint48 transition after actual staircase YES' in log
assert 'PASS exact cold boot600 party/count/counter/flags/full logical resources' in clog
assert 'PASS walking preservation armed frame=2044 counter=8 actual_friendship=88,84' in clog
assert [list(map(int,x.split())) for x in re.findall(r'^VITALS (.+)$',log,re.M)]==[[26,24,0,0,4,40,0,38]]*2
report={'summary':summary,'native_manual_Save_validation':save,'walking_event_comparison':safe,
    'walking_event_source_bonuses_absent':True,'first_clear_resources':checks,
    'first_clear_actual_per_frame_party_comparisons':5205,'first_clear_stable_party_comparisons':11,
    'counter_event_host_label':19138,'counter_event_actual_frame_interval':[19138,19189],
    'counter_event_label_limitation':'historical total updates after step batches; event label is batch start, not exact per-frame timestamp',
    'cold_exact_boot_party_count_counter_flags_resources':True,'cold_initial_stable_resources_exact':True,
    'cold_return_route_completed':False,'cold_stop_reason':57,'cold_stop_matches_transient_relocation_pattern':True,
    'cold_last_accepted_counter':14,'cold_stop_raw_counter':5953,'cold_stop_party600_exact':True,
    'cold_stop_party_count':2,'cold_Save_byte_identical':True,
    'cold_shifted_flags_overlap':{'displacement_bytes':68,'exact_bytes':232},
    'cold_shifted_owned_overlap':{'displacement_bytes':68,'matching_bytes':ownedOverlap,'compared_bytes':1204},
    'cold_stop_frame_interval':[3049,3348],'exact_stop_frame_not_captured':True,
    'diagnosis':'source-compatible transient SaveBlock relocation guard failure: native pointers move before copied data is restored; per-frame SaveBlock counter/flag reads are unsafe here. CPU PC/relocation pointers were not captured, so exact copy phase is not independently proven.',
    'resource_invariance_at_transient_stop_not_claimed':True,'strict_stop_preserved':True,
    'next_dependency':'Parent review of cold STOP and minimal readiness-aware relocation guard/counter bookkeeping correction; no battle retry or cold retry authorised here.'}
(ART/'safe-findings.json').write_text(json.dumps(report,indent=2)+'\n')
(ART/'private-decoded-fields.json').write_text(json.dumps({'walking_event':private,'anchor':[fields.decode(before[i*100:(i+1)*100])['fields'] for i in range(2)],'saved':[fields.decode(after[i*100:(i+1)*100])['fields'] for i in range(2)],'canonical_resources':anchor.hex()},indent=2)+'\n')
print('PASS new prepared victory/manual Save/native sectors:270 assertions,6952 battle frames,exact rewards/NO/YES;HP26/24 PP4/40/0/38')
print('PASS actual87/83→88/84 at observed127→0;native checksums/re-encoding/all other600 party bytes exact;11 stable logical resource checks')
print('PASS exact cold boot600 party/count/counter8/flags/resources and initial stable check; Save byte-identical;25 assertions/zero battles')
print('STOP57 during cold return warp:party600 exact;counter14→transient5953;flags232 bytes exactly displaced68;owned1196/1204 displaced68. Native relocation source fits; CPU phase not captured. No retry.')
print('LIMIT timestamp labels use batch-start total; event actual19138..19189, cold stop3049..3348; full cold return route remains unverified')
