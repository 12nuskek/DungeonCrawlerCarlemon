DCC_Entrance_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, DCC_Entrance_FrameTable
	.byte 0

DCC_Entrance_FrameTable:
	map_script_2 VAR_TEMP_0, 0, DCC_Entrance_Intro
	.2byte 0

DCC_Entrance_Intro:
	lockall
	setvar VAR_TEMP_0, 1
	goto_if_set FLAG_DCC_INTRO_SEEN, DCC_Entrance_IntroDone
	msgbox DCC_Entrance_Text_Intro, MSGBOX_DEFAULT
	setflag FLAG_DCC_INTRO_SEEN
DCC_Entrance_IntroDone:
	releaseall
	end

DCC_Entrance_Crate::
	lock
	faceplayer
	goto_if_set FLAG_DCC_CRATE_READ, DCC_Entrance_CrateAgain
	msgbox DCC_Entrance_Text_Crate, MSGBOX_DEFAULT
	setflag FLAG_DCC_CRATE_READ
	release
	end
DCC_Entrance_CrateAgain:
	msgbox DCC_Entrance_Text_CrateAgain, MSGBOX_DEFAULT
	release
	end

DCC_Entrance_Text_Intro:
	.string "CARL: A staircase. A dungeon.\n"
	.string "Sure. That makes this better.\p"
	.string "Donut clings to your shoulder.\n"
	.string "For now, you are both breathing.\p"
	.string "AI: Welcome, crawler. Try walking\n"
	.string "before attempting anything heroic.\p"
	.string "Use the D-pad to move. Face the\n"
	.string "supply crate and press A.$"

DCC_Entrance_Text_Crate:
	.string "A supply crate. Empty, naturally.\p"
	.string "A note reads: START opens the menu.\n"
	.string "Choose SAVE to record your progress.\p"
	.string "The ladder to the northeast leads\n"
	.string "to a quiet landing. You can return.$"

DCC_Entrance_Text_CrateAgain:
	.string "Still empty. You remember the note:\n"
	.string "START, then SAVE. Ladder northeast.$"

DCC_Entrance_Rock::
	lock
	msgbox DCC_Entrance_Text_Rock, MSGBOX_DEFAULT
	release
	end

DCC_Entrance_Text_Rock:
	.string "A heavy chunk of stone. There is\n"
	.string "room to walk around it.$"
