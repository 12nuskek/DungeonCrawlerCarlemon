/* Host read-only menu gate; requires mCore bus reads, never writes game state. */
#ifndef DCC_POTION_MENU_READINESS_H
#define DCC_POTION_MENU_READINESS_H
static int active_task(struct mCore *core, unsigned tasks, unsigned callback)
{
    if (!tasks || !callback) return 0;
    for (unsigned i=0;i<16;i++)
        if (core->busRead8(core,tasks+40*i+4)
            && (core->busRead32(core,tasks+40*i)&~1u)==(callback&~1u)) return 1;
    return 0;
}
static int menu_ready(struct mCore *core, unsigned tasks, unsigned fade, unsigned callback)
{
    return fade && !(core->busRead8(core,fade+7)&128) && active_task(core,tasks,callback);
}
/* Issuing A is insufficient: only the receiving menu confirms the transition. */
static unsigned acknowledged_stage(unsigned stage, unsigned pending,
    unsigned contextReady, unsigned recipientReady, unsigned selectedItem, unsigned recipient)
{
    if (stage==2 && pending && contextReady && selectedItem==13) return 3;
    if (stage==3 && pending && recipientReady && selectedItem==13 && recipient==0) return 4;
    return stage;
}
#endif
