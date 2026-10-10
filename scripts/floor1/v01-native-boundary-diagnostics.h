/* First-failure diagnostics only. No stream reads, seeks or CPU execution. */
#ifndef V01_NATIVE_BOUNDARY_DIAGNOSTICS_H
#define V01_NATIVE_BOUNDARY_DIAGNOSTICS_H
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
enum BvNativeFailureOrigin {
    BV_FAIL_METADATA_SHORT=1, BV_FAIL_METADATA_DIFFERENT, BV_FAIL_METADATA_WRITE,
    BV_FAIL_BOUNDARY_SEQUENCE, BV_FAIL_FRAME_KEYS, BV_FAIL_FRAME_COUNT,
    BV_FAIL_FINISH_SEQUENCE, BV_FAIL_TRAILING_BYTE, BV_FAIL_TRAILING_IO,
    BV_FAIL_FALLBACK
};
enum BvNativeHeaderSource { BV_HEADER_NONE, BV_HEADER_RECORD, BV_HEADER_GUARD, BV_HEADER_OUTPUT };
struct BvNativeMetadata {
    unsigned char actual[29],expected[29];
    unsigned kind,actualBytes,expectedBytes,headerReadBytes,operationReadBytes,writeBytes;
    unsigned actualSource,expectedSource,ioError,eof;
    int ioErrno;
    int64_t startPosition,endPosition;
};
struct BvNativeFailure {
    unsigned present,reason,origin,firstDifference;
    struct BvNativeMetadata metadata;
    uint64_t ordinal,expectedOrdinal;
    unsigned frameCount,expectedCount,video,inputEpoch,lastCount,started,finished;
    unsigned guardVideo,guardExpectedVideo,guardInput,guardExpectedInput;
    unsigned keysAtFrameStart,observedKeys,observedKeysAvailable,trailingPresent,trailingByte;
    unsigned cpuAvailable,pc,lr,sp,cpsr,executionMode,privilegeMode,halted,frame;
    int cycles,nextEvent;
    uint32_t timingCurrent,masterCycles;
    uint64_t globalCycles;
    unsigned eventDue;
};
static inline const char *bv_diag_origin(unsigned origin)
{
    switch(origin){
    case BV_FAIL_METADATA_SHORT:return "metadata_read_short";
    case BV_FAIL_METADATA_DIFFERENT:return "metadata_bytes_differ";
    case BV_FAIL_METADATA_WRITE:return "metadata_write_short";
    case BV_FAIL_BOUNDARY_SEQUENCE:return "boundary_sequence_compare";
    case BV_FAIL_FRAME_KEYS:return "frame_input_keys_changed";
    case BV_FAIL_FRAME_COUNT:return "frame_boundary_count";
    case BV_FAIL_FINISH_SEQUENCE:return "finish_boundary_sequence";
    case BV_FAIL_TRAILING_BYTE:return "finish_trailing_byte";
    case BV_FAIL_TRAILING_IO:return "finish_trailing_read_error";
    default:return "native_fail_fallback";
    }
}
static inline unsigned bv_diag_difference(const struct BvNativeMetadata *m)
{
    unsigned n=m->actualBytes<m->expectedBytes?m->actualBytes:m->expectedBytes;
    for(unsigned i=0;i<n;i++)if(m->actual[i]!=m->expected[i])return i;
    return m->actualBytes!=m->expectedBytes?n:29;
}
static inline unsigned bv_diag_word(const unsigned char *p)
{return p[0]|(unsigned)p[1]<<8|(unsigned)p[2]<<16|(unsigned)p[3]<<24;}
static inline uint64_t bv_diag_ordinal(const unsigned char *p)
{uint64_t n=0;for(unsigned i=0;i<8;i++)n|=(uint64_t)p[i]<<(8*i);return n;}
static inline void bv_diag_decoded(FILE *f,const unsigned char *p,unsigned bytes)
{
    fprintf(f,"{\"available_bytes\":%u",bytes);
    if(bytes>=1)fprintf(f,",\"kind_byte\":%u",p[0]);
    if(bytes>=9)fprintf(f,",\"ordinal\":%llu",(unsigned long long)bv_diag_ordinal(p+1));
    if(bytes>=13)fprintf(f,",\"video_epoch\":%u",bv_diag_word(p+9));
    if(bytes>=17)fprintf(f,",\"input_epoch\":%u",bv_diag_word(p+13));
    if(bytes>=21)fprintf(f,",\"boundary_count\":%u",bv_diag_word(p+17));
    if(bytes>=25)fprintf(f,",\"absolute_frame\":%u",bv_diag_word(p+21));
    fputc('}',f); // Keys at25..28 are private, never in the safe projection.
}
static inline void bv_diag_hex(FILE *f,const unsigned char bytes[29])
{fputc('"',f);for(unsigned i=0;i<29;i++)fprintf(f,"%02x",bytes[i]);fputc('"',f);}
static inline unsigned bv_diag_write(const struct BvNativeFailure *d,const char *path,unsigned privateKeys)
{
    if(!d || !d->present)return 0;
    /* Exclusive create preserves an existing first failure. No overwrite,
     * replay, stream-position changes or new instructions while retaining it. */
    int fd=open(path,O_WRONLY|O_CREAT|O_EXCL,0600);if(fd<0)return 0;
    FILE *f=fdopen(fd,"w");if(!f){close(fd);return 0;}
    const struct BvNativeMetadata *m=&d->metadata;
    fprintf(f,"{\"reason\":%u,\"origin\":\"%s\",\"first_failure\":true,\"requested_record_kind\":%u,\"first_differing_header_offset\":%u,\"no_header_byte_difference_sentinel\":29,\"actual_header_source\":%u,\"expected_header_source\":%u,\"header_source_legend\":\"0 absent,1 original record,2 explicitly derived guard projection,3 intended baseline output\",\"actual_header\":",d->reason,bv_diag_origin(d->origin),m->kind,d->firstDifference,m->actualSource,m->expectedSource);
    bv_diag_decoded(f,m->actual,m->actualBytes);fputs(",\"expected_header\":",f);bv_diag_decoded(f,m->expected,m->expectedBytes);
    fprintf(f,",\"header_read_length\":%u,\"original_operation_read_length\":%u,\"original_write_length\":%u,\"stream_record_start\":%lld,\"stream_position_after_failure\":%lld,\"stream_position_unavailable_sentinel\":-1,\"stream_error\":%u,\"stream_eof\":%u,\"operation_errno\":%d,\"state_ordinal\":%llu,\"guard_expected_ordinal\":%llu,\"state_frame_boundary_count\":%u,\"guard_expected_count\":%u,\"state_video_epoch\":%u,\"state_input_epoch\":%u,\"last_frame_count\":%u,\"started\":%u,\"finished\":%u,\"keys_differ\":%u,\"trailing_byte_present\":%u",m->headerReadBytes,m->operationReadBytes,m->writeBytes,(long long)m->startPosition,(long long)m->endPosition,m->ioError,m->eof,m->ioErrno,(unsigned long long)d->ordinal,(unsigned long long)d->expectedOrdinal,d->frameCount,d->expectedCount,d->video,d->inputEpoch,d->lastCount,d->started,d->finished,d->observedKeysAvailable&&d->keysAtFrameStart!=d->observedKeys,d->trailingPresent);
    fprintf(f,",\"guard_video_epoch\":%u,\"guard_expected_video_epoch\":%u,\"guard_input_epoch\":%u,\"guard_expected_input_epoch\":%u",d->guardVideo,d->guardExpectedVideo,d->guardInput,d->guardExpectedInput);
    fprintf(f,",\"CPU_available\":%u,\"CPU_PC_raw\":%u,\"CPU_LR\":%u,\"CPU_SP\":%u,\"CPU_CPSR\":%u,\"execution_mode\":%u,\"privilege_mode\":%u,\"halted\":%u,\"CPU_cycles\":%d,\"CPU_next_event\":%d,\"event_due\":%u,\"absolute_frame\":%u,\"timing_current\":%u,\"timing_master_cycles\":%u,\"timing_global_cycles\":%llu",d->cpuAvailable,d->pc,d->lr,d->sp,d->cpsr,d->executionMode,d->privilegeMode,d->halted,d->cycles,d->nextEvent,d->eventDue,d->frame,d->timingCurrent,d->masterCycles,(unsigned long long)d->globalCycles);
    if(privateKeys){
        fputs(",\"actual_typed29_hex\":",f);bv_diag_hex(f,m->actual);
        fputs(",\"expected_typed29_hex\":",f);bv_diag_hex(f,m->expected);
        fprintf(f,",\"unread_header_bytes\":\"zero initialised but NOT claimed read/valid; consult available_bytes\",\"keys_at_frame_start\":%u,\"observed_keys\":%u,\"observed_keys_available\":%u,\"trailing_byte\":%u",d->keysAtFrameStart,d->observedKeys,d->observedKeysAvailable,d->trailingByte);
    }else fputs(",\"typed29_headers_keys_trailer\":\"retained privately only; safe projection omits raw bytes and input-key values\"",f);
    fputs("}\n",f);unsigned failed=ferror(f)!=0;if(fclose(f))failed=1;return !failed;
}
#endif
