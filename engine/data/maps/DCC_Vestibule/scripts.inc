DCC_Vestibule_MapScripts::
	.byte 0

DCC_Vestibule_Crate::
	lock
	faceplayer
	goto_if_set FLAG_DCC_WRAP_TAKEN, DCC_Vestibule_WrapTaken
	additem ITEM_DCC_WRIST_WRAP, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Vestibule_WrapNoRoom
	setflag FLAG_DCC_WRAP_TAKEN
	msgbox DCC_Vestibule_Text_Wrap, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_WrapTaken:
	msgbox DCC_Vestibule_Text_WrapTaken, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_WrapNoRoom:
	msgbox DCC_Vestibule_Text_WrapNoRoom, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_Wrap:
	.string "CARL found a WRIST WRAP.\n"
	.string "Finally. Something without teeth.\p"
	.string "Open INVENTORY and GIVE it to CARL.\n"
	.string "Equipped, it strengthens STRIKE.\p"
	.string "It is optional. You can finish the\n"
	.string "trial with or without it.$"
DCC_Vestibule_Text_WrapTaken:
	.string "The crate is empty. Your WRIST WRAP\n"
	.string "is in inventory or on a crawler.$"
DCC_Vestibule_Text_WrapNoRoom:
	.string "Your inventory is full. The wrap\n"
	.string "will wait here until you make room.$"

DCC_Vestibule_Trial::
	trainerbattle_double TRAINER_DCC_TRIAL, DCC_Vestibule_Text_Trial, DCC_Vestibule_Text_Defeat, DCC_Vestibule_Text_NeedDuo, DCC_Vestibule_TrialResolved
DCC_Vestibule_TrialResolved:
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Vestibule_TrialWon
	msgbox DCC_Vestibule_Text_Retry, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_TrialWon:
	goto_if_set FLAG_DCC_ACH_DUO, DCC_Vestibule_TrialWonAgain
	setflag FLAG_DCC_ACH_DUO
	msgbox DCC_Vestibule_Text_DuoAchievement, MSGBOX_DEFAULT
DCC_Vestibule_TrialWonAgain:
	msgbox DCC_Vestibule_Text_Won, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_Trial:
	.string "AI: CARL has STRIKE and BRACE.\n"
	.string "DONUT has SPARK and WEAKEN.\p"
	.string "SPARK has two casts. Choose carefully.\n"
	.string "Defeat restores you. Win, then rest.$"
DCC_Vestibule_Text_Defeat:
	.string "AI: Teamwork. Disturbingly effective.$"
DCC_Vestibule_Text_NeedDuo:
	.string "The trial needs both CARL and DONUT.\n"
	.string "Return when you are both ready.$"
DCC_Vestibule_Text_Retry:
	.string "You both catch your breath.\n"
	.string "The trial can be attempted again.$"
DCC_Vestibule_Text_Won:
	.string "The targets fold away. Trial complete.\n"
	.string "Visit the guide by the south wall.$"

DCC_Vestibule_Guide::
	lock
	faceplayer
	goto_if_set FLAG_DCC_GUIDE_MET, DCC_Vestibule_GuideRest
	msgbox DCC_Vestibule_Text_GuideIntro, MSGBOX_DEFAULT
	setflag FLAG_DCC_GUIDE_MET
DCC_Vestibule_GuideRest:
	special HealPlayerParty
	msgbox DCC_Vestibule_Text_Rested, MSGBOX_DEFAULT
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Vestibule_GuideAfterTrial
	msgbox DCC_Vestibule_Text_TrialAdvice, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_GuideAfterTrial:
	msgbox DCC_Vestibule_Text_ReturnAdvice, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_GuideIntro:
	.string "GUIDE: Take a breath. This room is safe.\n"
	.string "You can rest here as often as you need.\p"
	.string "No fee. No trick. I'd rather explain\n"
	.string "the rules once than carry you twice.$"
DCC_Vestibule_Text_Rested:
	.string "CARL and DONUT recover their health\n"
	.string "and all their action uses.$"
DCC_Vestibule_Text_TrialAdvice:
	.string "Try the rehearsal across the room.\n"
	.string "BRACE raises CARL's defense.\p"
	.string "WEAKEN lowers both enemies' attack.\n"
	.string "I restore all your action uses.$"
DCC_Vestibule_Text_ReturnAdvice:
	.string "GUIDE: You made it back together. Good.\n"
	.string "The ladder returns to the entrance.\p"
	.string "Press START, then SAVE outside battle.\n"
	.string "A saved rest is one less worry.$"

DCC_Vestibule_Text_DuoAchievement:
	.string "AI: ACHIEVEMENT! Better Together.\n"
	.string "The workshop box is unlocked.$"

DCC_Vestibule_WorkshopBox::
	lock
	faceplayer
	goto_if_set FLAG_DCC_LOOT_SCRAP, DCC_Vestibule_WorkshopOpened
	goto_if_unset FLAG_DCC_ACH_DUO, DCC_Vestibule_WorkshopLocked
	additem ITEM_DCC_SCRAP, 2
	goto_if_eq VAR_RESULT, FALSE, DCC_Vestibule_WorkshopFull
	setflag FLAG_DCC_LOOT_SCRAP
	msgbox DCC_Vestibule_Text_Workshop, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_WorkshopOpened:
	msgbox DCC_Vestibule_Text_WorkshopOpened, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_WorkshopLocked:
	msgbox DCC_Vestibule_Text_WorkshopLocked, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_WorkshopFull:
	msgbox DCC_Vestibule_Text_WorkshopFull, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_Workshop:
	.string "WORKSHOP BOX: Two pieces of SCRAP.\n"
	.string "Keep them for a crafting recipe.$"
DCC_Vestibule_Text_WorkshopOpened:
	.string "Workshop box: already opened.\n"
	.string "Two pieces of SCRAP were claimed.$"
DCC_Vestibule_Text_WorkshopLocked:
	.string "Box label: Complete the duo trial.\n"
	.string "Teamwork before tools. How charming.$"
DCC_Vestibule_Text_WorkshopFull:
	.string "Two pieces of SCRAP will not fit.\n"
	.string "Make room and try this box again.$"
