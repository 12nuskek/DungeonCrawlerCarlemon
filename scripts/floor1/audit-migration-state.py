#!/usr/bin/env python3
"""Read committed engine state ownership. No game/save edits or allocation."""
from pathlib import Path
import json, re, subprocess, tempfile

ROOT = Path(__file__).resolve().parents[2]
BASE = 'ef5c012aba10b61cbcdbbc3313d7e25c5f448473'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True)

def audit():
    paths = git('ls-tree', '-r', '--name-only', BASE, 'engine').splitlines()
    texts = {p: git('show', BASE + ':' + p) for p in paths
             if Path(p).suffix in ('.h', '.c', '.s', '.inc', '.json')}
    names = sorted(set(re.findall(r'^#define\s+((?:FLAG_|VAR_)\w+)\s',
                         texts['engine/include/constants/flags.h'] + '\n' +
                         texts['engine/include/constants/vars.h'], re.M)))
    bounds = ['TEMP_FLAGS_START', 'TEMP_FLAGS_END', 'DAILY_FLAGS_START',
              'DAILY_FLAGS_END', 'TRAINER_FLAGS_START', 'TRAINER_FLAGS_END',
              'SYSTEM_FLAGS', 'FLAGS_COUNT', 'TEMP_VARS_START', 'TEMP_VARS_END',
              'VARS_START', 'VARS_END', 'VARS_COUNT', 'MAX_TRAINERS_COUNT']
    # Let the actual C preprocessor resolve chained aliases/arithmetic.
    with tempfile.TemporaryDirectory(prefix='dcc-state-') as tmp:
        d = Path(tmp)
        for p in ('flags.h', 'vars.h', 'opponents.h', 'rematches.h'):
            target = d / 'constants' / p; target.parent.mkdir(exist_ok=True)
            target.write_text(texts['engine/include/constants/' + p])
        code = '#include <stdio.h>\n#include "constants/flags.h"\n#include "constants/vars.h"\nint main(void){\n'
        code += ''.join(f'printf("{n}=%u\\n",(unsigned)({n}));\n' for n in names + bounds)
        code += 'return 0;}\n'
        (d / 'audit.c').write_text(code)
        subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-I', str(d),
                        str(d / 'audit.c'), '-o', str(d / 'audit')], check=True)
        values = dict((n, int(v)) for n, v in
                      (x.split('=') for x in subprocess.check_output([str(d / 'audit')], text=True).splitlines()))
    candidates = {'layout_version': ('VAR_', 0x404E), 'opening_loop': ('FLAG_', 0x31)}
    findings = {}; raw_flag_literals = []; array_access = []
    for purpose, (prefix, value) in candidates.items():
        aliases = [n for n in names if n.startswith(prefix) and values[n] == value]
        pattern = re.compile(r'\b(?:' + '|'.join(re.escape(n) for n in aliases) + r')\b')
        hits = []
        for p, content in texts.items():
            for i, line in enumerate(content.splitlines(), 1):
                if pattern.search(line): hits.append({'path': p, 'line': i, 'text': line.strip()})
        assert len(hits) == 1 and hits[0]['text'].startswith('#define'), (purpose, hits)
        findings[purpose] = {'value': value, 'hex': hex(value), 'aliases': aliases,
                             'symbol_references': hits, 'allocated': False}
    flag_api = r'(?:FlagGet|FlagSet|FlagClear|GetFlagPointer)\s*\(\s*(?:49|0[xX]0*31)\b'
    flag_script = r'^\s*(?:setflag|clearflag|checkflag|goto_if_set|goto_if_unset|call_if_set|call_if_unset)\s+(?:49|0[xX]0*31)\b'
    var_api = r'(?:VarGet|VarSet|GetVarPointer)\s*\(\s*(?:16462|0[xX]404[eE])\b'
    var_script = r'^\s*(?:setvar|addvar|subvar|copyvar|copyvarifnotzero|compare|compare_var_to_value|compare_var_to_var)\s+(?:16462|0[xX]404[eE])\b'
    typed_raw = []; raw_var = []
    for p, content in texts.items():
        for i, line in enumerate(content.splitlines(), 1):
            record = {'path': p, 'line': i, 'text': line.strip()}
            if re.search(r'\b(?:49|0[xX]0*31)\b', line): raw_flag_literals.append(record)
            if re.search(r'\b(?:16462|0[xX]404[eE])\b', line): raw_var.append(record)
            if re.search('|'.join((flag_api, flag_script, var_api, var_script)), line): typed_raw.append(record)
            if re.search(r'gSaveBlock1Ptr->(?:flags|vars)\b', line): array_access.append(record)
    assert not typed_raw, typed_raw
    assert len(raw_var) == 1 and raw_var[0]['text'].startswith('#define'), raw_var
    json_state = []
    def visit(obj, path, trail=''):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in ('flag', 'flag_id', 'flagId', 'var', 'var_id', 'trigger'):
                    token = str(v)
                    resolved = values.get(token)
                    if resolved is None:
                        try: resolved = int(token, 0)
                        except ValueError: pass
                    if resolved in (49, 16462): json_state.append({'path': path, 'key': trail + '.' + k, 'value': v})
                visit(v, path, trail + '.' + k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj): visit(v, path, trail + f'[{i}]')
    for p, content in texts.items():
        if p.endswith('.json'): visit(json.loads(content), p)
    assert not json_state, json_state
    assert values['MAX_TRAINERS_COUNT'] == 864 and values['SYSTEM_FLAGS'] == 0x860
    assert values['TEMP_FLAGS_END'] < 49 < values['DAILY_FLAGS_START']
    assert values['TEMP_VARS_END'] < 0x404E <= values['VARS_END']
    groups = json.loads(texts['engine/data/maps/map_groups.json'])
    layouts = json.loads(texts['engine/data/layouts/layouts.json'])['layouts']
    assert len(groups['group_order']) == 35
    old = []
    for i, name in enumerate(groups[groups['group_order'][34]]):
        m = json.loads(texts[f'engine/data/maps/{name}/map.json'])
        layout = next(x for x in layouts if x['id'] == m['layout'])
        old.append({'name': name, 'full_identity': [34, i],
                    'layout_id': layouts.index(layout) + 1, 'dimensions': [layout['width'], layout['height']],
                    'warps': m['warp_events'], 'coord_events': m['coord_events'], 'bg_events': m['bg_events'],
                    'objects': [{'local_id': j + 1, **o} for j, o in enumerate(m['object_events'])]})
    return {'engine_source': BASE, 'method': 'Committed tracked inputs; host C preprocessor evaluates every FLAG_/VAR_ alias. Typed raw calls/opcodes, JSON state keys and all raw literals/direct saved-array references retained for human review. Dynamic indirect accesses require source review; this is not arbitrary C data-flow proof.',
            'candidates': findings, 'bounds': {n: values[n] for n in bounds},
            'owned_dcc_flags': {n: values[n] for n in names if n.startswith('FLAG_DCC_')},
            'typed_raw_candidate_uses': typed_raw, 'json_state_candidate_uses': json_state,
            'raw_var_literals': raw_var, 'raw_flag_literals': raw_flag_literals,
            'saved_array_accesses': array_access, 'legacy_maps': old,
            'proposed_group': 35, 'proposed_layout_start': len(layouts) + 1,
            'status': 'Audit only; engine unchanged. Slots and map IDs are candidates, not live allocations.'}

if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
