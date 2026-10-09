DCC_F1D1Workshop_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_F1D1Workshop_Load
	.byte 0
DCC_F1D1Workshop_Load:
	special DccRestoreMapPresentation
	end
