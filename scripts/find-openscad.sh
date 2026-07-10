#!/bin/bash
# find-openscad.sh — Discover OpenSCAD CLI path on Unix/Linux/macOS
# Returns the first found path, or exits 1 if not found.

# 1. Check PATH first
if command -v openscad &>/dev/null; then
    echo "$(command -v openscad)"
    exit 0
fi

# 2. macOS: check default .app bundle location
if [[ -f "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD" ]]; then
    echo "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    exit 0
fi

# 3. macOS: user-installed .app
if [[ -f "$HOME/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD" ]]; then
    echo "$HOME/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    exit 0
fi

# 4. Linux: check common install locations
for candidate in \
    /usr/bin/openscad \
    /usr/local/bin/openscad \
    /snap/bin/openscad \
    /opt/openscad/openscad; do
    if [[ -x "$candidate" ]]; then
        echo "$candidate"
        exit 0
    fi
done

# 5. Not found
echo "openscad: not found in PATH or standard locations" >&2
echo "Install from: https://openscad.org/downloads.html" >&2
exit 1
