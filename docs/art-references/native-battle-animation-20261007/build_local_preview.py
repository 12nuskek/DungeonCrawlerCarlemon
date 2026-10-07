from pathlib import Path
import json,base64
R=Path(__file__).resolve().parent
T=json.loads((R/'timing-proposal.json').read_text());M=json.loads((R/'manifest.json').read_text());assets={}
for ch,v in M['characters'].items():
 for f in v['frames']:
  for variant,p in [('source',f['path']),('lift8',f.get('runtime_lift8_path'))]:
   if p:assets[ch+'/'+f['name']+'/'+variant]='data:image/png;base64,'+base64.b64encode((R/p).read_bytes()).decode()
html='''<!doctype html><meta charset="utf-8"><title>Native keypose candidate preview</title><style>body{background:#262b34;color:#eaeae4;font:16px system-ui;padding:24px;max-width:900px}select,button{font:inherit;margin:8px;padding:8px}#views{display:flex;gap:24px;align-items:flex-end;margin:20px 0}.cell{background:repeating-conic-gradient(#424851 0% 25%,#373d45 0% 50%) 0 0/32px 32px;image-rendering:pixelated}#small{width:64px;height:64px}#large{width:256px;height:256px}.notice{color:#d7b779}</style><h1>Native keypose candidates</h1><p class="notice">Local art preview only. No GBA emulation, engine animation, hit timing or HUD acceptance. Warden actions are shown separately; looping WIND UP does not represent its in-game turn behavior.</p><label>Sequence <select id="seq"></select></label><label><input id="lift" type="checkbox"> Warden prospective lift 8px</label><button id="pause">Pause</button><div id="views"><div><img class="cell" id="small"><p>Native 1x</p></div><div><img class="cell" id="large"><p>Nearest-neighbor 4x</p></div></div><p id="label"></p><p>All source poses share the same per-character palette. Source feet end at y61; prospective Warden feet end at y53. No in-between poses are fabricated.</p><script>const timing=TIMING,assets=ASSETS;let paused=false,start=performance.now(),last='';const seq=document.querySelector('#seq');Object.keys(timing.sequences).forEach(k=>seq.add(new Option(k,k)));seq.onchange=()=>{start=performance.now()};document.querySelector('#pause').onclick=e=>{paused=!paused;e.target.textContent=paused?'Play':'Pause';start=performance.now()};function draw(now){if(!paused){const frames=timing.sequences[seq.value],total=frames.reduce((s,f)=>s+f.frames,0);let t=((now-start)*60/1000)%total,frame=frames[0];for(const f of frames){frame=f;if(t<f.frames)break;t-=f.frames}let variant=frame.character==='warden'&&document.querySelector('#lift').checked?'lift8':'source',key=frame.character+'/'+frame.pose+'/'+variant;if(key!==last){last=key;document.querySelector('#small').src=document.querySelector('#large').src=assets[key]}document.querySelector('#label').textContent=frame.character+' / '+frame.pose+' / '+frame.frames+' frame hold ('+Math.round(frame.frames*1000/60)+'ms) / '+variant}requestAnimationFrame(draw)}requestAnimationFrame(draw)</script>'''
html=html.replace('TIMING',json.dumps(T)).replace('ASSETS',json.dumps(assets))
(R/'review/local-preview.html').write_text(html)
# Animated local preview GIFs are convenience files, not native graphics.
from PIL import Image,ImageDraw
for key,seq in T['sequences'].items():
 frames=[];durations=[]
 for f in seq:
  rgba=Image.open(R/'frames'/f['character']/(f['pose']+'.png')).convert('RGBA').resize((256,256),Image.Resampling.NEAREST)
  canvas=Image.new('RGB',(288,328),(55,61,69));canvas.paste(rgba,(16,42),rgba);d=ImageDraw.Draw(canvas);d.text((10,8),key,fill=(240,240,235));d.text((10,24),f['pose'],fill=(180,192,204));d.text((10,307),'LOCAL ART PREVIEW, NOT EMULATOR',fill=(220,190,145));frames.append(canvas);durations.append(round(f['frames']*1000/60))
 frames[0].save(R/'review'/(key+'-local-preview.gif'),save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2)
print('Wrote portable local preview and six timing GIFs.')
