#!/usr/bin/env python3
"""Read-only actual native checkpoint/Save/cold review; never runs the emulator."""
from pathlib import Path
import argparse,importlib.util,json,re,struct,hashlib
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('corrected_native_review',ROOT/'scripts/floor1/guard-first-state.py');state=importlib.util.module_from_spec(s);s.loader.exec_module(state)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def safe_party(raw):
 out=[]
 for i,name in enumerate(('Carl','Donut')):
  decoded=state.fields.decode(raw[100*i:100*(i+1)]);d=decoded['fields']
  assert decoded['checksum_valid'] and decoded['reencoding_exact'] and not decoded['egg'] and not decoded['bad_egg']
  out.append(dict(member=name,level=d['level'],XP=d['experience'],HP=d['hp_maxhp_attack_defense_speed_spatk_spdef'][0],maxHP=d['hp_maxhp_attack_defense_speed_spatk_spdef'][1],PP=d['PP'],friendship=d['friendship'],EVs=d['effort_contest'][:6],status=d['status'],checksum_and_reencoding_valid=True))
 return out

def analyse(runtime):
 r=Path(runtime);summary=json.loads((r/'summary.json').read_text());assert [x['stage'] for x in summary]==['patrol','cold'] and all(x['exit']==x['errors_bytes']==0 for x in summary)
 assert not(r/'STOP.json').exists()
 patrol=r/'patrol';cold=r/'cold';old=ROOT/'artifacts/floor1/guard-first-current/runtime/patrol'
 for kind in ('party','flags','owned','context'):assert (patrol/('guard-win-'+kind+'.bin')).read_bytes()==(old/('stop-live-'+kind+'.bin')).read_bytes()
 pairs=[('guard-win','guard-before'),('guide-guard','guide-guard-before'),('howler-win','howler-before'),('guide-howler','guide-howler-before'),('guide-preboss','guide-preboss-before')]
 seed=state.snapshot(patrol/'expected');checkpoints=[]
 for name,prior in pairs:
  before=state.snapshot(patrol/prior);after=state.snapshot(patrol/name);state.validate(name,before,after,seed)
  checkpoints.append(dict(name=name,absolute_frame=after['absolute_frame'],map=after['map'],position=after['position'],counter=after['counter'],safe_party=safe_party(after['party']),complete_native_member_reconstruction=True,all300_flags_and1272_logical_resources_exact_to_declared_transition=True))
 expected_positions={'boot':([35,0],[37,31]),'guard-win':([35,0],[37,31]),'guide-guard':([35,1],[4,5]),'guard-repeat':([35,0],[37,31]),'howler-win':([35,0],[51,27]),'guide-howler':([35,1],[4,5]),'howler-repeat':([35,0],[51,27]),'guide-preboss':([35,1],[4,5]),'final':([35,3],[8,7]),'saved':([35,3],[8,7])}
 spec=json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text());layouts=json.loads((ROOT/'engine/data/layouts/layouts.json').read_text())['layouts']
 for name,(wanted_map,wanted_position) in expected_positions.items():
  observed=state.snapshot(patrol/name);assert observed['map']==wanted_map and observed['position']==wanted_position and observed['native_phase_valid']
  mapname=next(m['name'] for m in spec['production_identity_proposal']['maps'].values() if m['map_num']==wanted_map[1]);model=json.loads((ROOT/f'engine/data/maps/{mapname}/map.json').read_text());layout=next(x for x in layouts if x['id']==model['layout']);data=(ROOT/'engine'/layout['blockdata_filepath']).read_bytes();x,y=wanted_position
  assert not(struct.unpack_from('<H',data,2*(y*layout['width']+x))[0]&0xc00),'source-native stable legal position'
 final=state.snapshot(patrol/'saved');disk=state.snapshot(patrol/'disk');boot=state.snapshot(cold/'boot');last=state.snapshot(cold/'cold')
 for k in ('party','flags','logical','count','saved_count','counter','map','position'):assert final[k]==disk[k]==boot[k]==last[k],('exact native persistence',k)
 saved=state.fields.saved_party(r/'patrol.sav');assert saved['latest_sector_checksums_valid'] and saved['party']==final['party'] and saved['friendship_counter']==47
 assert saved['save_SHA256']==sha(r/'cold.sav')==summary[0]['output_Save_SHA256']==summary[1]['input_Save_SHA256']==summary[1]['output_Save_SHA256']
 flags=bytearray(seed['flags'])
 for flag in (2136,2137):flags[flag//8]|=1<<(flag%8)
 assert final['flags']==bytes(flags)
 owned=bytearray(seed['logical']);struct.pack_into('<I',owned,0,struct.unpack_from('<I',owned)[0]+680);assert final['logical']==bytes(owned)
 log=(patrol/'replay.log').read_text();assert len(re.findall(r'PASS repeat encounter no battle',log))==2
 assert all(x['clock']['absolute_frames']==sum(x['clock'][k] for k in ('valid_samples','deferred_samples','unarmed_frames','mutation_frames')) for x in summary)
 assert summary[0]['clock']['battle_attempts']==2 and summary[0]['clock']['battle_frames']==17336 and summary[1]['clock']['battle_attempts']==summary[1]['clock']['battle_frames']==0
 boundary=re.findall(r'WALK_STEP absolute_frame=(\d+) counter=127->0 friendship=(\d+),(\d+)',log);assert boundary==[('26157','89','81')]
 before_walk=state.snapshot(patrol/'guide-howler');after_walk=state.snapshot(patrol/'howler-repeat');walk,_=state.fields.compare(before_walk['party'],after_walk['party'])
 assert walk['remaining400_party_bytes_exact'] and all(x['all_other_canonical_bytes_exact'] and x['derived_checksum_delta_exact'] and x['only_derived_ciphertext_bytes_changed'] for x in walk['members'])
 assert [x['friendship_delta'] for x in walk['members']]==[2,0]
 return dict(method='Read-only review of actual newly executed native milestones/serialized Save/cold; raw identities and encoding contexts private',execution_source=summary[0]['execution_source'],current_order_travel_Save_cold='PASS, bounded only; unmerged',exact_original_PR109_Guard_output_reproduced=True,original_PR109_STOP_preserved=True,milestones=checkpoints,all10_stable_positions_match_route_and_source_native_collision=True,once_only_XP_money_and_patrol_flags=True,all_other_optional_preparation_boss_checkpoint_loop_flags_seed_exact=True,all_owned_except680_money_seed_exact=True,manual_Save_latest14_native_sector_checksums_valid=True,exact600_party_count_counter_flags_all1272_logical_resources_map_position_across_Save_and_cold=True,final_map=final['map'],final_position=final['position'],final_counter=final['counter'],final_party=safe_party(final['party']),walking_boundary=dict(absolute_frame=26157,counter='127->0',friendship_delta=[2,0],Carl_native_walk_base1_plus_matching1=True,Donut_engine_observed_skip=True,all_other_party_bytes_and_derived_checksum_ciphertext_exact=True),measured_travel=summary[0]['measurements'],combined_emulator_assertions=sum(x['assertions'] for x in summary),actual_only_trainers=[856,857],Warden_battles=0,output_Save_SHA256=saved['save_SHA256'],raw_snapshot_hashes={str(p.relative_to(r)):sha(p) for stage in ('patrol','cold') for p in sorted((r/stage).glob('*.bin'))},legacy_inputs_recovered=False,full_floor_C01_human_pacing_acceptance=False,next_dependency='Parent review then explicit reviewed-stack integration authority, preserving CP72e bridge and legacy limitation; staged V01 after integration. No further execution here.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=analyse(a.runtime);a.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS read-only actual native checkpoints/Save/cold/source collision/rewards/walking review; no emulator')
