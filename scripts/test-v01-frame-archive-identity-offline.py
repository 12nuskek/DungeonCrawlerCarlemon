#!/usr/bin/env python3
"""One bounded inert identity suite. Never invokes a controller or archive decoder."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
SCRATCH = Path('/workspace/scratch')
PREP = SCRATCH / 'v01-frame-archive-proposal-r1-20261011'
TESTS = SCRATCH / 'v01-frame-archive-offline-r1-20261011'
OUT = TESTS / 'identity-closure-offline-r2-20261011'
SOURCE_REVIEW = TESTS / 'identity-closure-source-review-r2-20261011.json'
CAP = 1024**2
MAX_CASES = 2000
STOP_SHA = '1cdf61781a87ceb436934d1b76088dccc60f27b744441b2514e1a849d93516e8'
NATIVE_SHA = '6e125316e3e366e7a20ab8e87e4583383217763f3537a44a9bc17a71342d0aa0'
REVIEW_FILES = ('scripts/floor1/v01-frame-archive-preflight-identity.py',
                'scripts/test-v01-frame-archive-identity-offline.py',
                'docs/floor1/v01-frame-archive-identity-correction-r2-contract.md')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load_module('identity_comparison', ROOT / REVIEW_FILES[0])
m = load_module('read_only_core', ROOT / 'scripts/floor1/v01-frame-archive.py')


def source_snapshot():
    return {p: m.identity(m.FRAMES / p) for p in m.names()}


def sync(directory):
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def save(name, value):
    data = m.encode(value)
    used = max(m.engine.usage(OUT).values())
    m.require(used + len(data) + 4096 + (0 if name == 'STOP-private.json' else 65536) <= CAP,
              'bounded fresh inert receipts with STOP reserve')
    with (OUT / name).open('xb') as file:
        os.fchmod(file.fileno(), 0o600)
        file.write(data); file.flush(); os.fsync(file.fileno())
    sync(OUT)


def wall_limit(*_):
    raise RuntimeError('one inert 240-second limit')


def main():
    start = time.monotonic()
    m.require(not os.path.lexists(OUT), 'one fresh inert check; no retry')
    m.require(not any(os.path.lexists(p) for p in (m.OUT, m.AUTHORITY)), 'no replacement output/authority')
    head = m.git('rev-parse', 'HEAD')
    m.require(not m.git('status', '--porcelain') and head != v.FROZEN_SOURCE and
              m.git('merge-base', v.FROZEN_SOURCE, head) == v.FROZEN_SOURCE,
              'clean separately committed correction; old source pins remain old')
    review = m.load_json(SOURCE_REVIEW)
    reviewed_hashes = {p: m.digest(ROOT / p) for p in REVIEW_FILES}
    m.require(review['PASS'] is True and review['source_commit'] == head and
              review['source_files_SHA256'] == reviewed_hashes and
              review['review_kind'] == 'implementation static source review; not independent review',
              'source review precedes the single bounded check')
    OUT.mkdir(mode=0o700); sync(OUT.parent)
    signal.signal(signal.SIGALRM, wall_limit)
    signal.alarm(240)
    proposal_bytes = (PREP / 'proposal-private.json').read_bytes()
    admission_bytes = (TESTS / 'offline-admission-private.json').read_bytes()
    proposal, admission = json.loads(proposal_bytes), json.loads(admission_bytes)
    history = {name: (Path(v.HISTORY_ROOT) / name).read_bytes() for name in v.HISTORY_FILES}
    inherited = v.sealed_history(history)
    direct_ast = ast.parse((ROOT / 'scripts/floor1/v01-frame-archive.py').read_text())
    literal = next(ast.literal_eval(n.value) for n in direct_ast.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'FILES' for t in n.targets))
    m.require(frozenset(literal) == v.DIRECT_FILES and len(literal) == 6, 'unchanged literal six-file FILES')
    current_sources = {p: m.digest(ROOT / p) for p in v.DIRECT_FILES | v.INHERITED_FILES}
    for path, sha in current_sources.items():
        blob = subprocess.check_output(['git', 'show', v.FROZEN_SOURCE + ':' + path], cwd=ROOT, timeout=10)
        m.require(hashlib.sha256(blob).hexdigest() == sha, 'live bytes match old committed fixture: ' + path)
    providers = m.provider_files()
    stop = TESTS / 'replacement-admission-r1-20261011/preflight-STOP-private.json'
    native = TESTS / 'native-consumer-r1-20261011/native-consumer-result-private.json'
    m.require(m.digest(stop) == STOP_SHA and m.digest(native) == NATIVE_SHA, 'old STOP/native receipts preserved')
    originals = source_snapshot()
    existing = {k: sum(m.engine.usage(p)[k] for p in (PREP, TESTS)) for k in ('logical_bytes', 'allocated_bytes')}
    # Both complete future 6,453,951-byte ledgers, their other receipts, this
    # suite, 2 MiB terminal reserve, directories and authority remain accounted.
    forecast = max(existing.values()) + 12910592 + 1024**2 + CAP + 2 * 1024**2 + 64 * 4096 + 4096
    m.require(forecast <= m.METADATA_CAP, 'aggregate future metadata budget')
    positive = v.validate(proposal_bytes, admission_bytes, history, current_sources, providers, v.FROZEN_SOURCE)
    records = []

    def reject(label, action, reason):
        m.require(len(records) < MAX_CASES, 'fixed inert case bound')
        try:
            action()
        except ValueError as error:
            m.require(str(error).startswith(reason), 'specific negative predicate: ' + label + ': ' + str(error))
            records.append(dict(case=label, rejected=True, reason=str(error)))
        else:
            raise AssertionError('accepted invalid identity fixture: ' + label)

    def compare(a=admission, p=proposal, i=inherited, s=current_sources, d=providers, commit=v.FROZEN_SOURCE):
        return v.compare_closure(a, p, i, s, d, commit, proposal['provider_files_SHA256'])

    for label, original, keys, reason in (
        ('direct', admission['source_files_SHA256'], v.DIRECT_FILES, 'exact six admission files keys'),
        ('inherited', inherited, v.INHERITED_FILES, 'exact fifteen inherited files keys'),
        ('union', proposal['source_files_SHA256'], v.DIRECT_FILES | v.INHERITED_FILES, 'exact twenty-one proposal files keys'),
        ('current', current_sources, v.DIRECT_FILES | v.INHERITED_FILES, 'exact current source files keys'),
    ):
        def check(mapping):
            if label == 'direct':
                a = copy.deepcopy(admission); a['source_files_SHA256'] = mapping; return compare(a=a)
            if label == 'inherited': return compare(i=mapping)
            if label == 'union':
                p = copy.deepcopy(proposal); p['source_files_SHA256'] = mapping; return compare(p=p)
            return compare(s=mapping)
        for key in sorted(keys):
            mapping = dict(original); del mapping[key]
            reject(label + '-missing:' + key, lambda mapping=mapping: check(mapping), reason)
        mapping = dict(original); mapping['unexpected/source.py'] = '0' * 64
        reject(label + '-extra', lambda: check(mapping), reason)

    for kind, keys in (('direct', v.DIRECT_FILES), ('inherited', v.INHERITED_FILES)):
        for key in sorted(keys):
            if kind == 'direct':
                a = copy.deepcopy(admission); a['source_files_SHA256'][key] = '0' * 64
                reject('wrong-direct-hash:' + key, lambda a=a: compare(a=a), 'direct source hash:')
            else:
                i = dict(inherited); i[key] = '0' * 64
                reject('wrong-inherited-six-direct-still-match:' + key, lambda i=i: compare(i=i), 'inherited source hash:')
            s = dict(current_sources); s[key] = '0' * 64
            reject('wrong-current-hash:' + key, lambda s=s: compare(s=s), kind + ' source hash:')
    for hash_value in ('0' * 64, admission['source_files_SHA256'][sorted(v.DIRECT_FILES)[0]]):
        i = dict(inherited); i[sorted(v.DIRECT_FILES)[0]] = hash_value
        reject('conflicting-overlap:' + hash_value, lambda i=i: compare(i=i), 'conflicting direct/inherited overlap')
    for owner in ('admission', 'proposal', 'current'):
        def provider_case(mapping):
            if owner == 'admission':
                a = copy.deepcopy(admission); a['provider_files_SHA256'] = mapping; return compare(a=a)
            if owner == 'proposal':
                p = copy.deepcopy(proposal); p['provider_files_SHA256'] = mapping; return compare(p=p)
            return compare(d=mapping)
        for key in sorted(providers):
            mapping = dict(providers); del mapping[key]
            reject(owner + '-missing-provider:' + key, lambda mapping=mapping: provider_case(mapping), 'exact 222 provider files keys')
            mapping = dict(providers); mapping[key] = '0' * 64
            reject(owner + '-changed-provider:' + key, lambda mapping=mapping: provider_case(mapping), 'exact unchanged provider hashes')
        mapping = dict(providers); mapping['/unexpected/provider'] = '0' * 64
        reject(owner + '-extra-provider', lambda: provider_case(mapping), 'exact 222 provider files keys')
    for commit in ('0' * 40, head):
        reject('stale-current-commit:' + commit, lambda commit=commit: compare(commit=commit), 'unchanged frozen/current source commit')
    for owner in ('admission', 'proposal'):
        a, p = copy.deepcopy(admission), copy.deepcopy(proposal)
        (a if owner == 'admission' else p)['source_commit'] = '0' * 40
        reject('stale-' + owner + '-commit', lambda a=a, p=p: compare(a=a, p=p), 'unchanged frozen/current source commit')
    for name in sorted(history):
        missing = dict(history); del missing[name]
        reject('unbound-history-missing:' + name, lambda missing=missing: v.sealed_history(missing), 'exact historical receipt bundle')
        replaced = dict(history); replaced[name] += b' '
        reason = 'sealed historical handoff' if name == 'execution-final-handoff-private.json' else 'historical artifact seal:'
        reject('replaced-history:' + name, lambda replaced=replaced: v.sealed_history(replaced), reason)
    extra = dict(history); extra['unexpected.json'] = b'{}'
    reject('unbound-history-extra', lambda: v.sealed_history(extra), 'exact historical receipt bundle')
    reject('replaced-proposal-bytes', lambda: v.validate(proposal_bytes + b' ', admission_bytes, history, current_sources, providers, v.FROZEN_SOURCE), 'exact frozen proposal receipt')
    reject('replaced-admission-bytes', lambda: v.validate(proposal_bytes, admission_bytes + b' ', history, current_sources, providers, v.FROZEN_SOURCE), 'exact frozen offline admission receipt')
    m.require(source_snapshot() == originals and not m.git('status', '--porcelain') and
              m.git('rev-parse', 'HEAD') == head and m.digest(stop) == STOP_SHA and m.digest(native) == NATIVE_SHA and
              not any(os.path.lexists(p) for p in (m.OUT, m.AUTHORITY)), 'originals/source/history untouched')
    result = dict(PASS=True, reviewed_source_commit=head, frozen_comparison_source_commit=v.FROZEN_SOURCE,
                  positive_commit_identity_is_explicit_inert_fixture=True,
                  actual_current_checkout_rejected_by_frozen_comparison=True,
                  original_21_files_current_and_frozen_blob_hashes_match=True,
                  positive_case=positive, negative_case_count=len(records), negative_cases=records,
                  preserved_STOP_SHA256=STOP_SHA, preserved_native_receipt_SHA256=NATIVE_SHA,
                  history_bundle_SHA256={name: v.digest(data) for name, data in history.items()},
                  source_review_receipt_SHA256=m.digest(SOURCE_REVIEW),
                  reviewed_source_files_SHA256=reviewed_hashes,
                  compared_source_files_SHA256=current_sources, provider_files_SHA256=providers,
                  original_identity_count_before_after=len(originals), one_inert_suite_run=True,
                  internal_wall_limit_seconds=240, outer_wall_limit_seconds=300,
                  elapsed_ms=int((time.monotonic()-start)*1000), private_receipt_cap_bytes=CAP,
                  aggregate_metadata_forecast_bytes=forecast, aggregate_metadata_cap_bytes=m.METADATA_CAP,
                  actual_authorities=0, actual_controllers=0, actual_archive_verifier_processes=0,
                  actual_replacements=0, actual_compression_processes=0, actual_materializations=0,
                  gameplay_processes=0, uploads=0, merges=0, dashboard_edits=0, retries=0,
                  execution_permitted=False, runtime='CLOSED', independent_backup_verified=False)
    save('identity-comparison-private.json', result)
    signal.alarm(0)
    print('PASS exact 6+15=21 closure / 222 providers; one positive and', len(records), 'negative cases')
    print('private receipt SHA256', m.digest(OUT / 'identity-comparison-private.json'))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        signal.alarm(0)
        if OUT.is_dir() and not (OUT / 'STOP-private.json').exists():
            save('STOP-private.json', dict(PASS=False, error=type(error).__name__ + ': ' + str(error),
                 first_failure_terminal=True, retry_permitted=False, runtime='CLOSED',
                 actual_authorities=0, actual_controllers=0, actual_archive_verifier_processes=0))
        raise
