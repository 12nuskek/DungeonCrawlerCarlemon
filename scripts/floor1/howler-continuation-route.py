"""Ordinary buttons only; immediate resolved repeat precedes the return leg."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def routes():
    # Exact Continue prefix already observed independently in cold2; this is a
    # new route operand, not authority to replay the old execution.
    cold=(ROOT/'scripts/contracts/f1-c01-guard-choice-cold.route').read_text().splitlines()
    prefix=cold[:cold.index('co cold-verify')]+['co continue-verify']
    outbound=['step 36 64 -','step 40 0 -','step 300 0 -','expect 35 0 37 26 7',
              'step 228 16 -','step 40 0 -','expect 35 0 51 26 7',
              'step 20 128 -','step 40 0 -','expect 35 0 51 27 7']
    inbound=['step 20 64 -','step 40 0 -','expect 35 0 51 26 7',
             'step 228 32 -','step 40 0 -','step 300 0 -','expect 35 1 4 3 7',
             'step 36 128 -','step 40 0 -','expect 35 1 4 5 7']
    lines=prefix+outbound+['phase begin howler','step 1 128 -','step 40 0 -','engage 3600',
        'step 1200 0 howler-start.ppm','pilot donut-heal 36000','step 600 0 howler-victory.ppm',
        'dialog 6000','ready','phase end howler',
        'phase begin howler-repeat','step 1 128 -','step 40 0 -','step 1 1 -',
        'step 400 0 howler-resolved.ppm','co howler-resolved',
        'dialog 3600','ready','step 40 0 -','phase end howler-repeat']+inbound+[
        'phase begin guide-howler','step 1 128 -','step 40 0 -','step 1 1 -',
        'step 400 0 guide-howler.ppm','dialog 3600','ready','step 40 0 -',
        'phase end guide-howler','duo healthy','uses 8 40 2 40','expect 35 1 4 5 7',
        'phase begin save','step 1 8 -','step 120 0 -','co start 0',
        'step 1 128 -','step 20 0 -','co start 1','step 1 128 -','step 20 0 -','co start 2',
        'step 1 1 -','co save-ready','step 1 1 -','co overwrite-ready',
        'step 1 1 -','co save-success','step 1 0 saved-success.ppm','step 600 0 -',
        'ready','phase end save','step 1 0 saved.ppm','quit']
    newcold=cold.copy();newcold[newcold.index('co cold-verify')]='co cold-verify'
    return {'howler-continuation':'\n'.join(lines)+'\n','howler-new-save-cold':'\n'.join(newcold)+'\n'}

def budget(text):
    fixed=sum(int(x.split()[1]) for x in text.splitlines() if x.startswith('step '))
    rows={'fixed_steps':fixed,'encounter':36000,'engage':3600,'dialogue':13200,'three_native_Save_waits':10800}
    return dict(components=rows,total=sum(rows.values()))
