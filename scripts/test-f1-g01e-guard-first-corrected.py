#!/usr/bin/env python3
"""ONE separately claimed correction; original PR109 STOP/outputs remain intact."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('frozen_current_route',ROOT/'scripts/test-f1-g01e-guard-first-current.py');prior=importlib.util.module_from_spec(s);s.loader.exec_module(prior)
prior.BASE='4eb46e72165d2f9c5125f0926c38a301de2184f7'
prior.SCOPED+=['scripts/test-f1-g01e-guard-first-corrected.py','scripts/floor1/native-friendship.py',
 'scripts/floor1/native-friendship-tests.py','docs/floor1/g01e-guard-first-corrected-contract.md']
prior.PRESERVED+=['scripts/test-f1-g01e-guard-first-current.py','scripts/floor1/guard-first-host.py',
 'scripts/floor1/guard-first-observer.h','scripts/floor1/guard-first-route.py',
 'scripts/contracts/f1-g01e-guard-first-current.route','scripts/contracts/f1-g01e-guard-first-current-cold.route',
 'docs/floor1/g01e-guard-first-current-contract.md','docs/evidence/floor1/g01e/guard-first-current',
 'scripts/analyze-f1-g01e-guard-first-current.py']
if __name__=='__main__':prior.main()
