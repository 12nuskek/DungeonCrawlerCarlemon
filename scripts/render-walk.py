#!/usr/bin/env python3
"""Package actual GBA framebuffers as a real-time 30fps GIF; never fabricate frames.

Input was captured every emulated frame. Keep every second frame, preserve total
59.7275Hz duration using GIF centisecond timing, and use a shared source palette.
"""
from pathlib import Path
from PIL import Image
import sys, hashlib, json
root=Path(sys.argv[1]);output=Path(sys.argv[2])
paths=sorted(root.glob('walk-*.ppm'))
assert paths and all(p.name==f'walk-{i:04d}.ppm' for i,p in enumerate(paths))
frames=[Image.open(p).convert('RGB') for p in paths[::2]]
colors=set()
for frame in frames:
    assert frame.size==(240,160)
    items=frame.getcolors(256)
    assert items is not None, 'Unexpected palette complexity; review before quantizing'
    colors.update(color for count,color in items)
assert len(colors)<=256, 'GIF must preserve all source colors'
palette=Image.new('P',(1,1));palette.putpalette(sum((list(c) for c in sorted(colors)),[])+[0]*(768-len(colors)*3))
indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
ends=[round(min(i*2,len(paths))*100/59.7275)*10 for i in range(len(frames)+1)]
ends[-1]=round(len(paths)*100/59.7275)*10
durations=[b-a for a,b in zip(ends,ends[1:])]
indexed[0].save(output,save_all=True,append_images=indexed[1:],duration=durations,loop=0,optimize=False,disposal=2)
metadata={'source_frames':len(paths),'source_hz':59.7275,'source_seconds':len(paths)/59.7275,'gif_duration_ms':sum(durations),'colors':len(colors),'format':'actual 240x160 emulator framebuffers; every second frame; no interpolation','source_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]}
output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
print(json.dumps({k:v for k,v in metadata.items() if k!='source_sha256'}))
