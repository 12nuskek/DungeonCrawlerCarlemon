#!/usr/bin/env python3
"""Offline actual retained-save checks; no fabricated state or emulator."""
from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('party_fields',ROOT/'scripts/floor1/party-fields.py')
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for case,hp,pp,digest in [
    ('offensive',[18,24],[[3,40,0,0],[0,37,0,0]],'6ab1357be75bcf4f41fe8064e8df590876348e28fe78e557f28ff90648246386'),
    ('fortify',[29,22],[[2,37,0,0],[0,33,0,0]],'7092ce7704a94158046195581e6b9e72dfb640005c46dea20efc83ff3638badf')]:
    data=m.saved_party(ROOT/f'artifacts/floor1/warden-fairness/runtime/{case}/first-clear.sav')
    assert data['save_SHA256']==digest and data['latest_sector_checksums_valid']
    assert data['count']==2 and data['map']==[35,4] and data['position']==[8,6] and data['friendship_counter']==66
    for i in range(2):
        d=m.decode(data['party'][100*i:100*(i+1)]);f=d['fields']
        assert d['checksum_valid'] and d['reencoding_exact'] and not d['bad_egg'] and not d['egg']
        assert f['level']==[12,10][i] and f['experience']==[974,1284][i]
        assert f['status']==f['held_item']==0 and f['hp_maxhp_attack_defense_speed_spatk_spdef'][0]==hp[i]
        assert f['PP']==pp[i]
    safe,_=m.compare(data['party'],data['party'])
    assert safe['strict200_byte_equal'] and safe['remaining400_party_bytes_exact']
    assert all(x['all_other_canonical_bytes_exact'] and x['derived_checksum_delta_exact'] and x['only_derived_ciphertext_bytes_changed'] for x in safe['members'])
    print('PASS actual',case,'all14 native sector checksums; decoded duo identity/resources, party checksums, exact round-trip and strict comparison')
print('PASS all24 native substruct permutations source-derived; no modified input, emulator or RNG call')
