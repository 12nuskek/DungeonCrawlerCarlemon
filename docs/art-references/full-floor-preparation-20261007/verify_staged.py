"""Validate this reference package only; does not build or test the game."""
from pathlib import Path
from PIL import Image, ImageChops
import hashlib,json,re
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_text())
rows=manifest['files'];expected={r['path'] for r in rows}|{'manifest.json'}
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert actual==expected,(actual-expected,expected-actual)
checks=pngs=0
for row in rows:
 p=root/row['path'];b=p.read_bytes()
 assert len(b)==row['bytes'];assert hashlib.sha256(b).hexdigest()==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob_sha'];checks+=3
 if p.suffix=='.png':
  assert b[:8]==b'\x89PNG\r\n\x1a\n';Image.open(p).verify();im=Image.open(p);im.load()
  assert list(im.size)==row['dimensions'] and im.mode==row['mode'];checks+=3;pngs+=1
 else:
  s=b.decode('utf-8')
  assert not re.search(r'lib' + r'file_[a-zA-Z0-9]+|/work' + r'space/|file_[0-9a-f]{20,}|chatgpt[.]com/space/page_',s);checks+=1
 assert p.suffix not in {'.gba','.sav','.4bpp','.zip','.b64','.exe'};checks+=1
for row in json.loads((root/'source-identities.json').read_text()):
 b=(root/row['file']).read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob_sha'];checks+=1
stitch=Image.open(root/'district-stitch-pilot/d1-d2-stitched-proof-v1.png').convert('RGB')
for fn,xy in [('d2-sluice-district-v1.png',(64,72)),('d1-opening-district-v2.png',(64,1096))]:
 im=Image.open(root/'district-stitch-pilot'/fn).convert('RGB');x,y=xy
 assert ImageChops.difference(im,stitch.crop((x,y,x+im.width,y+im.height))).getbbox() is None;checks+=1
print(json.dumps({'status':'PASS','payload_files':len(rows),'pngs':pngs,'source_identities':8,'exact_stitch_panels':2,'checks':checks,'runtime_verified':False},sort_keys=True))
