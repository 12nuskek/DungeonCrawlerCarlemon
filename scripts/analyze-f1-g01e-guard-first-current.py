#!/usr/bin/env python3
"""Read-only diagnosis of the preserved FIRST Guard milestone STOP. No emulator."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('gf_diagnostic_state',ROOT/'scripts/floor1/guard-first-state.py');native=importlib.util.module_from_spec(s);s.loader.exec_module(native)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def analyse(runtime):
 d=Path(runtime)/'patrol';before=native.snapshot(d/'guard-before');after=native.snapshot(d/'stop-live');seed=native.snapshot(d/'expected')
 assert after['absolute_frame']==14680 and after['native_phase_valid'];assert before['map']==after['map']==[35,0] and before['position']==after['position']==[37,31] and before['counter']==after['counter']==72
 assert before['count']==before['saved_count']==after['count']==after['saved_count']==2
 try:native.validate('guard-win',before,after,seed)
 except AssertionError as e:assert str(e)=='source friendship modifiers'
 else:raise AssertionError('Preserved original gate no longer rejects original input')
 # Source predicate/case text verified against unchanged native pokemon.c.
 source=(ROOT/'engine/src/pokemon.c').read_text();assert '[FRIENDSHIP_EVENT_GROW_LEVEL]      = { 5,  3,  2}' in source
 assert 'GetMonData(mon, MON_DATA_MET_LOCATION, NULL) == GetCurrentRegionMapSectionId()' in source and 'friendship++;' in source
 assert 'TRAINER_CLASS_PKMN_TRAINER_1' in (ROOT/'engine/src/data/trainers.h').read_text().split('[TRAINER_DCC_BOSS]')[0]
 expected=bytearray(before['party']);members=[]
 for i,name in enumerate(('Carl','Donut')):
  old=before['party'][100*i:100*(i+1)];new=after['party'][100*i:100*(i+1)];od=native.fields.decode(old);nd=native.fields.decode(new);c=bytearray(od['canonical']);n=nd['canonical']
  assert od['checksum_valid'] and nd['checksum_valid'] and od['reencoding_exact'] and nd['reencoding_exact']
  assert not any((od['bad_egg'],nd['bad_egg'],od['egg'],nd['egg']))
  met=c[69]==after['section'];luxury=((struct.unpack_from('<H',c,70)[0]>>11)&15)==11
  assert met and not luxury and c[68]==0 and struct.unpack_from('<H',c,34)[0]==0
  level=(10,9)[i];xp=(627,937)[i];levels_gained=level-c[84];old_friend=c[41]
  struct.pack_into('<I',c,36,xp);c[59]+=1;c[60]+=1
  for _ in range(levels_gained):c[41]=min(255,c[41]+(5 if c[41]<=99 else 3 if c[41]<=199 else 2)+int(met)+int(luxury))
  c[84]=level;stats=native.level_stats(c,level);struct.pack_into('<6H',c,88,*stats)
  hp=struct.unpack_from('<H',n,86)[0];assert 0<hp<=stats[0] and struct.unpack_from('<I',n,80)[0]==0;struct.pack_into('<H',c,86,hp)
  assert all(0<=n[52+j]<=c[52+j] for j in range(4)) and n[54:56]==bytes(2);c[52:56]=n[52:56]
  expected[100*i:100*(i+1)]=native.encode(c,old);assert expected[100*i:100*(i+1)]==new,'complete source-derived native member'
  changed=[k for k,v in od['fields'].items() if v!=nd['fields'][k]]
  members.append(dict(member=name,levels_gained=levels_gained,friendship_before=old_friend,friendship_after=nd['fields']['friendship'],met_location_matches_current_section=met,luxury_ball=luxury,source_base_friendship_mod=5 if levels_gained else 0,source_met_bonus=1 if levels_gained else 0,experience=xp,level=level,HP=hp,maxHP=stats[0],PP=nd['fields']['PP'],EVs=nd['fields']['effort_contest'][:6],status=nd['fields']['status'],changed_field_names=sorted(changed),checksum_and_reencoding_valid=True,all_other_native_bytes_exact=True))
 assert bytes(expected)==after['party'] and before['party'][200:]==after['party'][200:]
 flags=bytearray(before['flags']);flags[2136//8]|=1<<(2136%8);assert bytes(flags)==after['flags'] and not(after['flags'][2137//8]&(1<<(2137%8))) and before['flags'][2135//8]&(1<<(2135%8))
 logical=bytearray(before['logical']);struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+320);assert bytes(logical)==after['logical']
 summary=json.loads((Path(runtime)/'summary.json').read_text());assert len(summary)==1 and summary[0]['exit']==71 and summary[0]['clock']['battle_attempts']==1
 assert sha(Path(runtime)/'patrol.sav')==summary[0]['input_Save_SHA256']==summary[0]['output_Save_SHA256']
 assert not(Path(runtime)/'cold').exists()
 return dict(method='Read-only native STOP diagnosis; does not modify the frozen validator or transfer acceptance',STOP=summary[0],reason='Frozen observer incorrectly required met-location != current Field section; actual input matches, so native level-up friendship adds1 after base5',members=members,complete_source_derived600_party_matches=True,remaining400_exact=True,exact300_flags_only2136=True,exact1272_logical_owned_money_delta320_only=True,trial_gate_true_Howler_pending=True,manual_Save_not_reached=True,dependent_cold_not_executed=True,named_measurements_reached=[],current_order_travel_acceptance='UNVERIFIED / STOP',private_snapshot_hashes={p.name:sha(p) for p in sorted(d.glob('*.bin'))},next_dependency='Parent review of preserved STOP and narrowly source-derived met-location modifier before any separately authorised corrected route/cold. No further emulator execution or integration here.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();result=analyse(a.runtime);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print('PASS read-only STOP diagnosis: native Carl75->81 = base5+met1; complete600 party/300 flags/1272 owned source-compatible; no acceptance or emulator')
