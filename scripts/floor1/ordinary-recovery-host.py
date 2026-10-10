"""New ordinary recovery adapter; historical generators and gates stay intact."""
from pathlib import Path
import importlib.util


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def generate(git, source):
    code, base = module('ordinary_prior', source / 'scripts/floor1/guard-first-host.py').generate(git)

    def once(old, new):
        nonlocal code
        assert code.count(old) == 1, ('ordinary anchor', old[:80], code.count(old))
        code = code.replace(old, new)

    # The main archive supplies the native friendship source, not PR114's poses.
    once('python3 /workspace/DungeonCrawlerCarlemon/scripts/floor1/guard-first-state.py %s',
         'python3 ' + str(source / 'scripts/floor1/guard-first-state.py') + ' %s')
    point = 'static unsigned patrol_frame(struct mCore*c,struct PatrolGuard*g,struct PatrolAddresses a)'
    once(point, 'static unsigned ordinary_initial,ordinary_trial,ordinary_battle_was;\n' + point)
    point = 'int main(int argc, char **argv)'
    # One passive RGB sample per four actual frames. No capture advances time.
    once(point, r'''
static unsigned ordinary_frame(struct mCore*c,struct PatrolGuard*g,struct PatrolAddresses a,
    const color_t *pixels,unsigned width,unsigned height)
{
    unsigned result=0,before=g->frames;
    if(ordinary_initial){
        if(g->frames>=100000)return 51;
        c->runFrame(c);g->frames++;g->unarmedFrames++;
        unsigned battle=(c->busRead8(c,a.mainstate+0x439)&2)!=0;
        if(battle){
            if(ordinary_initial!=1||c->busRead16(c,a.trainer)!=855)return 70;
            if(!ordinary_battle_was&&ordinary_trial++)return 70;
            if(++g->battleFrames>36000)return 51;
        }
        ordinary_battle_was=battle;
    }else result=patrol_frame(c,g,a);
    if(g->frames!=before && !(g->frames%4)){
        if(width!=240||height!=160||g->frames>100000)return 60;
        unsigned char rgb[240*160*3];
        for(unsigned i=0;i<width*height;i++){
            rgb[3*i]=pixels[i]&255;rgb[3*i+1]=(pixels[i]>>8)&255;rgb[3*i+2]=(pixels[i]>>16)&255;
        }
        FILE*f=fopen("motion.rgb","ab");
        if(!f||fwrite(rgb,1,sizeof rgb,f)!=sizeof rgb||fclose(f))return 60;
    }
    return result;
}
''' + point)
    once('    if (argc != 4) return 2;', '''    if (argc != 5) return 2;
    if(!strcmp(argv[4],"fresh"))ordinary_initial=1;
    else if(!strcmp(argv[4],"seed"))ordinary_initial=2;
    else if(strcmp(argv[4],"patrol")&&strcmp(argv[4],"cold"))return 2;''')
    code = code.replace('patrol_frame(core,&pg,pa)', 'ordinary_frame(core,&pg,pa,pixels,width,height)')
    point = '        if (!strcmp(line,"quit\\n")) break;'
    once(point, point + r'''
        if (!strncmp(line,"ordinary-checkpoint ",20)){
            char label[32];struct PatrolSnapshot current={0};
            if(sscanf(line,"ordinary-checkpoint %31s %c",label,&extra)!=1
                ||(!strcmp(label,"fresh-saved")?ordinary_initial!=1:strcmp(label,"seed-saved")||ordinary_initial!=2)
                ||pg.armed||pg.pending){result=70;break;}
            result=patrol_read(core,pa,&current,1,1);if(result)break;
            unsigned w=core->busRead32(core,maplayout),h=core->busRead32(core,maplayout+4),tiles=core->busRead32(core,maplayout+8);
            if(!tiles||current.x+7>=w||current.y+7>=h||(core->busRead16(core,tiles+2*((current.y+7)*w+current.x+7))&0xC00)){result=57;break;}
            patrol_dump(&current,label,pg.frames);checks++;printf("PASS ordinary checkpoint %s absolute_frame=%u\n",label,pg.frames);continue;
        }
''')
    # Source ObjectEvent byte 0x18 holds the native facing nibble.
    point = '            patrol_dump(&current,label,pg.frames);pg.checkpoints++;'
    once(point, '''            printf("FIELD_FACING checkpoint=%s facing=%u\\n",label,core->busRead8(core,objects+core->busRead8(core,avatar+5)*0x24+0x18)&15);
''' + point)
    assert 'busWrite' not in code and 'loadState' not in code and code.count('->runFrame(') == 2
    return code, base
