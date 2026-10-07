"""Strict route evidence gate: absent measurements never imply a passing trip."""
from collections import Counter

TRAVEL_NAMES={
    'guard-first':['guard-out','guard-back','howler-out','howler-back'],
    'howler-first':['howler-out','howler-back','guard-out','guard-back'],
    'preboss':['preboss-out','preboss-back'],
}
NONTRAVEL={'guard-first-cold-buffer','howler-first-cold-buffer','preboss-cold-buffer','continuous-motion'}

def validate(route, measurements, spec, ceiling):
    assert route in TRAVEL_NAMES or route in NONTRAVEL,('Unknown route',route)
    expected=TRAVEL_NAMES.get(route,[])
    names=[v['name'] for v in measurements]
    assert Counter(names)==Counter(expected),('Exact measurements required',route,expected,names)
    for v in measurements:
        assert all(type(v[k]) is int and v[k]>=0 for k in ['frames','walking_frames','steps','warps'])
        assert v['frames']>=v['walking_frames']>0
    by_name={v['name']:v for v in measurements}
    for who in ['guard','howler']:
        if who+'-out' in expected:
            pair=[by_name[who+'-'+leg] for leg in ['out','back']]
            limit=ceiling['roundtrips'][who]
            assert all(v['steps']==spec['expected_steps'][who+'_each_leg'] for v in pair)
            assert all(v['walking_frames']<=limit['walking_frames_each_leg'] for v in pair)
            assert sum(v['steps'] for v in pair)<=limit['steps_total']
            assert sum(v['walking_frames'] for v in pair)<=limit['walking_frames_total']
    if route=='preboss':
        pair=[by_name['preboss-'+leg] for leg in ['out','back']]
        assert pair[0]['steps']==spec['expected_steps']['howler_each_leg']
        assert pair[1]['steps']==spec['expected_steps']['guide_to_warden']
        assert sum(v['steps'] for v in pair)==spec['expected_steps']['preboss_total']<=ceiling['preboss']['steps_total']
        assert pair[0]['walking_frames']<=ceiling['preboss']['walking_frames_out']
        assert pair[1]['walking_frames']<=ceiling['preboss']['walking_frames_back']
        assert sum(v['walking_frames'] for v in pair)<=ceiling['preboss']['walking_frames_total']
