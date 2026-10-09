DCC_F1D1Field_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_F1D1Field_Load
	map_script MAP_SCRIPT_ON_FRAME_TABLE, DCC_F1D1Field_FrameTable
	.byte 0
DCC_F1D1Field_Load:
	special DccRestoreMapPresentation
	setvar VAR_TEMP_0, 0
	goto_if_unset FLAG_DCC_TRAP_SPENT, DCC_F1D1Field_LoadDone
	setvar VAR_TEMP_0, 1
DCC_F1D1Field_LoadDone:
	end
DCC_F1D1Field_FrameTable:
	map_script_2 VAR_TEMP_1, 0, DCC_F1D1Field_Intro
	.2byte 0
DCC_F1D1Field_Intro:
	setvar VAR_TEMP_1, 1
	goto_if_set FLAG_DCC_INTRO_SEEN, DCC_F1D1Field_IntroDone
	lockall
	msgbox DCC_Entrance_Text_Intro, MSGBOX_DEFAULT
	setflag FLAG_DCC_INTRO_SEEN
	releaseall
DCC_F1D1Field_IntroDone:
	end
DCC_F1D1Field_Marker2::
	lock
	msgbox DCC_F1D1Field_MarkerText2, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Field_MarkerText2:
	.string "ROOM SIGN:\nQuiet Landing.$"
DCC_F1D1Field_Marker5::
	lock
	msgbox DCC_F1D1Field_MarkerText5, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Field_MarkerText5:
	.string "ROOM SIGN:\nFar junction; return west.$"
DCC_F1D1Field_Marker6::
	lock
	msgbox DCC_F1D1Field_MarkerText6, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Field_MarkerText6:
	.string "ROOM SIGN:\nWarden doorway.$"
DCC_F1D1Field_Marker7::
	lock
	msgbox DCC_F1D1Field_MarkerText7, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Field_MarkerText7:
	.string "ROOM SIGN:\nOptional workshop.$"
DCC_F1D1Field_Marker8::
	lock
	msgbox DCC_F1D1Field_MarkerText8, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Field_MarkerText8:
	.string "ROOM SIGN:\nOptional secret spur.$"
DCC_F1D1Field_Loop::
	lockall
	special DccTryOpenReturnLoop
	goto_if_eq VAR_RESULT, FALSE, DCC_F1D1Field_LoopLocked
	msgbox DCC_F1D1Field_LoopOpenText, MSGBOX_DEFAULT
	releaseall
	end
DCC_F1D1Field_LoopLocked:
	msgbox DCC_F1D1Field_LoopLockedText, MSGBOX_DEFAULT
	releaseall
	end
DCC_F1D1Field_LoopOpenText:
	.string "The return gate is open.\nThis crossing works both ways.$"
DCC_F1D1Field_LoopLockedText:
	.string "The latch is on the far side.\nFollow the southern route around.$"
