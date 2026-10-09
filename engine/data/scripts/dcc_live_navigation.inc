@ Generated from legacy scripts by scripts/floor1/live-navigation.py.
@ Control flow/state/rewards retained; original adaptation text only.
DCC_Live_Vestibule_Trial::
	trainerbattle_double TRAINER_DCC_TRIAL, DCC_Live_Vestibule_Text_Trial, DCC_Live_Vestibule_Text_Defeat, DCC_Live_Vestibule_Text_NeedDuo, DCC_Live_Vestibule_TrialResolved

DCC_Live_Vestibule_TrialResolved:
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Live_Vestibule_TrialWon
	msgbox DCC_Live_Vestibule_Text_Retry, MSGBOX_DEFAULT
	release
	end

DCC_Live_Vestibule_TrialWon:
	special DccRefreshMapPresentation
	goto_if_set FLAG_DCC_ACH_DUO, DCC_Live_Vestibule_TrialWonAgain
	setflag FLAG_DCC_ACH_DUO
	msgbox DCC_Live_Vestibule_Text_DuoAchievement, MSGBOX_DEFAULT

DCC_Live_Vestibule_TrialWonAgain:
	msgbox DCC_Live_Vestibule_Text_Won, MSGBOX_DEFAULT
	release
	end

DCC_Live_Vestibule_Text_Trial:
	.string "AI: CARL has STRIKE and BRACE.\n"
	.string "DONUT has SPARK and WEAKEN.\p"
	.string "SPARK has two casts. Choose carefully.\n"
	.string "Defeat restores you. Win, then rest.$"

DCC_Live_Vestibule_Text_Defeat:
	.string "AI: Teamwork. Disturbingly effective.$"

DCC_Live_Vestibule_Text_NeedDuo:
	.string "The trial needs both CARL and DONUT.\n"
	.string "Return when you are both ready.$"

DCC_Live_Vestibule_Text_Retry:
	.string "You both catch your breath.\n"
	.string "The trial can be attempted again.$"

DCC_Live_Vestibule_Text_Won:
	.string "The targets fold away. Trial done.\nThe guide is by the north exit.$"

DCC_Live_Vestibule_Guide::
	lock
	faceplayer
	goto_if_set FLAG_DCC_GUIDE_MET, DCC_Live_Vestibule_GuideRepeat
	msgbox DCC_Live_Vestibule_Text_GuideIntro, MSGBOX_DEFAULT
	setflag FLAG_DCC_GUIDE_MET

DCC_Live_Vestibule_GuideRest:
	special HealPlayerParty
	msgbox DCC_Live_Vestibule_Text_Rested, MSGBOX_DEFAULT
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Live_Vestibule_GuideAfterTrial
	msgbox DCC_Live_Vestibule_Text_TrialAdvice, MSGBOX_DEFAULT
	release
	end

DCC_Live_Vestibule_GuideAfterTrial:
	msgbox DCC_Live_Vestibule_Text_ReturnAdvice, MSGBOX_DEFAULT
	release
	end

@ First visit retains the full introduction and tactical/navigation advice.
@ Repeat visits restore exactly the same resources, with one contextual page.

DCC_Live_Vestibule_GuideRepeat:
	special HealPlayerParty
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Live_Vestibule_GuideRepeatAfterTrial
	msgbox DCC_Live_Vestibule_Text_RepeatTrial, MSGBOX_DEFAULT
	release
	end

DCC_Live_Vestibule_GuideRepeatAfterTrial:
	msgbox DCC_Live_Vestibule_Text_RepeatService, MSGBOX_DEFAULT
	release
	end

DCC_Live_Vestibule_Text_RepeatTrial:
	.string "CARL and DONUT are fully restored.\n"
	.string "Try the trial. BRACE and WEAKEN help.$"

DCC_Live_Vestibule_Text_RepeatService:
	.string "CARL and DONUT are fully restored.\nNorth exit: the patrols outside.$"

