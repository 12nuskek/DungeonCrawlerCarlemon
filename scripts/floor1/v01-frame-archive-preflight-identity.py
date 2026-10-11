"""Read-only identity comparison; no execution, authority or filesystem mutation API.

The old admission seals six direct files. The separately sealed Howler history
supplies fifteen inherited files. Validation requires their exact disjoint union,
not admission/proposal equality or an arbitrary subset. Old commit pins are never
rebound to a later checkout by this correction.
"""
import hashlib
import json
import re

FROZEN_SOURCE = '3fa36fb0f18e3fb8db4fe6a647992d4764bd6543'
HISTORICAL_SOURCE = '61c181d6fe67a9b9987351e63daf353449826ce7'
PROPOSAL_SHA = '4d92865f5eba94a74b8f8acb0d9d5bb24e34aa53f881976f6fe69fc5e2fdc9c1'
ADMISSION_SHA = 'ab7e951570ff58f15d9988a18cb2af27f6d8b3dbc88fce7ef1961cb8a2295da8'
HISTORY_ROOT = '/workspace/scratch/howler-rgb-preservation-r1-20261011/'
HISTORY_HANDOFF_SHA = '78e19cda733e7310a0dde92c0fa731ba0395d0443d38e97c3e80979f5fc6e0d0'
HISTORY_CONTRACT_SHA = '27ed6ea1bb3f0d7441c5eda4e7f2261aa156e59ae387312bf5a6921a3b1e953c'
DIRECT_FILES = frozenset((
    'scripts/floor1/v01-frame-archive.py',
    'scripts/floor1/v01-frame-archive-controller.py',
    'scripts/prepare-v01-frame-archive-r1.py',
    'scripts/retained-v01-frames.py',
    'scripts/test-v01-frame-archive-offline.py',
    'docs/floor1/v01-frame-archive-proposal-r1-contract.md',
))
INHERITED_FILES = frozenset((
    'docs/floor1/c01-rgb-preservation-r1-contract.md',
    'docs/floor1/rgb-expanded-preservation-r1-contract.md',
    'scripts/floor1/howler-rgb-preservation-controller.py',
    'scripts/floor1/rgb-howler-preservation-scope.py',
    'scripts/floor1/rgb-preservation-expanded.py',
    'scripts/floor1/rgb-preservation.py',
    'scripts/prepare-howler-rgb-preservation-r1.py',
    'scripts/preserve-c01-rgb-r1.py',
    'scripts/preserve-floor1-rgb-expanded-r1.py',
    'scripts/preserve-howler-rgb-r1.py',
    'scripts/test-howler-rgb-preservation-controller-offline.py',
    'scripts/test-howler-rgb-preservation-scope-offline.py',
    'scripts/test-rgb-preservation-expanded-offline.py',
    'scripts/test-rgb-preservation-offline.py',
    'scripts/verify-c01-rgb-r1.py',
))
HISTORY_FILES = frozenset((
    'execution-final-handoff-private.json', 'preservation-contract-private.json',
    'representation-mapping-private.json', 'verification-pass1-private.json',
    'verification-pass2-private.json', 'synchronization-complete-private.json',
    'preservation-result-private.json',
))


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pinset(value, keys, reason):
    require(type(value) is dict and set(value) == set(keys), reason + ' keys')
    require(all(type(h) is str and re.fullmatch('[0-9a-f]{64}', h)
                for h in value.values()), reason + ' hashes')


