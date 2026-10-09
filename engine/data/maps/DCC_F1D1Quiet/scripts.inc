DCC_F1D1Quiet_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_F1D1Quiet_Load
	.byte 0
DCC_F1D1Quiet_Load:
	special DccRestoreMapPresentation
	end
