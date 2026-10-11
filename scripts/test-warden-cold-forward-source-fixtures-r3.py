#!/usr/bin/env python3
"""Prepared fixtures ONLY. Not executed by the source-only preparation increment.

This main never calls source_inputs(), copy_correspondence(), build_proposal(),
discovery, a native observer, a codec or a game build.
"""
from pathlib import Path
import importlib.util
import json
import os
import signal

ROOT = Path(__file__).resolve().parents[1]
OUT = Path('/workspace/scratch/c01-warden-cold-forward-fixtures-r3-20261011')


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def serialization_cases(schema):
    key_maps = (('nested', 'files'),)
    value_fields = (('nested', 'entries', '*', 'operand'),)
    payload = dict(nested=dict(files={Path('/tmp/a'): 'pinned'},
                              entries=[dict(operand=Path('/tmp/b'))]))
    expected = dict(nested=dict(files={'/tmp/a': 'pinned'}, entries=[dict(operand='/tmp/b')]))
    validate = lambda value: schema.require(value == expected, 'complete nested fixture schema')
    encoded = schema.encode_receipt(payload, path_key_maps=key_maps,
                                    path_value_fields=value_fields, validate=validate)
    schema.require(json.loads(encoded) == expected, 'declared nested Path key/value conversions')
    accepted, rejected = ['complete nested Path key/value schema'], []
    invalid = (
        ('collision after key conversion', {'nested': {'files': {Path('/tmp/a'): 1, '/tmp/a': 2}}}, 'post-conversion receipt key collision'),
        ('undeclared Path key', {'unknown': {Path('/tmp/a'): 1}}, 'Path key outside declared schema'),
        ('undeclared nested Path value', {'nested': {'unknown': Path('/tmp/a')}}, 'Path value outside declared schema'),
        ('unsupported nested bytes', {'nested': {'entries': [{'operand': b'bytes'}]}}, 'unsupported receipt type'),
        ('unsupported object', {'nested': {'unknown': object()}}, 'unsupported receipt type'),
        ('unsupported set', {'nested': {'unknown': {1}}}, 'unsupported receipt type'),
        ('unsupported tuple', {'nested': {'unknown': (1,)}}, 'unsupported receipt type'),
        ('non-string numeric key', {'nested': {1: 'ambiguous'}}, 'receipt keys must be strings or declared Paths'),
        ('nonfinite float', {'nested': {'unknown': float('nan')}}, 'nonfinite receipt number'),
    )
    for index, (label, bad, reason) in enumerate(invalid):
        destination = OUT / ('invalid-%02d' % index)
        try:
            # First valid payload followed by invalid payload proves complete-bundle
            # validation precedes destination creation, not just first-file encoding.
            schema.write_bundle(destination, {'valid.json': payload, 'invalid.json': bad},
                path_key_maps=key_maps, path_value_fields=value_fields, validate=validate)
        except (AssertionError, TypeError, ValueError) as error:
            schema.require(reason in str(error), 'intended serializer rejection rather than later schema refusal')
            schema.require(not os.path.lexists(destination), 'invalid payload created destination')
            rejected.append(label)
        else:
            raise AssertionError('accepted invalid receipt fixture: ' + label)
    return accepted, rejected


def process_ownership_case():
    # Import the previous suite as a non-main module. Its suite main is never run.
    previous = module('cold_r1_model_for_ownership_fixture', 'scripts/test-warden-cold-only-offline-r1.py')
    w = previous.w
    proposal = dict(source_commit='SYNTHETIC-OWNERSHIP-ONLY', contract_SHA256='a'*64)
    io = previous.ModelIO(proposal, {})
    io.fail_start_record = True
    stopped = []
    io.stop = lambda process: stopped.append(process)
    try:
        w.execute(io)
    except OSError as error:
        w.require(str(error) == 'SYNTHETIC start-record failure after creation', 'exact intended ownership failure')
    else:
        raise AssertionError('modeled process-start recording unexpectedly succeeded')
    w.require(io.events.count('one-native-creation') == 1 and io.created_process is not None,
              'exactly one inert process creation')
    w.require(stopped == [io.created_process], 'owned created process passed to stop/reap by identity')
    w.require(io.failure['actual_processes'] == 1 and io.result is None and
              'verdict-private.json' not in io.present and 'complete-result' not in io.events,
              'created process counted; no success verdict')
    first_process = io.created_process
    original_failure = dict(io.failure)
    # LocalIO ownership is per invocation. Only durable lifecycle/STOP state and
    # the global event ledger survive; never carry created_process into a new IO.
    second = previous.ModelIO(proposal, {})
    second.present, second.failure = io.present, io.failure
    second.events = io.events
    second_stopped = []
    second.stop = lambda process: second_stopped.append(process)
    w.require(second.created_process is None, 'fresh second-invocation process ownership')
    try:
        w.execute(second)
    except AssertionError:
        pass
    else:
        raise AssertionError('terminal ownership failure permitted second launch')
    w.require(io.events.count('one-native-creation') == 1 and
              stopped == [first_process] and second_stopped == [None] and
              second.created_process is None and second.failure is io.failure and
              io.failure == original_failure and io.failure['actual_processes'] == 1 and
              io.result is None and second.result is None and 'verdict-private.json' not in second.present,
              'no second creation/reaping of prior process, verdict or replacement of first failure')
    return dict(case='process-start-record failure owns exactly one inert process',
                synthetic_creations=1, owned_process_passed_to_stop=True,
                modeled_actual_processes=1, success_verdicts=0, second_launches=0,
                second_ownership_fresh=True, prior_process_stopped_by_second_invocation=False)


def main():
    schema = module('cold_r3_serializer_fixtures', 'scripts/floor1/warden-cold-receipt-schema-r3.py')
    schema.require(not os.path.lexists(OUT), 'fresh fixture root; no retry')
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('bounded60-second inert fixtures')))
    signal.alarm(60)
    accepted, rejected = serialization_cases(schema)
    ownership = process_ownership_case()
    receipt = dict(schema='c01-cold-forward-source-fixtures/r3', PASS=True,
        accepted=accepted, expected_rejections=rejected, ownership=ownership,
        correspondence_comparisons=0, suites_invoked=0, actual_processes=0, actual_runtime=0)
    def validate(value):
        schema.require(value == receipt, 'complete fixture receipt')
    schema.write_bundle(OUT, {'fixtures-private.json': receipt}, validate=validate)
    signal.alarm(0)
    print('PASS inert serialization/ownership fixtures only; no correspondence or cold suite')


if __name__ == '__main__':
    main()
