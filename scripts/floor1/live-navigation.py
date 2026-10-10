"""Generate live copy from immutable legacy control flow, with text substitutions."""
from pathlib import Path
import re, importlib.util

ROOTS = ('DCC_Vestibule_Guide', 'DCC_Vestibule_Trial', 'DCC_Service_Mara',
         'DCC_Service_Lev', 'DCC_Service_Tag', 'DCC_Boss_Encounter', 'DCC_Journal')
SOURCES = ('Entrance', 'Vestibule', 'Service', 'Corridor', 'Boss', 'Exit')
TEXT = {
 'DCC_Vestibule_Text_Won': r'The targets fold away. Trial done.\nThe guide is by the north exit.$',
 'DCC_Vestibule_Text_RepeatService': r'CARL and DONUT are fully restored.\nNorth exit: the patrols outside.$',
 'DCC_Vestibule_Text_TrialAdvice': r'Try the training alcove to the east.\nBRACE raises CARL\'s defense.\pWEAKEN lowers both enemies\' attack.\nI restore all your action uses.$',
 'DCC_Vestibule_Text_ReturnAdvice': r'GUIDE: North exit leads outside.\nThe workshop is southeast.\pPress START, then SAVE outside battle.\nA saved rest is one less worry.$',
 'DCC_Service_Text_Offer': r'MARA: I am marking a safe route.\nMy tag bag is east of the workshop.\pBring it back for two SCRAP?\nThe job is optional. You can leave.$',
 'DCC_Service_Text_Waiting': r'MARA: Find my bag outside, east\nof the workshop. Watch the wire.$',
 'DCC_Service_Text_Done': r'MARA: North exit leads outside.\nThe warm door leads to the guide.$',
 'DCC_Service_Text_Lev': r'LEV: I look for supplies. MARA looks\nfor exits. Efficient teamwork.\pEast of her tag, a panel is hollow.\nHer tag is outside the workshop.\pThe workshop\'s north exit goes out.\nThe warm door leads to the guide.$',
 'DCC_Service_Text_Tag': r'A ROUTE TAG, numbered in pencil.\nBring it to MARA in the workshop.$',
 'DCC_Service_Text_TagReserved': r'A note: MARA\'s route supplies.\nFind her in the workshop first.$',
 'DCC_Boss_Text_Won': r'The gate warden is beaten.\nThe southeast stairs go onward.$',
 'DCC_Boss_Text_Locked': r'AI: Clear the landing trial and both\npatrols outside before this fight.$',
 'DCC_Journal_Text_Patrols': r'OBJECTIVE: Clear both patrols.\nUse Quiet Landing\'s north exit.$',
 'DCC_Journal_Text_Guard': r'OBJECTIVE: Clear the guard patrol.\nIt waits south of the warm door.$',
 'DCC_Journal_Text_Howler': r'OBJECTIVE: Clear the howler patrol.\nIts bay is east of the warm door.$',
 'DCC_Journal_Text_Boss': r'OBJECTIVE: Defeat the gate warden.\nIts door is north of the workshop.\pBRACE or WEAKEN answers its windup.$',
 'DCC_Journal_Text_Stairs': r'OBJECTIVE: Use the southeast stairs\nin the warden room. You can return.$',
 'DCC_Journal_Text_Done': r'OPENING CHECKPOINT REACHED.\nMore of Floor 1 is in progress.$',
 'DCC_Journal_Text_Optional': r'OPTIONAL: MARA has a workshop job.\nThe job and wire spur are optional.$',
 'DCC_Journal_Text_QuestActive': r'MARA: Find the tag east of her\nworkshop. Return it for SCRAP.$',
 'DCC_Journal_Text_QuestReturn': r'MARA: You have the ROUTE TAG.\nReturn to her workshop for SCRAP.$',
}

def live(label):
    return 'DCC_Live_' + label.removeprefix('DCC_')

def blocks(engine):
    result = {}
    for name in SOURCES:
        source = (engine / 'data/maps' / ('DCC_' + name) / 'scripts.inc').read_text()
        starts = list(re.finditer(r'^(\w+)::?\s*$', source, re.M))
        for i, match in enumerate(starts):
            end = starts[i + 1].start() if i + 1 < len(starts) else len(source)
            assert match[1] not in result
            result[match[1]] = source[match.start():end].rstrip() + '\n'
    return result

def generate(engine):
    originals = blocks(engine)
    selected = set(ROOTS)
    todo = list(ROOTS)
    order = list(originals)
    successors = dict(zip(order, order[1:]))
    while todo:
        current = todo.pop()
        block = originals[current]
        commands = [line.strip().split()[0] for line in block.splitlines()[1:]
                    if line.strip() and not line.lstrip().startswith('@')]
        # Some original labels intentionally fall through (Guide -> Rest,
        # Journal QuestReturn -> Close). Preserve those edges too.
        if '.string' not in block and commands[-1] not in ('end', 'return', 'goto'):
            following = successors[current]
            if following not in selected:
                selected.add(following); todo.append(following)
        for name in re.findall(r'\bDCC_\w+\b', block):
            if name in originals and name not in selected:
                selected.add(name); todo.append(name)
    assert set(TEXT) <= selected, 'A changed text must be reachable from a live root'
    renames = {name: live(name) for name in selected}
    output = ['@ Generated from legacy scripts by scripts/floor1/live-navigation.py.\n'
              '@ Control flow/state/rewards retained; original adaptation text only.\n']
    for name, original in originals.items():
        if name not in selected:
            continue
        if name in TEXT:
            assert '.string' in original
            # Keep apostrophes literal; assembler strings are double-quoted.
            text = TEXT[name].replace("\\'", "'")
            replacement = original.splitlines()[0] + '\n\t.string "' + text + '"\n'
        else:
            replacement = original
        replacement = re.sub(r'\bDCC_\w+\b', lambda m: renames.get(m[0], m[0]), replacement)
        # Every non-text command remains byte-identical after label normalization.
        inverse = {value: key for key, value in renames.items()}
        normalized = re.sub(r'\bDCC_\w+\b', lambda m: inverse.get(m[0], m[0]), replacement)
        if name not in TEXT:
            assert normalized == original
        output.append(replacement + '\n')
    path = engine / 'data/scripts/dcc_live_navigation.inc'
    path.parent.mkdir(parents=True, exist_ok=True)
    # The legacy control-flow assertions above remain unchanged. The reviewed
    # optional Journal extension is checked separately through its projection.
    spec = importlib.util.spec_from_file_location('journal_notes', Path(__file__).with_name('journal-combat-notes.py'))
    notes = importlib.util.module_from_spec(spec); spec.loader.exec_module(notes)
    path.write_text(notes.extend(''.join(output).rstrip() + '\n'))
    return {name: renames[name] for name in ROOTS}
