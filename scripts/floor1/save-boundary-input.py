"""Explicit checksum-valid synthetic save inputs. Never mutate an ordinary original."""
import struct
SIZE=3968
SIZES=[3884,3968,3968,3968,3848]+[3968]*8+[2000]

def sectors(data):
    for at in range(0,28*4096,4096):
        sid,check,sig,count=struct.unpack_from('<HHII',data,at+0xff4)
        if sig==0x8012025 and sid<14:
            yield at,sid,count

def blocks(data):
    rows=list(sectors(data));counter=max(v[2] for v in rows)
    selected={sid:at for at,sid,count in rows if count==counter}
    assert set(selected)==set(range(14)), 'Complete ordinary save slot required'
    return (b''.join(data[selected[i]:selected[i]+SIZES[i]] for i in range(1,5)),
            bytes(data[selected[0]:selected[0]+SIZES[0]]))

def patch(original, sb1_changes=(), sb2_changes=()):
    data=bytearray(original)
    for at,sid,count in list(sectors(data)):
        changes=sb2_changes if sid==0 else sb1_changes if 1<=sid<=4 else ()
        base=0 if sid==0 else (sid-1)*SIZE
        changed=False
        for offset,value in changes:
            for i,b in enumerate(value):
                if base<=offset+i<base+SIZES[sid]:
                    data[at+offset+i-base]=b;changed=True
        if not changed:continue
        total=sum(struct.unpack_from('<'+'I'*(SIZES[sid]//4),data,at))&0xffffffff
        struct.pack_into('<H',data,at+0xff6,((total>>16)+total)&0xffff)
    return bytes(data)

def warp(group,num,index,x,y):return struct.pack('<bbbBhh',group,num,index,0,x,y)

def inventory(raw,key):
    data=bytearray(raw[:0x848-0x490]);struct.pack_into('<I',data,0,struct.unpack_from('<I',data)[0]^key)
    struct.pack_into('<H',data,4,struct.unpack_from('<H',data,4)[0]^(key&0xffff))
    for at in range(0x560-0x490,0x848-0x490,4):
        struct.pack_into('<H',data,at+2,struct.unpack_from('<H',data,at+2)[0]^(key&0xffff))
    return bytes(data)
