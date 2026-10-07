#!/usr/bin/env bash
set -euo pipefail
export DCC_MEMBERSHIP_PROBES=1
bash "$(dirname -- "$0")/test-f1-t01.sh"
