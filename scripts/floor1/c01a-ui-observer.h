/* Read-only menu observations; native callback identity, no guessed label. */
struct C01Ui {unsigned a[16],candidate,mainstate,battleCB2,exec;FILE *trace;};
static struct C01Ui ui;
static unsigned ui_kind(const char *name)
{const char *names[]={"action","move","target","bag","party","context","summary"};for(unsigned i=0;i<7;i++)if(!strcmp(name,names[i]))return i+1;return 0;}
static unsigned ui_ready(struct mCore *core,struct C01Ui *u,unsigned controls,unsigned tasks,unsigned fade,unsigned actor,unsigned kind)
{
    if(core->busRead8(core,fade+7)&128)return 0;
    if(kind<=3)return (core->busRead8(core,u->mainstate+0x439)&2)
        && (core->busRead32(core,u->mainstate+4)&~1u)==(u->battleCB2&~1u)
        && (core->busRead32(core,u->exec)&(1u<<actor))
        && (core->busRead32(core,controls+4*actor)&~1u)==(u->a[8+kind]&~1u);
    return active_task(core,tasks,u->a[8+kind]);
}
static unsigned ui_sample(struct mCore *core,struct C01Ui *u,struct BvSnapshotContext *c,unsigned mainstate,unsigned tasks,unsigned pixels[],unsigned width,unsigned height)
{
    unsigned char actual[2700]={0},expected[2700];unsigned at=2560;
    unsigned reason=bv_native_snapshot_reader(c,actual);if(reason)return reason;
#define UI_BYTES(address,n) do {for(unsigned z=0;z<(n);z++)actual[at++]=core->busRead8(core,(address)+z);}while(0)
    UI_BYTES(u->exec,4);UI_BYTES(u->a[0],4);UI_BYTES(u->a[1],4);UI_BYTES(u->a[2],4);UI_BYTES(u->a[3],4);
    for(unsigned z=4;z<8;z++){UI_BYTES(u->a[z],1);}
    // No build-address bytes in callback records; full scoped STT_FUNC identities.
    for(unsigned z=0;z<18;z++){
        unsigned address=core->busRead32(core,z<2?mainstate+4*z:tasks+40*(z-2))&~1u;
        if(z>=2 && !core->busRead8(core,tasks+40*(z-2)+4))address=0;
        unsigned id=bv_callback(c->visual,address);if(address && !id)return 112;
        for(unsigned i=0;i<4;i++)actual[at++]=id>>(8*i);
    }
    unsigned sb=core->busRead32(core,c->saveptr);UI_BYTES(sb+0x13f0,2);UI_BYTES(sb+0x234,1);
#undef UI_BYTES
    if(at>sizeof actual)return 124;
    if(u->candidate){if(fread(expected,1,sizeof expected,u->trace)!=sizeof expected || memcmp(actual,expected,sizeof actual))return 124;}
    else if(fwrite(actual,1,sizeof actual,u->trace)!=sizeof actual)return 124;
    char name[80];snprintf(name,sizeof name,"battle-%05u.ppm",c->visual->frames);
    return capture(name,pixels,width,height)?104:0;
}
