/* Source-derived stationary route endpoints. Shared production/inert checks. */
static unsigned wc_anchor(const struct CoSnapshot*s,unsigned map,unsigned x,unsigned y,
                          unsigned counter,unsigned poison,unsigned section) {
    return s->group!=35||s->map!=map||s->x!=x||s->y!=y||s->section!=section
        ||s->facing!=1||s->counter!=counter||walk_u16(s->vars+0x54)!=counter
        ||walk_u16(s->vars+0x56)!=poison ? 96 : 0;
}
static unsigned wc_continue_anchor(const struct CoSnapshot*s) {
    return wc_anchor(s,1,4,5,110,0,214);
}
static unsigned wc_cold_anchor(const struct CoSnapshot*s) {
    return wc_anchor(s,4,8,6,20,1,218);
}
static unsigned wc_phase_anchor(const struct CoSnapshot*s,unsigned phase,unsigned before) {
    if(phase>5||before>1)return 96;
    if(phase<2)return wc_anchor(s,3,8,7,7,phase==0&&before?1:0,217);
    if(phase==2||phase==3) {
        if(phase==3&&!before)return wc_anchor(s,4,4,4,14,3,218);
        return wc_anchor(s,3,12,10,14,3,217);
    }
    return wc_cold_anchor(s);
}
