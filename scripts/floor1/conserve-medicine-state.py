"""Unchanged full native state/medicine/Save/cold validators; new choice only."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[2]
def module(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('conserve_native_state',ROOT/'scripts/floor1/guard-choice-r2-state.py')
medicine=module('conserve_choice_model',ROOT/'scripts/floor1/conserve-medicine-model.py')
prior=base.prior;fields=base.fields;friendship=base.friendship
EMPTY_POKEMON=base.EMPTY_POKEMON;POKEMON_BYTES=base.POKEMON_BYTES;MAIL_OFFSET=base.MAIL_OFFSET;MAIL_NONE=base.MAIL_NONE
snapshot=base.snapshot;change_item=base.change_item;disk_equivalence=base.disk_equivalence;cold_equivalence=base.cold_equivalence
NAMES=base.NAMES;audit=base.audit;validate=base.validate;acknowledgement_audit=base.acknowledgement_audit
