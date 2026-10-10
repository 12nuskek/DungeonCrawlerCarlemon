"""Unchanged native state model plus strictly ordered per-use acknowledgement audit."""
from pathlib import Path
import importlib.util,re,sys
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('gc_retained_state',ROOT/'scripts/floor1/guard-choice-state.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
prior=base.prior;fields=base.fields;friendship=base.friendship;medicine=base.medicine
EMPTY_POKEMON=base.EMPTY_POKEMON;POKEMON_BYTES=base.POKEMON_BYTES;MAIL_OFFSET=base.MAIL_OFFSET;MAIL_NONE=base.MAIL_NONE
snapshot=base.snapshot;change_item=base.change_item;disk_equivalence=base.disk_equivalence;cold_equivalence=base.cold_equivalence
NAMES=base.NAMES

def acknowledgement_audit(log,uses):
    acknowledgements=re.findall(r'^MEDICINE_ACK absolute=(\d+) turn=(\d+) use=(\d+) WAIT=1 owner=2 fresh_A=1 full_state_exact=1$',log,re.M)
    heals=re.findall(r'^MEDICINE_HEAL absolute=(\d+) turn=(\d+) .*$',log,re.M)
    returns=re.findall(r'^MEDICINE_RETURN absolute=(\d+) turn=(\d+) uses=(\d+) full_state_exact=1 ack_frame=(\d+) released=1 printer_done=1 print_task_destroyed=1 party_fade=1 field_order=1 exit=1 setup=1 reshow_entry=1 reshow=1$',log,re.M)
    assert len(acknowledgements)==len(heals)==len(returns)==uses<=2
    assert sum(line.startswith('MEDICINE_ACK') for line in log.splitlines())==uses
    assert sum(line.startswith('MEDICINE_RETURN') for line in log.splitlines())==uses
    last=-1
    for i,(heal,ack,ret) in enumerate(zip(heals,acknowledgements,returns),1):
        hf,ht=map(int,heal);af,at,au=map(int,ack);rf,rt,ru,ra=map(int,ret)
        assert last<hf<=af<rf and ht==at==rt and au==ru==i and ra==af
        last=rf
    return {'uses':uses,'single_fresh_A_each':True,'all_native_closure_stages_observed':True}

def audit(directory=Path('.')):
    positions=base.audit(directory)
    acknowledgement_audit((directory/'runtime.log').read_text(),len(positions))
    return positions

def validate(name,before,after,consumption_positions=None):
    if name=='guard' and consumption_positions is None:consumption_positions=audit()
    return base.validate(name,before,after,consumption_positions=consumption_positions)

if __name__=='__main__':
    name=sys.argv[1];after=snapshot('current-state.bin')
    if name=='cold':cold_equivalence(snapshot('expected-final-state.bin'),after,'game.sav')
    else:validate(name,snapshot('before-state.bin'),after)
    print('PASS complete source-native Guard-choice transition and native acknowledgement '+name)
