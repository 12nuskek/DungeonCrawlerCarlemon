/* Host-only exact native reconstruction; no game writes or broad field mask. */
#ifndef WALKING_PRESERVATION_H
#define WALKING_PRESERVATION_H
static const unsigned char walk_orders[24][4]={
 {0,1,2,3},{0,1,3,2},{0,2,1,3},{0,3,1,2},{0,2,3,1},{0,3,2,1},
 {1,0,2,3},{1,0,3,2},{2,0,1,3},{3,0,1,2},{2,0,3,1},{3,0,2,1},
 {1,2,0,3},{1,3,0,2},{2,1,0,3},{3,1,0,2},{2,3,0,1},{3,2,0,1},
 {1,2,3,0},{1,3,2,0},{2,1,3,0},{3,1,2,0},{2,3,1,0},{3,2,1,0}};
static unsigned walk_u16(const unsigned char *p) {return p[0]|((unsigned)p[1]<<8);}
static void walk_put16(unsigned char *p,unsigned v) {p[0]=v&255;p[1]=(v>>8)&255;}
static unsigned walk_checksum(const unsigned char *plain)
{
    unsigned sum=0;for(unsigned i=0;i<48;i+=2) sum+=walk_u16(plain+i);return sum&65535;
}
static void walk_decode(const unsigned char *raw,unsigned char *plain)
{
    unsigned context=resource_word(raw)^resource_word(raw+4);
    for(unsigned i=0;i<48;i+=4) resource_put_word(plain+i,resource_word(raw+32+i)^context);
}
static unsigned walk_valid(const unsigned char *raw)
{
    unsigned char plain[48],encoded[48];walk_decode(raw,plain);
    unsigned context=resource_word(raw)^resource_word(raw+4);
    for(unsigned i=0;i<48;i+=4) resource_put_word(encoded+i,resource_word(plain+i)^context);
    unsigned growth=12*walk_orders[resource_word(raw)%24][0];
    unsigned misc=12*walk_orders[resource_word(raw)%24][3];
    return walk_checksum(plain)==walk_u16(raw+28) && !memcmp(encoded,raw+32,48)
        && (raw[19]&7)==2 && walk_u16(plain+growth)!=0 && !(resource_word(plain+misc+4)&0x40000000u);
}
static unsigned walk_friend(const unsigned char *raw)
{
    unsigned char plain[48];walk_decode(raw,plain);return plain[12*walk_orders[resource_word(raw)%24][0]+9];
}
static unsigned walk_target(const unsigned char *raw,unsigned section,unsigned holdEffect)
{
    unsigned char plain[48];walk_decode(raw,plain);
    const unsigned char *order=walk_orders[resource_word(raw)%24];
    unsigned friendship=plain[12*order[0]+9],mod=1;
    if(holdEffect==27) mod=150*mod/100; /* native HOLD_EFFECT_FRIENDSHIP_UP */
    unsigned misc=12*order[3],ball=(walk_u16(plain+misc+2)>>11)&15;
    friendship+=mod+(ball==11)+(plain[misc+1]==section); /* ITEM_LUXURY_BALL */
    return friendship>255?255:friendship;
}
static unsigned walk_member_equal(const unsigned char *before,const unsigned char *after,
                                  unsigned boundary,unsigned section,unsigned holdEffect)
{
    if(!walk_valid(before) || !walk_valid(after)) return 0;
    unsigned a=walk_friend(before),b=walk_friend(after);
    if(a==b) return !memcmp(before,after,100);
    if(!boundary || b!=walk_target(before,section,holdEffect)) return 0;
    unsigned char expected[100],plain[48];memcpy(expected,before,100);walk_decode(before,plain);
    plain[12*walk_orders[resource_word(before)%24][0]+9]=b;
    walk_put16(expected+28,walk_checksum(plain));
    unsigned context=resource_word(before)^resource_word(before+4);
    for(unsigned i=0;i<48;i+=4) resource_put_word(expected+32+i,resource_word(plain+i)^context);
    return !memcmp(expected,after,100);
}
static unsigned walk_party_equal(const unsigned char *before,const unsigned char *after,
                                  unsigned boundary,unsigned section,const unsigned *holdEffects)
{
    return walk_member_equal(before,after,boundary,section,holdEffects[0])
        && walk_member_equal(before+100,after+100,boundary,section,holdEffects[1])
        && !memcmp(before+200,after+200,400);
}
static unsigned walk_counter_valid(unsigned a,unsigned b) {return a<128 && b<128 && (b==a || b==(a+1)%128);}
static unsigned walk_flags_equal(const unsigned char *before,const unsigned char *after,unsigned actualYes)
{
    unsigned char expected[300];memcpy(expected,before,300);
    if(actualYes && (after[6]&1)) expected[6]|=1;
    return !memcmp(expected,after,300);
}
#endif
