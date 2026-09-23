#!/usr/bin/env bash
# Rebuild every Module 5 lab and solution from the one source, then check both.
set -euo pipefail
cd "$(dirname "$0")"
python3 gen_labs.py
echo; echo "=== solutions must score full marks ==="; python3 verify.py
echo; echo "=== untouched labs must survive Run All ==="; python3 verify_labs.py
