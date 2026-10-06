DCC_Corridor_MapScripts::
	.byte 0

DCC_Corridor_Guard::
	trainerbattle_double TRAINER_DCC_GUARD, DCC_Corridor_Text_Guard, DCC_Corridor_Text_Defeat, DCC_Corridor_Text_Duo, DCC_Corridor_GuardResult
DCC_Corridor_GuardResult:
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_GUARD, DCC_Corridor_Retry
	special DccRefreshMapPresentation
	msgbox DCC_Corridor_Text_GuardClear, MSGBOX_DEFAULT
	release
	end
DCC_Corridor_Howler::
	trainerbattle_double TRAINER_DCC_HOWLER, DCC_Corridor_Text_Howler, DCC_Corridor_Text_Defeat, DCC_Corridor_Text_Duo, DCC_Corridor_HowlerResult
DCC_Corridor_HowlerResult:
	goto_if_unset TRAINER_FLAGS_START + TRAINER_DCC_HOWLER, DCC_Corridor_Retry
	special DccRefreshMapPresentation
	msgbox DCC_Corridor_Text_HowlerClear, MSGBOX_DEFAULT
	release
	end
DCC_Corridor_Retry:
	msgbox DCC_Corridor_Text_Retry, MSGBOX_DEFAULT
	release
	end
DCC_Corridor_Rules::
	lock
	faceplayer
	msgbox DCC_Corridor_Text_Rules, MSGBOX_DEFAULT
	release
	end
DCC_Corridor_Text_Guard:
	.string "AI: The guard BRACES on its first turn.\n"
	.string "SPARK ignores that raised defense.\p"
	.string "Clear both patrols, then take the\n"
	.string "northeast ladder to the gate chamber.$"
DCC_Corridor_Text_Howler:
	.string "AI: The howler uses WEAKEN every\n"
	.string "third turn. Your STRIKE gets softer.\p"
	.string "SPARK still works. Keep both crawlers\n"
	.string "standing, and rest between patrols.$"
DCC_Corridor_Text_Defeat:
	.string "AI: Patrol cleared. Try not to gloat.$"
DCC_Corridor_Text_Duo:
	.string "Both crawlers must be ready.\n"
	.string "The landing guide restores you.$"
DCC_Corridor_Text_Retry:
	.string "You recover beside the patrol.\n"
	.string "Try again, or return to the guide.$"
DCC_Corridor_Text_GuardClear:
	.string "The guard patrol is cleared.\n"
	.string "It will stay cleared after saving.$"
DCC_Corridor_Text_HowlerClear:
	.string "The howler patrol is cleared.\n"
	.string "It will stay cleared after saving.$"
DCC_Corridor_Text_Rules:
	.string "FLOOR RULE: Cleared rooms stay clear.\n"
	.string "Rest and return without a countdown.\p"
	.string "Clear the trial and both patrols.\n"
	.string "The gate warden guards the staircase.\p"
	.string "The service cache is optional.\n"
	.string "Its blast weakens the warden's gear.$"
