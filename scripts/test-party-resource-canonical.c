/* Fixed host-only fixtures; no emulator, Save or injected game state. */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "floor1/party-resource-canonical.h"
static unsigned checks;
#define REQUIRE(x) do {assert(x);checks++;} while(0)
static void put16(unsigned char *p,unsigned value) {p[0]=value&255;p[1]=(value>>8)&255;}
/* Independent native typed-value fixture encoding, as load_save/item.c specify. */
static void encoded(unsigned char *out,const unsigned char *logical,unsigned context)
{
    const unsigned starts[]={0x560,0x5d8,0x650,0x690,0x790},counts[]={30,30,16,64,46};
    memcpy(out,logical,LOGICAL_OWNED_BYTES);
    unsigned money;memcpy(&money,logical,4);money^=context;memcpy(out,&money,4);
    unsigned short coins;memcpy(&coins,logical+4,2);coins^=(unsigned short)context;memcpy(out+4,&coins,2);
    for(unsigned p=0;p<5;p++) for(unsigned i=0;i<counts[p];i++) {
        unsigned q=starts[p]-0x490+4*i+2;unsigned short quantity;
        memcpy(&quantity,logical+q,2);quantity^=(unsigned short)context;memcpy(out+q,&quantity,2);
    }
}
int main(void)
{
    const unsigned starts[]={0x560,0x5d8,0x650,0x690,0x790},counts[]={30,30,16,64,46};
    unsigned char logical[LOGICAL_OWNED_BYTES]={0},corrupt[LOGICAL_OWNED_BYTES];
    unsigned char rawA[LOGICAL_OWNED_BYTES],relocatedB[LOGICAL_OWNED_BYTES],decoded[LOGICAL_OWNED_BYTES];
    unsigned contextA=0x12345678,contextB=0x9abcdef0;
    unsigned money=4360;memcpy(logical,&money,4);put16(logical+4,7);
    put16(logical+0x560-0x490,378);put16(logical+0x562-0x490,2);
    put16(logical+0x498-0x490,13);put16(logical+0x49a-0x490,3);
    encoded(rawA,logical,contextA);encoded(relocatedB,logical,contextB);
    REQUIRE(&rawA[0]!=&relocatedB[0]);REQUIRE(memcmp(rawA,relocatedB,sizeof rawA)!=0);
    REQUIRE(resource_equal(rawA,contextA,relocatedB,contextB));
    resource_canonical(decoded,relocatedB,contextB);REQUIRE(memcmp(decoded,logical,sizeof logical)==0);
    encoded(relocatedB,logical,contextA^0xffff0000u);
    REQUIRE(resource_equal(rawA,contextA,relocatedB,contextA^0xffff0000u));
    REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextA));
    encoded(relocatedB,logical,contextB);REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB^1));
    REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB^0x10000u));
    memcpy(corrupt,logical,sizeof corrupt);money++;memcpy(corrupt,&money,4);encoded(relocatedB,corrupt,contextB);
    REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB));
    memcpy(corrupt,logical,sizeof corrupt);put16(corrupt+4,8);encoded(relocatedB,corrupt,contextB);
    REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB));
    for(unsigned p=0;p<5;p++) for(unsigned i=0;i<counts[p];i++) {
        unsigned id=starts[p]-0x490+4*i,q=id+2;
        memcpy(corrupt,logical,sizeof corrupt);unsigned short quantity;memcpy(&quantity,corrupt+q,2);put16(corrupt+q,quantity+1);
        encoded(relocatedB,corrupt,contextB);REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB));
        memcpy(corrupt,logical,sizeof corrupt);corrupt[id]^=1;encoded(relocatedB,corrupt,contextB);
        REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB));
    }
    const unsigned plainOffsets[]={6,0x498-0x490,0x49a-0x490,0x848-0x490,LOGICAL_OWNED_BYTES-1};
    for(unsigned i=0;i<sizeof plainOffsets/sizeof *plainOffsets;i++) {
        memcpy(corrupt,logical,sizeof corrupt);corrupt[plainOffsets[i]]^=1;encoded(relocatedB,corrupt,contextB);
        REQUIRE(!resource_equal(rawA,contextA,relocatedB,contextB));
    }
    unsigned char empty[LOGICAL_OWNED_BYTES]={0};encoded(relocatedB,empty,0);
    REQUIRE(resource_equal(empty,0,relocatedB,0));encoded(rawA,empty,contextA);
    REQUIRE(resource_equal(rawA,contextA,empty,0));
    memcpy(corrupt,empty,sizeof corrupt);put16(corrupt+0x562-0x490,1);encoded(relocatedB,corrupt,0);
    REQUIRE(!resource_equal(rawA,contextA,relocatedB,0));
    unsigned char partyA[600]={0},partyB[600]={0},flagsA[300]={0},flagsB[300]={0};
    const unsigned duoOffsets[]={0,99,100,199};
    for(unsigned i=0;i<4;i++) {
        memset(partyB,0,sizeof partyB);partyB[duoOffsets[i]]=1;flagsB[0]=1;
        REQUIRE(party_resource_reason(partyA,partyB,2,1,flagsA,flagsB,rawA,contextA,relocatedB,0)==53);
    }
    memset(partyB,0,sizeof partyB);memset(flagsB,0,sizeof flagsB);partyB[599]=1;
    REQUIRE(party_guard_reason(partyA,partyB,2,2,flagsA,flagsB)==57);
    memset(partyB,0,sizeof partyB);REQUIRE(party_guard_reason(partyA,partyB,2,1,flagsA,flagsB)==57);
    flagsB[299]=1;REQUIRE(party_guard_reason(partyA,partyB,2,2,flagsA,flagsB)==57);
    memset(flagsB,0,sizeof flagsB);REQUIRE(party_guard_reason(partyA,partyB,2,2,flagsA,flagsB)==0);
    printf("PASS %u exact-header host cases: relocation/rekey/high-half; money/coin/all186 quantity+ID corruptions; unencoded/wrong/zero contexts/empty slots; strict53 priority/party/count/flags\n",checks);
    return 0;
}
