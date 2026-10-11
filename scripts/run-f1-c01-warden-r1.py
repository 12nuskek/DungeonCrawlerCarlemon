#!/usr/bin/env python3
"""Future separately authorized Warden stages. Missing authority refuses before writes."""
from pathlib import Path
import argparse,importlib.util

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=('prepare','warden-continuation','warden-new-save-cold'),required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('warden_runtime',Path(__file__).parent/'floor1/warden-runtime-supervisor.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    if args.stage=='prepare':runner.prepare()
    else:runner.execute(args.stage)

if __name__=='__main__':main()
