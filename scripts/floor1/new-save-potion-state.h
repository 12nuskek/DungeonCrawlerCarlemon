/* Fresh ordinary inputs: capped Potion healing, with no historical HP fixture. */
static unsigned new_save_potion_hp(unsigned hp, unsigned maximum)
{
    unsigned missing=maximum-hp;
    return hp+(missing<20?missing:20);
}
static int new_save_potion_decision(unsigned trainer, unsigned turn, unsigned actor,
    unsigned hp, unsigned maximum, unsigned donutHp, unsigned owned)
{
    return trainer==856 && turn==4 && actor==0 && hp>0 && hp<maximum
        && donutHp>0 && owned==1;
}
