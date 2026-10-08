/* Pure host comparison; actual native contexts are supplied, never inferred. */
#ifndef PARTY_RESOURCE_CANONICAL_H
#define PARTY_RESOURCE_CANONICAL_H
#define LOGICAL_OWNED_BYTES (0x988 - 0x490)
_Static_assert(sizeof(unsigned)==4,"Native context requires32-bit unsigned");
static inline unsigned resource_word(const unsigned char *p)
{
    return (unsigned)p[0] | ((unsigned)p[1]<<8) | ((unsigned)p[2]<<16) | ((unsigned)p[3]<<24);
}
static inline void resource_put_word(unsigned char *p,unsigned value)
{
    for(unsigned i=0;i<4;i++) p[i]=(value>>(8*i))&255;
}
static inline void resource_canonical(unsigned char *out,const unsigned char *raw,unsigned context)
{
    const unsigned starts[]={0x560,0x5D8,0x650,0x690,0x790};
    const unsigned slots[]={30,30,16,64,46};
    memcpy(out,raw,LOGICAL_OWNED_BYTES);
    resource_put_word(out,resource_word(raw)^context);
    out[4]^=context&255;out[5]^=(context>>8)&255;
    for(unsigned pocket=0;pocket<5;pocket++) for(unsigned i=0;i<slots[pocket];i++) {
        unsigned q=starts[pocket]-0x490+4*i+2;
        out[q]^=context&255;out[q+1]^=(context>>8)&255;
    }
}
static inline unsigned resource_equal(const unsigned char *a,unsigned contextA,const unsigned char *b,unsigned contextB)
{
    unsigned char logicalA[LOGICAL_OWNED_BYTES],logicalB[LOGICAL_OWNED_BYTES];
    resource_canonical(logicalA,a,contextA);resource_canonical(logicalB,b,contextB);
    return memcmp(logicalA,logicalB,sizeof logicalA)==0;
}
static inline unsigned party_guard_reason(const unsigned char *a,const unsigned char *b,unsigned countA,unsigned countB,
                                         const unsigned char *flagsA,const unsigned char *flagsB)
{
    if(memcmp(a,b,200)) return 53;
    if(memcmp(a+200,b+200,400) || countA!=countB || memcmp(flagsA,flagsB,300)) return 57;
    return 0;
}
static inline unsigned party_resource_reason(const unsigned char *a,const unsigned char *b,unsigned countA,unsigned countB,
    const unsigned char *flagsA,const unsigned char *flagsB,const unsigned char *ownedA,unsigned contextA,
    const unsigned char *ownedB,unsigned contextB)
{
    unsigned reason=party_guard_reason(a,b,countA,countB,flagsA,flagsB);
    if(reason) return reason;
    return resource_equal(ownedA,contextA,ownedB,contextB)?0:57;
}
#endif
