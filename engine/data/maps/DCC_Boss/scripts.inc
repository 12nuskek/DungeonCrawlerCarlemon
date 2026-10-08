DCC_Boss_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_Boss_Load
	.byte 0

DCC_Boss_Load:
	special DccRestoreMapPresentation
	end

DCC_Boss_Encounter::
	goto_if_set FLAG_DCC_BOSS_CLEARED, DCC_Boss_Already
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_TRIAL, DCC_Boss_Locked
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_GUARD, DCC_Boss_Locked
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Boss_Locked
	goto_if_set FLAG_DCC_CACHE_BLASTED, DCC_Boss_Prepared
	trainerbattle_double TRAINER_DCC_BOSS, DCC_Boss_Text_Intro, DCC_Boss_Text_Defeat, DCC_Corridor_Text_Duo, DCC_Boss_Result
	end
DCC_Boss_Prepared:
	trainerbattle_double TRAINER_DCC_BOSS_PREPARED, DCC_Boss_Text_Prepared, DCC_Boss_Text_Defeat, DCC_Corridor_Text_Duo, DCC_Boss_Result
	end
DCC_Boss_Result:
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_BOSS, DCC_Boss_Won
	goto_if_set TRAINER_FLAGS_START + TRAINER_DCC_BOSS_PREPARED, DCC_Boss_Won
	msgbox DCC_Boss_Text_Retry, MSGBOX_DEFAULT
	release
	end
DCC_Boss_Won:
	setflag FLAG_DCC_BOSS_CLEARED
	special DccRefreshMapPresentation
	msgbox DCC_Boss_Text_Won, MSGBOX_DEFAULT
	release
	end
DCC_Boss_Already:
	lock
	faceplayer
	msgbox DCC_Boss_Text_Won, MSGBOX_DEFAULT
	release
	end
DCC_Boss_Locked:
	lock
	faceplayer
	msgbox DCC_Boss_Text_Locked, MSGBOX_DEFAULT
	release
	end
DCC_Boss_Stairs::
	lockall
	goto_if_unset FLAG_DCC_BOSS_CLEARED, DCC_Boss_StairsLocked
	msgbox DCC_Boss_Text_Stairs, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, DCC_Boss_StairsCancel
	setflag FLAG_DCC_SLICE_COMPLETE
	warp MAP_DCC_EXIT, 4, 6
	waitstate
	releaseall
	end
DCC_Boss_StairsLocked:
	msgbox DCC_Boss_Text_StairsLocked, MSGBOX_DEFAULT
	releaseall
	end
DCC_Boss_StairsCancel:
	msgbox DCC_Boss_Text_StairsCancel, MSGBOX_DEFAULT
	releaseall
	end
DCC_Boss_Text_Intro:
	.string "AI: The gate warden alternates\n"
	.string "WIND UP, then SLAM. Watch its arms.\p"
	.string "BRACE softens each SLAM. WEAKEN\n"
	.string "offsets its attack. Or strike fast.\p"
	.string "The helper hits DONUT on the first\n"
	.string "WIND UP, then every other WIND UP.\p"
	.string "Between those hits, it rests.\n"
	.string "SLAM cannot bypass your support.$"
DCC_Boss_Text_Prepared:
	.string "AI: Your cache blast spoiled the\n"
	.string "warden's supplies. It is weaker now.\p"
	.string "It still alternates WIND UP and SLAM.\n"
	.string "BRACE and WEAKEN reliably soften it.\p"
	.string "The helper hits DONUT on the first\n"
	.string "WIND UP, then every other WIND UP.\p"
	.string "Between those hits, it rests.\n"
	.string "SLAM cannot bypass your support.$"
DCC_Boss_Text_Defeat:
	.string "AI: A staircase. You earned this one.$"
DCC_Boss_Text_Retry:
	.string "You recover at the gate. No progress\n"
	.string "was lost. Rest, prepare, or retry.$"
DCC_Boss_Text_Won:
	.string "The gate warden is beaten. Examine\n"
	.string "the northeast stairs to finish.$"
DCC_Boss_Text_Locked:
	.string "AI: Clear the landing trial and both\n"
	.string "gauntlet patrols before this fight.$"
DCC_Boss_Text_Stairs:
	.string "Finish this playable slice?\n"
	.string "You can return from the review room.$"
DCC_Boss_Text_StairsLocked:
	.string "The stairs are sealed until the\n"
	.string "gate warden is defeated.$"
DCC_Boss_Text_StairsCancel:
	.string "The stairs can wait. Save or recover\n"
	.string "before you continue.$"
