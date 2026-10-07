#ifndef GUARD_CRAWLER_H
#define GUARD_CRAWLER_H
// This fork has permanent protagonists, never collectible creatures.
#define DCC_ALLOW_COLLECTION FALSE
// Membership is explicit: map numbers and trainer ranges are not identities.
bool8 DccIsMap(u8 mapGroup, u8 mapNum);
bool8 DccIsEncounter(u16 trainerId);
void InitCrawlerParty(void);
void DccApplyServiceTrap(void);
void DccRestoreMapPresentation(void);
void DccRefreshMapPresentation(void);
bool8 DccObjectIsResolved(u8 graphicsId);
#endif
