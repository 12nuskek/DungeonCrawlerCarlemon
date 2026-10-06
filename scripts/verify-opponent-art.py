#!/usr/bin/env python3
"""Verify exported enemy contracts and byte ownership before building I01."""
from pathlib import Path
from PIL import Image
import hashlib,json,sys
import numpy as np
root=Path(sys.argv[1]);source=root/'docs/art-references/opponent-native-candidates'
assert (root/'engine/graphics/dcc/shared.pal').read_text()==(source/'source/existing-shared.pal').read_text()
checked=[]
for src in sorted((source/'assets').glob('*/*')):
 dst=root/'engine/graphics/dcc'/src.relative_to(source/'assets')
 # Upstream engine/.gitattributes exports .pal with CRLF; colors/order stay exact.
 if src.name in ('front.png','back.png','anim_front.png'):
  a=Image.open(src);b=Image.open(dst);assert a.size==b.size and a.getpalette()==b.getpalette()
  aa=np.asarray(a);bb=np.asarray(b)
  for top in range(0,a.height,64):
   assert not aa[top:top+8].any()
   assert np.array_equal(aa[top+8:top+64],bb[top:top+56])
   assert not bb[top+56:top+64].any()
 else:
  assert (dst.read_text()==src.read_text() if src.suffix=='.pal' else dst.read_bytes()==src.read_bytes()),str(dst)
 if src.suffix=='.png':
  im=Image.open(dst);assert im.mode=='P' and im.info.get('transparency')==0
  assert dst.read_bytes()[24]==4 and im.getextrema()[1]<16
 checked.append({'file':str(dst.relative_to(root)),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
assert len(checked)==34
assert not (root/'engine/graphics/dcc/grub/overworld.png').exists()
print(json.dumps({'verified_native_files':checked,'shared_palette_unchanged':True},indent=2))
