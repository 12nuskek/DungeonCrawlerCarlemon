/* Independent native fixture encoding; no emulator or synthetic game inputs. */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include "floor1/party-resource-canonical.h"
#include "floor1/walking-preservation.h"
static unsigned cases;
#define CHECK(x) do {assert(x);cases++;} while(0)
static const unsigned char native_positions[24][4]={
 {0,1,2,3},{0,1,3,2},{0,2,1,3},{0,3,1,2},{0,2,3,1},{0,3,2,1},
 {1,0,2,3},{1,0,3,2},{2,0,1,3},{3,0,1,2},{2,0,3,1},{3,0,2,1},
 {1,2,0,3},{1,3,0,2},{2,1,0,3},{3,1,0,2},{2,3,0,1},{3,2,0,1},
 {1,2,3,0},{1,3,2,0},{2,1,3,0},{3,1,2,0},{2,3,1,0},{3,2,1,0}};
static void native_encode(unsigned char *out,unsigned personality,unsigned friendship,unsigned ball,unsigned met)
{
    unsigned char blocks[4][12]={{0}},plain[48];memset(out,0,100);
    unsigned owner=0x13579bdf;memcpy(out,&personality,4);memcpy(out+4,&owner,4);out[19]=2;out[84]=11;
    unsigned short species=293;memcpy(blocks[0],&species,2);blocks[0][4]=17;blocks[0][9]=friendship;
    blocks[1][0]=33;blocks[1][8]=8;blocks[3][1]=met;
    unsigned short origin=(unsigned short)(ball<<11);memcpy(blocks[3]+2,&origin,2);
    for(unsigned i=0;i<4;i++) memcpy(plain+12*native_positions[personality%24][i],blocks[i],12);
    unsigned short checksum=0;
    for(unsigned i=0;i<24;i++) {unsigned short value;memcpy(&value,plain+2*i,2);checksum+=value;}
    memcpy(out+28,&checksum,2);
    for(unsigned i=0;i<12;i++) {unsigned value;memcpy(&value,plain+4*i,4);value^=personality^owner;memcpy(out+32+4*i,&value,4);}
}
static void repair_checksum(unsigned char *raw)
{unsigned char plain[48];walk_decode(raw,plain);walk_put16(raw+28,walk_checksum(plain));}
int main(void)
{
    unsigned char a[600]={0},b[600]={0};unsigned effects[2]={0,0};
    for(unsigned order=0;order<24;order++) {
        native_encode(a,order,92,4,9);native_encode(a+100,order+24,71,4,9);memcpy(b,a,600);
        CHECK(walk_party_equal(a,b,0,10,effects));CHECK(walk_friend(a)==92);CHECK(walk_valid(a));
        for(unsigned mask=0;mask<4;mask++) {
            native_encode(b,order,92+(mask&1),4,9);native_encode(b+100,order+24,71+((mask>>1)&1),4,9);
            CHECK(walk_party_equal(a,b,1,10,effects));
            if(mask) CHECK(!walk_party_equal(a,b,0,10,effects));
        }
        native_encode(b,order,94,4,9);CHECK(!walk_member_equal(a,b,1,10,0));
        native_encode(b,order,91,4,9);CHECK(!walk_member_equal(a,b,1,10,0));
        native_encode(b,order,93,4,9);b[28]^=1;CHECK(!walk_member_equal(a,b,1,10,0));
        native_encode(b,order,93,4,9);b[32]^=1;CHECK(!walk_member_equal(a,b,1,10,0));
        native_encode(b,order+48,93,4,9);CHECK(walk_valid(b));CHECK(!walk_member_equal(a,b,1,10,0));
        native_encode(b,order,93,4,9);a[28]^=1;CHECK(!walk_member_equal(a,b,1,10,0));a[28]^=1;
        /* Valid checksums never excuse any unrelated canonical/header field. */
        for(unsigned i=0;i<100;i++) {
            if(i==28 || i==29 || i==32u+12u*native_positions[order][0]+9u) continue;
            memcpy(b,a,100);b[i]^=1;if(i>=32 && i<80) repair_checksum(b);
            CHECK(!walk_member_equal(a,b,1,10,0));
        }
        native_encode(a,order,253,11,10);native_encode(b,order,255,11,10);
        CHECK(walk_target(a,10,27)==255);CHECK(walk_member_equal(a,b,1,10,27));
        native_encode(a,order,252,11,10);native_encode(b,order,255,11,10);CHECK(walk_member_equal(a,b,1,10,0));
        native_encode(a,order,255,4,9);memcpy(b,a,100);CHECK(walk_member_equal(a,b,1,10,0));
        native_encode(a,order,92,4,9);CHECK(walk_target(a,10,27)==93); /* rounding */
    }
    native_encode(a,3,92,4,9);native_encode(a+100,9,71,4,9);memcpy(b,a,600);b[599]=1;
    CHECK(!walk_party_equal(a,b,1,10,effects));
    /* Native checksum wrap is derived exactly, not accepted as a tolerance. */
    native_encode(a,0,92,4,9);unsigned char plain[48];walk_decode(a,plain);
    unsigned short filler=(unsigned short)(0xff80-walk_checksum(plain));memcpy(plain+10,&filler,2);
    unsigned context=resource_word(a)^resource_word(a+4);
    for(unsigned i=0;i<12;i++) {unsigned v;memcpy(&v,plain+4*i,4);v^=context;memcpy(a+32+4*i,&v,4);}
    repair_checksum(a);memcpy(b,a,100);plain[9]++;
    for(unsigned i=0;i<12;i++) {unsigned v;memcpy(&v,plain+4*i,4);v^=context;memcpy(b+32+4*i,&v,4);}
    repair_checksum(b);CHECK(walk_u16(a+28)==0xff80);CHECK(walk_u16(b+28)==0x80);CHECK(walk_member_equal(a,b,1,10,0));
    CHECK(walk_counter_valid(127,0));CHECK(walk_counter_valid(66,66));CHECK(walk_counter_valid(66,67));
    CHECK(!walk_counter_valid(126,0));CHECK(!walk_counter_valid(127,1));CHECK(!walk_counter_valid(128,0));
    unsigned char flagsA[300]={0},flagsB[300]={0};flagsB[6]=1;
    CHECK(!walk_flags_equal(flagsA,flagsB,0));CHECK(walk_flags_equal(flagsA,flagsB,1));flagsB[299]=1;
    CHECK(!walk_flags_equal(flagsA,flagsB,1));flagsA[6]=1;memset(flagsB,0,300);CHECK(!walk_flags_equal(flagsA,flagsB,1));
    unsigned char logical[LOGICAL_OWNED_BYTES]={0},raw[LOGICAL_OWNED_BYTES];memcpy(raw,logical,sizeof raw);
    /* XOR is involutive; canonical comparison's decoder is independently tested elsewhere. */
    resource_canonical(raw,logical,0x10203040);CHECK(resource_equal(logical,0,raw,0x10203040));
    raw[0]^=1;CHECK(!resource_equal(logical,0,raw,0x10203040));
    printf("PASS %u narrow walking host cases:24 native permutations;0/+1/skip;off-boundary/excess/negative;checksums/derived encoding;all unrelated bytes;native bonuses/clamp/rounding;remaining party/counter/YES-only flags/resources\n",cases);
    return 0;
}
