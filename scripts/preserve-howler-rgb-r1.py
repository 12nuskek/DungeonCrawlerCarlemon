#!/usr/bin/env python3
"""Separately gated local preservation; no runtime, cache cleanup or upload mode."""
from pathlib import Path
import argparse
import importlib.util

PATH = Path(__file__).resolve().parent / 'floor1/howler-rgb-preservation-controller.py'
SPEC = importlib.util.spec_from_file_location('howler_rgb_controller', PATH)
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('freeze', 'execute', 'verify-zlib', 'verify-gzip'))
    action = parser.parse_args().action
    try:
        if action == 'freeze':
            controller.freeze()
        elif action == 'execute':
            controller.execute()
        else:
            controller.verify_worker(action)
    except Exception as error:
        controller.record_stop(action, error)
        raise


if __name__ == '__main__':
    main()