DCC_Live_Vestibule_Text_GuideIntro:
	.string "GUIDE: Take a breath. This room is safe.\n"
	.string "You can rest here as often as you need.\p"
	.string "No fee. No trick. I'd rather explain\n"
	.string "the rules once than carry you twice.$"

DCC_Live_Vestibule_Text_Rested:
	.string "CARL and DONUT recover their health\n"
	.string "and all their action uses.$"

DCC_Live_Vestibule_Text_TrialAdvice:
	.string "Try the training alcove to the east.\nBRACE raises CARL's defense.\pWEAKEN lowers both enemies' attack.\nI restore all your action uses.$"

DCC_Live_Vestibule_Text_ReturnAdvice:
	.string "GUIDE: North exit leads outside.\nThe workshop is southeast.\pPress START, then SAVE outside battle.\nA saved rest is one less worry.$"

DCC_Live_Vestibule_Text_DuoAchievement:
	.string "AI: ACHIEVEMENT! Better Together.\n"
	.string "The workshop box is unlocked.$"

DCC_Live_Journal::
	lockall
	goto_if_set FLAG_DCC_SLICE_COMPLETE, DCC_Live_Journal_Done
	goto_if_set FLAG_DCC_BOSS_CLEARED, DCC_Live_Journal_Stairs
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Live_Journal_Trial
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_GUARD, DCC_Live_Journal_CheckGuard
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Live_Journal_Howler
	msgbox DCC_Live_Journal_Text_Boss, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_Trial:
	msgbox DCC_Live_Journal_Text_Trial, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_CheckGuard:
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Live_Journal_Patrols
	msgbox DCC_Live_Journal_Text_Guard, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_Howler:
	msgbox DCC_Live_Journal_Text_Howler, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_Patrols:
	msgbox DCC_Live_Journal_Text_Patrols, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_Stairs:
	msgbox DCC_Live_Journal_Text_Stairs, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Rules

DCC_Live_Journal_Done:
	msgbox DCC_Live_Journal_Text_Done, MSGBOX_DEFAULT

DCC_Live_Journal_Rules:
	msgbox DCC_Live_Journal_Text_Rules, MSGBOX_DEFAULT
	goto_if_set FLAG_DCC_QUEST_COMPLETE, DCC_Live_Journal_QuestDone
	goto_if_set FLAG_DCC_QUEST_ACCEPTED, DCC_Live_Journal_QuestActive
	msgbox DCC_Live_Journal_Text_Optional, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Close

DCC_Live_Journal_QuestDone:
	msgbox DCC_Live_Journal_Text_QuestDone, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Close

DCC_Live_Journal_QuestActive:
	goto_if_set FLAG_DCC_TAG_FOUND, DCC_Live_Journal_QuestReturn
	msgbox DCC_Live_Journal_Text_QuestActive, MSGBOX_DEFAULT
	goto DCC_Live_Journal_Close

DCC_Live_Journal_QuestReturn:
	msgbox DCC_Live_Journal_Text_QuestReturn, MSGBOX_DEFAULT

DCC_Live_Journal_Close:
	releaseall
	end

DCC_Live_Journal_Text_Trial:
	.string "OBJECTIVE: Clear the landing trial.\n"
	.string "The guide restores health and actions.$"

DCC_Live_Journal_Text_Patrols:
	.string "OBJECTIVE: Clear both patrols.\nUse Quiet Landing's north exit.$"

DCC_Live_Journal_Text_Guard:
	.string "OBJECTIVE: Clear the guard patrol.\nIt waits south of the warm door.$"

DCC_Live_Journal_Text_Howler:
	.string "OBJECTIVE: Clear the howler patrol.\nIts bay is east of the warm door.$"

DCC_Live_Journal_Text_Boss:
	.string "OBJECTIVE: Defeat the gate warden.\nIts door is north of the workshop.\pBRACE or WEAKEN answers its windup.$"

DCC_Live_Journal_Text_Stairs:
	.string "OBJECTIVE: Use the southeast stairs\nin the warden room. You can return.$"

DCC_Live_Journal_Text_Done:
	.string "OPENING CHECKPOINT REACHED.\nMore of Floor 1 is in progress.$"

