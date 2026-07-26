from pathlib import Path

import trimesh

from scripts.inspect_stl import load_mesh, mesh_report
from scripts.repair_stl import repair_mesh


def _fixture_mesh() -> trimesh.Trimesh:
    main = trimesh.creation.box(extents=[20, 10, 3])
    isolated = trimesh.creation.box(extents=[1, 1, 1])
    isolated.apply_translation([40, 0, 0])
    return trimesh.util.concatenate([main, isolated])


def test_inspect_supports_binary_and_ascii(tmp_path: Path):
    mesh = trimesh.creation.box(extents=[20, 10, 3])
    binary = tmp_path / "box-binary.stl"
    ascii_path = tmp_path / "box-ascii.stl"
    mesh.export(binary)
    mesh.export(ascii_path, file_type="stl_ascii")

    binary_report = mesh_report(load_mesh(binary))
    ascii_report = mesh_report(load_mesh(ascii_path))
    assert binary_report["extents_mm"] == ascii_report["extents_mm"]
    assert binary_report["component_count"] == 1
    assert binary_report["watertight"] is True


def test_repair_removes_isolated_component_and_keeps_main_geometry():
    repaired = repair_mesh(_fixture_mesh())
    report = mesh_report(repaired)
    assert report["component_count"] == 1
    assert report["watertight"] is True
    assert report["extents_mm"] == [20.0, 10.0, 3.0]
