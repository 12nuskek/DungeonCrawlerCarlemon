#!/usr/bin/env python3
"""Verify exported enemy contracts and byte ownership before building I01."""
from pathlib import Path
from PIL import Image
import hashlib,json,subprocess,sys
root=Path(sys.argv[1]);source=root/'docs/art-references/opponent-native-candidates'
assert (root/'engine/graphics/dcc/shared.pal').read_bytes()==(source/'source/existing-shared.pal').read_bytes()
checked=[]
for src in sorted((source/'assets').glob('*/*')):
 dst=root/'engine/graphics/dcc'/src.relative_to(source/'assets')
 assert dst.read_bytes()==src.read_bytes(),str(dst)
 if src.suffix=='.png':
  im=Image.open(dst);assert im.mode=='P' and im.info.get('transparency')==0
  assert dst.read_bytes()[24]==4 and max(im.getdata())<16
 checked.append({'file':str(dst.relative_to(root)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
assert len(checked)==34
assert not (root/'engine/graphics/dcc/grub/overworld.png').exists()
print(json.dumps({'verified_native_files':checked,'shared_palette_unchanged':True},indent=2))
