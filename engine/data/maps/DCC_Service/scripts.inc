DCC_Service_MapScripts::
	map_script MAP_SCRIPT_ON_LOAD, DCC_Service_Load
	.byte 0

DCC_Service_Load:
	setvar VAR_TEMP_0, 0
	goto_if_unset FLAG_DCC_TRAP_SPENT, DCC_Service_LoadDone
	setvar VAR_TEMP_0, 1
DCC_Service_LoadDone:
	end

DCC_Service_Warning::
	lock
	faceplayer
	msgbox DCC_Service_Text_Warning, MSGBOX_DEFAULT
	release
	end
DCC_Service_Text_Warning:
	.string "DANGER: The cracked tile sparks.\n"
	.string "Walk around it. Both sides are clear.\p"
	.string "If shocked, return to the guide.\n"
	.string "Recovery costs nothing.$"

DCC_Service_Trap::
	setvar VAR_TEMP_0, 1
	goto_if_set FLAG_DCC_TRAP_SPENT, DCC_Service_TrapDone
	lockall
	special DccApplyServiceTrap
	setflag FLAG_DCC_TRAP_SPENT
	msgbox DCC_Service_Text_Trap, MSGBOX_DEFAULT
	releaseall
DCC_Service_TrapDone:
	end
DCC_Service_Text_Trap:
	.string "A live wire snaps at CARL.\n"
	.string "The damaged switch burns out.\p"
	.string "If hurt or paralyzed, the guide\n"
	.string "will restore you for free.$"

DCC_Service_Mara::
	lock
	faceplayer
	goto_if_set FLAG_DCC_QUEST_COMPLETE, DCC_Service_MaraDone
	goto_if_set FLAG_DCC_QUEST_ACCEPTED, DCC_Service_MaraAccepted
	msgbox DCC_Service_Text_Offer, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, DCC_Service_MaraDecline
	setflag FLAG_DCC_QUEST_ACCEPTED
	clearflag FLAG_DCC_QUEST_DECLINED
	msgbox DCC_Service_Text_Accept, MSGBOX_DEFAULT
	release
	end
DCC_Service_MaraDecline:
	setflag FLAG_DCC_QUEST_DECLINED
	msgbox DCC_Service_Text_Decline, MSGBOX_DEFAULT
	release
	end
DCC_Service_MaraAccepted:
	checkitem ITEM_DCC_ROUTE_TAG, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Service_MaraWaiting
	additem ITEM_DCC_SCRAP, 2
	goto_if_eq VAR_RESULT, FALSE, DCC_Service_MaraFull
	removeitem ITEM_DCC_ROUTE_TAG, 1
	setflag FLAG_DCC_QUEST_COMPLETE
	msgbox DCC_Service_Text_Complete, MSGBOX_DEFAULT
	release
	end
DCC_Service_MaraWaiting:
	msgbox DCC_Service_Text_Waiting, MSGBOX_DEFAULT
	release
	end
DCC_Service_MaraFull:
	msgbox DCC_Service_Text_Full, MSGBOX_DEFAULT
	release
	end
DCC_Service_MaraDone:
	msgbox DCC_Service_Text_Done, MSGBOX_DEFAULT
	release
	end
DCC_Service_Text_Offer:
	.string "MARA: I am marking a safe route.\n"
	.string "My numbered tag is in the north crate.\p"
	.string "Bring it back for two SCRAP?\n"
	.string "It is optional. The ladder stays open.$"
DCC_Service_Text_Accept:
	.string "MARA: Thank you. I need a map that\n"
	.string "does not label every room 'panic'.$"
DCC_Service_Text_Decline:
	.string "MARA: Fair enough. Come back if you\n"
	.string "change your mind. Watch the sparks.$"
DCC_Service_Text_Waiting:
	.string "MARA: The tag is in the north crate.\n"
	.string "Take either path around the hazard.$"
DCC_Service_Text_Full:
	.string "MARA: No room for two SCRAP.\n"
	.string "Keep the tag until there is space.$"
DCC_Service_Text_Complete:
	.string "MARA takes the ROUTE TAG.\n"
	.string "CARL receives two SCRAP.\p"
	.string "MARA: A route home beats a shortcut\n"
	.string "with teeth. I will mark the safe way.$"
DCC_Service_Text_Done:
	.string "MARA: Your tag helped. The ladder\n"
	.string "leads straight back to the guide.$"

DCC_Service_Tag::
	lock
	faceplayer
	goto_if_set FLAG_DCC_TAG_FOUND, DCC_Service_TagEmpty
	goto_if_unset FLAG_DCC_QUEST_ACCEPTED, DCC_Service_TagReserved
	additem ITEM_DCC_ROUTE_TAG, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Service_TagFull
	setflag FLAG_DCC_TAG_FOUND
	msgbox DCC_Service_Text_Tag, MSGBOX_DEFAULT
	release
	end
DCC_Service_TagEmpty:
	msgbox DCC_Service_Text_TagEmpty, MSGBOX_DEFAULT
	release
	end
DCC_Service_TagReserved:
	msgbox DCC_Service_Text_TagReserved, MSGBOX_DEFAULT
	release
	end
DCC_Service_TagFull:
	msgbox DCC_Service_Text_TagFull, MSGBOX_DEFAULT
	release
	end
DCC_Service_Text_Tag:
	.string "A ROUTE TAG, numbered in pencil.\n"
	.string "Bring it back to MARA.$"
DCC_Service_Text_TagEmpty:
	.string "The numbered tag was already taken.$"
DCC_Service_Text_TagReserved:
	.string "A note: MARA's route supplies.\n"
	.string "Ask her before taking anything.$"
DCC_Service_Text_TagFull:
	.string "No room for the tag. It stays here.$"

DCC_Service_Lev::
	lock
	faceplayer
	msgbox DCC_Service_Text_Lev, MSGBOX_DEFAULT
	release
	end
DCC_Service_Text_Lev:
	.string "LEV: I look for supplies. MARA looks\n"
	.string "for exits. We disagree efficiently.\p"
	.string "Try the north wall, right of the\n"
	.string "crate. One panel sounds hollow.$"

DCC_Service_Secret::
	lockall
	goto_if_set FLAG_DCC_SECRET_TAKEN, DCC_Service_SecretEmpty
	additem ITEM_PARALYZE_HEAL, 1
	goto_if_eq VAR_RESULT, FALSE, DCC_Service_SecretFull
	setflag FLAG_DCC_SECRET_TAKEN
	msgbox DCC_Service_Text_Secret, MSGBOX_DEFAULT
	releaseall
	end
DCC_Service_SecretEmpty:
	msgbox DCC_Service_Text_SecretEmpty, MSGBOX_DEFAULT
	releaseall
	end
DCC_Service_SecretFull:
	msgbox DCC_Service_Text_SecretFull, MSGBOX_DEFAULT
	releaseall
	end
DCC_Service_Text_Secret:
	.string "A hollow panel! Inside: one\n"
	.string "PARLYZ HEAL. A secret worth finding.$"
DCC_Service_Text_SecretEmpty:
	.string "The hidden panel is empty now.$"
DCC_Service_Text_SecretFull:
	.string "No room for the medicine.\n"
	.string "The hidden panel will keep it safe.$"
