"""Reuse twelve authoritative masters; append one native attention cleanup."""
from pathlib import Path
from PIL import Image
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def export():
    manifest={'scope':'Existing Carl nine gait frames, Donut three standing frames; one side attention cleanup, right via native horizontal flip','masters':[]}
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    for name,height,frames,path in [
        ('carl',32,['down','up','left','down-1','down-2','up-1','up-2','left-1','left-2'],'engine/graphics/object_events/pics/people/carl/walking.png'),
        ('donut',16,['down','up','left'],'engine/graphics/dcc/donut/overworld.png')]:
        atlas=Image.open(ROOT/path);palette=atlas.getpalette()
        for i,frame in enumerate(frames):
            p=ROOT/'scripts/content/masters'/f'{name}-{frame}.txt';rows=p.read_text().splitlines()
            assert len(rows)==height and all(len(row)==16 for row in rows)
            data=bytes(0 if c=='.' else int(c,16) for row in rows for c in row)
            assert atlas.crop((i*16,0,(i+1)*16,height)).tobytes()==data
            manifest['masters'].append({'path':str(p.relative_to(ROOT)),'SHA256':sha(p),'existing_atlas_exact':True})
    source=ROOT/'docs/art-references/native-battle-animation-20261007/frames/donut/attention.png'
    staged=Image.open(source);base=Image.open(ROOT/'engine/graphics/dcc/donut/overworld.png')
    assert staged.mode=='P' and staged.size==(64,64) and staged.getpalette()[:48]==base.getpalette()[:48]
    master=ROOT/'scripts/content/masters/donut-attention-left.txt';rows=master.read_text().splitlines()
    assert len(rows)==16 and all(len(row)==16 for row in rows)
    frame=Image.new('P',(16,16));frame.putpalette(base.getpalette());frame.putdata([0 if c=='.' else int(c,16) for row in rows for c in row]);frame.info['transparency']=0
    left=base.crop((32,0,48,16));assert frame.crop((0,12,16,16)).tobytes()==left.crop((0,12,16,16)).tobytes()
    assert max(frame.tobytes())<16 and frame.convert('RGBA').getbbox()==(1,2,15,15)
    # Side reference faces right. Cleanup raises the existing left head/neck,
    # preserves tortie body/tail/feet and collar jewel; engine mirrors it right.
    atlas=Image.new('P',(64,16));atlas.putpalette(base.getpalette());atlas.paste(base.crop((0,0,48,16)),(0,0));atlas.paste(frame,(48,0));atlas.save(ROOT/'engine/graphics/dcc/donut/overworld.png',bits=4,transparency=0)
    manifest['attention']={'staged_source':str(source.relative_to(ROOT)),'staged_SHA256':sha(source),'native_master':str(master.relative_to(ROOT)),'master_SHA256':sha(master),'size':[16,16],'bbox':list(frame.convert('RGBA').getbbox()),'feet_and_pivot_rows12_15_identical':True,'native_palette_unchanged':True,'single_side_pose_right_mirrored':True}
    (ROOT/'scripts/contracts/f1-v01-overworld-assets.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Verified twelve existing authoritative frames; one16x16 attention cleanup appended')
if __name__=='__main__':export()
