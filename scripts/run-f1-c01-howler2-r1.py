#!/usr/bin/env python3
"""Separately admitted Howler2 runtime only; no action on import."""
from pathlib import Path
import argparse,importlib.util
def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['prepare','howler-continuation','howler-new-save-cold'],required=True);args=p.parse_args()
    spec=importlib.util.spec_from_file_location('howler2_runtime',Path(__file__).parent/'floor1/howler2-runtime-supervisor.py');runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    if args.stage=='prepare':runner.prepare()
    else:runner.execute(args.stage)
if __name__=='__main__':main()
