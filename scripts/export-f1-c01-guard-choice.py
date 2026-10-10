#!/usr/bin/env python3
"""One bounded lossy review export; raw RGB stays the lossless authority."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,struct,subprocess
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
OUTPUT=Path('/workspace/scratch/c01-guard-choice-r1-20261010')
PUBLIC=ROOT/'docs/evidence/floor1/c01/guard-choice-r1-20261010'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(1024**2),b''):h.update(block)
    return h.hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('opening','cold'),required=True);a=parser.parse_args()
    freeze=json.loads((OUTPUT/'freeze.json').read_text());d=OUTPUT/a.mode
    assert (OUTPUT/'STOP.json').exists() or (OUTPUT/f'{a.mode}-verdict-private.json').exists()
    for p,h in freeze['tool_files'].items():assert sha(Path(p))==h
    export=d/'review-export';export.mkdir() # No second attempt to this export.
    frames=(d/'frame-index.bin').stat().st_size//16;assert frames>0 and (d/'frame-index.bin').stat().st_size==frames*16
    chunks=sorted(d.glob('motion-*.rgb'));assert sum(p.stat().st_size for p in chunks)==frames*115200
    capture_frames={name:int(frame) for name,frame in re.findall(r'CAPTURE name=(\S+) absolute=(\d+) width=240 height=160',(d/'runtime.log').read_text())}
    screenshots={}
    for ppm in sorted(d.glob('*.ppm')):
        assert ppm.name in capture_frames
        frame=capture_frames[ppm.name];assert 1<=frame<=frames
        chunk=chunks[(frame-1)//2000]
        with chunk.open('rb') as f:f.seek(((frame-1)%2000)*115200);native=f.read(115200)
        with Image.open(ppm) as im:
            assert im.size==(240,160) and im.convert('RGB').tobytes()==native
            png=export/(ppm.stem+'.png');im.save(png)
        with Image.open(png) as im:assert im.convert('RGB').tobytes()==native
        screenshots[png.name]={'absolute_native_frame':frame,'SHA256':sha(png),'indexed_RGB_exact':True}
    mp4=export/'native-review.mp4';cap=(16 if a.mode=='opening' else 8)*1024**2
    cmd=['ffmpeg','-nostdin','-v','error','-f','rawvideo','-pixel_format','rgb24','-video_size','240x160',
      '-framerate','16777216/280896','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',
      '-fs',str(cap),'-movflags','+faststart',str(mp4)]
    with (export/'encoder-errors.log').open('wb') as err:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
        try:
            for chunk in chunks:
                with chunk.open('rb') as f:
                    for block in iter(lambda:f.read(1024**2),b''):process.stdin.write(block)
            process.stdin.close();code=process.wait(timeout=600)
        except BaseException:
            process.terminate();process.wait();raise
    assert code==0 and not (export/'encoder-errors.log').stat().st_size and mp4.stat().st_size<cap
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
      '-show_entries','stream=nb_read_frames,r_frame_rate,width,height,duration','-of','json',str(mp4)]))['streams'][0]
    assert int(probe['nb_read_frames'])==frames and probe['r_frame_rate']=='262144/4389' and (probe['width'],probe['height'])==(240,160)
    public=PUBLIC/a.mode;public.mkdir(parents=True)
    for png in export.glob('*.png'):shutil.copyfile(png,public/png.name)
    shutil.copyfile(mp4,public/'native-review.mp4')
    result={'actual_native_frames':frames,'raw_RGB_bytes':frames*115200,'review_MP4':{'SHA256':sha(mp4),'bytes':mp4.stat().st_size,'all_frames':True,'lossy':True,'probe':probe},
      'screenshots':screenshots,'second_lossless_container':False,'tested_source_commit':freeze['helper_commit'],'compiled_game':freeze['compiled_game'],
      'ROM_SHA256':freeze['ROM_SHA256'],'ELF_SHA256':freeze['ELF_SHA256'],'independent_backup_verified':False}
    (export/'actual-export-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (public/'actual-export-receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'frames':frames,'screenshots':len(screenshots),'MP4_bytes':mp4.stat().st_size,'source':freeze['helper_commit']}))
if __name__=='__main__':main()
