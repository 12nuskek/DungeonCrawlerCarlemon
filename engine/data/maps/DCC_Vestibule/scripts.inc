DCC_Vestibule_MapScripts::
	.byte 0

DCC_Vestibule_Crate::
	lock
	faceplayer
	goto_if_set FLAG_DCC_WRAP_TAKEN, DCC_Vestibule_WrapTaken
	additem ITEM_DCC_WRIST_WRAP, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Vestibule_WrapNoRoom
	setflag FLAG_DCC_WRAP_TAKEN
	special DccRefreshMapPresentation
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
	special DccRefreshMapPresentation
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
	goto_if_set FLAG_DCC_GUIDE_MET, DCC_Vestibule_GuideRepeat
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

@ First visit retains the full introduction and tactical/navigation advice.
@ Repeat visits restore exactly the same resources, with one contextual page.
DCC_Vestibule_GuideRepeat:
	special HealPlayerParty
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Vestibule_GuideRepeatAfterTrial
	msgbox DCC_Vestibule_Text_RepeatTrial, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_GuideRepeatAfterTrial:
	msgbox DCC_Vestibule_Text_RepeatService, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_Text_RepeatTrial:
	.string "CARL and DONUT are fully restored.\n"
	.string "Try the trial. BRACE and WEAKEN help.$"
DCC_Vestibule_Text_RepeatService:
	.string "CARL and DONUT are fully restored.\n"
	.string "West ladder: Service Room.$"

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
	.string "GUIDE: East returns to the entrance.\n"
	.string "West leads to the service room.\p"
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

DCC_Donut_Talk::
	lock
	faceplayer
	msgbox DCC_Donut_Text, MSGBOX_DEFAULT
	release
	end
DCC_Donut_Text:
	.string "DONUT: This room has no cushions.\n"
	.string "I intend to mention that in my review.\p"
	.string "CARL: Let's survive the stairs first.$"

DCC_Journal::
	lockall
	goto_if_set FLAG_DCC_SLICE_COMPLETE, DCC_Journal_Done
	goto_if_set FLAG_DCC_BOSS_CLEARED, DCC_Journal_Stairs
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Journal_Trial
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_GUARD, DCC_Journal_CheckGuard
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Journal_Howler
	msgbox DCC_Journal_Text_Boss, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_Trial:
	msgbox DCC_Journal_Text_Trial, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_CheckGuard:
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Journal_Patrols
	msgbox DCC_Journal_Text_Guard, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_Howler:
	msgbox DCC_Journal_Text_Howler, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_Patrols:
	msgbox DCC_Journal_Text_Patrols, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_Stairs:
	msgbox DCC_Journal_Text_Stairs, MSGBOX_DEFAULT
	goto DCC_Journal_Rules
DCC_Journal_Done:
	msgbox DCC_Journal_Text_Done, MSGBOX_DEFAULT
DCC_Journal_Rules:
	msgbox DCC_Journal_Text_Rules, MSGBOX_DEFAULT
	goto_if_set FLAG_DCC_QUEST_COMPLETE, DCC_Journal_QuestDone
	goto_if_set FLAG_DCC_QUEST_ACCEPTED, DCC_Journal_QuestActive
	msgbox DCC_Journal_Text_Optional, MSGBOX_DEFAULT
	goto DCC_Journal_Close
DCC_Journal_QuestDone:
	msgbox DCC_Journal_Text_QuestDone, MSGBOX_DEFAULT
	goto DCC_Journal_Close
DCC_Journal_QuestActive:
	goto_if_set FLAG_DCC_TAG_FOUND, DCC_Journal_QuestReturn
	msgbox DCC_Journal_Text_QuestActive, MSGBOX_DEFAULT
	goto DCC_Journal_Close
DCC_Journal_QuestReturn:
	msgbox DCC_Journal_Text_QuestReturn, MSGBOX_DEFAULT
DCC_Journal_Close:
	releaseall
	end
DCC_Journal_Text_Trial:
	.string "OBJECTIVE: Clear the landing trial.\n"
	.string "The guide restores health and actions.$"
DCC_Journal_Text_Patrols:
	.string "OBJECTIVE: Clear both gauntlet patrols.\n"
	.string "Use the service room's southwest exit.$"
DCC_Journal_Text_Guard:
	.string "OBJECTIVE: Clear the guard patrol.\n"
	.string "Find it on the gauntlet's west side.$"
DCC_Journal_Text_Howler:
	.string "OBJECTIVE: Clear the howler patrol.\n"
	.string "Find it on the gauntlet's east side.$"
DCC_Journal_Text_Boss:
	.string "OBJECTIVE: Defeat the gate warden.\n"
	.string "BRACE or WEAKEN answers its windup.$"
DCC_Journal_Text_Stairs:
	.string "OBJECTIVE: Examine the gate's northeast\n"
	.string "stairs. You can return after finishing.$"
DCC_Journal_Text_Done:
	.string "SLICE COMPLETE: The next floor waits.\n"
	.string "Explore, save, or return for a review.$"
DCC_Journal_Text_Rules:
	.string "RULE: Cleared encounters stay cleared.\n"
	.string "The guide restores health and actions.\p"
	.string "Defeat recovers you nearby for free.\n"
	.string "Save outside battle with START, SAVE.$"
DCC_Journal_Text_Optional:
	.string "OPTIONAL: Mara has a job in the service\n"
	.string "room. Neither it nor the trap is required.$"
DCC_Journal_Text_QuestActive:
	.string "MARA: Find the tag bag by the north wall\n"
	.string "of the service room. Return it for SCRAP.$"
DCC_Journal_Text_QuestReturn:
	.string "MARA: You have the ROUTE TAG.\n"
	.string "Return it to her for two SCRAP.$"
DCC_Journal_Text_QuestDone:
	.string "MARA: Route tag returned. Job complete.\n"
	.string "Two scrap make one charge.$"
