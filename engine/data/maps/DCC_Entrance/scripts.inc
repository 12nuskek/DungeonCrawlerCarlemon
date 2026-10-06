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
	call DCC_Entrance_AwardReader
	release
	end
DCC_Entrance_CrateAgain:
	msgbox DCC_Entrance_Text_CrateAgain, MSGBOX_DEFAULT
	call DCC_Entrance_AwardReader
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

DCC_Entrance_AwardReader:
	goto_if_set FLAG_DCC_ACH_READER, DCC_Entrance_AwardReaderDone
	setflag FLAG_DCC_ACH_READER
	msgbox DCC_Entrance_Text_Reader, MSGBOX_DEFAULT
DCC_Entrance_AwardReaderDone:
	return

DCC_Entrance_Text_Reader:
	.string "AI: ACHIEVEMENT! Careful Reader.\n"
	.string "The south supply box is unlocked.$"

DCC_Entrance_SupplyBox::
	lock
	faceplayer
	goto_if_set FLAG_DCC_LOOT_SUPPLY, DCC_Entrance_SupplyOpened
	goto_if_unset FLAG_DCC_ACH_READER, DCC_Entrance_SupplyLocked
	additem ITEM_POTION, 2
	goto_if_eq VAR_RESULT, FALSE, DCC_Entrance_SupplyFull
	setflag FLAG_DCC_LOOT_SUPPLY
	msgbox DCC_Entrance_Text_Supply, MSGBOX_DEFAULT
	release
	end
DCC_Entrance_SupplyOpened:
	msgbox DCC_Entrance_Text_SupplyOpened, MSGBOX_DEFAULT
	release
	end
DCC_Entrance_SupplyLocked:
	msgbox DCC_Entrance_Text_SupplyLocked, MSGBOX_DEFAULT
	release
	end
DCC_Entrance_SupplyFull:
	msgbox DCC_Entrance_Text_SupplyFull, MSGBOX_DEFAULT
	release
	end

DCC_Entrance_Text_Supply:
	.string "SUPPLY BOX: Two POTIONS.\n"
	.string "Use INVENTORY to recover health.$"
DCC_Entrance_Text_SupplyOpened:
	.string "Supply box: already opened.\n"
	.string "Two POTIONS were claimed.$"
DCC_Entrance_Text_SupplyLocked:
	.string "Box label: Read the nearby note.\n"
	.string "Even free supplies have paperwork.$"
DCC_Entrance_Text_SupplyFull:
	.string "Two POTIONS will not fit.\n"
	.string "Make room and try this box again.$"
