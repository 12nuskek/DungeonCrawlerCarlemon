#!/usr/bin/env python3
"""Separately authorized one-use earned-Warden-Save Continue-only cold."""
from pathlib import Path
import argparse, importlib.util

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=('prepare', 'cold'), required=True)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('warden_cold_only', Path(__file__).parent/'floor1/warden-cold-only-supervisor-r1.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    if args.stage == 'prepare': runner.prepare()
    else: runner.execute()

if __name__ == '__main__': main()
