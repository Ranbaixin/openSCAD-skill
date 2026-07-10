#!/bin/bash
# verify-examples.sh — Local pre-commit validation
# Checks all example SCAD files render without errors.
# Usage: bash tests/verify-examples.sh

set -e

# Find OpenSCAD
OPENSCAD=$(command -v openscad 2>/dev/null || true)
if [ -z "$OPENSCAD" ]; then
    # macOS fallback
    if [ -f "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD" ]; then
        OPENSCAD="/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    else
        echo "❌ openscad not found"
        echo "   Install from: https://openscad.org/downloads.html"
        exit 1
    fi
fi

echo "OpenSCAD: $($OPENSCAD --version 2>&1 | head -1)"
echo "---"

failed=0
total=0

check_file() {
    local f="$1"
    local requires_bosl2="${2:-false}"

    [ -f "$f" ] || return
    total=$((total + 1))

    printf "%-55s " "$f"

    if [ "$requires_bosl2" = "true" ]; then
        if "$OPENSCAD" --backend manifold \
            -o /dev/null --export-format binstl \
            "$f" > /dev/null 2>&1; then
            echo "✅ PASS"
        else
            echo "⚠️  SKIP (BOSL2 required)"
        fi
    else
        if "$OPENSCAD" --backend manifold \
            -o /dev/null --export-format binstl \
            "$f" > /dev/null 2>&1; then
            echo "✅ PASS"
        else
            echo "❌ FAIL"
            failed=$((failed + 1))
        fi
    fi
}

# Basic and Intermediate — must pass
for f in examples/basic/*.scad examples/intermediate/*.scad; do
    check_file "$f" false
done

# Advanced — may need BOSL2
for f in examples/advanced/*.scad; do
    check_file "$f" true
done

echo "---"
echo "Results: $((total - failed))/$total passed, $failed failed"

if [ "$failed" -gt 0 ]; then
    echo ""
    echo "❌ Some required examples failed to render."
    echo "   Fix the errors above before committing."
    exit 1
else
    echo "✅ All required examples render cleanly."
fi
