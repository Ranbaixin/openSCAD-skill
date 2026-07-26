from pathlib import Path

from scripts.validate_scad import find_openscad


def test_find_openscad_honors_existing_override(monkeypatch, tmp_path: Path):
    executable = tmp_path / "openscad"
    executable.write_text("", encoding="utf-8")
    monkeypatch.setenv("OPENSCAD", str(executable))
    assert find_openscad() == str(executable)


def test_find_openscad_returns_none_for_missing_override(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("OPENSCAD", str(tmp_path / "missing-openscad"))
    monkeypatch.setattr("scripts.validate_scad.shutil.which", lambda _: None)
    assert find_openscad() is None
