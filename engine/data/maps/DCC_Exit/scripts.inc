DCC_Exit_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, DCC_Exit_FrameTable
	.byte 0
DCC_Exit_FrameTable:
	map_script_2 VAR_TEMP_0, 0, DCC_Exit_Complete
	.2byte 0
DCC_Exit_Complete:
	lockall
	setvar VAR_TEMP_0, 1
	msgbox DCC_Exit_Text_Complete, MSGBOX_DEFAULT
	releaseall
	end
DCC_Exit_Review::
	lock
	faceplayer
	msgbox DCC_Exit_Text_Complete, MSGBOX_DEFAULT
	release
	end
DCC_Exit_Text_Complete:
	.string "PLAYABLE SLICE COMPLETE\n"
	.string "CARL and DONUT reached the stairs.\p"
	.string "Save here to keep your progress.\n"
	.string "The west ladder returns to the gate.\p"
	.string "More floors await after playtest\n"
	.string "review. Thanks for crawling with us.$"

DCC_Exit_Donut_Talk::
	lock
	faceplayer
	msgbox DCC_Exit_Text_Donut, MSGBOX_DEFAULT
	release
	end
DCC_Exit_Text_Donut:
	.string "DONUT: We reached the stairs, Carl.\n"
	.string "My review still mentions cushions.\p"
	.string "CARL: Put 'still alive' at the top.$"
