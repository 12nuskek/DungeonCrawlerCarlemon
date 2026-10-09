/* Installed-library introspection + synthetic CPU-register breakpoint probe.
 * No ROM/Save loaded, no reset, runFrame, runLoop, CPU step or gameplay. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <mgba/core/core.h>
#include <mgba/core/version.h>
#include <mgba/gba/core.h>
#include <mgba/internal/arm/arm.h>
#include <mgba/internal/arm/debugger/debugger.h>
#include <mgba/internal/gba/gba.h>
#include "v01-native-boundary-adapter.h"
static unsigned hits;
static struct mDebuggerEntryInfo last;
static void entered(struct mDebugger *d,enum mDebuggerEntryReason reason,struct mDebuggerEntryInfo *info)
{(void)d;assert(reason==DEBUGGER_ENTER_BREAKPOINT && info);last=*info;hits++;}
/* Per-instance custom debugger platform entry hook. Hardware-only; deliberately
 * avoids default ARMDebuggerEnter's nextEvent=cycles scheduling write. No CPU
 * field is changed/restored. Software breakpoints/watchpoints are unsupported. */
static void passive_enter(struct mDebuggerPlatform *p,enum mDebuggerEntryReason reason,struct mDebuggerEntryInfo *info)
{
    assert(reason==DEBUGGER_ENTER_BREAKPOINT && info && info->type.bp.breakType==BREAKPOINT_HARDWARE);
    p->p->entered(p->p,reason,info);p->p->state=DEBUGGER_RUNNING;
}
int main(void)
{
    setvbuf(stdout,NULL,_IONBF,0);
    struct mCore *core=GBACoreCreate();assert(core && core->init(core));
    assert(core->step && core->runFrame && core->runLoop && core->supportsDebuggerType);
    assert(core->supportsDebuggerType(core,DEBUGGER_CUSTOM));
    assert(core->debuggerPlatform && core->attachDebugger && core->detachDebugger);
    struct mDebugger debugger={0};debugger.type=DEBUGGER_CUSTOM;debugger.entered=entered;
    mDebuggerAttach(&debugger,core);assert(core->debugger==&debugger);
    struct mDebuggerPlatform *platform=debugger.platform;
    assert(platform && platform->setBreakpoint && platform->clearBreakpoint && platform->checkBreakpoints);
    assert(platform->getStackTraceMode(platform)==STACK_TRACE_DISABLED);
    platform->entered=passive_enter;
    struct ARMCore *cpu=core->cpu;assert(cpu);
    unsigned frame=core->frameCounter(core);
    // Synthetic register fixture only; there is no game instance or loaded ROM.
    cpu->executionMode=MODE_THUMB;cpu->privilegeMode=MODE_SYSTEM;cpu->cpsr.packed=0x3f;
    cpu->gprs[ARM_PC]=0x080008ae;cpu->gprs[ARM_LR]=0x080004bf;cpu->prefetch[0]=0xb500;
    cpu->halted=0;cpu->cycles=1;cpu->nextEvent=10;
    struct ARMCore original=*cpu;
    struct mBreakpoint bp={.address=0x080008ac,.segment=-1,.type=BREAKPOINT_HARDWARE};
    ssize_t id=platform->setBreakpoint(platform,&bp);assert(id>0);
    assert(!memcmp(cpu,&original,sizeof original)); // No memory shim or opcode patch.
    assert(platform->hasBreakpoints(platform));
    platform->checkBreakpoints(platform);
    assert(hits==1 && last.address==bp.address && last.pointId==id && last.type.bp.breakType==BREAKPOINT_HARDWARE);
    assert(!memcmp(cpu,&original,sizeof original));assert(core->frameCounter(core)==frame);
    struct BvBoundaryAuthority a={1,bp.address,0x080004bf,(unsigned)id};
    struct BvBoundaryCpu c={1,(unsigned)cpu->gprs[ARM_PC],(unsigned)cpu->gprs[ARM_LR],(unsigned)cpu->cpsr.packed,
        cpu->executionMode,cpu->privilegeMode,cpu->halted,cpu->cycles,cpu->nextEvent,cpu->prefetch[0]};
    assert(bv_boundary_authority(&a,&c,1,(unsigned)last.pointId,last.address));
    cpu->gprs[ARM_PC]+=2;platform->checkBreakpoints(platform);assert(hits==1);
    assert(platform->clearBreakpoint(platform,id));assert(!platform->hasBreakpoints(platform));
    printf("PASS installed mGBA version=%s commit=%s: custom debugger attach; passive hardware breakpoint add/hit/clear; Thumb rawPC-width2 semantics; complete ARMCore byte-exact/no CPU/memory/timing scheduling/frame change; step API present, never called\n",projectVersion,gitCommit);
    core->detachDebugger(core);core->deinit(core); // Native core deinit owns/free(core).
    puts("PASS capability probe: no ROM/Save/reset/runFrame/runLoop/CPU instructions/gameplay; zero video frames and execution claims");
    return 0;
}
