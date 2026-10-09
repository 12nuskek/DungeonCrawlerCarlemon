"""Wrap the unchanged environment/phase/resource observers with native OBJ checks."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[2]
def generate(git):
    path=ROOT/'scripts/floor1/v01-environment-host.py';spec=importlib.util.spec_from_file_location('character_prior',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    code,base=m.generate(git)
    assert hashlib.sha256(code.encode()).hexdigest()=='500c4bff81fd73e9d22b699812f961c63867c592aa02af94b521a529a0bb9d6b'
    marker='int main(int argc, char **argv)';assert code.count(marker)==1
    code=code.replace(marker,(ROOT/'scripts/floor1/v01-character-observer.h').read_text()+'\n'+marker)
    marker='struct V01Peak peaks[5]={0};unsigned recording=0,clipFrames=0;';assert code.count(marker)==1
    code=code.replace(marker,marker+'struct CharacterState characters={0};char clipName[64]={0};')
    marker='    if(recording){char filename[80];if(clipFrames>=1200)WALK_STOP(85);snprintf(filename,sizeof filename,"clip-%05u.ppm",clipFrames++);if(capture(filename,pixels,width,height))WALK_STOP(85);} \\\n'
    assert code.count(marker)==1
    code=code.replace(marker,r'''    unsigned characterReason=character_sample(core,scene,walkAddresses,&characters,walking.guard.frames,pixels,width,height);if(characterReason)WALK_STOP(characterReason); \
    if(recording){char filename[96];if(clipFrames>=2000)WALK_STOP(85);snprintf(filename,sizeof filename,"%s-%05u.ppm",clipName,clipFrames++);if(capture(filename,pixels,width,height))WALK_STOP(85);} \
''')
    start=code.index('        if(!strcmp(line,"record start\\n"))');end=code.index('        if(!strncmp(line,"scene ",6))',start)
    code=code[:start]+r'''
        if(!strncmp(line,"record start ",13)){
            if(recording||!characters.observing||sscanf(line,"record start %63s %c",clipName,&extra)!=1)WALK_STOP(85);
            recording=1;clipFrames=0;continue;
        }
        if(!strcmp(line,"record stop\n")){if(!recording)WALK_STOP(85);recording=0;printf("CLIP label=%s native_frames=%u rate=262144/4389\n",clipName,clipFrames);continue;}
        if(!strcmp(line,"character start\n")){
            unsigned char mode;
            if(characters.observing||!walking.armed||character_load("character-mode.bin",&mode,1)
                ||character_load("character-carl.bin",&characters.carl[0][0],2304)
                ||character_load("character-donut.bin",&characters.donut[0][0],mode?512:384)
                ||character_load("character-palettes.bin",characters.palettes,64))WALK_STOP(90);
            characters.candidate=mode;characters.observing=1;characters.lastFrame[0]=characters.lastFrame[1]=255;
            unsigned reason=character_sample(core,scene,walkAddresses,&characters,walking.guard.frames,pixels,width,height);if(reason)WALK_STOP(reason);
            checks++;continue;
        }
        if(!strncmp(line,"character talk-check ",21)){
            unsigned direction,object=0;
            if(sscanf(line,"character talk-check %u %c",&direction,&extra)!=1||direction!=characters.talkDirection)WALK_STOP(96);
            for(unsigned i=0;i<16;i++)if((core->busRead8(core,objects+36*i)&1)&&core->busRead8(core,objects+36*i+8)==5)object=objects+36*i;
            unsigned expected=characters.candidate&&(direction==3||direction==4)?24:0;
            if(!object || (core->busRead8(core,object+24)&15)!=direction || characters.talkReactions!=expected
                ||core->busRead8(core,fieldLock)||core->busRead8(core,scriptStatus)!=2)WALK_STOP(96);
            printf("CHAR_TALK direction=%u frames=%u native_reaction_frames=%u field_controls_ready=1 exact_resources=1\n",direction,characters.talkFrames,characters.talkReactions);
            characters.talkDirection=0;checks++;continue;
        }
        if(!strncmp(line,"character talk ",15)){
            unsigned direction;if(characters.talkDirection||sscanf(line,"character talk %u %c",&direction,&extra)!=1||direction<1||direction>4)WALK_STOP(96);
            characters.talkDirection=direction;characters.talkFrames=characters.talkReactions=0;continue;
        }
        if(!strcmp(line,"character finish\n")){
            if(!characters.observing||characters.talkDirection||characters.carlSeen[0]!=511
                ||(characters.carlSeen[1]&388)!=388||(characters.donutSeen[0]&7)!=7||!(characters.donutSeen[1]&4)
                ||characters.reactionFrames[0]!=(characters.candidate?24:0)||characters.reactionFrames[1]!=(characters.candidate?24:0))WALK_STOP(97);
            printf("CHAR_FINISH samples=%u carl_normal=%u carl_mirrored=%u donut_normal=%u donut_mirrored=%u reaction_west=%u reaction_east=%u\n",characters.samples,characters.carlSeen[0],characters.carlSeen[1],characters.donutSeen[0],characters.donutSeen[1],characters.reactionFrames[0],characters.reactionFrames[1]);
            characters.observing=0;checks++;continue;
        }
''' +code[end:]
    assert code.count('core->runFrame(core);')==1 and 'busWrite' not in code
    return code,base
