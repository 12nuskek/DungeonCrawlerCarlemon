"""Exact immutable-base/art projection for only three accepted map binaries."""
from pathlib import Path
import hashlib,json,struct,subprocess
BASE='ce43420b1c76210f0fa4aaee18c0e195b9354b2d'
MAPS={'field':'DCC_F1D1Field','quiet':'DCC_F1D1Quiet','workshop':'DCC_F1D1Workshop'}
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root)
def verify(root):
    head=git(root,'rev-parse','HEAD').decode().strip()
    def tree(rev):
        result={}
        for line in git(root,'ls-tree','-r','-t',rev,'--','engine/data/layouts').decode().splitlines():
            metadata,path=line.split('\t');mode,kind,oid=metadata.split()
            if path in ('engine','engine/data','engine/data/layouts'):continue
            assert kind in ('blob','tree');result[path]=(mode,kind,oid)
        return result
    old,new=tree(BASE),tree(head);assert len(old)==len(new)==1358 and old.keys()==new.keys()
    paths={k:'engine/data/layouts/'+n+'/map.bin' for k,n in MAPS.items()}
    assert all(old[p][:2]==new[p][:2] for p in old)
    differences={p for p in old if old[p][1]=='blob' and old[p]!=new[p]};assert differences==set(paths.values())
    directory_differences={p for p in old if old[p][1]=='tree' and old[p]!=new[p]}
    assert directory_differences=={str(Path(p).parent) for p in paths.values()}
    manifest=json.loads((root/'scripts/contracts/f1-v01-environment-assets.json').read_text())
    spec=json.loads((root/'scripts/contracts/f1-g01d-relocation.json').read_text())
    attrs=(root/'engine/data/tilesets/secondary/dcc/metatile_attributes.bin').read_bytes()
    oldattrs=git(root,'show',BASE+':engine/data/tilesets/secondary/dcc/metatile_attributes.bin')
    assert attrs[:len(oldattrs)]==oldattrs
    proofs=[];total=0;unique=0
    for key,path in paths.items():
        base=git(root,'show',BASE+':'+path);current=git(root,'show',head+':'+path);edited=bytearray(base);projection=bytearray(current);positions=set()
        assert (root/path).read_bytes()==current and old[path][0]==new[path][0]
        for change in manifest['changes']:
            if change['map']!=key:continue
            offset=2*(change['y']*spec['maps'][key]['width']+change['x'])
            before=struct.unpack_from('<H',base,offset)[0];assert before==change['before']
            assert before&0xfc00==change['after']&0xfc00
            attribute=lambda word:struct.unpack_from('<H',attrs,2*((word&0x3ff)-512))[0]
            assert attribute(before)==attribute(change['after'])
            struct.pack_into('<H',edited,offset,change['after'])
            struct.pack_into('<H',projection,offset,before);positions.add(offset);total+=1
        assert bytes(edited)==current and bytes(projection)==base
        unique+=len(positions);proofs.append({'path':path,'final_cells':len(positions),'manifest_final_SHA256':hashlib.sha256(edited).hexdigest(),'immutable_base_projection_exact':True})
    assert (total,unique,total-unique)==(217,205,12)
    for p in ('engine/src/crawler.c','engine/src/crawler_save.c','engine/src/data/dcc_opening.h','engine/include/global.h'):
        assert git(root,'show',BASE+':'+p)==git(root,'show',head+':'+p)==(root/p).read_bytes(),p
    return {'PASS':True,'historical_and_current_entries':1358,'identical_paths_no_deletions':True,'only_three_exact_manifest_differences':proofs,'placements':total,'final_cells':unique,'intentional_overlaps':12,'all_other_layout_and_crawler_source_bytes_identical':True}
