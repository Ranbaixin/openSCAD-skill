#!/usr/bin/env python3
"""Render SCAD files through OpenSCAD and report failures without repo artifacts."""

from __future__ import annotations

import argparse
import glob
import json
import locale
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


def native_path(path: str | Path) -> str:
    """Convert common Git Bash /mnt/<drive>/ paths for Windows OpenSCAD."""
    value = str(path)
    if os.name == "nt":
        mount = re.fullmatch(r"/mnt/([a-zA-Z])/(.*)", value.replace("\\", "/"))
        if mount:
            return mount[1].upper() + ":\\" + mount[2].replace("/", "\\")
    if os.name != "nt" and Path("/mnt").is_dir() and re.match(r"^[A-Za-z]:[\\/]", value):
        return "/mnt/" + value[0].lower() + "/" + value[3:].replace("\\", "/")
    return value


def find_openscad() -> str | None:
    """Find OpenSCAD on Windows, macOS, or Linux."""
    override = os.environ.get("OPENSCAD")
    candidates = [native_path(override)] if override else []
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


def decode_log(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("mbcs" if os.name == "nt" else locale.getpreferredencoding(False), errors="replace")


def configure_console():
    for stream in (sys.stdout, sys.stderr):
        if not stream.isatty():
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")


@dataclass
class OpenSCAD:
    executable: str
    version: str
    backend_option: str | None

    @classmethod
    def probe(cls, executable, backend="manifold"):
        def info(option):
            result = subprocess.run([native_path(executable), option], capture_output=True, timeout=20)
            return decode_log(result.stdout + result.stderr).strip()
        help_text = info("--help")
        choice = "Manifold" if backend.lower() == "manifold" and "Manifold" in help_text else backend
        return cls(native_path(executable), info("--version"), choice if "--backend" in help_text else None)

    def render(self, source, output, *, defines=None, expression=None, strict=True):
        args = [self.executable]
        if self.backend_option:
            args += ["--backend", self.backend_option]
        for name, value in (defines or {}).items():
            args += ["-D", name + "=" + json.dumps(value, allow_nan=False)]
        args += ["--export-format", "binstl", "-o", output.name,
                 "-" if expression is not None else str(Path(native_path(source)).resolve())]
        record = {"command": args, "cwd": str(output.parent), "expression": expression, "exit_code": None}
        try:
            if os.path.lexists(output):
                raise FileExistsError(f"render target already exists: {output}")
            proc = subprocess.run(args, cwd=output.parent, capture_output=True, timeout=120,
                                  input=expression.encode("utf-8") if expression is not None else None)
            log = decode_log(proc.stdout) + "\n" + decode_log(proc.stderr)
            record.update(exit_code=proc.returncode, log=log.strip())
            marker = re.search(r"Top level object is a 3D object \((manifold|CGAL)\)", log, re.I)
            if marker:
                record["backend_observed"] = marker.group(1)
            diagnostics = [s for s in log.splitlines() if re.search(
                r"ERROR:|parser error|can't (?:open|parse)|unknown (?:module|function)", s, re.I)
                or (strict and "WARNING:" in s.upper())]
            if proc.returncode or diagnostics:
                reason = "\n".join(diagnostics) or log.strip() or f"exit {proc.returncode}"
                raise ValueError(reason if output.is_file() else "empty or missing STL: " + reason)
            if not output.is_file():
                raise ValueError("empty or missing STL despite successful exit")
            with output.open("rb") as stream:
                header = stream.read(84)
                faces = struct.unpack_from("<I", header, 80)[0] if len(header) == 84 else 0
            if not faces or output.stat().st_size != 84 + 50 * faces:
                raise ValueError("empty or truncated binary STL")
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            record["error"] = str(exc)
        return record


def validate_file(path: Path, executable: str, backend: str = "manifold") -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix=".openscad-validate-") as temp_dir:
        output = Path(temp_dir) / "output.stl"
        result = OpenSCAD.probe(executable, backend).render(path, output, strict=False)
        return "error" not in result, result.get("error", "nonempty binary STL")


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
        matches = [Path(value) for value in glob.glob(native_path(item))]
        files.extend(matches or [item])
    failures = 0
    for path in files:
        ok, detail = validate_file(path, executable, args.backend)
        print(f"{'PASS' if ok else 'FAIL'} {path}{': ' + detail if detail else ''}")
        failures += not ok
    return int(failures)


if __name__ == "__main__":
    configure_console()
    raise SystemExit(main())
