#!/usr/bin/env python3
"""Explicit retained-frame consumer; original receipts and paths are never rewritten."""
from pathlib import Path
import argparse
import importlib.util
import json

PATH = Path(__file__).resolve().parent / 'floor1/v01-frame-archive.py'
SPEC = importlib.util.spec_from_file_location('retained_frames', PATH)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('inspect', 'materialize', 'check-retention'))
    parser.add_argument('members', nargs='*')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    contract, rows, protected = m.proposal()
    m.recheck(contract, protected)
    if args.action == 'check-retention':
        m.require(not args.members and args.output is None, 'read-only retention check')
        result = m.check_capture_retention(contract, rows)
    elif args.action == 'materialize':
        m.require(args.output is not None, 'explicit fresh materialization destination required')
        result = m.materialize(contract, rows, args.members, args.output)
    else:
        m.require(args.output is None, 'inspect writes no files')
        data = m.retained_frames(contract, rows, args.members)
        result = [dict(member=name, bytes=len(value), SHA256=m.engine.hashlib.sha256(value).hexdigest(),
                       provenance='retained archive bytes; no raw-path/inode identity claim', archive_SHA256=m.ARCHIVE_SHA)
                  for name, value in data.items()]
    print(json.dumps(result, indent=2))
