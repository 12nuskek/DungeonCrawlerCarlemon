/* Bag/party tasks exist during setup. Inputs require the running menu callback. */
static int recovery_field_ready(struct mCore *core, unsigned mainstate, unsigned expectedMain,
    unsigned tasks, unsigned fade, unsigned callback)
{
    return mainstate && expectedMain
        && (core->busRead32(core,mainstate+4)&~1u)==(expectedMain&~1u)
        && menu_ready(core,tasks,fade,callback);
}
