"""Prospective ordinary continuation. Generation has no runtime authority."""
from pathlib import Path
import importlib.util, json
ROOT = Path(__file__).resolve().parents[2]

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result

def native_maps():
    """Production map numbers and sections, independently of graybox names."""
    names={0:'DCC_F1D1Field',1:'DCC_F1D1Quiet',3:'DCC_F1D1Warden',4:'DCC_F1D1Checkpoint'}
    sections=json.loads((ROOT/'engine/src/data/region_map/region_map_sections.json').read_text())['map_sections']
    ids={s['id']:i for i,s in enumerate(sections)}
    return {number:dict(json.loads((ROOT/f'engine/data/maps/{name}/map.json').read_text()),
                        native_name=name,section=ids[json.loads((ROOT/f'engine/data/maps/{name}/map.json').read_text())['region_map_section']])
            for number,name in names.items()}

def routes():
    live = module('wc_live', ROOT/'scripts/floor1/live-route.py')
    geo = module('wc_geo', ROOT/'scripts/floor1/relocation-graybox.py')
    spec = json.loads((ROOT/'scripts/contracts/f1-g01d-relocation.json').read_text())
    walks = [];native=native_maps()
    class Traced(live.Route):
        def follow(self, end):
            end = tuple(end); old_key = self.key
            # This route starts adjacent to, never standing on, a departure warp.
            assert not (end == self.pos and any(tuple(w['at']) == end for w in self.maps[self.key]['warps']))
            path = self.g.path(self.maps[self.key], self.opened, self.pos, end)
            warp = next((w for w in self.maps[self.key]['warps'] if tuple(w['at']) == end), None)
            for a, b in zip(path, path[1:]):
                number=self.ids[old_key]['map_num']
                walks.append(dict(map=number,section=native[number]['section'],before=list(a),after=list(b),
                                  kind='ladder' if warp and b == end else 'ordinary'))
            super().follow(end)
            if warp:
                walks[-1]['destination'] = [self.ids[self.key]['map_num'], *self.pos]
    approach = Traced(spec, geo, 'quiet', (4,5), 1, 7)
    approach.anchor('arrival'); approach.anchor('warden_door'); approach.anchor('warden')
    assert (approach.key, approach.pos) == ('boss', (8,7))
    approach_walks = len(walks)
    inherited = module('wc_tail', ROOT/'scripts/floor1/continuous-opening-route.py').routes()['opening'].splitlines()
    tail = inherited[inherited.index('phase begin boss'):]
    # Reuse the authored dialogue and staircase inputs, with a separately scoped
    # acknowledgement phase and the actual fresh-process Start cursor.
    i = next(i for i, s in enumerate(tail) if s == 'pages opening-checkpoint DCC_F1D1Checkpoint_ReviewText')
    tail.insert(i-4, 'phase begin checkpoint')
    i = tail.index('phase begin save'); tail.insert(i, 'phase end checkpoint')
    start = tail.index('phase begin save')
    tail[start:] = ['phase begin save','step 1 8 -','step 120 0 -','co start 0',
        'step 1 128 -','step 20 0 -','co start 1','step 1 128 -','step 20 0 -','co start 2',
        'step 1 1 -','co save-ready','step 1 1 -','co overwrite-ready','step 1 1 -','co save-success',
        'step 1 0 saved-success.ppm','step 600 0 -','ready','phase end save','step 1 0 saved.ppm','quit']
    # Independently derive the two postbattle walking legs, without duplicating
    # their inherited ordinary inputs. The staircase Yes is a script warp, not
    # a physical step; its zero step-counter delta is intentional.
    post = Traced(spec, geo, 'boss', (8,7), 1, 7, True); post.face = 128
    post.anchor('stairs'); post.key = 'checkpoint'; post.pos = (4,4)
    post.anchor('review')
    prefix = (ROOT/'scripts/contracts/f1-c01-guard-choice-cold.route').read_text().splitlines()
    prefix = prefix[:prefix.index('co cold-verify')]+['co continue-verify']
    cold = module('wc_cold', ROOT/'scripts/floor1/continuous-opening-route.py').routes()['cold']
    return dict(continuation='\n'.join(prefix+approach.lines+tail)+'\n', cold=cold,
                walks=walks, approach_walks=approach_walks)

def counters(walks, counter=110, poison=0):
    events=[]
    for index, row in enumerate(walks):
        assert row['kind'] in ('ordinary','ladder')
        if row['kind']=='ordinary':
            counter=(counter+1)%128;poison=(poison+1)%4
            if counter==0:events.append(index)
    return dict(counter=counter, poison=poison, walking_friendship_events=events,
                physical_steps=len(walks), step_script_updates=sum(r['kind']=='ordinary' for r in walks))

def budget(text):
    rows=dict(fixed_steps=0, engage=0, whole_battle=0, dialogue=0, native_Save=0, ready=0, pages=0)
    for line in text.splitlines():
        bits=line.split()
        if bits[0]=='step': rows['fixed_steps']+=int(bits[1])
        elif bits[0]=='engage': rows['engage']+=int(bits[1])
        elif bits[0]=='pilot':
            assert line=='pilot fortify 30000';rows['whole_battle']+=30000
        elif bits[0]=='dialog':rows['dialogue']+=int(bits[1])
        elif bits[0]=='ready':pass # Assertion only; the native command advances no frame.
        elif bits[0]=='pages':rows['pages']+=32*401
        elif line in ('co save-ready','co overwrite-ready','co save-success'):rows['native_Save']+=3600
    # The whole-battle counter covers intro/sendout/exit as well as pilot. The
    # sum conservatively reserves all individual waits, without reusing credit.
    return dict(components=rows,total=sum(rows.values()))
