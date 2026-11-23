import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import trimesh

from scripts.inspect_stl import load_mesh

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def parts(tmp_path):
    first = trimesh.creation.box()
    second = trimesh.creation.icosphere(subdivisions=0)
    second.apply_translation([4, 0, 0])
    source = tmp_path / "两件 original.stl"
    trimesh.util.concatenate([first, second]).export(source)
    return source


def repair(source, output, *options):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(ROOT / "scripts/repair_stl.py"),
         str(source), str(output), *options, "--json"],
        cwd=source.parent, capture_output=True, encoding="utf-8",
    )


@pytest.mark.parametrize("options,expected,removed", [
    ([], [12, 20], []), (["--min-component-ratio", "0.6"], [12, 20], []),
    (["--min-component-ratio", "0.61"], [20], [12]), (["--keep-largest"], [20], [12]),
    (["--min-component-ratio", "1"], [20], [12]),
])
def test_component_selection(parts, options, expected, removed):
    output = parts.with_name("result.stl")
    before = digest(parts)
    run = repair(parts, output, *options)
    assert run.returncode == 0, run.stderr + run.stdout
    report = json.loads(run.stdout)
    assert report["before"]["component_count"] == 2
    assert sorted(report["after"]["component_face_counts"]) == expected
    assert [row["faces"] for row in report["filtered"]] == removed
    assert load_mesh(output).is_volume
    assert digest(parts) == before


@pytest.mark.parametrize("alias", ["absolute", "relative", "hardlink", "symlink", "case"])
def test_same_file_protected(parts, alias):
    out = parts
    if alias == "relative":
        out = Path(".") / parts.name
    elif alias == "hardlink":
        out = parts.with_name("hard.stl")
        os.link(parts, out)
    elif alias == "symlink":
        out = parts.with_name("soft.stl")
        try:
            out.symlink_to(parts)
        except OSError as exc:
            pytest.skip(f"symlink creation unavailable: {exc}")
    elif alias == "case":
        out = parts.with_name(parts.name.upper())
        if not out.exists():
            pytest.skip("case-sensitive filesystem")
    original = digest(parts)
    result = repair(parts, out)
    assert result.returncode != 0
    assert "same file" in result.stdout
    assert digest(parts) == original


def test_existing_output_protected(parts):
    output = parts.with_name("result.stl")
    output.write_bytes(b"preserve-previous-run")
    before = digest(output)
    result = repair(parts, output)
    assert result.returncode != 0 and "already exists" in result.stdout
    assert digest(output) == before


def test_failed_repair_does_not_publish(tmp_path):
    source, output = tmp_path / "open.stl", tmp_path / "out.stl"
    trimesh.Trimesh(vertices=[[0,0,0],[4,0,0],[4,4,0],[0,4,0]],
                    faces=[[0,1,2],[0,2,3]]).export(source)
    before = digest(source)
    result = repair(source, output)
    assert result.returncode != 0 and "watertight" in result.stdout
    assert digest(source) == before and not output.exists()
    assert set(tmp_path.iterdir()) == {source}


def test_filters_are_mutually_exclusive(parts):
    out = parts.with_name("no.stl")
    result = repair(parts, out, "--keep-largest", "--min-component-ratio", "0.2")
    assert result.returncode != 0 and not out.exists()
    assert "not allowed with argument" in result.stderr


@pytest.mark.parametrize("case,reason", [("edge", "watertight"), ("cavity", "nested"),
                                         ("precision", "precision")])
def test_ambiguous_or_invalid_output_is_never_published(tmp_path, case, reason):
    if case == "edge":
        a = trimesh.creation.box(extents=[2]*3)
        b = a.copy()
        b.apply_translation([2,2,0])
        mesh = trimesh.util.concatenate([a,b])
    elif case == "cavity":
        outer = trimesh.creation.box(extents=[10]*3)
        outer.invert()
        mesh = trimesh.util.concatenate([outer, trimesh.creation.box(extents=[4]*3)])
    else:
        mesh = trimesh.creation.box(extents=[5,2,2])
        mesh.apply_translation([100000006,0,0])
    source, out = tmp_path/"original.stl", tmp_path/"out.stl"
    mesh.export(source, file_type="stl_ascii")
    result = repair(source, out)
    assert result.returncode != 0 and reason in result.stdout.lower()
    assert not out.exists()


def test_nonfinite_filter_returns_diagnostic(parts):
    out = parts.with_name("invalid.stl")
    result = repair(parts, out, "--min-component-ratio", "nan")
    assert result.returncode != 0 and "ratio" in (result.stderr + result.stdout)
    assert "Traceback" not in result.stderr and not out.exists()


def test_duplicate_triangle_is_cleaned_before_component_selection(tmp_path):
    box = trimesh.creation.box()
    mesh = trimesh.util.concatenate([box, box.submesh([[0]], append=True)])
    src, out = tmp_path/"duplicate.stl", tmp_path/"clean.stl"
    mesh.export(src)
    run = repair(src, out)
    assert run.returncode == 0, run.stdout
    assert json.loads(run.stdout)["after"]["component_face_counts"] == [12]
