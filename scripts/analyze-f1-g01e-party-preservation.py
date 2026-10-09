#!/usr/bin/env python3
"""Offline bounded findings only; complete decoded identities stay private."""
from pathlib import Path
import hashlib, importlib.util, json, re, struct

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts/floor1/party-preservation-diagnosis'
DATA=ART/'runtime'
loader=importlib.util.spec_from_file_location('party_fields',ROOT/'scripts/floor1/party-fields.py')
fields=importlib.util.module_from_spec(loader);loader.loader.exec_module(fields)
before=(DATA/'anchor-party.bin').read_bytes()
stable=(DATA/'last-stable-party.bin').read_bytes()
after=(DATA/'after-party.bin').read_bytes()
safe,private=fields.compare(before,after)
adjacent,private_adjacent=fields.compare(stable,after)
assert before==stable==after and all(x['checksums_valid_before_after'] and x['reencoding_exact'] for x in safe['members'])
meta=json.loads((DATA/'private-buffer-metadata.json').read_text())
summary=json.loads((DATA/'summary.json').read_text())
owned_before=(DATA/'anchor-owned.bin').read_bytes();owned_after=(DATA/'after-owned.bin').read_bytes()
assert len(owned_before)==len(owned_after)==0x988-0x490
header=(ROOT/'engine/include/constants/global.h').read_text()
quantity_offsets=[];pockets=[]
for label,base in [('ITEMS',0x560),('KEYITEMS',0x5d8),('POKEBALLS',0x650),('TMHM',0x690),('BERRIES',0x790)]:
    count=int(re.search(r'#define BAG_'+label+r'_COUNT\s+(\d+)',header)[1]);pockets.append({'pocket':label,'slots':count})
    quantity_offsets.extend(base+4*j+2 for j in range(count))
u16=lambda data,offset:struct.unpack_from('<H',data,offset-0x490)[0]
shift=u16(owned_before,0x494)^u16(owned_after,0x494)
same_shift=all(u16(owned_before,q)^u16(owned_after,q)==shift for q in quantity_offsets)
money_shift=struct.unpack_from('<I',owned_before)[0]^struct.unpack_from('<I',owned_after)[0]
encoded=set(range(0x490,0x496))|{q+j for q in quantity_offsets for j in range(2)}
changed=[0x490+i for i,(a,b) in enumerate(zip(owned_before,owned_after)) if a!=b]
plain_exact=all(a==b for i,(a,b) in enumerate(zip(owned_before,owned_after)) if i+0x490 not in encoded)
assert set(changed)<=encoded and same_shift and (money_shift&0xffff)==shift and plain_exact
assert meta['counter_last_stable']==meta['counter_after']==72 and meta['counter_anchor']==66
assert meta['other400_exact'] and meta['flags_exact'] and not meta['owned_exact']
assert summary['exit']==57 and summary['frames']==2236 and summary['battle_frames']==0 and summary['input_copy_unchanged']
assert (DATA/'STOP.json').exists()
hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in DATA.glob('*.bin')}
report={
    'scope':'new single noncombat probe; no retrospective prepared-field identification',
    'summary':summary,'capture_metadata':meta,'party_comparison':safe,
    'last_stable_comparison':adjacent,'private_buffer_SHA256':hashes,
    'resource_findings':{
        'raw_changed_bytes':len(changed),'owned_region_bytes':len(owned_before),
        'changes_confined_to_native_encoded_money_coins_bag_quantities':True,
        'bag_pockets':pockets,'bag_quantity_words':len(quantity_offsets),
        'all_bag_quantities_and_coins_have_same_XOR_difference':same_shift,
        'money_low16_XOR_difference_matches':(money_shift&0xffff)==shift,
        'every_unencrypted_owned_region_byte_exact':plain_exact,
        'encoding_pattern_matches_native_map_load_rekey_source':True,
        'actual_resource_encryption_context_captured':False,
        'decoded_money_resource_invariance_independently_proven':False,
        'limitation':'No old/new resource key context retained. Inferring keys from assumed unchanged values would be circular; no such inference is used as acceptance.'},
    'natural_counter_transitions':re.findall(r'^STEP (.+)$',(DATA/'replay.log').read_text(),re.M),
    'actual_staircase_NO_reached':False,'natural128_boundary_reached':False,
    'legitimate_friendship_delta_proven':False,'original_prepared_changed_field_identified':False,
    'preservation_relaxation_implemented':False,
    'next_dependency':'Parent review of resource-observer encoding flaw; any new probe requires separate authorisation. No friendship-delta preservation contract recommended on this evidence.',
    'source_paths':['engine/src/overworld.c:LoadMapInStepsLocal/ResetMirageTowerAndSaveBlockPtrs',
                    'engine/src/load_save.c:MoveSaveBlocks_ResetHeap/ApplyNewEncryptionKeyToAllEncryptedData',
                    'engine/src/item.c:ApplyNewEncryptionKeyToBagItems',
                    'engine/src/pokemon.c:GetSubstruct/CalculateBoxMonChecksum/EncryptBoxMon/AdjustFriendship',
                    'engine/src/field_control_avatar.c:UpdateFriendshipStepCounter']}
(ART/'private-decoded-fields.json').write_text(json.dumps({'anchor_to_after':private,'last_stable_to_after':private_adjacent},indent=2)+'\n')
(ART/'safe-findings.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS offline exact decoding: all600 party bytes unchanged; both native checksums and re-encoding valid; friendship deltas0')
print('OBSERVED strict new resource stop:378 encoded bytes,186 bag words/common XOR difference, unencrypted resource bytes exact')
print('LIMIT counter66→72; NO/128 boundary unreached. Actual key context absent; no independent decoded-resource invariance or friendship mechanism proof.')
print('STOP/claim preserved; no new emulator frames, prepared replay, retry or preservation relaxation')
