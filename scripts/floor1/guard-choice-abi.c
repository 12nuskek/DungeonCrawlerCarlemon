/* Compile-only native layout; no ROM, engine writes or gameplay. */
#include "global.h"
#include "main.h"
#include "battle.h"
#include "task.h"
#include "item_menu.h"
#include "party_menu.h"
#include "pokemon.h"
#include "constants/items.h"
#include "constants/party_menu.h"
#include "constants/battle.h"
#include "item.h"
struct GcInternalPrefix {TaskFunc task;MainCallback exitCallback;};
const struct PartyMenu guardPartyLayout={.menuType=PARTY_MENU_TYPE_IN_BATTLE,.layout=PARTY_LAYOUT_DOUBLE,.action=PARTY_ACTION_USE_ITEM};
#define CO_OFFSET(type,field) ((unsigned)&(((type *)0)->field))
const u32 continuousLayout[]={
 sizeof(struct BackupMapLayout),CO_OFFSET(struct BackupMapLayout,width),CO_OFFSET(struct BackupMapLayout,height),CO_OFFSET(struct BackupMapLayout,map),
 sizeof(struct BagPosition),CO_OFFSET(struct BagPosition,location),CO_OFFSET(struct BagPosition,pocket),CO_OFFSET(struct BagPosition,cursorPosition),CO_OFFSET(struct BagPosition,scrollPosition),
 sizeof(struct PartyMenu),CO_OFFSET(struct PartyMenu,slotId),sizeof(struct BattlePokemon),CO_OFFSET(struct BattlePokemon,level),CO_OFFSET(struct BattlePokemon,hp),CO_OFFSET(struct BattleResults,battleTurnCounter),
 sizeof(struct Task),CO_OFFSET(struct Task,data),
 sizeof(struct Pokemon),CO_OFFSET(struct Pokemon,mail),MAIL_NONE,
 CO_OFFSET(struct PartyMenu,action),CO_OFFSET(struct GcInternalPrefix,exitCallback),CO_OFFSET(struct BattleResults,numHealingItemsUsed),
 sizeof(gBattlerPartyIndexes),sizeof(gBattlePartyCurrentOrder),sizeof(gChosenMoveByBattler),sizeof(gChosenActionByBattler),sizeof(struct ItemSlot),
 ITEMMENULOCATION_BATTLE,PARTY_MENU_TYPE_IN_BATTLE,PARTY_ACTION_USE_ITEM,B_ACTION_USE_ITEM
};
