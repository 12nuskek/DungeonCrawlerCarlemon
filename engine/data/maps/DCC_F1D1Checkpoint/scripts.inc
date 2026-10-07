DCC_F1D1Checkpoint_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_F1D1Checkpoint_Load
	.byte 0
DCC_F1D1Checkpoint_Load:
	special DccRestoreMapPresentation
	end
DCC_F1D1Checkpoint_Review::
	lock
	faceplayer
	msgbox DCC_F1D1Checkpoint_ReviewText, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Checkpoint_ReviewText:
	.string "OPENING CHECKPOINT\nSave here to keep your progress.\pThe ladder returns to the warden.\nThe rest of Floor 1 is in progress.$"
DCC_F1D1Checkpoint_Donut::
	lock
	faceplayer
	msgbox DCC_F1D1Checkpoint_DonutText, MSGBOX_DEFAULT
	release
	end
DCC_F1D1Checkpoint_DonutText:
	.string "DONUT: Another room survived.\nMy next request is still cushions.$"