DCC_Live_Journal_Text_Rules:
	.string "RULE: Cleared encounters stay cleared.\n"
	.string "The guide restores health and actions.\p"
	.string "Defeat recovers you nearby for free.\n"
	.string "Save outside battle with START, SAVE.$"

DCC_Live_Journal_Text_Optional:
	.string "OPTIONAL: MARA has a workshop job.\nThe job and wire spur are optional.$"

DCC_Live_Journal_Text_QuestActive:
	.string "MARA: Find the tag east of her\nworkshop. Return it for SCRAP.$"

DCC_Live_Journal_Text_QuestReturn:
	.string "MARA: You have the ROUTE TAG.\nReturn to her workshop for SCRAP.$"

DCC_Live_Journal_Text_QuestDone:
	.string "MARA: Route tag returned. Job complete.\n"
	.string "Two scrap make one charge.$"

DCC_Live_Service_Mara::
	lock
	faceplayer
	goto_if_set FLAG_DCC_QUEST_COMPLETE, DCC_Live_Service_MaraDone
	goto_if_set FLAG_DCC_QUEST_ACCEPTED, DCC_Live_Service_MaraAccepted
	msgbox DCC_Live_Service_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, DCC_Live_Service_MaraDecline
	setflag FLAG_DCC_QUEST_ACCEPTED
	clearflag FLAG_DCC_QUEST_DECLINED
	msgbox DCC_Live_Service_Text_Accept, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_MaraDecline:
	setflag FLAG_DCC_QUEST_DECLINED
	msgbox DCC_Live_Service_Text_Decline, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_MaraAccepted:
	checkitem ITEM_DCC_ROUTE_TAG, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Live_Service_MaraWaiting
	additem ITEM_DCC_SCRAP, 2
	goto_if_eq VAR_RESULT, FALSE, DCC_Live_Service_MaraFull
	removeitem ITEM_DCC_ROUTE_TAG, 1
	setflag FLAG_DCC_QUEST_COMPLETE
	msgbox DCC_Live_Service_Text_Complete, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_MaraWaiting:
	msgbox DCC_Live_Service_Text_Waiting, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_MaraFull:
	msgbox DCC_Live_Service_Text_Full, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_MaraDone:
	msgbox DCC_Live_Service_Text_Done, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_Text_Offer:
	.string "MARA: I am marking a safe route.\nMy tag bag is east of the workshop.\pBring it back for two SCRAP?\nThe job is optional. You can leave.$"

DCC_Live_Service_Text_Accept:
	.string "MARA: Thank you. I need a map that\n"
	.string "does not label every room 'panic'.$"

DCC_Live_Service_Text_Decline:
	.string "MARA: Fair enough. Come back if you\n"
	.string "change your mind. Watch the sparks.$"

DCC_Live_Service_Text_Waiting:
	.string "MARA: Find my bag outside, east\nof the workshop. Watch the wire.$"

DCC_Live_Service_Text_Full:
	.string "MARA: No room for two SCRAP.\n"
	.string "Keep the tag until there is space.$"

DCC_Live_Service_Text_Complete:
	.string "MARA takes the ROUTE TAG.\n"
	.string "CARL receives two SCRAP.\p"
	.string "MARA: A route home beats a shortcut\n"
	.string "with teeth. I will mark the safe way.$"

DCC_Live_Service_Text_Done:
	.string "MARA: North exit leads outside.\nThe warm door leads to the guide.$"

DCC_Live_Service_Tag::
	lock
	faceplayer
	goto_if_set FLAG_DCC_TAG_FOUND, DCC_Live_Service_TagEmpty
	goto_if_unset FLAG_DCC_QUEST_ACCEPTED, DCC_Live_Service_TagReserved
	additem ITEM_DCC_ROUTE_TAG, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Live_Service_TagFull
	setflag FLAG_DCC_TAG_FOUND
	msgbox DCC_Live_Service_Text_Tag, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_TagEmpty:
	msgbox DCC_Live_Service_Text_TagEmpty, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_TagReserved:
	msgbox DCC_Live_Service_Text_TagReserved, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_TagFull:
	msgbox DCC_Live_Service_Text_TagFull, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_Text_Tag:
	.string "A ROUTE TAG, numbered in pencil.\nBring it to MARA in the workshop.$"