def sealed_history(bundle):
    """Authenticate bytes before using the contract's inherited hash inventory."""
    require(set(bundle) == HISTORY_FILES, 'exact historical receipt bundle')
    require(digest(bundle['execution-final-handoff-private.json']) == HISTORY_HANDOFF_SHA,
            'sealed historical handoff')
    handoff = json.loads(bundle['execution-final-handoff-private.json'])
    require(handoff['PASS'] is True and handoff['source_commit'] ==
            handoff['tested_commit'] == handoff['published_commit'] == HISTORICAL_SOURCE,
            'historical handoff source')
    artifacts = handoff['private_execution_artifact_SHA256']
    for name in HISTORY_FILES - {'execution-final-handoff-private.json'}:
        require(digest(bundle[name]) == artifacts[name], 'historical artifact seal: ' + name)
    require(digest(bundle['preservation-contract-private.json']) == HISTORY_CONTRACT_SHA,
            'sealed historical contract')
    contract = json.loads(bundle['preservation-contract-private.json'])
    require(contract['preservation_source_commit'] == HISTORICAL_SOURCE and
            contract['status'] == 'FROZEN_LOCAL_PRESERVATION_ONLY', 'historical contract binding')
    mapping_sha = digest(bundle['representation-mapping-private.json'])
    mapping = json.loads(bundle['representation-mapping-private.json'])
    require(mapping['contract_SHA256'] == HISTORY_CONTRACT_SHA and
            mapping['proposal_SHA256'] == contract['approved_proposal_SHA256'] == handoff['proposal_SHA256'],
            'historical mapping binding')
    receipts = [json.loads(bundle[name]) for name in
                ('verification-pass1-private.json', 'verification-pass2-private.json')]
    for receipt, label in zip(receipts, ('pass1-zlib', 'pass2-independent-gzip')):
        require(receipt['PASS'] is True and receipt['verification'] == label and
                receipt['contract_SHA256'] == HISTORY_CONTRACT_SHA and
                receipt['mapping_SHA256'] == mapping_sha and
                receipt['source_commit'] == HISTORICAL_SOURCE and
                receipt['controller_PID'] == handoff['controller_PID'] and
                receipt['fresh_verifier_process'] is True, 'historical verifier binding')
    require(receipts[0]['pid'] != receipts[1]['pid'], 'historical separate verifier identities')
    sync = json.loads(bundle['synchronization-complete-private.json'])
    require(sync['PASS'] is True and sync['contract_SHA256'] == HISTORY_CONTRACT_SHA and
            sync['mapping_SHA256'] == mapping_sha and
            set(sync['verifier_PIDs']) == {r['pid'] for r in receipts}, 'historical synchronization binding')
    for name in ('preservation-contract-private.json', 'representation-mapping-private.json',
                 'verification-pass1-private.json', 'verification-pass2-private.json'):
        require(sync['synchronized_files_SHA256'][HISTORY_ROOT + name] == digest(bundle[name]),
                'historical synchronized evidence seal')
    require(json.loads(bundle['preservation-result-private.json'])['PASS'] is True,
            'historical terminal result')
    pinset(contract['source_files_SHA256'], INHERITED_FILES, 'exact fifteen inherited files')
    return contract['source_files_SHA256']


def compare_closure(admission, proposal, inherited, current_sources, current_providers,
                    current_source_commit, sealed_providers):
    """Pure predicate for inert mutations; inherited/provider seals come from validate."""
    direct, union = admission['source_files_SHA256'], proposal['source_files_SHA256']
    require(not set(direct) & set(inherited), 'conflicting direct/inherited overlap')
    pinset(direct, DIRECT_FILES, 'exact six admission files')
    pinset(inherited, INHERITED_FILES, 'exact fifteen inherited files')
    pinset(union, DIRECT_FILES | INHERITED_FILES, 'exact twenty-one proposal files')
    pinset(current_sources, DIRECT_FILES | INHERITED_FILES, 'exact current source files')
    require(admission['PASS'] is True and admission['execution_permitted'] is False and
            proposal['execution_permitted'] is False, 'offline receipt scope')
    require(admission['source_commit'] == proposal['source_commit'] ==
            current_source_commit == FROZEN_SOURCE, 'unchanged frozen/current source commit')
    for path, sha in direct.items():
        require(sha == union[path] == current_sources[path], 'direct source hash: ' + path)
    for path, sha in inherited.items():
        require(sha == union[path] == current_sources[path], 'inherited source hash: ' + path)
    require(len(sealed_providers) == 222, 'exact sealed provider count')
    for value in (admission['provider_files_SHA256'], proposal['provider_files_SHA256'], current_providers):
        pinset(value, sealed_providers, 'exact 222 provider files')
        require(value == sealed_providers, 'exact unchanged provider hashes')
    return dict(PASS=True, direct_files=6, inherited_files=15, union_files=21,
                provider_files=222, source_commit=FROZEN_SOURCE, execution_permitted=False)


def validate(proposal_bytes, admission_bytes, history_bundle, current_sources,
             current_providers, current_source_commit):
    """Public comparison entry: exact receipt bytes and historical chain are mandatory."""
    require(digest(proposal_bytes) == PROPOSAL_SHA, 'exact frozen proposal receipt')
    require(digest(admission_bytes) == ADMISSION_SHA, 'exact frozen offline admission receipt')
    proposal, admission = json.loads(proposal_bytes), json.loads(admission_bytes)
    require(proposal['offline_admission_SHA256'] == ADMISSION_SHA, 'proposal/admission binding')
    inherited = sealed_history(history_bundle)
    return compare_closure(admission, proposal, inherited, current_sources, current_providers,
                           current_source_commit, proposal['provider_files_SHA256'])
