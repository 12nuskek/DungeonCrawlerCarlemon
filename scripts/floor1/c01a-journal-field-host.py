"""Bounded field-only ordinary buttons, native pages and immutable-state reads."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
GUARD=r'''
static unsigned jf_frames;
static void jf_run(struct mCore *c,unsigned mainstate,const color_t *pixels,unsigned width,unsigned height) {
    if(width!=240 || height!=160 || jf_frames>=18000 || (c->busRead8(c,mainstate+0x439)&2)) {
        capture("field-first-failure.ppm",pixels,width,height);fprintf(stderr,"Field-only frame admission failed at%u\n",jf_frames);exit(61);
    }
    c->runFrame(c);jf_frames++;
    char name[64];snprintf(name,sizeof name,"field-%05u.ppm",jf_frames-1);
    if(capture(name,pixels,width,height) || (c->busRead8(c,mainstate+0x439)&2)) {
        capture("field-first-failure.ppm",pixels,width,height);fprintf(stderr,"Field-only frame failed at%u\n",jf_frames);exit(61);
    }
}
static unsigned jf_task(struct mCore *c,unsigned tasks,unsigned fn,unsigned offset,unsigned value) {
    unsigned found=0;
    for(unsigned i=0;i<16;i++) {
        unsigned task=tasks+40*i;
        if(c->busRead8(c,task+4) && (c->busRead32(c,task)&~1u)==(fn&~1u)) {
            if(c->busRead16(c,task+offset)<value)return 0;
            found++;
        }
    }
    return found==1;
}
'''
COMMANDS=r'''
        if(!strcmp(line,"jf yesno\n")) {
            if(!jf_task(core,jtasks,jyesno,12,5) || !core->busRead8(core,fieldLock)
               || (core->busRead32(core,mainstate+4)&~1u)!=(fieldCallback&~1u)
               || (core->busRead8(core,jfade+7)&128)) {result=62;break;}
            checks++;printf("PASS JF native-yesno-ready\n");continue;
        }
        if(!strcmp(line,"jf start 4\n")) {
            if(core->busRead8(core,jcursor)!=4 || !jf_task(core,jtasks,jstarttask,8,1)
               || (core->busRead32(core,jcallback)&~1u)!=(jstartinput&~1u)
               || !core->busRead8(core,fieldLock) || (core->busRead8(core,jfade+7)&128)) {result=62;break;}
            checks++;printf("PASS JF native-start-ready cursor=4\n");continue;
        }
        if(!strncmp(line,"jf answer ",10)) {
            unsigned expected;
            if(sscanf(line,"jf answer %u %c",&expected,&extra)!=1 || expected>1 || core->busRead16(core,janswer)!=expected) {result=62;break;}
            checks++;printf("PASS JF native-answer=%u\n",expected);continue;
        }
        if(!strncmp(line,"jf preserve ",12)) {
            char phase[16];unsigned sb=core->busRead32(core,saveptr),sb2=core->busRead32(core,save2ptr),offset=0;
            if(sscanf(line,"jf preserve %15s %c",phase,&extra)!=1 || (strcmp(phase,"start") && strcmp(phase,"end"))) {result=63;break;}
            const unsigned addresses[]={party,count,sb+0x13f0,sb+0x1270,sb+0x139c,sb+0x490,sb2+0xac,sb+0x238,sb+0x234,sb};
            const unsigned sizes[]={600,1,2,300,512,0x5a0,4,600,4,6};
            unsigned char state[4096];
            for(unsigned region=0;region<10;region++)for(unsigned i=0;i<sizes[region];i++)state[offset++]=core->busRead8(core,addresses[region]+i);
            char filename[64];snprintf(filename,sizeof filename,"field-%s-state.bin",phase);FILE *file=fopen(filename,"wb");
            if(!file || fwrite(state,1,offset,file)!=offset || fclose(file)) {result=63;break;}
            if(!strcmp(phase,"start")) {
                if(jpreserved) {result=63;break;}
                memcpy(jinitial,state,offset);jsize=offset;jpreserved=1;
                unsigned char expected[600];FILE *input=fopen("expected-party.bin","rb");
                if(!input || fread(expected,1,600,input)!=600 || fgetc(input)!=EOF || fclose(input) || memcmp(expected,state,600)) {result=63;break;}
                if(state[600]!=2 || core->busRead16(core,sb+0x13f0)!=47) {result=63;break;}
            } else if(!jpreserved || offset!=jsize || memcmp(jinitial,state,offset)) {result=63;break;}
            checks++;printf("PASS JF preserve-%s bytes=%u party600/count/counter/flags300/vars512/resources1440/key/savedparty600/savedcount/legalfield\n",phase,offset);continue;
        }
'''
def generate():
    code=(ROOT/'scripts/playtest.c').read_text()
    code=module('fieldSaveRead',ROOT/'scripts/floor1/live-save-observer.py').instrument(code)
    code=module('fieldNativeText',ROOT/'scripts/floor1/native-text-observer.py').instrument(code)
    needle="    fputc('\\n', stderr);";assert code.count(needle)==1
    code=code.replace(needle,needle+'\n    exit(65); // First native emulator ERROR/FATAL is terminal.')
    needle='scriptStatus=0, string4=0, printers=0, addr;';assert code.count(needle)==1
    code=code.replace(needle,'scriptStatus=0, string4=0, printers=0, jtasks=0, jyesno=0, jstarttask=0, jstartinput=0, jcursor=0, jcallback=0, janswer=0, jfade=0, addr;')
    needle='        if (!strcmp(symbol,"gMain")) mainstate=addr;';assert code.count(needle)==1
    names={'gtasks':'jtasks','jfYesNo':'jyesno','jfStartTask':'jstarttask','jfStartInput':'jstartinput','jfStartCursor':'jcursor','gMenuCallback':'jcallback','gSpecialVar_Result':'janswer','gPaletteFade':'jfade'}
    code=code.replace(needle,needle+'\n'+'\n'.join(f'        if (!strcmp(symbol,"{n}")) {v}=addr;' for n,v in names.items()))
    # Exact gTasks native symbol; no game writes or engine calls.
    code=code.replace('"gtasks"','"gTasks"')
    needle='    FILE *save=fopen(argv[2], "ab+");';assert code.count(needle)==1
    code=code.replace(needle,'    if(!jtasks || !jyesno || !jstarttask || !jstartinput || !jcursor || !jcallback || !janswer || !jfade || !fieldCallback || !fieldLock || !scriptStatus || !string4 || !printers)return 60;\n'+needle)
    needle='    int result=0;\n    while (fgets(line,sizeof(line),stdin)) {';assert code.count(needle)==1
    code=code.replace(needle,'    unsigned char jinitial[4096];unsigned jsize=0,jpreserved=0;\n'+needle)
    needle='        if (!strcmp(line,"quit\\n")) break;';assert code.count(needle)==1
    allow='''        if(strncmp(line,"step ",5) && strncmp(line,"pages ",6) && strncmp(line,"jf ",3) && strncmp(line,"expect ",7) && strncmp(line,"uses ",5) && strncmp(line,"item ",5) && strncmp(line,"flag ",5) && strcmp(line,"ready\\n") && strcmp(line,"snapshot\\n") && strcmp(line,"duo healthy\\n") && strcmp(line,"quit\\n")) {result=64;break;}\n'''
    code=code.replace(needle,allow+needle+COMMANDS)
    count=code.count('core->runFrame(core)');assert count>=4
    code=code.replace('core->runFrame(core)','jf_run(core,mainstate,pixels,width,height)')
    code=code.replace('int main(int argc, char **argv)',GUARD+'\nint main(int argc, char **argv)')
    assert 'busWrite' not in code and code.count('->runFrame(')==1
    return code
