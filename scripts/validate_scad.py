#!/usr/bin/env python3
"""Render SCAD files through OpenSCAD and report failures without repo artifacts."""

from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def native_path(path: str | Path) -> str:
    """Convert common Git Bash /mnt/<drive>/ paths for Windows OpenSCAD."""
    value = str(path)
    if value.startswith("/mnt/") and len(value) > 6:
        drive, _, rest = value[5:].partition("/")
        if len(drive) == 1:
            return f"{drive.upper()}:\\{rest.replace('/', '\\')}"
    if Path("/mnt").is_dir() and len(value) >= 3 and value[1:3] in (":\\", ":/"):
        return f"/mnt/{value[0].lower()}/{value[3:].replace('\\', '/')}"
    return value


def find_openscad() -> str | None:
    """Find OpenSCAD on Windows, macOS, or Linux."""
    override = os.environ.get("OPENSCAD")
    candidates = [override] if override else []
    candidates.extend(shutil.which(name) for name in ("openscad", "openscad.com", "openscad.exe"))
    if os.name == "nt":
        candidates.extend(
            [
                r"C:\Program Files\OpenSCAD\openscad.com",
                r"C:\Program Files\OpenSCAD\openscad.exe",
                r"C:\Program Files (x86)\OpenSCAD\openscad.com",
                r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
                r"C:\Program Files\OpenSCAD (Nightly)\openscad.com",
                r"C:\Program Files\OpenSCAD (Nightly)\openscad.exe",
            ]
        )
    else:
        candidates.extend(
            [
                "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD",
                str(Path.home() / "Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"),
                "/usr/bin/openscad",
                "/usr/local/bin/openscad",
                "/snap/bin/openscad",
            ]
        )
    return next((str(Path(p)) for p in candidates if p and Path(p).is_file()), None)


def validate_file(path: Path, executable: str, backend: str = "manifold") -> tuple[bool, str]:
    # Keep the temporary path Windows-native even when Python is launched from Git Bash.
    with tempfile.TemporaryDirectory(prefix=".openscad-validate-", dir=str(Path.cwd())) as temp_dir:
        output = Path(temp_dir) / "output.stl"
        executable_arg = native_path(executable)
        help_result = subprocess.run([executable_arg, "--help"], capture_output=True, text=True, check=False)
        supports_backend = "--backend" in (help_result.stdout + help_result.stderr)
        command = [executable_arg]
        if supports_backend:
            command.extend(["--backend", backend])
        command.extend(["-o", native_path(output), "--export-format", "binstl", native_path(path)])
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        detail = (result.stderr or result.stdout).strip().splitlines()
        return result.returncode == 0 and output.is_file(), detail[-1] if detail else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--backend", choices=("manifold", "CGAL"), default="manifold")
    args = parser.parse_args()
    executable = find_openscad()
    if not executable:
        parser.error("OpenSCAD not found; set OPENSCAD or install it from https://openscad.org/downloads.html")
    files: list[Path] = []
    for item in args.files:
        matches = [Path(value) for value in glob.glob(str(item))]
        files.extend(matches or [item])
    failures = 0
    for path in files:
        ok, detail = validate_file(path, executable, args.backend)
        print(f"{'PASS' if ok else 'FAIL'} {path}{': ' + detail if detail else ''}")
        failures += not ok
    return int(failures)


if __name__ == "__main__":
    raise SystemExit(main())
