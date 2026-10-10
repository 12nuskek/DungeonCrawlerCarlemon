"""Source-backed ordinary player strategy; simultaneous critical risk retained."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('unchanged_native_medicine',Path(__file__).with_name('guard-choice-model.py'))
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
remove=base.remove;compact=base.compact;order=base.order;to_ui=base.to_ui;to_field=base.to_field;healed=base.healed
def choice(carl_hp,carl_max,donut_hp,donut_max,guard_alive,scuttler_alive,potions,strike,brace):
    assert isinstance(guard_alive,bool) and isinstance(scuttler_alive,bool)
    assert all(isinstance(x,int) for x in (carl_hp,carl_max,donut_hp,donut_max,potions,strike,brace))
    assert 0<=carl_hp<=carl_max<=36 and 0<=donut_hp<=donut_max<=28
    assert 0<=potions<=2 and 0<=strike<=8 and 0<=brace<=40
    if not carl_hp or not donut_hp:return 90
    if not guard_alive and not scuttler_alive:return 0
    if not strike and brace:return 92
    threshold=(21 if scuttler_alive else 15) if guard_alive else 12
    risk=(carl_hp<=threshold,scuttler_alive and donut_hp<=12)
    if all(risk):return 100
    if not any(risk):return 0
    if not potions:return 101
    target=0 if risk[0] else 1;hp=(carl_hp,donut_hp)[target];maximum=(carl_max,donut_max)[target]
    if min(hp+20,maximum)<=(threshold if target==0 else 12):return 102
    return target+1
