#ifndef GUARD_DCC_BATTLE_POSE_H
#define GUARD_DCC_BATTLE_POSE_H

void DccBattlePoseStart(u16 move);
void DccBattlePoseUpdate(void);
void DccBattlePoseImpact(void);
void DccBattlePoseFaint(u8 battler);
void DccBattlePoseReset(void);

#endif
