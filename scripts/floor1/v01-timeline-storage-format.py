"""Decode bounded detail and full-run summaries; never infer full-history losslessness."""
import hashlib, struct
HEADER = struct.Struct('<8s6I')
ROW = struct.Struct('<46I')

def header(stream, magic):
    data = stream.read(32)
    if len(data)!=32: raise ValueError('Incomplete storage header')
    values = HEADER.unpack(data)
    if values[:5]!=(magic,46,4096,2046,250): raise ValueError('Wrong diagnostic contract')
    return values

def summaries(stream):
    header(stream,b'BVTS0003'); previous=bytes(32); total=0; stopped=False; ordinal=-1
    for sequence in range(38046):
        raw=stream.read(184)
        if not raw: return
        if len(raw)!=184 or sequence>=38045 or stopped: raise ValueError('Incomplete/overflow/post-stop summary')
        words=ROW.unpack(raw)
        if words[0]!=sequence or words[5]>4096 or words[6]>words[5] or words[19]!=46:
            raise ValueError('Invalid summary counts')
        total+=words[5]
        if words[8]!=total or words[9]!=0: raise ValueError('Observation count continuity failed')
        if raw[88:120]!=previous or raw[152:]!=hashlib.sha256(previous+raw[:88]+raw[120:152]).digest():
            raise ValueError('Summary hash continuity failed')
        if words[17]:
            current=words[10]|words[11]<<32
            if current<ordinal or words[14]>250: raise ValueError('Boundary/window continuity failed')
            ordinal=current
        elif words[14]>2046: raise ValueError('Startup window exceeded')
        previous=raw[152:]; stopped=bool(words[4]&3)
        yield words, raw

def detail(stream):
    values=header(stream,b'BVTD0003'); limit=250 if values[5] else 2046
    records=chunks=batch=0
    while raw:=stream.read(184):
        if len(raw)!=184: raise ValueError('Incomplete detailed record')
        records+=1; batch+=1
        if records>limit*4096 or batch>4096: raise ValueError('Detailed storage exceeded')
        words=ROW.unpack(raw)
        if words[0] not in range(1,10) or words[1]!=(1 if words[0] in (1,3) else 2):
            raise ValueError('Invalid detailed event')
        if words[0] in (6,7,8):
            chunks+=1; batch=0
            if chunks>limit: raise ValueError('Detailed chunk window exceeded')
        yield words,raw
