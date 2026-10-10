"""Read-only complete native transition and live/Save equivalence, never inputs."""
from pathlib import Path
import importlib.util,json,struct,sys
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prior=module('co_models',ROOT/'scripts/floor1/continuous-opening-native-model.py')
fields=prior.fields;friendship=prior.friendship
def snapshot(path):
    raw=Path(path).read_bytes();assert len(raw)==3324
    values=struct.unpack('<10I',raw[3284:]);keys=['context','counter','count','saved_count','group','mapnum','section','x','y','facing']
    d=dict(zip(keys,values));d.update(party=raw[:600],flags=raw[600:900],owned=raw[900:2172],vars=raw[2172:2684],saved=raw[2684:3284],map=[values[4],values[5]],position=list(values[7:9]))
    d['logical']=prior.resources.canonical(d['owned'],struct.pack('<I',d['context']))
    assert d['count']==2 and 0<=d['counter']<128 and d['map'][0]==35 and d['map'][1] in (0,1,3,4)
    for i in range(6):
        raw=d['party'][100*i:100*(i+1)];m=fields.decode(raw);assert m['checksum_valid'] and m['reencoding_exact']
        if i<2:assert not m['bad_egg'] and not m['egg'] and m['fields']['species']==(66 if i==0 else 52) and m['fields']['held_item']==0
        else:assert raw==bytes(100)
    for flag in (35,40,41,42,43,44,45,46,49,2139):assert not(d['flags'][flag//8]&(1<<(flag%8)))
    return d
def change_item(logical,item,delta):
    data=bytearray(logical);offset=None
    for i in range(30):
        off=0xd0+4*i
        if struct.unpack_from('<H',data,off)[0]==item:offset=off;break
    if offset is None:
        assert delta>0
        offset=next(0xd0+4*i for i in range(30) if struct.unpack_from('<H',data,0xd0+4*i)[0]==0)
        struct.pack_into('<H',data,offset,item)
    qty=struct.unpack_from('<H',data,offset+2)[0]+delta;assert 0<qty<=99
    struct.pack_into('<H',data,offset+2,qty);return bytes(data)
def validate(name,before,after):
    if name=='boot':
        assert after['map']==[35,0] and bool(after['flags'][4]&1)
        for i in range(2):
            decoded=fields.decode(after['party'][100*i:100*(i+1)]);f=decoded['fields'];c=decoded['canonical']
            assert f['level']==8 and f['experience']==(399 if i==0 else 709) and f['PP']==([8,40,0,0] if i==0 else [2,40,0,0])
            assert f['personality']==(128 if i==0 else 0) and f['moves']==([355,356,0,0] if i==0 else [357,358,0,0])
            iv=struct.unpack_from('<I',c,72)[0];assert all((iv>>(5*j))&31==20 for j in range(6)) and (iv>>31)==i
            stats=prior.level_stats(c,8);assert f['hp_maxhp_attack_defense_speed_spatk_spdef']==[stats[0]]+stats and f['status']==0
        assert struct.unpack_from('<I',after['logical'])[0]==3000 and struct.unpack_from('<H',after['vars'],0x9c)[0]==1
        return
    assert before['counter']==after['counter'],'no counter jump in stationary phase'
    if name=='stairs-yes':assert before['map']==[35,3] and before['position']==[12,10] and after['map']==[35,4] and after['position']==[4,4]
    else:assert before['map']==after['map'] and before['position']==after['position'],'stationary declared phase'
    flags=bytearray(before['flags']);logical=before['logical'];party=bytearray(before['party'])
    additions={'note':[33,36],'supply':[38],'guide-initial':[34],'trial':[37,2135],'scrap':[39],'guard':[2136],'howler':[2137],'boss':[47,2138],'stairs-yes':[48]}
    for flag in additions.get(name,[]):assert not(flags[flag//8]&(1<<(flag%8)));flags[flag//8]|=1<<(flag%8)
    if name in ('supply','scrap'):logical=change_item(logical,13 if name=='supply' else 378,2)
    if name=='potion':
        c=bytearray(fields.decode(before['party'][100:200])['canonical']);hp,maxhp=struct.unpack_from('<HH',c,86);assert hp<maxhp,'demonstration requires actual missingHP, never manufactured'
        gain=min(20,maxhp-hp);struct.pack_into('<H',c,86,hp+gain);party[100:200]=prior.encode(c,before['party'][100:200]);logical=change_item(logical,13,-1)
        print('POTION_DEMONSTRATION necessary_survival_cost=0 demonstration_cost=1 actual_missingHP='+str(maxhp-hp)+' native_capped_gain='+str(gain))
    if name.startswith('guide-'):
        for i in range(2):
            old=before['party'][100*i:100*(i+1)];c=bytearray(fields.decode(old)['canonical']);c[52:56]=bytes((8 if i==0 else 2,40,0,0));struct.pack_into('<I',c,80,0);c[86:88]=c[88:90];party[100*i:100*(i+1)]=prior.encode(c,old)
    if name in ('trial','guard','howler','boss'):
        gain={'trial':96,'guard':132,'howler':121,'boss':226}[name];money=320 if name in ('trial','guard') else 360
        logical=bytearray(logical);struct.pack_into('<I',logical,0,struct.unpack_from('<I',logical)[0]+money);logical=bytes(logical)
        ev={'trial':(1,0,0,1,0,0),'guard':(0,0,0,1,1,0),'howler':(1,0,0,1,0,0),'boss':(3,0,0,0,0,0)}[name]
        for i in range(2):
            old=before['party'][100*i:100*(i+1)];new=after['party'][100*i:100*(i+1)];c=bytearray(fields.decode(old)['canonical']);n=fields.decode(new)['canonical']
            xp=struct.unpack_from('<I',c,36)[0]+gain;struct.pack_into('<I',c,36,xp)
            for j,v in enumerate(ev):c[56+j]+=v
            level=c[84]
            def threshold(l):return max(0,(6*l**3)//5-15*l*l+100*l-140) if i==0 else l**3
            while level<100 and xp>=threshold(level+1):level+=1
            c[41]=friendship.level_ups(c[41],levels=level-c[84],met_location=c[69],section=after['section'],ball=(struct.unpack_from('<H',c,70)[0]>>11)&15,held_item=struct.unpack_from('<H',c,34)[0],pokerus=c[68]);c[84]=level
            stats=prior.level_stats(c,level);struct.pack_into('<6H',c,88,*stats)
            hp=struct.unpack_from('<H',n,86)[0];assert 0<hp<=stats[0] and struct.unpack_from('<I',n,80)[0]==0
            struct.pack_into('<H',c,86,hp);assert all(0<=n[52+j]<=c[52+j] for j in range(4));c[52:56]=n[52:56]
            party[100*i:100*(i+1)]=prior.encode(c,old)
    assert after['party']==bytes(party),'all600 party bytes exactly derived with actual battle HP/PP/native friendship'
    assert after['flags']==bytes(flags),'all300 flags: only source-earned transition'
    assert after['logical']==logical,'all1272 logical money/coins/bag/PC bytes'
    variables=bytearray(before['vars'])
    if name in ('trial','guard','howler','boss'):struct.pack_into('<H',variables,0x56,0)
    assert after['vars']==bytes(variables),'all512 vars; exact native battle poison-counter reset only'
    if name!='save':assert after['saved']==before['saved'] and after['saved_count']==before['saved_count']
    else:assert after['saved']==after['party'] and after['saved_count']==2
def disk_equivalence(save,live):
    d=fields.saved_party(save);raw=Path(save).read_bytes();selected={}
    latest=max(struct.unpack_from('<I',raw,i*4096+0xffc)[0] for i in range(28) if struct.unpack_from('<I',raw,i*4096+0xff8)[0]==0x08012025)
    for i in range(28):
        sec=raw[i*4096:(i+1)*4096];sid,_,signature,count=struct.unpack_from('<HHII',sec,0xff4)
        if signature==0x08012025 and count==latest and sid<14:selected[sid]=sec
    sb=b''.join(selected[i+1][:min(3968,0x3d88-i*3968)] for i in range(4));key=selected[0][0xac:0xb0]
    assert d['party']==live['party']==live['saved'] and d['count']==live['count']==live['saved_count']==2
    assert d['friendship_counter']==live['counter'] and d['map']==live['map']==[35,4] and d['position']==live['position']==[8,6]
    assert sb[0x1270:0x139c]==live['flags'] and sb[0x139c:0x159c]==live['vars']
    assert prior.resources.canonical(sb[0x490:0x988],key)==live['logical']
    return {'PASS':True,'all14_sector_checksums':True,'full_live_disk_party_count_counter_flags_vars_resources_legalfield':True}
if __name__=='__main__':
    name=sys.argv[1];after=snapshot('current-state.bin')
    if name=='cold':
        before=snapshot('expected-final-state.bin')
        for k in ('party','count','counter','flags','vars','logical','saved','saved_count','map','position'):assert before[k]==after[k],('actual cold state',k)
        disk_equivalence('game.sav',after)
    else:validate(name,snapshot('before-state.bin'),after)
    print('PASS complete source-native transition '+name)
