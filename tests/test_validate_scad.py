from pathlib import Path
import json
import os
import subprocess
import sys

from scripts.validate_scad import find_openscad, native_path


def test_find_openscad_honors_existing_override(monkeypatch, tmp_path: Path):
    executable = tmp_path / "openscad"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setenv("OPENSCAD", str(executable))
    assert find_openscad() == str(executable)


def test_mounted_drive_path_respects_native_platform():
    path = Path("/mnt/d/CAD files/盒.scad")
    assert native_path(path) == (r"D:\CAD files\盒.scad" if os.name == "nt" else str(path))


def test_find_openscad_returns_none_for_missing_override(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENSCAD", str(tmp_path / "missing-openscad"))
    monkeypatch.setattr("scripts.validate_scad.shutil.which", lambda _: None)
    monkeypatch.setattr(Path, "is_file", lambda _: False)
    assert find_openscad() is None


def test_missing_dependencies_report_in_unicode_directory(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "装配 evidence"
    result = subprocess.run([sys.executable, "-S", str(root/"scripts/verify_assembly.py"), "--out", str(output)],
                            env=dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONPATH=""), capture_output=True)
    path, = output.glob("*/report.json")
    assert result.returncode != 0 and str(path) in result.stdout.decode("utf-8")
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["status"] == "INDETERMINATE"
    assert "requirements.txt" in report["error"]
    assert all(c["status"] != "PASS" for c in report["checks"])
