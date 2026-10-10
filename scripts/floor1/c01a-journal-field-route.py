"""One fixed field-only Yes/No/B/reopen route after full battle PASS."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def generate():
    source=(ROOT/'scripts/contracts/f1-c01a-ui-r3.route').read_text().splitlines();startup=source[:9]
    assert len(startup)==9 and all(line.startswith('step ') for line in startup)
    route=[line.replace('boot.ppm','field-boot.ppm') for line in startup]
    route+=['ready','expect 35 3 8 7 7','duo healthy','uses 8 40 2 40','item 13 1','item 378 2','flag 47 0','jf preserve start','snapshot']
    labels=','.join('DCC_Live_Journal_Text_'+n for n in ['Boss','Rules','Optional','CombatPrompt'])
    for i,choice in enumerate(['yes','no','b','repeat']):
        route+=['step 1 8 -','step 120 0 -']
        if i==0:
            for _ in range(4):route+=['step 1 128 -','step 20 0 -']
        route+=['jf start 4','step 1 1 -','step 400 0 -',f'pages {choice}-objective {labels}','jf yesno']
        if choice in ('yes','repeat'):
            route+=['step 1 1 -','step 400 0 -',f'pages {choice}-notes DCC_Live_Journal_Text_CombatNotes','jf answer 1','step 1 2 -',f'step 120 0 after-{choice}.ppm','ready']
        else:
            if choice=='no':route+=['step 1 128 -','step 20 0 -','step 1 1 -']
            else:route+=['step 1 2 -']
            route+=[f'step 120 0 after-{choice}.ppm','ready','jf answer 0']
    route+=['jf preserve end','snapshot','expect 35 3 8 7 7','flag 47 0','uses 8 40 2 40','item 13 1','item 378 2','quit']
    assert len(route)<100 and not any(line.startswith(('engage ','pilot ','battle ','dialog ','save ')) for line in route)
    return '\n'.join(route)+'\n'