DCC_Live_Service_Text_TagEmpty:
	.string "The numbered tag was already taken.$"

DCC_Live_Service_Text_TagReserved:
	.string "A note: MARA's route supplies.\nFind her in the workshop first.$"

DCC_Live_Service_Text_TagFull:
	.string "No room for the tag. It stays here.$"

DCC_Live_Service_Lev::
	lock
	faceplayer
	msgbox DCC_Live_Service_Text_Lev, MSGBOX_DEFAULT
	release
	end

DCC_Live_Service_Text_Lev:
	.string "LEV: I look for supplies. MARA looks\nfor exits. Efficient teamwork.\pEast of her tag, a panel is hollow.\nHer tag is outside the workshop.\pThe workshop's north exit goes out.\nThe warm door leads to the guide.$"

DCC_Live_Corridor_Text_Duo:
	.string "Both crawlers must be ready.\n"
	.string "The landing guide restores you.$"

DCC_Live_Boss_Encounter::
	goto_if_set FLAG_DCC_BOSS_CLEARED, DCC_Live_Boss_Already
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Live_Boss_Locked
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_GUARD, DCC_Live_Boss_Locked
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Live_Boss_Locked
	goto_if_set FLAG_DCC_CACHE_BLASTED, DCC_Live_Boss_Prepared
	trainerbattle_double TRAINER_DCC_BOSS, DCC_Live_Boss_Text_Intro, DCC_Live_Boss_Text_Defeat, DCC_Live_Corridor_Text_Duo, DCC_Live_Boss_Result
	end

DCC_Live_Boss_Prepared:
	trainerbattle_double TRAINER_DCC_BOSS_PREPARED, DCC_Live_Boss_Text_Prepared, DCC_Live_Boss_Text_Defeat, DCC_Live_Corridor_Text_Duo, DCC_Live_Boss_Result
	end

DCC_Live_Boss_Result:
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_BOSS, DCC_Live_Boss_Won
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_BOSS_PREPARED, DCC_Live_Boss_Won
	msgbox DCC_Live_Boss_Text_Retry, MSGBOX_DEFAULT
	release
	end

DCC_Live_Boss_Won:
	setflag FLAG_DCC_BOSS_CLEARED
	special DccRefreshMapPresentation
	msgbox DCC_Live_Boss_Text_Won, MSGBOX_DEFAULT
	release
	end

DCC_Live_Boss_Already:
	lock
	faceplayer
	msgbox DCC_Live_Boss_Text_Won, MSGBOX_DEFAULT
	release
	end

DCC_Live_Boss_Locked:
	lock
	faceplayer
	msgbox DCC_Live_Boss_Text_Locked, MSGBOX_DEFAULT
	release
	end

DCC_Live_Boss_Text_Intro:
	.string "AI: The gate warden alternates\n"
	.string "WIND UP, then SLAM. Watch its arms.\p"
	.string "BRACE softens the hit. WEAKEN offsets\n"
	.string "its rising attack. Or strike fast.$"

DCC_Live_Boss_Text_Prepared:
	.string "AI: Your cache blast spoiled the\n"
	.string "warden's supplies. It is weaker now.\p"
	.string "It still alternates WIND UP and SLAM.\n"
	.string "BRACE or WEAKEN can blunt the blow.$"

DCC_Live_Boss_Text_Defeat:
	.string "AI: A staircase. You earned this one.$"

DCC_Live_Boss_Text_Retry:
	.string "You recover at the gate. No progress\n"
	.string "was lost. Rest, prepare, or retry.$"

DCC_Live_Boss_Text_Won:
	.string "The gate warden is beaten.\nThe southeast stairs go onward.$"

DCC_Live_Boss_Text_Locked:
	.string "AI: Clear the landing trial and both\npatrols outside before this fight.$"
