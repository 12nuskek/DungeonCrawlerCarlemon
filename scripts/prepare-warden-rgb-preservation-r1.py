#!/usr/bin/env python3
"""One private, source-bound proposal. No preservation or gameplay execution."""
from pathlib import Path
import importlib.util
import json
import os
import resource
import shutil
import signal
import subprocess
import sys

spec = importlib.util.spec_from_file_location('warden_proposal_scope',
    Path(__file__).resolve().parent / 'floor1/rgb-warden-preservation-scope.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
e, require = s.engine, s.require


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    data = (json.dumps(value, indent=2, sort_keys=True)+'\n').encode()
    require(s.metadata_usage()['logical_bytes']+len(data) <= s.METADATA_CAP,
            'bounded aggregate proposal write')
    with (s.PREPARATION/name).open('xb') as file:
        os.fchmod(file.fileno(), 0o600)
        file.write(data)
        file.flush()
        os.fsync(file.fileno())
    s.metadata_usage()


def main():
    require(len(sys.argv) == 1, 'preparation only; no operation arguments')
    require(not s.PREPARATION.exists() and not s.OFFLINE.exists() and
            not s.PROPOSED_OUTPUT.exists() and not s.AUTHORITY.exists(), 'fresh names; execution closed')
    require(not s.bindings.git('status', '--porcelain'), 'clean committed reviewed source')
    head = s.bindings.git('rev-parse', 'HEAD')
    require(s.bindings.git('merge-base', s.BASE, head) == s.BASE and
            set(s.bindings.git('diff', '--name-only', s.BASE, head).splitlines()) == set(s.FILES),
            'only four new scoped files since accepted source')
    s.PREPARATION.mkdir(mode=0o700)
    require(e.digest(s.HANDOFF) == s.HANDOFF_SHA, 'actual Warden handoff seal')
    h = read(s.HANDOFF)
    r = read(s.VISUAL/'readback-and-samples-private.json')
    require(r['PASS'] is True and r['handoff_SHA256'] == s.HANDOFF_SHA and
            r['full_14_sector_live_disk'] is True and r['cold_processes'] == 0 and
            r['native_motion_frames'] == s.FRAMES, 'independent actual evidence readback')
    visual = s.VISUAL/'visual-inspection-private.json'
    review = read(visual)
    require(review['readback_SHA256'] == e.digest(s.VISUAL/'readback-and-samples-private.json') and
            review['viewed_sample_ordinals'] == [x['ordinal'] for x in r['samples']] and
            review['viewed_screenshot_SHA256'] == h['captures']['captures_SHA256'],
            'native sampled visual inspection binding')
    protected = {}
    def protect(path, pin=None):
        path = Path(path)
        before = e.identity(path)
        actual = e.digest(path)
        require(pin is None or actual == pin, 'protected hash: '+str(path))
        require(e.identity(path) == before, 'protected identity changed during read')
        entry = dict(identity=before, SHA256=actual)
        require(path.stat().st_nlink == 1, 'protected regular single link')
        if str(path) in protected:
            require(protected[str(path)] == entry, 'conflicting protected inventory')
        protected[str(path)] = entry
    rows = []
    for want in s.definitions():
        path = Path(want['raw_path'])
        retained = h['runtime_private_files'][str(path)]
        row = dict(want, raw_identity=e.identity(path), raw_SHA256=retained['SHA256'])
        s.check_entry(row)
        rows.append(row)
    targets = {x['raw_path'] for x in rows}
    require({str(p) for p in (s.RUNTIME/'warden-continuation').glob('motion-*.rgb')} == targets,
            'exact live thirteen-chunk namespace')
    for key in ('runtime_private_files', 'admission_private_files'):
        for path, row in h[key].items():
            if path not in targets:
                protect(path, row['SHA256'])
    protect(s.HANDOFF, s.HANDOFF_SHA)
    protect(s.SCRATCH/'c01-warden-runtime-r2-authority.json', h['authority_SHA256'])
    protect(s.SCRATCH/'c01-howler2-continuation-r1-20261011/howler-continuation/game.sav',
            h['original_patrol_Save_SHA256'])
    for p in s.VISUAL.iterdir():
        protect(p)
    # Retain all completed Howler representations, receipts and protected entries;
    # rehash only, never replay their codec/decoded passes or replacements.
    prior = s.SCRATCH/'howler-rgb-preservation-r1-20261011'
    hand = read(prior/'execution-final-handoff-private.json')
    require(hand['PASS'] is True and hand['replaced_raw_files'] == 17 and
            hand['complete_verifier_processes'] == 2, 'completed preservation history')
    for name, pin in hand['private_execution_artifact_SHA256'].items():
        protect(prior/name, pin)
    for p in prior.rglob('*'):
        if p.is_file():
            protect(p)
    old = read(prior/'preservation-contract-private.json')
    for p, entry in old['protected_entries'].items():
        protect(p, entry['SHA256'])
        require(e.identity(Path(p)) == entry['identity'], 'old protected identity')
    replaced = old['previously_replaced_paths'] + hand['replaced_paths']
    require(len(set(replaced)) == 90 and all(not Path(p).exists() for p in replaced),
            'completed 31/42/17 historical replacements unchanged')
    frozen = read(s.RUNTIME/'freeze.json')
    sources = dict(frozen['source_files'])
    for rel in s.FILES:
        sources[rel] = e.digest(s.ROOT/rel)
    for rel, pin in sources.items():
        require(e.digest(s.ROOT/rel) == pin, 'complete source closure: '+rel)
    for path, pin in frozen['tool_files'].items():
        require(e.digest(Path(path)) == pin, 'actual Warden provider: '+path)
    codec_keys = ('format', 'compress_command', 'decoder_pass1', 'decoder_pass2',
        'gzip_version', 'gzip_executable_SHA256', 'python_executable_SHA256',
        'zlib_version', 'zlib_module_origin', 'tool_dependencies_SHA256')
    codec = {k: old[k] for k in codec_keys}
    for path, pin in codec['tool_dependencies_SHA256'].items():
        require(e.digest(Path(path)) == pin, 'accepted codec provider: '+path)
    config = read(s.bindings.CONFIG)
    env = s.bindings.environment(Path(config['tool_root']))
    deps = s.bindings.merge_exact(s.bindings.linked(e.GZIP, env),
        s.bindings.linked(Path(s.bindings.provider('python3')), env),
        {str(e.GZIP): e.digest(e.GZIP), s.bindings.provider('python3'): e.digest(Path(s.bindings.provider('python3')))})
    require(deps == codec['tool_dependencies_SHA256'] and e.zlib.ZLIB_RUNTIME_VERSION == codec['zlib_version'] and
            s.accepted.accepted.zlib_provider(e.zlib, Path(s.bindings.provider('python3')))[1] == codec['zlib_module_origin'] and
            subprocess.check_output([str(e.GZIP), '--version'], env=env, text=True, timeout=10).splitlines()[0] == codec['gzip_version'],
            'exact existing codec dependency/provider closure')
    index = s.RUNTIME/'warden-continuation/frame-index.bin'
    e.index_check(index, s.FRAMES)
    recordings = [dict(recording='Warden-continuation-PASS', frames=s.FRAMES, chunks=s.CHUNKS,
                       index_path=str(index), index_SHA256=e.digest(index))]
    inventory = s.bindings.retention.PREP/'protected-inventory-private.jsonl'
    refs = {str(inventory): dict(identity=e.identity(inventory), SHA256=e.digest(inventory)),
            str(prior/'execution-final-handoff-private.json'): dict(identity=e.identity(prior/'execution-final-handoff-private.json'), SHA256=e.digest(prior/'execution-final-handoff-private.json'))}
    require(refs[str(inventory)]['SHA256'] == h['archive_representation']['protected_inventory_SHA256'],
            '37,000-entry historical protection reference')
    s.validate_scope(rows, protected, replaced)
    require(s.storage_cap(rows)['all_inclusive_cap_bytes'] == s.CAP, 'exact derived new cap')
    proposal = dict(codec, status='PROPOSED_OFFLINE_REVIEW_ONLY', source_base=s.BASE,
        proposal_source_commit=head, source_files_SHA256=sources, runtime='CLOSED',
        runtime_authority=False, runtime_freeze=False, preservation_execution_permitted=False,
        runtime_reservation_bytes=17694519296, width=240, height=160, pixel_format='RGB24',
        bytes_per_frame=s.FRAME, chunk_count=s.CHUNKS, frames=s.FRAMES, original_bytes=s.RAW_BYTES,
        chunks=rows, recordings=recordings, protected_entries=protected,
        previously_replaced_paths=replaced, historical_protection_refs=refs,
        actual_runtime_handoff_SHA256=s.HANDOFF_SHA, visual_review_SHA256=e.digest(visual),
        actual_provider_files_SHA256=frozen['tool_files'], output_root=str(s.PROPOSED_OUTPUT),
        storage=s.storage_cap(rows), runtime_history={k:h[k] for k in
        ('prior_failure_history','prior_read_only_KeyError','prior_pre_suite_DNS_failure',
         'conditional_cold_refusal','Library_history')},
        private_retention='local only; independent backup unverified', first_failure_terminal=True,
        scope_suite_limit=1, actual_compression=0, actual_decoded_passes=0, real_unlinks=0,
        gameplay_processes=0, source_builds=0, future_production_wiring_requires_review=True)
    write('proposal-contract-private.json', proposal)
    write('proposal-preparation-receipt-private.json', dict(PASS=True, source_commit=head,
        proposal_SHA256=e.digest(s.PREPARATION/'proposal-contract-private.json'),
        source_files_SHA256={p:sources[p] for p in s.FILES}, cap=proposal['storage'],
        protected_entries=len(protected), historical_reference_entries=37000,
        current_free_bytes=shutil.disk_usage(s.SCRATCH).free, runtime_capacity_admitted=False,
        metadata=s.metadata_usage(), actual_compression=0, real_unlinks=0, emulators=0))
    print('PASS private proposal; cap', proposal['storage']['all_inclusive_cap_bytes'],
          'protected', len(protected), '; execution closed')


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_FSIZE, (8*1024**2, 8*1024**2))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('240-second preparation bound')))
    signal.alarm(240)
    try:
        main()
    except Exception as error:
        if s.PREPARATION.exists():
            write('preparation-STOP-private.json', dict(PASS=False, error=type(error).__name__+': '+str(error), retry=False))
        raise
