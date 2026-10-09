"""Read-only native message assertions/captures, driven by ordinary buttons.

Observe gStringVar4 and the existing printer's documented state/active fields.
No RAM, ROM, save or policy writes. Captures include every paragraph, not a
host-rendered transcription. Raw logs/saves remain local.
"""
def instrument(code):
    code = code.replace('scriptStatus=0, addr;', 'scriptStatus=0, string4=0, printers=0, addr;')
    point = '        if (!strcmp(symbol,"gMain")) mainstate=addr;'
    code = code.replace(point, point + '\n        if (!strcmp(symbol,"gStringVar4")) string4=addr;\n        if (!strcmp(symbol,"sTextPrinters")) printers=addr;')
    code = code.replace('char line[256],name[128]', 'char line[2048],name[128]')
    point = '        if (!strcmp(line,"quit\\n")) break;'
    assert code.count(point) == 1
    addition = r'''
        if (!strncmp(line,"pages ",6)) {
            char prefix[96], labels[1536], wanted[128], filename[128];
            unsigned addresses[32], countText=0, index=0, page=0, seen=0;
            if (!string4 || !printers || sscanf(line,"pages %95s %1535s %c",prefix,labels,&extra)!=2) {result=41;break;}
            char *label=strtok(labels,",");
            while (label && countText<32) {
                FILE *table=fopen(argv[3],"r");
                unsigned found=0;
                if (!table) {result=41;break;}
                while (fscanf(table,"%x %c %127s",&addr,&type,wanted)==3)
                    if (!strcmp(label,wanted)) {found=addr;break;}
                fclose(table);
                if (!found) {result=41;break;}
                addresses[countText++]=found;label=strtok(NULL,",");
            }
            if (result || label || !countText) {result=41;break;}
            unsigned done=0;
            for (unsigned attempt=0;attempt<32 && !done;attempt++) {
                unsigned match=0;
                for (unsigned candidate=index;candidate<countText && candidate<=index+1;candidate++) {
                    unsigned equal=1, ended=0;
                    for (unsigned i=0;i<1024;i++) {
                        unsigned expected=core->busRead8(core,addresses[candidate]+i);
                        if (core->busRead8(core,string4+i)!=expected) {equal=0;break;}
                        if (expected==255) {ended=1;break;}
                    }
                    if (equal && ended) {index=candidate;match=1;break;}
                }
                if (!match || core->busRead8(core,mainstate+0x439)&2) {result=41;break;}
                unsigned active=core->busRead8(core,printers+0x1B), state=core->busRead8(core,printers+0x1C);
                if (active && state!=2 && state!=3) {result=41;break;}
                snprintf(filename,sizeof(filename),"%s-%02u-%02u.ppm",prefix,index,page++);
                result=capture(filename,pixels,width,height);
                if (result) break;
                seen|=1u<<index;
                if (!active && index==countText-1) {done=1;break;}
                core->setKeys(core,1);core->runFrame(core);total++;
                core->setKeys(core,0);
                for (unsigned frame=0;frame<400;frame++) {core->runFrame(core);total++;}
            }
            if (result || !done || seen!=(countText==32?UINT_MAX:((1u<<countText)-1))) {
                result=41;fprintf(stderr,"Native message/page sequence failed\n");break;
            }
            checks++;printf("PASS native-pages messages=%u pages=%u\n",countText,page);continue;
        }
'''
    result = code.replace(point, point + addition)
    assert 'busWrite' not in result
    return result
