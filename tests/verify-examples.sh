#!/bin/bash
# verify-examples.sh — Local pre-commit validation
# Checks all example SCAD files render without errors.
# Usage: bash tests/verify-examples.sh

set -e

PYTHON=${PYTHON:-python3}
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON=python
fi

"$PYTHON" scripts/validate_scad.py \
    "examples/basic/*.scad" \
    "examples/intermediate/*.scad"

echo "Advanced examples are informational because BOSL2 may not be installed."
"$PYTHON" scripts/validate_scad.py "examples/advanced/*.scad" || true
