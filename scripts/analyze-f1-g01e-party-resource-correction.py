#!/usr/bin/env python3
"""Offline new probe fields; actual encoding context/full identities stay private."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/floor1/party-resource-correction';DATA=ART/'runtime'
l=importlib.util.spec_from_file_location('resource_fields',ROOT/'scripts/floor1/party-fields.py')
fields=importlib.util.module_from_spec(l);l.loader.exec_module(fields)
def canonical(raw,context):
    assert len(raw)==0x988-0x490 and len(context)==4
    key=struct.unpack('<I',context)[0];out=bytearray(raw)
    struct.pack_into('<I',out,0,struct.unpack_from('<I',raw)[0]^key)
    struct.pack_into('<H',out,4,struct.unpack_from('<H',raw,4)[0]^(key&0xffff))
    for base,count in [(0x560,30),(0x5d8,30),(0x650,16),(0x690,64),(0x790,46)]:
        for i in range(count):
            q=base-0x490+4*i+2;struct.pack_into('<H',out,q,struct.unpack_from('<H',raw,q)[0]^(key&0xffff))
    return bytes(out)
before=(DATA/'anchor-party.bin').read_bytes();after=(DATA/'after-party.bin').read_bytes();stable=(DATA/'last-stable-party.bin').read_bytes()
safe,private=fields.compare(before,after);adjacent,privateAdjacent=fields.compare(stable,after)
assert stable==before and not safe['strict200_byte_equal'] and safe['remaining400_party_bytes_exact']
assert all(m['checksums_valid_before_after'] and m['reencoding_exact'] and m['all_other_canonical_bytes_exact']
           and m['derived_checksum_delta_exact'] and m['only_derived_ciphertext_bytes_changed'] for m in safe['members'])
assert [m['friendship_delta'] for m in safe['members']]==[1,0]
assert safe['members'][0]['changed_field_names']==['checksum','friendship']
assert safe['members'][0]['safe_changed_fields']=={'friendship':{'before':92,'after':93},'checksum':{'before':70,'after':326}}
assert safe['members'][0]['raw_changed_offsets']==[29,65]
anchorRaw=(DATA/'anchor-owned.bin').read_bytes();anchorContext=(DATA/'anchor-context.bin').read_bytes();logical=canonical(anchorRaw,anchorContext)
checkpointResults=[]
for f in sorted(DATA.glob('ready-*-owned.bin')):
    c=f.with_name(f.name.replace('-owned','-context'));raw=f.read_bytes();context=c.read_bytes()
    assert canonical(raw,context)==logical
    checkpointResults.append({'snapshot':f.stem,'logical_exact':True,'actual_context_captured':len(context)==4,
                              'context_changed':context!=anchorContext,'raw_encoded_changed':raw!=anchorRaw})
assert len(checkpointResults)==12 and all(x['context_changed'] for x in checkpointResults)
for prefix in ['last-stable','after']:
    assert canonical((DATA/(prefix+'-owned.bin')).read_bytes(),(DATA/(prefix+'-context.bin')).read_bytes())==logical
money,coins=struct.unpack_from('<IH',logical);assert money==4360 and coins==0
metadata=json.loads((DATA/'private-buffer-metadata.json').read_text());summary=json.loads((DATA/'summary.json').read_text())
assert metadata['counter_last_stable']==127 and metadata['counter_after']==0
assert metadata['flags_exact'] and metadata['other400_exact'] and metadata['owned_exact']
assert summary['exit']==53 and summary['frames']==4702 and summary['battle_frames']==0 and summary['input_copy_unchanged']
log=(DATA/'replay.log').read_text();assert 'PASS choice-result 0' in log and 'PASS expect 35 3 12 10 7' in log
build=ROOT/'artifacts/floor1/warden-fairness/build/source/engine'
def enum_value(path,target):
    text=re.sub(r'/\*.*?\*/|//[^\n]*','',path.read_text(),flags=re.S)
    block=re.search(r'enum\s*\{(.*?)\}',text,re.S)[1];value=-1
    for token in block.split(','):
        token=token.strip()
        if not token:continue
        pair=token.split('=');name=pair[0].strip();value=int(pair[1].strip(),0) if len(pair)==2 else value+1
        if name==target:return value
    raise AssertionError(target)
boss=enum_value(build/'include/constants/region_map_sections.h','MAPSEC_DCC_BOSS')
luxury=enum_value(build/'include/constants/items.h','ITEM_LUXURY_BALL')
d=fields.decode(after[:100]);misc=bytes.fromhex(d['fields']['origin_IV_ribbons'])
origin=struct.unpack_from('<H',misc,2)[0]
assert d['fields']['held_item']==0 and ((origin>>11)&15)!=luxury and misc[1]!=boss
sourceFacts={'walking_base_modifier':1,'held_item_bonus_absent':True,'luxury_ball_bonus_absent':True,
             'current_map_met_location_bonus_absent':True,'Carl_delta_matches_native_base_modifier':True,
             'native_clamping_not_needed':True,'Donut_unchanged_is_source_valid_skip_outcome':True}
report={'scope':'new separately claimed corrected noncombat probe only','summary':summary,'capture_metadata':metadata,
        'party_comparison':safe,'last_stable_comparison':adjacent,
        'resource_comparison':{'stable_checkpoints':checkpointResults,'all_logical_owned_bytes_exact':True,
            'money_before_after':money,'coins_before_after':coins,'all186_bag_IDs_quantities_including_empty_exact':True,
            'PC_items_and_unencoded_bytes_exact':True,'actual_native_context_used':True,'context_inferred':False,
            'independent_offline_decode_agrees_with_host':True,'at_stop_logical_resources_exact':True},
        'source_walking_compatibility':sourceFacts,'actual_staircase_NO_verified':True,
        'new_natural_boundary_friendship_delta_proven':True,'original_prepared_changed_field_identified':False,
        'strict_gate_relaxed':False,'new_battle_Save_prepared_replay':False,
        'private_buffer_SHA256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in DATA.glob('*.bin')},
        'next_dependency':'Parent review of proven new walking mechanism and separate narrow preservation contract; no further execution authorised.'}
privateResource={'money':money,'coins':coins,'canonical_owned_bytes':logical.hex(),
                 'checkpoint_results':checkpointResults}
(ART/'private-decoded-fields.json').write_text(json.dumps({'party':private,'last_stable':privateAdjacent,'resources':privateResource},indent=2)+'\n')
(ART/'safe-findings.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS new actual boundary127→0: Carl friendship92→93, checksum70→326 (+256), only derived bytes29/65; Donut/rest400 exact')
print('PASS native party checksums, exact re-encoding, source walking+1/no bonus; every other canonical party byte exact')
print('PASS12 stable resource snapshots and stop independently decoded with actual privately captured context: money4360/coins0/all186 IDs+quantities/PC/unencoded exact')
print('STOP53 remains strict:4702frames/72assertions/2658armed checks/zero battles; actualNO passed; no Save/retry/exception; original prepared field unknown')
