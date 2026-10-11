#!/usr/bin/env python3
"""One bounded inert suite for thirteen Warden chunks; no real target IO model."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import os
import resource
import signal

spec = importlib.util.spec_from_file_location('warden_inert_scope',
    Path(__file__).resolve().parent / 'floor1/rgb-warden-preservation-scope.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


def main():
    require = s.require
    require(not s.OFFLINE.exists() and not s.PROPOSED_OUTPUT.exists() and not s.AUTHORITY.exists(),
            'one fresh inert suite; no authority/output')
    require(not s.bindings.git('status', '--porcelain'), 'clean committed source')
    path = s.PREPARATION/'proposal-contract-private.json'
    proposal = json.loads(path.read_text())
    prepared = json.loads((s.PREPARATION/'proposal-preparation-receipt-private.json').read_text())
    head = s.bindings.git('rev-parse', 'HEAD')
    proposal_hash = s.engine.digest(path)
    require(prepared['PASS'] is True and prepared['proposal_SHA256'] == proposal_hash and
            prepared['source_commit'] == proposal['proposal_source_commit'] == head,
            'exact private proposed source/hash')
    require(proposal['actual_compression'] == proposal['actual_decoded_passes'] == proposal['real_unlinks'] == 0 and
            proposal['status'] == 'PROPOSED_OFFLINE_REVIEW_ONLY' and
            proposal['preservation_execution_permitted'] is False, 'proposal grants no authority')
    require(proposal['storage'] == s.storage_cap(proposal['chunks']) and
            proposal['storage']['all_inclusive_cap_bytes'] == s.CAP, 'actual thirteen-chunk cap')
    for rel, pin in proposal['source_files_SHA256'].items():
        require(s.engine.digest(s.ROOT/rel) == pin, 'complete proposed source closure')
    for name, pin in proposal['tool_dependencies_SHA256'].items():
        require(s.engine.digest(Path(name)) == pin, 'pinned accepted codec provider bytes')
    s.OFFLINE.mkdir(mode=0o700)
    controller = s.inert_controller(proposal, proposal_hash)
    # Reuse only the accepted fixture/model definitions. Its main, historical
    # suite and LocalIO are never executed. Global controller is this narrow adapter.
    original = s.ROOT/'scripts/test-howler-rgb-preservation-controller-offline.py'
    parsed = ast.parse(original.read_text())
    names = {'sha', 'encoded', 'fixture_contract', 'VirtualIO'}
    selected = [node for node in parsed.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    require(len(selected) == 4, 'exact reused inert fixture definitions')
    namespace = dict(controller=controller, copy=copy, json=json, hashlib=hashlib, Path=Path)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(original), 'exec'), namespace)
    encoded = namespace['encoded']
    inherited = namespace['VirtualIO']
    class VirtualIO(inherited):
        inert_only = True
        def __init__(self, contract, approved):
            super().__init__(contract, approved)
            usage = s.metadata_usage()
            self.preparation = dict(logical_bytes=usage['logical_bytes'], allocated_bytes=usage['allocated_bytes'])
            for receipt, name in zip((self.one, self.two), controller.RECEIPT_NAMES):
                receipt.update(chunk_count=s.CHUNKS, frames=s.FRAMES, decoded_bytes=s.RAW_BYTES)
                self.files[str(controller.OUT/name)] = encoded(receipt)
    contract = namespace['fixture_contract'](proposal)
    cases, negatives = [], []

    def reject(name, mutation=None, ticket_mutation=None, premature=False):
        io = VirtualIO(contract, proposal)
        if mutation:
            mutation(io)
        for filename, value in ((controller.CONTRACT_NAME, io.contract),
            (controller.MAPPING_NAME, io.mapping), (controller.RECEIPT_NAMES[0], io.one),
            (controller.RECEIPT_NAMES[1], io.two)):
            io.files[str(controller.OUT/filename)] = encoded(value)
        try:
            ticket = None if premature else controller.synchronize_barrier(
                io, io.contract, proposal, io.mapping, io.one, io.two)
            if ticket_mutation:
                ticket_mutation(io, ticket)
            controller.replace_originals(io, ticket, io.contract, proposal, io.mapping, io.one, io.two)
        except (RuntimeError, OSError, KeyError, ValueError) as error:
            require(io.removed == [], 'negative simulated a premature removal')
            cases.append(name)
            negatives.append(dict(case=name, reason=type(error).__name__+': '+str(error),
                                  virtual_originals_retained=13, real_unlinks=0))
        else:
            raise AssertionError('negative accepted: '+name)

    reject('premature-unlink', premature=True)
    reject('wrong-output', lambda io: io.contract.update(output_root='/tmp/forbidden'))
    reject('wrong-cap', lambda io: io.contract['storage'].update(all_inclusive_cap_bytes=3459215360))
    reject('wrong-mapping-cap', lambda io: io.mapping.update(cap_bytes=3459215360))
    reject('wrong-approved-hash', lambda io: io.contract.update(approved_proposal_SHA256='wrong'))
    reject('wrong-source-inventory', lambda io: io.contract['source_files_SHA256'].pop(s.FILES[0]))
    reject('wrong-codec', lambda io: io.contract['compress_command'].append('-9'))
    reject('missing-chunk', lambda io: io.mapping['chunks'].pop())
    reject('reordered-chunks', lambda io: io.mapping['chunks'].reverse())
    reject('wrong-target', lambda io: io.mapping['chunks'][0].update(raw_path='/tmp/forbidden.rgb'))
    reject('changed-raw-binding', lambda io: io.contract['chunks'][0].update(raw_SHA256='wrong'))
    reject('missing-protected', lambda io: io.contract['protected_entries'].pop(next(iter(io.contract['protected_entries']))))
    for key in ('actual_runtime_handoff_SHA256', 'historical_protection_refs', 'visual_review_SHA256',
                'source_base', 'runtime_history'):
        reject('changed-'+key, lambda io, key=key: io.contract.update({key:'wrong'}))
    for attr in ('changed_raw', 'changed_protected', 'changed_source'):
        reject(attr, lambda io, attr=attr: setattr(io, attr, True))
    reject('missing-replacement', lambda io: io.files.pop(str(controller.OUT/io.mapping['chunks'][0]['compressed_relative_path'])))
    for key in ('compressed_relative_path', 'frame_hashes_relative_path'):
        reject('changed-'+key, lambda io, key=key: io.files.update({str(controller.OUT/io.mapping['chunks'][0][key]):b'changed'}))
    for key, value in (('PASS',False), ('chunk_count',12), ('frames',24206),
                      ('decoded_bytes',2788646399), ('originals_retained',False),
                      ('contract_SHA256','wrong'), ('mapping_SHA256','wrong'),
                      ('pid',101), ('pid',0), ('pid',100), ('controller_PID',999),
                      ('source_commit','wrong'), ('fresh_verifier_process',False),
                      ('no_second_full_decoded_copy',False)):
        reject('incomplete-second-'+key+'-'+str(value), lambda io,key=key,value=value: io.two.update({key:value}))
    for key in ('exact_EOF', 'exact_frame_bytes'):
        reject('partial-'+key, lambda io,key=key: io.two['chunks'][0].update({key:False}))
    reject('missing-receipt-chunk', lambda io: io.two['chunks'].pop())
    reject('reordered-receipt', lambda io: io.two['chunks'].reverse())
    reject('child-lineage', lambda io: io.files.update({str(controller.OUT/'verify-gzip-started-private.json'):encoded(dict(pid=999,controller_PID=100))}))
    reject('over-cap', lambda io: setattr(io,'usage_override',dict(logical_bytes=controller.CAP,allocated_bytes=controller.CAP)))
    reject('no-positive-net', lambda io: setattr(io,'usage_override',dict(logical_bytes=s.RAW_BYTES,allocated_bytes=s.RAW_BYTES)))
    reject('no-audit-room', lambda io: setattr(io,'free',0))
    model = VirtualIO(contract, proposal)
    # Every reused synchronization boundary, including the persisted completion
    # receipt, is faulted before the first virtual removal.
    file_bound = len(controller.synchronized_paths(model.mapping))+1
    dir_bound = len({p.parent for p in controller.synchronized_paths(model.mapping)})+2
    for at in range(1, file_bound+1):
        reject('file-fsync-'+str(at), lambda io,at=at: setattr(io,'fail_file_at',at))
    for at in range(1, dir_bound+1):
        reject('directory-fsync-'+str(at), lambda io,at=at: setattr(io,'fail_dir_at',at))
    reject('missing-sync-coverage', ticket_mutation=lambda io,t: t.hashes.pop(next(iter(t.hashes))))
    reject('changed-synced-receipt', ticket_mutation=lambda io,t: io.files.update({str(controller.OUT/controller.RECEIPT_NAMES[0]):b'changed'}))
    reject('changed-sync-record', ticket_mutation=lambda io,t: io.files.update({str(controller.OUT/'synchronization-complete-private.json'):b'changed'}))
    model.free = 1024**3
    ticket = controller.synchronize_barrier(model,model.contract,proposal,model.mapping,model.one,model.two)
    require(ticket.accounting['runtime_capacity_admitted'] is False, 'no runtime reservation inheritance')
    controller.replace_originals(model,ticket,model.contract,proposal,model.mapping,model.one,model.two)
    require(model.removed == [r['raw_path'] for r in proposal['chunks']], 'exact 13 virtual removals')
    cases.append('positive-complete-inert-barrier-13-only')
    try:
        controller.replace_originals(model,ticket,model.contract,proposal,model.mapping,model.one,model.two)
    except RuntimeError:
        cases.append('ticket-one-use')
    else:
        raise AssertionError('ticket replay accepted')
    for name in ('LocalIO','freeze','execute','verify_worker','run_verifier','admission','accepted_inputs','authority_check','record_stop'):
        try:
            getattr(controller,name)()
        except RuntimeError as error:
            require(str(error).startswith('CLOSED:'), 'exact inert-only closure')
            cases.append('real-entrypoint-closed-'+name)
        else:
            raise AssertionError('real operation available')
    try:
        list(s.engine.frame_blocks([b'X'*(s.FRAME-1)],1))
    except RuntimeError:
        cases.append('inert-partial-frame-EOF')
    else:
        raise AssertionError('partial frame accepted')
    require(not s.PROPOSED_OUTPUT.exists() and not s.AUTHORITY.exists() and
            s.engine.digest(path) == proposal_hash and not s.bindings.git('status','--porcelain'),
            'source/proposal unchanged; real operations absent')
    result = dict(PASS=True, source_commit=head, base_commit=s.BASE, proposal_SHA256=proposal_hash,
        source_files_SHA256={p:s.engine.digest(s.ROOT/p) for p in s.FILES},
        case_count=len(cases), negative_count=len(negatives), cases=cases, negative_receipts=negatives,
        synchronized_file_fault_bound=file_bound, synchronized_directory_fault_bound=dir_bound,
        chunk_count=13, frames=24207, raw_bytes=2788646400,
        cap_bytes=controller.CAP, all_originals_retained=True, virtual_removals_only=True,
        real_unlinks=0, compressors=0, real_decoder_processes=0, gameplay_processes=0,
        preservation_processes=0, runtime_authorities=0, runtime_claims=0, runtime_freezes=0,
        accepted_barrier_and_fixture_definitions_reused=True, completed_suites_replayed=False,
        production_controller_available=False, independent_review_required=True,
        first_failure_terminal=True, retry=False, wall_bound_seconds=240,
        aggregate_metadata_cap_bytes=s.METADATA_CAP)
    with (s.OFFLINE/'scope-suite-private.json').open('x') as file:
        os.fchmod(file.fileno(),0o600)
        json.dump(result,file,indent=2)
        file.write('\n')
        file.flush()
        os.fsync(file.fileno())
    s.metadata_usage()
    print('PASS',len(cases),'inert cases;',len(negatives),'negatives; real codecs/unlinks/emulators=0')


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_FSIZE,(8*1024**2,8*1024**2))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('240-second inert suite bound')))
    signal.alarm(240)
    try:
        main()
    except Exception as error:
        if s.OFFLINE.exists():
            with (s.OFFLINE/'scope-suite-STOP-private.json').open('x') as file:
                os.fchmod(file.fileno(),0o600)
                json.dump(dict(PASS=False,error=type(error).__name__+': '+str(error),retry=False,
                               partial_outputs_retained=True),file,indent=2)
        raise
