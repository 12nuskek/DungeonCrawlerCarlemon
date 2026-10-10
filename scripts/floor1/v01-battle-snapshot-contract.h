/* Offline contract only. NOT connected to the runtime observer: native CPU
 * serialization authority has not been established. No caller may infer these
 * states from callback names, matching plaintext, checksums, or frame numbers. */
enum BvSnapshotAuthority { BV_SNAPSHOT_UNKNOWN, BV_SNAPSHOT_VALID, BV_SNAPSHOT_TRANSIENT };
struct BvSnapshotGuard {unsigned frames,valid,deferred,reentries,pending;};
static unsigned bv_snapshot_word(const unsigned char *p)
{return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static unsigned bv_snapshot_party_valid(const unsigned char party[600])
{
    for(unsigned mon=0;mon<6;mon++){
        const unsigned char *p=party+100*mon;
        unsigned key=bv_snapshot_word(p)^bv_snapshot_word(p+4),sum=0;
        if(p[19]&1)return 0; // Native isBadEgg.
        for(unsigned i=32;i<80;i+=4){unsigned word=bv_snapshot_word(p+i)^key;sum+=(word&65535)+(word>>16);}
        if((sum&65535)!=(unsigned)(p[28]|p[29]<<8))return 0;
    }
    return 1;
}
/* The caller must record every frame/control independently. Only party reads
 * may defer; every other byte remains exact. A deferred party pointer may be
 * NULL: it must never be read, compared, accepted or used as a new anchor.
 * Reentry compares all 600 bytes against the SAME FRAME's complete reference.
 * Explicit checkpoints cannot defer. UNKNOWN stops, including missing CPU. */
static unsigned bv_snapshot_pair(struct BvSnapshotGuard *g,
    enum BvSnapshotAuthority actualAuthority,enum BvSnapshotAuthority expectedAuthority,
    const unsigned char *actualParty,const unsigned char *expectedParty,
    const unsigned char *actualOther,const unsigned char *expectedOther,unsigned otherBytes,unsigned checkpoint)
{
    g->frames++;
    if((actualAuthority!=BV_SNAPSHOT_VALID && actualAuthority!=BV_SNAPSHOT_TRANSIENT)
        || (expectedAuthority!=BV_SNAPSHOT_VALID && expectedAuthority!=BV_SNAPSHOT_TRANSIENT))return 115;
    if(memcmp(actualOther,expectedOther,otherBytes))return 103;
    if(actualAuthority==BV_SNAPSHOT_VALID && (!actualParty || !bv_snapshot_party_valid(actualParty)))return 116;
    if(expectedAuthority==BV_SNAPSHOT_VALID && (!expectedParty || !bv_snapshot_party_valid(expectedParty)))return 116;
    if(actualAuthority==BV_SNAPSHOT_TRANSIENT || expectedAuthority==BV_SNAPSHOT_TRANSIENT){
        if(checkpoint)return 115;
        g->deferred++;g->pending=1;return 0;
    }
    if(memcmp(actualParty,expectedParty,600))return 103;
    g->valid++;if(g->pending){g->reentries++;g->pending=0;}return 0;
}
