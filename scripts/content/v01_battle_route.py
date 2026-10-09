"""One identical fortify-then-offence route from retained ordinary preboss Save."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def build():
    boot=['step 720 0 -','step 1 8 -','step 360 0 -','step 1 8 -','step 180 0 -','step 1 1 -','step 180 0 -','step 1 1 -','step 600 0 boot.ppm','ready']
    gate=['visual input-exact','candidate 858 fortify','expect 35 3 8 7 7','levels 11 10','duo healthy','vitals 38 30 0 0 8 40 2 40','uses 8 40 2 40','flag 2135 1','flag 2136 1','flag 2137 1','flag 46 0','flag 47 0','flag 48 0','flag 2138 0','flag 2139 0','item 13 1','item 378 2','inventory start','money remember']
    visual=['visual start','step 1 64 -','step 40 0 -','engage 3600','step 1200 0 battle-start.ppm','foes 42 30','battle 1 4 0 8 2 1 0','visual ready','pilot fortify 30000','step 600 0 battle-result.ppm','dialog 6000','ready','expect 35 3 8 7 7','inventory check','money gain 360','vitals record','flag 47 1','visual finish','quit']
    return boot+gate+visual
if __name__=='__main__':
    (ROOT/'scripts/contracts/f1-v01-battle.route').write_text('\n'.join(build())+'\n')
