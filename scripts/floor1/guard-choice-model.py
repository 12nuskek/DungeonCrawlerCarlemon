"""Native medicine equations; comparison fixtures never supply gameplay state."""
import struct
def choice(carl_hp,carl_max,donut_hp,donut_max,guard_alive,potions,strike,brace):
    assert isinstance(guard_alive,bool)
    assert all(isinstance(x,int) for x in (carl_hp,carl_max,donut_hp,donut_max,potions,strike,brace))
    assert 0<=carl_hp<=carl_max<=36 and 0<=donut_hp<=donut_max<=28
    assert 0<=potions<=2 and 0<=strike<=8 and 0<=brace<=40
    if not carl_hp or not donut_hp:return 90
    if not strike and brace:return 92
    risk=(carl_hp<=(27 if guard_alive else 12),donut_hp<=12)
    if all(risk):return 100
    if not any(risk):return 0
    if not potions:return 101
    target=0 if risk[0] else 1;hp=(carl_hp,donut_hp)[target];maximum=(carl_max,donut_max)[target]
    if min(hp+20,maximum)<=(27 if target==0 and guard_alive else 12):return 102
    return target+1
def remove(logical,item=13,count=1,position=0):
    """Exact native preferred-slot then matching-slot subtraction; no compaction."""
    assert len(logical)==1272 and 0<=position<30 and count>0
    slots=[list(struct.unpack_from('<HH',logical,0xd0+4*i)) for i in range(30)]
    assert sum(q for n,q in slots if n==item)>=count
    for i in [position]+[j for j in range(30) if j!=position]:
        if slots[i][0]!=item:continue
        spent=min(slots[i][1],count);slots[i][1]-=spent;count-=spent
        if not slots[i][1]:slots[i][0]=0
        if not count:break
    assert not count
    result=bytearray(logical)
    for i,slot in enumerate(slots):struct.pack_into('<HH',result,0xd0+4*i,*slot)
    return bytes(result)
def compact(logical):
    """Native nested swap algorithm, including the positions of empty records."""
    assert len(logical)==1272
    result=bytearray(logical)
    for i in range(29):
        for j in range(i+1,30):
            a=0xd0+4*i;b=0xd0+4*j
            if struct.unpack_from('<H',result,a+2)[0]==0:
                result[a:a+4],result[b:b+4]=result[b:b+4],result[a:a+4]
    return bytes(result)
def order(raw):
    assert len(raw)==3
    result=[n for b in raw for n in (b>>4,b&15)]
    assert sorted(result)==list(range(6)) and set(result[:2])=={0,1}
    return result
def to_ui(party,positions):
    assert len(party)==600 and sorted(positions)==list(range(6))
    return b''.join(party[100*i:100*i+100] for i in positions)
def to_field(party,positions):
    assert len(party)==600 and sorted(positions)==list(range(6))
    return b''.join(party[100*positions.index(i):100*positions.index(i)+100] for i in range(6))
def healed(party,recipient):
    assert len(party)==600 and recipient in (0,1)
    result=bytearray(party);off=100*recipient+86;hp,maximum=struct.unpack_from('<HH',result,off)
    assert 0<hp<maximum
    struct.pack_into('<H',result,off,min(hp+20,maximum));return bytes(result)
