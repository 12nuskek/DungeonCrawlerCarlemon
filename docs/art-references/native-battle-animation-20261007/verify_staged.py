#!/usr/bin/env python3
"""Verify committed package bytes and decoded native pixel identities; no runtime claim."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
M=json.loads((R/'package-inventory.json').read_text());checks=0
for f in M['files']:
 p=R/f['path'];b=p.read_bytes()
 assert len(b)==f['bytes'];checks+=1
 assert hashlib.sha256(b).hexdigest()==f['sha256'];checks+=1
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob_sha'];checks+=1
 if 'decoded_rgba_sha256' in f:
  im=Image.open(p);assert list(im.size)==f['dimensions'] and im.mode==f['mode'];checks+=1
  assert hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()==f['decoded_rgba_sha256'];checks+=1
for f in M['existing_inputs']:
 p=R/f['relative_path'];b=p.read_bytes()
 assert hashlib.sha256(b).hexdigest()==f['sha256'];checks+=1
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['git_blob_sha'];checks+=1
print(json.dumps({'status':'PASS','checks':checks,'new_files':len(M['files'])+1,'native_pngs':24,'existing_inputs':len(M['existing_inputs']),'emulator_verified':False}))
