"""Optional native Journal appendix; no changes to legacy roots/state/rewards."""
OLD_CLOSE = 'DCC_Live_Journal_Close:\n\treleaseall\n\tend\n'
NEW_CLOSE = '''DCC_Live_Journal_Close:
\tmsgbox DCC_Live_Journal_Text_CombatPrompt, MSGBOX_YESNO
\tgoto_if_eq VAR_RESULT, TRUE, DCC_Live_Journal_CombatNotes
\tgoto DCC_Live_Journal_Exit

DCC_Live_Journal_CombatNotes:
\tmsgbox DCC_Live_Journal_Text_CombatNotes, MSGBOX_DEFAULT

DCC_Live_Journal_Exit:
\treleaseall
\tend
'''
TEXT = r'''
DCC_Live_Journal_Text_CombatPrompt:
\t.string "Read combat notes?$"

DCC_Live_Journal_Text_CombatNotes:
\t.string "STRIKE: Select a target.\nPP means uses remaining.\p"
\t.string "BRACE raises the user's Defense.\nIt only boosts the user.\p"
\t.string "SPARK hits both foes.\nIt normally has two uses.\p"
\t.string "WEAKEN lowers both foes' Attack.\nThe guide restores CARL and DONUT.$"
'''.replace('\\t', '\t')

def extend(legacy_live):
    assert legacy_live.count(OLD_CLOSE) == 1
    output = legacy_live.replace(OLD_CLOSE, NEW_CLOSE).rstrip() + '\n' + TEXT
    assert project(output) == legacy_live
    return output

def project(extended):
    assert extended.count(NEW_CLOSE) == 1 and extended.endswith(TEXT)
    return extended[:-len(TEXT)].replace(NEW_CLOSE, OLD_CLOSE).rstrip() + '\n'
