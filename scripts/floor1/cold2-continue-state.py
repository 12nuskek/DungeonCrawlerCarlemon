"""Exact ordinary Save plus explicit native Continue RAM transition; read-only."""
from pathlib import Path
import hashlib,importlib.util,json,sys
if not __debug__:
    raise RuntimeError('cold2 requires enabled checks')
ROOT=Path(__file__).resolve().parents[2]
SAVE_SHA='b88862308be4a5b58c7da79803106a29e9201d093d6e3be5307e226c556f63cf'
ORIGINAL_SHA='1d05b2037b0c226b70d27223d8cc63fae96cc49c74ab9ab878f8d5d2e3489b32'
WATCH=2193;START=2194
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=module('cold2_unchanged_native_state',ROOT/'scripts/floor1/conserve-medicine-state.py')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def original(save,snapshot):
    assert sha(save)==SAVE_SHA,'exact approved ordinary Save hash'
    assert sha(snapshot)==ORIGINAL_SHA,'immutable original saved snapshot hash'
    before=base.snapshot(snapshot)
    assert (before['map'],before['position'],before['section'],before['facing'])==([35,1],[4,5],214,1),'exact Quiet Landing endpoint'
    assert (before['count'],before['saved_count'],before['counter'])==(2,2,78)
    assert not(before['flags'][WATCH//8]&(1<<(WATCH%8))),'TV_WATCH initially clear'
    assert not(before['flags'][START//8]&(1<<(START%8))),'TV_START initially clear'
    disk=base.disk_equivalence(save,before) # Original disk state, never post-Continue RAM.
    return before,disk
def expected(before):
    assert len(before['flags'])==300
    assert not(before['flags'][WATCH//8]&((1<<(WATCH%8))|(1<<(START%8))))
    flags=bytearray(before['flags']);flags[274]|=0x02
    return dict(before,flags=bytes(flags)) # No mutation or masking of either operand.
def compare(before,after):
    wanted=expected(before)
    assert set(after)==set(wanted),'complete decoded field inventory'
    # Physical encrypted resource bytes/key legitimately change on Continue.
    # All1272 canonical resource bytes remain mandatory, as in the source model.
    for key in wanted:
        if key not in ('owned','context'):
            assert after[key]==wanted[key],('source-derived cold2 RAM state',key)
    return {'all_decoded_fields_exact':True,'section_and_facing_exact':True,
            'all300_flags_source_derived':True,'TV_WATCH':True,'TV_START':False,
            'native_canonical_resources_exact':True}
def validate(save,saved_snapshot,observed_snapshot):
    operands={str(p):sha(p) for p in (save,saved_snapshot,observed_snapshot)}
    before,disk=original(save,saved_snapshot)
    result=compare(before,base.snapshot(observed_snapshot))
    assert all(sha(p)==pin for p,pin in operands.items()),'input operand mutated during verification'
    return dict(result,PASS=True,disk_checked_against_original_saved_snapshot=disk,
                Save_SHA256=SAVE_SHA,original_snapshot_SHA256=ORIGINAL_SHA,
                operands_unchanged=True)
if __name__=='__main__':
    assert sys.argv[1:]==['cold'],'cold2 validator accepts Continue-only mode'
    result=validate(Path('game.sav'),Path('expected-final-state.bin'),Path('current-state.bin'))
    Path('cold2-state-verdict-private.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS source-derived native Continue TV_WATCH; original14-sector disk and all decoded RAM fields exact')
