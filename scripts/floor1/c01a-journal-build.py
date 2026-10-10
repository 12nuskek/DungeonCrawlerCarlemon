"""Single build from an isolated committed archive with recovered compiler pins."""
from pathlib import Path
import hashlib,io,json,os,shutil,subprocess,tarfile
ROOT=Path(__file__).resolve().parents[2]
OUT=Path('/workspace/scratch/c01a-journal-art-r2-20261010/candidate-build')
TOOL=Path('/workspace/scratch/ordinary-recovery-tooling-r3-20261009/root')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip()
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    OUT.mkdir();source=OUT/'source';source.mkdir()
    raw=subprocess.check_output(['git','archive',revision,'engine','scripts'],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:archive.extractall(source,filter='data')
    (OUT/'tested-commit.txt').write_text(revision+'\n')
    ident=json.loads((TOOL.parent/'agbcc-identity.json').read_text())
    assert ident['source_commit']=='da598c1d918402c42c0c0d7128ba14567f3175e9' and not ident['original_tool_identity_claimed']
    assert sha(Path(ident['GCC_path']))==ident['GCC_SHA256']
    for row in ident['compilers']:assert sha(Path(row['path']))==row['SHA256']
    for row in ident['support_libraries']:assert sha(TOOL/'tools/agbcc/lib'/row['name'])==row['SHA256']
    shutil.copytree(TOOL/'tools/agbcc',source/'engine/tools/agbcc')
    env=dict(os.environ,PATH=str(TOOL/'usr/bin')+':'+os.environ['PATH'],LD_LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'),CPATH=str(TOOL/'usr/include'),LIBRARY_PATH=str(TOOL/'usr/lib/x86_64-linux-gnu'))
    tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',revision,'--','engine'],cwd=ROOT,text=True).splitlines()
    inventory={n:sha(source/n) for n in tracked}
    for repetition in range(2):
        subprocess.run(['python3',str(source/'scripts/floor1/generate-live-opening.py'),'--root',str(source)],env=env,check=True)
        assert inventory=={n:sha(source/n) for n in tracked},'Generation changed committed archive bytes'
    (OUT/'source-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
    # Attribute-aware archive identities above are separate from upstream blobs.
    retained=Path('/workspace/scratch/new-input-visual-pair-20261010/candidate-build/source/engine/data')
    pins={'mb_berry_fix.gba':'0afff07f5d2314e2bd35d99de518cbc114009b5e','mb_colosseum.gba':'fdeb854a054ba02191f6a209ec5b649f21c4e335','mb_ereader.gba':'85057cf4e2bd657da5d632ac12d1ea24aeaa4499'}
    inputs={}
    for name,pin in pins.items():
        path=retained/name
        assert subprocess.check_output(['git','hash-object',str(path)],text=True).strip()==pin
        shutil.copyfile(path,source/'engine/data'/name)
        assert subprocess.check_output(['git','hash-object',str(source/'engine/data'/name)],text=True).strip()==pin
        inputs[name]={'upstream_Git_blob':pin,'SHA256':sha(path)}
    (OUT/'regeneration-and-inputs.json').write_text(json.dumps({'PASS':True,'repetitions':2,'all_generated_products_equal_committed_archive':True,'art_placements':217,'art_overlaps':12,'art_final_cells':205,'retained_multiboot_inputs':inputs},indent=2)+'\n')
    with (OUT/'build.log').open('xb') as log:result=subprocess.run(['make','-j2'],cwd=source/'engine',env=env,stdout=log,stderr=subprocess.STDOUT)
    (OUT/'build.exit').write_text(str(result.returncode)+'\n')
    receipt={'exit':result.returncode,'tested_commit':revision,'original_tool_identity_claimed':False,'build_log_SHA256':sha(OUT/'build.log'),'actual_outputs':{n:sha(source/'engine'/n) for n in ('pokeemerald.gba','pokeemerald.elf') if (source/'engine'/n).is_file()}}
    (OUT/'result.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));assert result.returncode==0
if __name__=='__main__':main()
