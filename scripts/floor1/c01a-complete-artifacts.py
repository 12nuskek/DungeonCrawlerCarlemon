"""Read-only complete original-byte gates; never writes old result receipts."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
classifier=module('captureClassifier',ROOT/'scripts/floor1/c01a-capture-classifier.py')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
def edges(directory,frames):
    p=Path(directory);data=(p/'native-input-edge-private.bin').read_bytes()
    assert data[:8]==b'C01EDGE4' and struct.unpack_from('<II',data,8)==(40,18000*64+156*3+1) and (len(data)-16)%160==0
    rows=[struct.unpack_from('<40I',data,i) for i in range(16,len(data),160)];assert 0<len(rows)<=18000*64+156*3+1
    points=json.loads((p/'edge-profile.json').read_text())['points'];functions=json.loads((p/'verified-functions.json').read_text());ids={r['address']:r['hash32'] for r in functions}
    tags={};endframes=[];consumed=[]
    for w in rows:
        assert w[0] in [1,2,3,4,5,6,7,8,9,11] and w[1]<=156 and w[4]<=1023 and w[5]<=1023
        tags[str(w[0])]=tags.get(str(w[0]),0)+1
        if w[39]<12:
            point=points[w[39]];assert w[35]==point['address'] and w[36]==ids[point['function']]
        if w[0]==8:endframes.append(w[3])
        if w[0]==4:assert w[30] in (0,1) and w[23] and w[24]==w[30] and w[25]==w[2]
        if w[31]:assert w[0]==6 and w[30]==0xfffffffe and w[9]&2;consumed.append(dict(command=w[1],visual=w[3],epoch=w[2]))
    assert rows[-1][0]==11 and rows[-1][30]==0 and rows[-1][1]==156
    assert endframes==list(range(frames)) and tags['9']==27 and consumed==[dict(command=53,visual=3472,epoch=5517)]
    return dict(PASS=True,complete=True,rows=len(rows),bytes=len(data),SHA256=sha(p/'native-input-edge-private.bin'),tags=tags,frame_end_rows=len(endframes),terminal_tag=11,terminal_result=0,terminal_command=156,ListMenu_native_B_consumed_events=consumed,scope='New complete validation; old r4 complete=false fallback receipt untouched')
def verify(directory,identity,seed,declared_derivatives=None,candidate=False):
    p=Path(directory);log=(p/'runtime.log').read_text();lines=log.splitlines()
    result=json.loads((p/'runtime-result.json').read_text())
    assert result['exit']==0 and result['Save_unchanged'] and result['log_SHA256']==sha(p/'runtime.log')
    if candidate:assert result['PASS']
    finish=[l for l in lines if l.startswith('UI_FINISH frames=')]
    assert finish==['UI_FINISH frames=7051 full_native_BFE_EOF=1 full_frame_state_rng_targets_callbacks_EOF=1']
    assert lines[-1]=='result=0 assertions=59' and lines.count(lines[-1])==1
    assert sha(seed)==sha(p/'game.sav')==identity['Save_SHA256']
    numbered=classifier.classify(p,7051,declared_derivatives)
    np=p/('expected-native-boundary-trace.bin' if candidate else 'native-boundary-trace.bin');up=p/('expected-ui-frame-trace.bin' if candidate else 'ui-frame-trace.bin')
    native=module('completeReference',ROOT/'scripts/floor1/v01-new-input-reference.py').scan(np)
    assert native['boundaries']==6883 and native['frames']==7051 and native['typed_finish_complete']
    assert up.stat().st_size==19037700
    # Read to a checked EOF; never reinterpret/trim/normalize the strict stream.
    with up.open('rb') as f:
        for _ in range(7051):assert len(f.read(2700))==2700
        assert f.read(1)==b''
    ready=[l for l in lines if l.startswith('UI_READY ')];moves=[l for l in lines if l.startswith('UI_MOVE ')]
    assert len(ready)==27 and len(moves)==14
    expected_moves=[(0,0,8),(0,0,8),(0,1,40),(0,0,8),(0,0,8),(2,0,2),(2,1,40),(2,0,2),(0,1,39),(2,0,1),(0,1,38),(2,0,0),(2,0,0),(2,1,40)]
    assert [tuple(map(int,re.match(r'UI_MOVE actor=(\d+) cursor=(\d+) pp=(\d+)',l).groups())) for l in moves]==expected_moves
    expected_ready=[('action',0),('move',0),('target',0),('move',0),('action',0),('bag',0),('action',0),('party',0),('context',0),('summary',0),('context',0),('party',0),('action',0),('move',0),('action',2),('move',2),('action',2),('move',2),('action',0),('move',0),('action',2),('move',2),('action',0),('move',0),('action',2),('move',2),('move',2)]
    assert [(m[1],int(m[2])) for l in ready for m in [re.match(r'UI_READY (\w+) actor=(\d+)',l)]]==expected_ready
    assert lines.count('PASS flag 47 0')==2 and lines.count('PASS item 13 1')==2 and lines.count('PASS item 378 2')==2
    diag=edges(p,7051)
    return dict(PASS=True,emulator_exit=0,assertions=59,visual_frames=7051,native_reference=native,reference_stream_SHA256={np.name:sha(np),up.name:sha(up)},supplemental_bytes=19037700,supplemental_frame_bytes=2700,supplemental_EOF=True,numbered_capture_count=len(numbered),named_capture_SHA256={n:sha(p/n) for n in classifier.NAMED},numbered_capture_SHA256={f.name:sha(f) for f in numbered},UI_READY=ready,UI_MOVE=moves,complete_passive_diagnostics=diag,Save_unchanged=True,Save_SHA256=sha(p/'game.sav'),no_Save=True,scope='Corrected complete native menu artifact gates only; no legacy/original oracle/human/full-floor acceptance')
