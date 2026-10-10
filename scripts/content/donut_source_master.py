"""Derive/rebuild a local source master from pinned native indexed PNGs.

Serialization only: no generated concept, drawing, resampling, recoloring,
integrated asset write or upload. Output is always a separate directory.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
SOURCE='a86ceca9a3e642e87d3319e7072d35fd9adea21a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def native_palette(path):
    rows=Path(path).read_text().splitlines();assert rows[:2]==['JASC-PAL','0100'] and int(rows[2])==16
    return [v for line in rows[3:] for v in map(int,line.split())]
def derive(output):
    output=output.resolve();assert not output.exists(),'Keep every derived checkpoint distinct'
    assert ROOT/'engine' not in [output,*output.parents],'Do not write integrated assets';output.mkdir(parents=True)
    sources=[ROOT/'engine/graphics/dcc/donut'/name for name in ['front.png','back.png','anim_front.png','icon.png','overworld.png']]
    poses=json.loads((ROOT/'scripts/contracts/f1-v01-battle-assets.json').read_text())
    sources += [ROOT/r['source'] for r in poses if r['character']=='donut' and r['pose']!='rest']
    assert len(sources)==10 and len(set(sources))==10
    palette_path=ROOT/'engine/graphics/dcc/donut/normal.pal';palette=native_palette(palette_path);assert len(palette)==48
    palette_blob=subprocess.check_output(['git','show',SOURCE+':'+str(palette_path.relative_to(ROOT))],cwd=ROOT)
    assert palette_blob.replace(b'\r\n',b'\n')==palette_path.read_bytes().replace(b'\r\n',b'\n'),'Palette text changed beyond declared CRLF checkout normalization'
    records=[]
    for i,p in enumerate(sources):
        relative=str(p.relative_to(ROOT));frozen=subprocess.check_output(['git','show',SOURCE+':'+relative],cwd=ROOT)
        assert hashlib.sha256(frozen).hexdigest()==sha(p),'Native source changed since pinned checkpoint'
        pose=next((r for r in poses if r['source']==relative),None)
        if pose:assert pose['SHA256']==sha(p) and pose['palette_exact']
        im=Image.open(p);assert im.mode=='P' and im.getpalette()==palette and im.info.get('transparency')==0 and im.getextrema()[1]<16
        stem=f'{i:02d}-'+p.stem;pixels=im.tobytes();rows=[]
        for y in range(im.height):rows.append(''.join('.' if v==0 else format(v,'x') for v in pixels[y*im.width:(y+1)*im.width]))
        text=output/(stem+'.txt');text.write_text('\n'.join(rows)+'\n')
        records.append({'name':stem,'native_source':relative,'native_source_SHA256':sha(p),'master':text.name,'master_SHA256':sha(text),'size':list(im.size),'mode':'P','transparency':0,'indexed_pixels_SHA256':hashlib.sha256(pixels).hexdigest(),'palette_SHA256':hashlib.sha256(bytes(palette)).hexdigest(),'native_asset_manifest_verified':bool(pose),'source_commit_blob_verified':True})
    (output/'palette.json').write_text(json.dumps({'native_source':str(palette_path.relative_to(ROOT)),'native_source_SHA256':sha(palette_path),'git_blob_SHA256':hashlib.sha256(palette_blob).hexdigest(),'checkout_eol':'CRLF by .gitattributes; pinned Git blob LF; RGB values identical','RGB':palette,'transparency_index':0},indent=2)+'\n')
    manifest={'kind':'Derived indexed-pixel source master; not original illustration or new approved art','source_commit':SOURCE,'source_engine_tree':subprocess.check_output(['git','rev-parse',SOURCE+':engine'],cwd=ROOT,text=True).strip(),'recipe':'Each original P-mode pixel becomes dot for index0 or lowercase hex1-f. Rebuild directly with original48 RGB palette bytes, PNG bits4/transparency0; no pixel conversion or color matching.','palette':'palette.json','recipe_script':'scripts/content/donut_source_master.py','recipe_SHA256':sha(__file__),'native_images':records,'integrated_assets_changed':False,'runtime_evidence':'No new runtime evidence. Existing battle candidate stopped before poses; assets remain unverified in gameplay.','public_upload':False}
    (output/'master.json').write_text(json.dumps(manifest,indent=2)+'\n');return manifest
def rebuild(master,output):
    master=master.resolve();output=output.resolve();assert not output.exists(),'Keep original native/master files intact'
    assert ROOT/'engine' not in [output,*output.parents],'Do not write integrated assets';output.mkdir(parents=True)
    manifest=json.loads((master/'master.json').read_text());palette=json.loads((master/manifest['palette']).read_text());rgb=palette['RGB'];assert len(rgb)==48
    records=[]
    for r in manifest['native_images']:
        p=master/r['master'];assert sha(p)==r['master_SHA256'];rows=p.read_text().splitlines();w,h=r['size'];assert len(rows)==h and all(len(row)==w for row in rows)
        pixels=bytes(0 if c=='.' else int(c,16) for row in rows for c in row);assert max(pixels)<16 and hashlib.sha256(pixels).hexdigest()==r['indexed_pixels_SHA256']
        im=Image.new('P',(w,h));im.putpalette(rgb);im.putdata(pixels);destination=output/(r['name']+'.png');im.save(destination,bits=4,transparency=0)
        assert sha(ROOT/r['native_source'])==r['native_source_SHA256'],'Pinned native source changed'
        restored=Image.open(destination);original=Image.open(ROOT/r['native_source'])
        assert restored.size==original.size and restored.mode=='P' and restored.tobytes()==original.tobytes()
        assert restored.getpalette()==original.getpalette()==rgb and restored.info['transparency']==original.info['transparency']==0
        assert restored.convert('RGBA').tobytes()==original.convert('RGBA').tobytes()
        records.append({'source':r['native_source'],'source_SHA256':r['native_source_SHA256'],'reconstructed_png_SHA256':sha(destination),'indexed_pixels_exact':True,'full_palette_bytes_exact':True,'transparency_exact':True,'RGBA_pixels_exact':True,'PNG_file_bytes_equal':sha(destination)==sha(ROOT/r['native_source'])})
    result={'result':'PASS derived master native pixel/full palette/transparency/RGBA roundtrip','images':records,'images_count':len(records),'emulator_frames':0,'integrated_assets_changed':False,'PNG_encoding_note':'PNG file compression/metadata may differ; decoded indexed pixels, full48 palette bytes and transparency must be exact.'}
    (output/'roundtrip.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'result':result['result'],'images':len(records),'emulator_frames':0,'integrated_assets_changed':False}));return result
def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='command',required=True)
    d=s.add_parser('derive');d.add_argument('--output',type=Path,required=True)
    r=s.add_parser('rebuild');r.add_argument('--master',type=Path,required=True);r.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.command=='derive':derive(a.output)
    else:rebuild(a.master,a.output)
if __name__=='__main__':main()
