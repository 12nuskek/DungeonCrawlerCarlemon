"""Separate noncombat phase-aware route; immutable historical host/gates retained."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    s=importlib.util.spec_from_file_location('v01_prior',ROOT/'scripts/floor1/prepared-cold-phase-host.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
    code,base=m.generate(git)
    # New authorised scene domain includes Field/Quiet/Workshop; historical guards
    # remain byte-identical files. Full exact state/phase/boundary gates are retained.
    assert code.count('(current.map!=3 && current.map!=4)')==1
    assert code.count('(s->map!=3 && s->map!=4)')==1
    code=code.replace('(current.map!=3 && current.map!=4)','current.map>4')
    code=code.replace('(s->map!=3 && s->map!=4)','s->map>4')
    code=code.replace('int main(int argc, char **argv)',(ROOT/'scripts/floor1/v01-scene-observer.h').read_text()+'\nint main(int argc, char **argv)')
    code=code.replace('    FILE *symbols=fopen(argv[3], "r");','    struct V01Addresses scene={0};struct V01Peak peaks[5]={0};unsigned recording=0,clipFrames=0;\n    FILE *symbols=fopen(argv[3], "r");')
    bindings={'gSprites':'sprites','sSpriteTileAllocBitmap':'tiles','sSpritePaletteTags':'palettes','sHeapStart':'heapStart','sHeapSize':'heapSize','gBackupMapLayout':'layout'}
    point='        if (!strcmp(symbol,"gMapGroups")) mapgroups=addr;'
    assert code.count(point)==1
    code=code.replace(point,point+'\n'+''.join(f'        if (!strcmp(symbol,"{name}")) scene.{field}=addr;\n' for name,field in bindings.items()))
    point='    unsigned walkReason=walk_frame_check(core,&walking,walkAddresses,walking.guard.frames);if(walkReason) WALK_STOP(walkReason); \\\n'
    assert code.count(point)==1
    code=code.replace(point,point+r'''    unsigned sceneReason=v01_sample(core,scene,walkAddresses,peaks);if(sceneReason) WALK_STOP(sceneReason); \
    if(recording){char filename[80];if(clipFrames>=1200)WALK_STOP(85);snprintf(filename,sizeof filename,"clip-%05u.ppm",clipFrames++);if(capture(filename,pixels,width,height))WALK_STOP(85);} \
''')
    point='    while (fgets(line,sizeof(line),stdin)) {'
    assert code.count(point)==1
    code=code.replace(point,point+r'''
        if(!scene.sprites||!scene.tiles||!scene.palettes||!scene.heapStart||!scene.heapSize||!scene.layout)WALK_STOP(86);
        if(!strcmp(line,"record start\n")){if(recording||clipFrames||!walking.armed)WALK_STOP(85);recording=1;continue;}
        if(!strcmp(line,"record stop\n")){if(!recording)WALK_STOP(85);recording=0;printf("CLIP native_frames=%u rate=262144/4389\n",clipFrames);continue;}
        if(!strncmp(line,"scene ",6)){
            char label[64];if(sscanf(line,"scene %63s %c",label,&extra)!=1)WALK_STOP(80);
            unsigned reason=walk_stable_check(core,&walking,walkAddresses,walking.guard.frames);if(reason)WALK_STOP(reason);
            reason=v01_scene(core,scene,walkAddresses,label);if(reason)WALK_STOP(reason);checks+=3;continue;
        }
''')
    point='    if (ferror(stdin)) result=15;'
    assert code.count(point)==1
    code=code.replace(point,r'''    for(unsigned i=0;i<5;i++)printf("SCENE_PEAK map=%u samples=%u objects=%u sprites=%u obj_tiles=%u obj_palettes=%u heap_used=%u heap_free_min=%u\n",i,peaks[i].samples,peaks[i].objects,peaks[i].sprites,peaks[i].objTiles,peaks[i].objPalettes,peaks[i].heapUsed,peaks[i].heapFreeMin);
'''+point)
    assert 'busWrite' not in code and code.count('core->runFrame(core);')==1
    return code,base
