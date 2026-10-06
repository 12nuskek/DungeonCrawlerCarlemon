#!/usr/bin/env python3
"""Package the verified N05 production copy; never upload or publish anything."""
import argparse,base64,hashlib,json,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--production-rom',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[1];m=json.loads((root/'docs/review/manifest.json').read_text());digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(a.production_rom)==m['production_sha256'], 'Wrong ROM: require accepted immutable production copy'
assert not a.output.exists(), 'Preserve existing packages; choose a new output path'
subprocess.run(['git','diff','--exit-code',m['tested_commit'],'--','engine'],cwd=root,check=True,stdout=subprocess.DEVNULL)
page=(root/'docs/review/index.html').read_text();embedded=re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)',page)
frames=[f for c in m['cards'] for f in c['frames']];assert len(embedded)==len(frames)==22
for f,b in zip(frames,embedded):
 assert digest(root/f['path'])==f['sha256']
 assert base64.b64decode(b)==(root/f['path']).read_bytes()
assert not re.search(r'<(?:script|iframe)\b|<img[^>]+src="https?://',page,re.I), 'Review must remain offline'
a.output.parent.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='dcc-package-',dir=a.output.parent) as temp:
 d=Path(temp)
 copies={'docs/review/index.html':'REVIEW.html','docs/review/manifest.json':'CAPTURE-MANIFEST.json','docs/review/BUILD-AND-PLAY.md':'BUILD-AND-PLAY.md','docs/playtest.md':'PLAYTEST.md','docs/upstream/provenance.md':'PROVENANCE.md','docs/content-ledger.md':'CONTENT-LEDGER.md','docs/testing.md':'testing.md'}
 for src,dest in copies.items():shutil.copyfile(root/src,d/dest)
 shutil.copyfile(a.production_rom,d/'DungeonCrawlerCarlemon-N05.gba')
 shutil.copytree(root/'docs/evidence/n05',d/'evidence/n05')
 files=sorted(x for x in d.rglob('*') if x.is_file());assert sum(x.suffix=='.gba' for x in files)==1
 assert not any(x.suffix in ['.sav','.elf','.ppm','.ss0'] for x in files)
 (d/'SHA256SUMS').write_text(''.join(f'{digest(x)}  {x.relative_to(d).as_posix()}\n' for x in files))
 files=sorted(x for x in d.rglob('*') if x.is_file())
 with zipfile.ZipFile(a.output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for f in files:
   info=zipfile.ZipInfo(f.relative_to(d).as_posix(),date_time=(2026,10,6,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;z.writestr(info,f.read_bytes())
with zipfile.ZipFile(a.output) as z:
 assert z.testzip() is None
 assert hashlib.sha256(z.read('DungeonCrawlerCarlemon-N05.gba')).hexdigest()==m['production_sha256']
 for line in z.read('SHA256SUMS').decode().splitlines():
  expected,path=line.split('  ',1);assert hashlib.sha256(z.read(path)).hexdigest()==expected
report={'package':a.output.name,'bytes':a.output.stat().st_size,'sha256':digest(a.output),'production_sha256':m['production_sha256'],'tested_commit':m['tested_commit'],'entries':len(z.namelist()),'actual_capture_count':len(frames),'zip_crc':'PASS','entry_sha256':'PASS','no_saves_or_diagnostic_roms':True}
assert report['bytes']<50*1024*1024
print(json.dumps(report,indent=2))
