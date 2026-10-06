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
