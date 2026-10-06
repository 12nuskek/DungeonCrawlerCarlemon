DCC_Vestibule_MapScripts::
	.byte 0

DCC_Vestibule_Crate::
	lock
	faceplayer
	msgbox DCC_Vestibule_Text_Crate, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_Crate:
	.string "CARL: Quiet. I'll take quiet.\p"
	.string "This landing is safe to explore.\n"
	.string "The ladder leads back to the entrance.\p"
	.string "For the moment, there is nothing\n"
	.string "chasing you.$"

DCC_Vestibule_Trial::
	trainerbattle_double TRAINER_DCC_TRIAL, DCC_Vestibule_Text_Trial, DCC_Vestibule_Text_Defeat, DCC_Vestibule_Text_NeedDuo, DCC_Vestibule_TrialResolved
DCC_Vestibule_TrialResolved:
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Vestibule_TrialWon
	msgbox DCC_Vestibule_Text_Retry, MSGBOX_DEFAULT
	release
	end
DCC_Vestibule_TrialWon:
	msgbox DCC_Vestibule_Text_Won, MSGBOX_DEFAULT
	release
	end

DCC_Vestibule_Text_Trial:
	.string "AI: A little rehearsal. Two targets,\n"
	.string "two crawlers. Try helping each other.\p"
	.string "Choose an action for CARL, then DONUT.\n"
	.string "This trial restores you both afterward.$"
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
	.string "CARL and DONUT are both restored.$"
