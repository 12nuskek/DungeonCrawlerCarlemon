/* Ordinary player strategy. Simultaneous criticals remain an accepted risk. */
static unsigned gc_choice(unsigned c,unsigned cm,unsigned d,unsigned dm,unsigned guard,unsigned scuttler,unsigned n,unsigned strike,unsigned brace) {
    if(c>cm||d>dm||cm>36||dm>28||n>2||strike>8||brace>40||guard>1||scuttler>1)return 103;
    if(!c||!d)return 90;
    if(!guard&&!scuttler)return 0; /* native no-foe resolution; no medicine */
    if(!strike&&brace)return 92;
    unsigned threshold=guard?(scuttler?21u:15u):12u;
    unsigned cr=c<=threshold,dr=scuttler&&d<=12;
    if(cr&&dr)return 100;
    if(!cr&&!dr)return 0;
    if(!n)return 101;
    unsigned hp=cr?c:d,max=cr?cm:dm,cap=hp+20;if(cap>max)cap=max;
    if(cap<=(cr?threshold:12u))return 102;
    return cr?1:2;
}
struct GcFoeAddresses {unsigned count,positions,absent;};
static struct GcFoeAddresses gcf;
static unsigned gc_decision(struct mCore*c,unsigned*guard,unsigned*scuttler) {
    unsigned mons=co.a.mons;
    if(c->busRead8(c,gcf.count)!=4)return 103;
    const unsigned species[]={66,308,52,288};
    for(unsigned i=0;i<4;i++)if(c->busRead8(c,gcf.positions+i)!=i||c->busRead16(c,mons+88*i)!=species[i])return 103;
    if(c->busRead16(c,gc.a.indexes)!=0||c->busRead16(c,gc.a.indexes+4)!=1)return 103;
    unsigned gh=c->busRead16(c,mons+88+40),sh=c->busRead16(c,mons+3*88+40);
    if(c->busRead16(c,mons+88+44)!=29||c->busRead16(c,mons+3*88+44)!=24||gh>29||sh>24)return 103;
    *guard=gh!=0;*scuttler=sh!=0;
    unsigned ch=c->busRead16(c,mons+40),dh=c->busRead16(c,mons+2*88+40),absent=c->busRead8(c,gcf.absent);
    if(!ch||!dh)return 90;
    if((absent&~10u)||(*guard&&(absent&2))||(*scuttler&&(absent&8)))return 103;
    return gc_choice(ch,c->busRead16(c,mons+44),dh,c->busRead16(c,mons+2*88+44),
        *guard,*scuttler,gc_quantity(gc.owned),c->busRead8(c,mons+36),c->busRead8(c,mons+37));
}
