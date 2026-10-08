/* Count every frame entering, inside or leaving battle; permit no 30001st frame. */
static int warden_before_frame(unsigned battleFrames, unsigned inBattle)
{
    return !inBattle || battleFrames<30000;
}
static int warden_after_frame(unsigned battleFrames, unsigned stillInBattle)
{
    return !stillInBattle || battleFrames<30000;
}
