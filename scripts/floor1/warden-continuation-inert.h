/* Inert tail for exact generated production readers; no emulator core. */
static void wc_save_inert(void) {
    setup();memset(&hc,0,sizeof hc);hc.overwrite=0x170;hc.different=0xd2;
    const unsigned callback=0xd4,confirm=0x160,success=0x180,done=0x190;
    const unsigned fade=0xe0,printers=0x300,menu=0x400;unsigned checks=0;
    for(unsigned stage=0;stage<3;stage++) {
        assert(!hc_save_key(1,1));checks++;
        assert(hc_save_key(1,1)==95);checks++; /* A must have a fresh edge. */
        assert(hc_save_key(1,2)==95);checks++;
        put32(callback,0x999);
        assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu)==1);checks++;
        unsigned wanted=stage==0?confirm:stage==1?hc.overwrite:success;put32(callback,wanted|1);
        memory[printers+27]=1;
        assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu)==1);checks++;memory[printers+27]=0;
        memory[fade+7]=128;
        assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu)==1);checks++;memory[fade+7]=0;
        memory[hc.different]=1;
        assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu)==95);checks++;memory[hc.different]=0;
        if(stage<2) {
            memory[menu+2]=1;
            assert(hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu)==95);checks++;memory[menu+2]=0;
        }
        assert(!hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu));checks++;
        if(stage==2) {
            put32(callback,done|1);
            assert(!hc_save_ready(&mock,stage,callback,confirm,success,done,fade,printers,menu));checks++;
        }
        /* Same release performed by the generated readiness polling command. */
        assert(!hc_save_key(0,1));hc.saveStage++;
    }
    assert(hc.saveStage==3&&hc.presses==3&&hc.keys==0);checks++;
    assert(hc_save_key(1,1)==95);checks++;
    memset(&hc,0,sizeof hc);assert(hc_save_key(3,1)==95);checks++;
    hc.saveStage=1;assert(hc_save_key(1,1)==95);checks++;
    closeFiles();printf("PASS exact generated native Save release/two-Yes/completion checks=%u\n",checks);
}
int main(int argc,char**argv) {
    if(argc==1){wc_save_inert();return 0;}
    if(argc==4&&!strcmp(argv[1],"--terminal")) {
        mustStop((unsigned)strtoul(argv[2],NULL,10),(unsigned)strtoul(argv[3],NULL,10));return 0;
    }
    if((argc==5&&!strcmp(argv[1],"--route-anchor"))
        ||(argc==3&&(!strcmp(argv[1],"--continue-anchor")||!strcmp(argv[1],"--cold-anchor")))) {
        setup();struct CoSnapshot s;readSnapshot(argv[2],&s);
        unsigned result=argc==5?wc_phase_anchor(&s,(unsigned)strtoul(argv[3],NULL,10),(unsigned)strtoul(argv[4],NULL,10))
            :!strcmp(argv[1],"--continue-anchor")?wc_continue_anchor(&s):wc_cold_anchor(&s);
        closeFiles();printf("INERT_ANCHOR reason=%u\n",result);return result;
    }
    return historical_inert_main(argc,argv);
}
