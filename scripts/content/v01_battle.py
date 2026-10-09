"""Copy verified native pose PNGs exactly; preserve palettes and pre-shifted Warden."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[2]
def export():
 source=ROOT/'docs/art-references/native-battle-animation-20261007'
 rows=[('carl','rest',ROOT/'engine/graphics/dcc/carl/back.png')]+[('carl',p,source/'frames/carl'/f'{p}.png') for p in ['strike-anticipation','strike-contact','strike-recovery','brace-set','brace-hold']]
 rows += [('donut','rest',ROOT/'engine/graphics/dcc/donut/back.png')]+[('donut',p,source/'frames/donut'/f'{p}.png') for p in ['spark-anticipation','spark-cast','spark-recovery','weaken-preparation','weaken-release']]
 rows += [('warden',p,source/'frames/warden'/f'{p}-runtime-lift8.png') for p in ['idle','windup','hold','slam','recovery']]
 dest=ROOT/'engine/graphics/dcc/battle-poses';dest.mkdir(exist_ok=True)
 records=[];header=[]
 for i,(ch,pose,src) in enumerate(rows):
  im=Image.open(src);assert im.mode=='P' and im.size==(64,64) and im.info.get('transparency')==0
  base=Image.open(ROOT/'engine/graphics/dcc'/ch/('front.png' if ch=='warden' else 'back.png'))
  assert im.getpalette()[:48]==base.getpalette()[:48]
  dst=dest/f'{ch}-{pose}.png';shutil.copyfile(src,dst)
  header.append(f'static const u32 sDccPose{i}[] = INCGFX_U32("graphics/dcc/battle-poses/{ch}-{pose}.png", ".4bpp");')
  records.append({'index':i,'character':ch,'pose':pose,'source':str(src.relative_to(ROOT)),'SHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'bbox':im.getbbox(),'palette_exact':True,'shift_applied':False,'already_lift8':ch=='warden'})
 header.append('static const u32 *const sDccPosePictures[] = { '+', '.join(f'sDccPose{i}' for i in range(len(rows)))+' };')
 (ROOT/'engine/src/data/dcc_battle_pose_graphics.h').write_text('\n'.join(header)+'\n')
 (ROOT/'scripts/contracts/f1-v01-battle-assets.json').write_text(json.dumps(records,indent=2)+'\n')
 print('Verified17 direct native frames; no palette edits or additional lift')
if __name__=='__main__':export()
