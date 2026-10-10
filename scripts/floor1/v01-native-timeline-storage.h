/* Bounded diagnostic detail, not lossless full-history retention. Observation
 * and strict comparison paths are unchanged. Rotation and SHA summaries run
 * only when the original frame flush runs, outside CPU/event dispatch. */
#ifndef V01_NATIVE_TIMELINE_STORAGE_H
#define V01_NATIVE_TIMELINE_STORAGE_H
#include <limits.h>
enum { BV_TS_ACTIVE_CHUNKS=248+2, BV_TS_STARTUP_CHUNKS=2044+2,
       BV_TS_HEADER=32, BV_TS_SUMMARY_WORDS=46,
       BV_TS_SUMMARY_LIMIT=BV_TL_FRAME_CALLS+1 };
struct BvSha256 {uint32_t h[8];uint64_t bytes;unsigned used;unsigned char block[64];};
static inline uint32_t bv_sha_rotr(uint32_t x,unsigned n){return x>>n|x<<(32-n);}
static inline void bv_sha_block(struct BvSha256 *s)
{
    static const uint32_t k[64]={
        0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
        0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
        0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
        0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
        0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
        0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
        0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
        0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
    uint32_t w[64];for(unsigned i=0;i<16;i++)w[i]=(uint32_t)s->block[4*i]<<24|(uint32_t)s->block[4*i+1]<<16|(uint32_t)s->block[4*i+2]<<8|s->block[4*i+3];
    for(unsigned i=16;i<64;i++){uint32_t x=w[i-15],y=w[i-2];w[i]=w[i-16]+(bv_sha_rotr(x,7)^bv_sha_rotr(x,18)^(x>>3))+w[i-7]+(bv_sha_rotr(y,17)^bv_sha_rotr(y,19)^(y>>10));}
    uint32_t a=s->h[0],b=s->h[1],c=s->h[2],d=s->h[3],e=s->h[4],f=s->h[5],g=s->h[6],h=s->h[7];
    for(unsigned i=0;i<64;i++){uint32_t t1=h+(bv_sha_rotr(e,6)^bv_sha_rotr(e,11)^bv_sha_rotr(e,25))+((e&f)^(~e&g))+k[i]+w[i];
        uint32_t t2=(bv_sha_rotr(a,2)^bv_sha_rotr(a,13)^bv_sha_rotr(a,22))+((a&b)^(a&c)^(b&c));h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;}
    s->h[0]+=a;s->h[1]+=b;s->h[2]+=c;s->h[3]+=d;s->h[4]+=e;s->h[5]+=f;s->h[6]+=g;s->h[7]+=h;
}
static inline void bv_sha_init(struct BvSha256 *s)
{*s=(struct BvSha256){.h={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19}};}
static inline void bv_sha_update(struct BvSha256 *s,const unsigned char *p,size_t n)
{s->bytes+=n;while(n){unsigned take=64-s->used;if(take>n)take=(unsigned)n;memcpy(s->block+s->used,p,take);s->used+=take;p+=take;n-=take;if(s->used==64){bv_sha_block(s);s->used=0;}}}
static inline void bv_sha_end(struct BvSha256 *s,unsigned char out[32])
{
    uint64_t bits=s->bytes*8;unsigned char pad[128]={0x80};unsigned n=s->used<56?56-s->used:120-s->used;
    bv_sha_update(s,pad,n);for(unsigned i=0;i<8;i++)pad[i]=(unsigned char)(bits>>(56-8*i));bv_sha_update(s,pad,8);
    for(unsigned i=0;i<8;i++)for(unsigned j=0;j<4;j++)out[4*i+j]=(unsigned char)(s->h[i]>>(24-8*j));
}
struct BvTimelineStorage {
    FILE *summary;unsigned summaries,chunks,records,anchored,rotate,anchorIndex,boundaries;
    uint64_t anchorOrdinal;unsigned anchorInput,anchorVisual;
    unsigned char chain[32];
};
static inline void bv_ts_pack(unsigned char *bytes,const uint32_t *words,unsigned n)
{for(unsigned j=0;j<n;j++)for(unsigned k=0;k<4;k++)bytes[4*j+k]=(unsigned char)(words[j]>>(8*k));}
static inline unsigned bv_ts_header(FILE *file,const char magic[8],const struct BvTimelineStorage *s)
{
    unsigned char bytes[BV_TS_HEADER];memcpy(bytes,magic,8);
    uint32_t w[6]={BV_TL_WORDS,BV_TL_BUFFER,BV_TS_STARTUP_CHUNKS,BV_TS_ACTIVE_CHUNKS,s->anchorInput,s->anchorVisual};
    bv_ts_pack(bytes+8,w,6);return fwrite(bytes,1,sizeof bytes,file)!=sizeof bytes||fflush(file)||ferror(file)?119:0;
}
static inline unsigned bv_tl_storage_enable(struct BvTimeline *t,const char *summaryPath)
{
    if(!t||!t->file||t->storage||t->total||t->used||t->reason)return 119;
    struct BvTimelineStorage *s=calloc(1,sizeof *s);if(!s)return t->reason=119;
    t->storage=s;int fd=open(summaryPath,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0)return t->reason=119;
    s->summary=fdopen(fd,"wb");if(!s->summary){close(fd);return t->reason=119;}
    /* Only the brand-new recorder file is rewritten, never prior evidence. */
    if(fseeko(t->file,0,SEEK_SET)||ftruncate(fileno(t->file),0)
        ||bv_ts_header(t->file,"BVTD0003",s)||bv_ts_header(s->summary,"BVTS0003",s))return t->reason=119;
    return 0;
}
static inline unsigned bv_tl_storage_boundary(struct BvTimeline *t,uint64_t ordinal)
{
    if(!t||!t->storage)return 0;
    struct BvTimelineStorage *s=t->storage;
    if(t->reason||t->stopped||!t->used||(s->anchored&&ordinal<=s->anchorOrdinal))return t->reason=119;
    /* Called only after the original metadata + complete2560 state compare.
     * The matching passive BEFORE record was appended before the native hook. */
    unsigned at=t->used-1;const uint32_t *w=t->buffer[at].word;
    if(w[BV_TL_EVENT]!=BV_TL_BEFORE||!(w[BV_TL_POINT]&(1u<<BV_TL_WAIT)))return t->reason=119;
    s->anchorIndex=at;s->anchorOrdinal=ordinal;s->anchorInput=t->inputEpoch;s->anchorVisual=t->visualEpoch;
    s->anchored=1;s->rotate=1;s->boundaries++;return 0;
}
static inline unsigned bv_tl_storage_frame(struct BvTimeline *t)
{
    if(!t||!t->storage)return 0;
    struct BvTimelineStorage *s=t->storage;
    if(t->reason)return t->reason;
    if(s->summaries>=BV_TL_FRAME_CALLS||s->chunks>=(s->anchored?BV_TS_ACTIVE_CHUNKS:BV_TS_STARTUP_CHUNKS))return t->reason=119;
    return 0;
}
static inline unsigned bv_tl_storage_write(struct BvTimeline *t)
{
    struct BvTimelineStorage *s=t->storage;unsigned used=t->used,start=s->rotate?s->anchorIndex:0;
    struct BvSha256 frame;bv_sha_init(&frame);
    unsigned char bytes[BV_TL_WORDS*4],digest[32];
    for(unsigned i=0;i<used;i++){bv_ts_pack(bytes,t->buffer[i].word,BV_TL_WORDS);bv_sha_update(&frame,bytes,sizeof bytes);}
    bv_sha_end(&frame,digest);
    if(s->summaries>=BV_TS_SUMMARY_LIMIT||start>used)return t->reason=119;
    if(s->rotate){
        if(fseeko(t->file,0,SEEK_SET)||ftruncate(fileno(t->file),0)||bv_ts_header(t->file,"BVTD0003",s))return t->reason=119;
        s->chunks=s->records=0;
    }
    unsigned count=used-start;
    if(count&&s->chunks>=(s->anchored?BV_TS_ACTIVE_CHUNKS:BV_TS_STARTUP_CHUNKS))return t->reason=119;
    unsigned writeComplete=1;
    for(unsigned i=start;i<used;i++){
        bv_ts_pack(bytes,t->buffer[i].word,BV_TL_WORDS);
        if(fwrite(bytes,1,sizeof bytes,t->file)!=sizeof bytes||ferror(t->file)){t->reason=119;writeComplete=0;break;}
    }
    if(fflush(t->file)||ferror(t->file)){t->reason=119;writeComplete=0;}
    if(writeComplete){s->chunks+=count!=0;s->records+=count;}
    uint32_t w[BV_TS_SUMMARY_WORDS]={s->summaries,t->inputEpoch,t->visualEpoch,
        t->flushReason?t->flushReason:t->reason,(t->flushFinish?1u:0)|(t->flushReason||t->reason?2u:0)|(s->anchored?4u:0),
        used,writeComplete?count:0,s->boundaries,t->total,0,(uint32_t)s->anchorOrdinal,(uint32_t)(s->anchorOrdinal>>32),
        s->anchorInput,s->anchorVisual,s->chunks,s->records,0,s->anchored,start,BV_TS_SUMMARY_WORDS,
        used?t->buffer[used-1].word[BV_TL_RAWPC]:0,used?t->buffer[used-1].word[BV_TL_CPSR]:0};
    unsigned char summary[BV_TS_SUMMARY_WORDS*4];bv_ts_pack(summary,w,BV_TS_SUMMARY_WORDS);
    memcpy(summary+88,s->chain,32);memcpy(summary+120,digest,32);
    struct BvSha256 chain;bv_sha_init(&chain);bv_sha_update(&chain,s->chain,32);bv_sha_update(&chain,summary,88);bv_sha_update(&chain,digest,32);bv_sha_end(&chain,summary+152);
    unsigned summaryComplete=fwrite(summary,1,sizeof summary,s->summary)==sizeof summary;
    if(fflush(s->summary)||ferror(s->summary))summaryComplete=0;
    if(!summaryComplete)t->reason=119;
    else {memcpy(s->chain,summary+152,32);s->summaries++;}
    t->used=0;s->rotate=s->boundaries=0;return t->reason;
}
static inline unsigned bv_tl_storage_close(struct BvTimeline *t)
{if(!t||!t->storage)return 0;unsigned reason=0;if(t->storage->summary&&fclose(t->storage->summary))reason=119;free(t->storage);t->storage=NULL;return reason;}
#endif
