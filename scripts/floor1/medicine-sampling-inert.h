/* Instruction-cut audit of the unchanged r2 guard; never an emulator.
 * Every cut starts from the same complete, validated healed state. No cut is
 * admitted by weakening the guard: legitimate source intermediates expose gaps. */
static unsigned samplingNextPC;
static bool samplingRegister(const struct mCore*c,const char*n,void*out) {
    if(!strcmp(n,"r15")||!strcmp(n,"pc")){unsigned value=samplingNextPC+2;memcpy(out,&value,4);return true;}
    if(!strcmp(n,"cpsr")){unsigned value=0x3f;memcpy(out,&value,4);return true;}
    return mock_register(c,n,out);
}
static void samplingNativeText(unsigned acknowledged) {
    unsigned char text[1000];FILE*f=fopen("../native-restored-text.bin","rb");assert(f);
    size_t size=fread(text,1,sizeof text,f);assert(size>3&&size<sizeof text&&fgetc(f)==EOF&&!fclose(f));
    assert(text[size-3]==0xfc&&text[size-2]==9&&text[size-1]==255);
    unsigned out=gc.a.string4,base=out;
    for(unsigned i=0;i<size;i++) {
        unsigned value=text[i];
        if(value==0xfd) {
            assert(i+1<size);unsigned id=text[++i];
            if(id==2){for(unsigned j=0;j<10&&gc.healed.party[100*gc.slot+8+j]!=255;j++)memory[out++]=gc.healed.party[100*gc.slot+8+j];}
            else {assert(id==3);unsigned gain=gc.battleHp-gc.hp;assert(gain>0&&gain<=20);if(gain>=10)memory[out++]=0xa1+gain/10;memory[out++]=0xa1+gain%10;}
        }else memory[out++]=value;
        assert(out-base<1000);
    }
    assert(memory[out-1]==255);put32(gc_message(&mock),acknowledged?out-1:base);
    memory[gc.a.textFlags]=1; /* PrintMessage's native canABSpeedUpPrint bit. */
}
static void samplingRestore(unsigned acknowledged) {
    installSnapshot(&gc.healed);put32(co.a.main+4,gc.a.partyMain|1);
    nativeMessageSetup();samplingNativeText(acknowledged);memory[gc.a.fade+7]=0;put32(gc.a.internal,0x3900);put32(0x3904,gc.a.exitBattle|1);
    gc.stage=5;gc.ack=acknowledged;gc.keys=0;gc.ackFrame=co.frames-2;
    gc.released=acknowledged;gc.printerFinished=gc.taskDestroyed=gc.fadeSeen=0;
    gc.exitSeen=gc.setupSeen=gc.reshowEntrySeen=gc.reshowSeen=0;
    mock.readRegister=samplingRegister;
}
static unsigned samplingCheck(const char*name,unsigned i,unsigned bytes,unsigned nextPC,const unsigned char*expected) {
    samplingNextPC=nextPC;
    /* Validate the entire native party representation against the source copy.
     * Do not normalize duplicated records or repair a torn actor checksum. */
    assert(!memcmp(memory+co.a.party,expected,600));
    struct GcMedicine before=gc;unsigned reason=gc_observe(&mock,mockPixels,240,160);gc=before;
    if(!reason){struct CoSnapshot actual={0};assert(!gc_read(&mock,&actual)&&gc_same(&actual,&gc.healed));gc=before;}
    printf("SAMPLING_CUT name=%s order=%u recipient=%u quantity=%u record=%u copied=%u next_pc=%08x reason=%u full_party_source_bytes=1 key=0\n",
        name,gc.order[0],gc.recipient,gc_quantity(gc.owned)+1,i,bytes,nextPC,reason);
    return reason;
}
static void samplingCuts(unsigned swapped,unsigned recipient,unsigned quantity) {
    medicineSetup(swapped,recipient,quantity);medicineUse(swapped,recipient,quantity);
    unsigned char expected[600];unsigned positions[6];assert(gc_order(gc.order,positions));
    memcpy(expected,gc.healed.party,600);
    /* 1: printer/wait task exists; restoration task has not stored its new func. */
    samplingRestore(0);put32(gc.a.tasks,gc.a.restored|1);
    assert(samplingCheck("printer-created-before-restored-func",0,0,AUDIT_RESTORED+0x2e,expected)==107);
    /* 2: native active store has executed; print task still owns cleanup. */
    samplingRestore(1);memory[gc_message(&mock)+27]=0;
    assert(samplingCheck("printer-inactive-before-task-destroy",0,0,AUDIT_RUN_TEXT+0x70,expected)==107);
    /* 3: fade active store has executed; close-text task func remains unchanged. */
    samplingRestore(1);memory[gc_message(&mock)+27]=0;memory[0x342c]=0;
    memory[gc.a.fade+7]=128;gc.printerFinished=gc.taskDestroyed=1;
    assert(samplingCheck("fade-active-before-close-func",0,0,AUDIT_CLOSE+0x1a,expected)==107);
    /* 4: native aligned memcpy commits individual four-byte words. Every full
     * prefix of every record is tested, including duplicate complete actors and
     * torn encoded actors. A strict checksum failure remains a failure. */
    for(unsigned record=0;record<6;record++)for(unsigned copied=0;copied<=100;copied+=4) {
        samplingRestore(1);memory[gc_message(&mock)+27]=0;memory[0x342c]=0;
        medicineTask(gc.a.closeFade);gc.printerFinished=gc.taskDestroyed=gc.fadeSeen=1;
        memcpy(expected,gc.healed.party,600);
        for(unsigned j=0;j<record;j++)memcpy(expected+100*positions[j],gc.healed.party+100*j,100);
        memcpy(expected+100*positions[record],gc.healed.party+100*record,copied);
        memcpy(memory+co.a.party,expected,600);
        unsigned nextPC=copied==0?AUDIT_COPY+0x1c:copied==100?AUDIT_COPY+0x38:
            AUDIT_COPY+0x1a+4*(copied/4%4?copied/4%4:4);
        unsigned reason=samplingCheck("party-copy-before-CB2",record,copied,nextPC,expected);
        if(!memcmp(expected,gc.healed.party,600))assert(!reason);
        else assert(reason==82||reason==106);
    }
    /* 5: CB2 has been published; native sprite/pointer/task cleanup is pending.
     * FreePartyPointers does not null the global pointer as the grouped mock did. */
    samplingRestore(1);memory[gc_message(&mock)+27]=0;memory[0x342c]=0;
    medicineTask(gc.a.closeFade);gc.printerFinished=gc.taskDestroyed=gc.fadeSeen=1;
    gc_permute(gc.healed.party,expected,positions,1);memcpy(memory+co.a.party,expected,600);
    put32(co.a.main+4,gc.a.exitBattle|1);
    assert(samplingCheck("exit-published-before-cleanup",0,0,AUDIT_CLOSE_FADE+0x46,expected)==107);
    /* Stable cleanup-complete boundary remains accepted, with the actual stale
     * (non-null) global pointer; no dereference or input on the exited menu. */
    memory[gc.a.tasks+4]=0;samplingNextPC=AUDIT_CLOSE_FADE+0x54;
    assert(!gc_observe(&mock,mockPixels,240,160)&&gc.exitSeen&&gc.stage==5);
    closeFiles();mock.readRegister=mock_register;mock.runFrame=advance;mock.setKeys=NULL;
}
static void samplingAudit(void) {
    for(unsigned swapped=0;swapped<2;swapped++)for(unsigned recipient=0;recipient<2;recipient++)for(unsigned quantity=1;quantity<=2;quantity++)samplingCuts(swapped,recipient,quantity);
    puts("PASS static instruction-cut audit fixtures: current native sampling admission remains FALSE; zero emulators");
}
