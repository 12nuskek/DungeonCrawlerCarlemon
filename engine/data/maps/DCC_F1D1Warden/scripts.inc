DCC_F1D1Warden_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_F1D1Warden_Load
	.byte 0
DCC_F1D1Warden_Load:
	special DccRestoreMapPresentation
	end
DCC_F1D1Warden_Stairs::
	lockall
	goto_if_unset FLAG_DCC_BOSS_CLEARED, DCC_Boss_StairsLocked
	msgbox DCC_F1D1Warden_StairsText, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, DCC_Boss_StairsCancel
	setflag FLAG_DCC_SLICE_COMPLETE
	warp MAP_DCC_F1D1CHECKPOINT, 4, 4
	waitstate
	releaseall
	end
DCC_F1D1Warden_StairsText:
	.string "Go to the opening checkpoint?\nYou can return from there.$"
