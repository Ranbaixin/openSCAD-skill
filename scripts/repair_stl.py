#!/usr/bin/env python3
"""Repair an STL to a new binary STL. By default preserve every component."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

try:
    if __package__:
        from .inspect_stl import load_mesh, mesh_report
    else:
        from inspect_stl import load_mesh, mesh_report
    import numpy as np
    import trimesh
except ModuleNotFoundError as exc:
    if __name__ == "__main__":
        raise SystemExit(f"Missing geometry dependency {exc.name}; install with python -m pip install -r requirements.txt") from None
    raise


def _repair(mesh, ratio, keep_largest, report):
    if ratio is not None and (keep_largest or not 0 <= ratio <= 1):
        raise ValueError("choose one filter; min_component_ratio must be in [0, 1]")
    mesh = mesh.copy()
    initial_faces = len(mesh.faces)
    mesh.update_faces(mesh.nondegenerate_faces() & mesh.unique_faces())
    report["removed_degenerate_or_duplicate_faces"] = initial_faces - len(mesh.faces)
    mesh.remove_unreferenced_vertices()
    components = sorted(mesh.split(only_watertight=False, repair=False),
                        key=lambda part: len(part.faces), reverse=True)
    if not components:
        raise ValueError("input contains no mesh components")
    threshold = len(components[0].faces) * (ratio or 0)
    kept = []
    for index, part in enumerate(components):
        if (index and (keep_largest or ratio == 1)) or len(part.faces) < threshold:
            report["filtered"].append({"component": index + 1, "faces": len(part.faces),
                                       "bounds_mm": part.bounds.tolist()})
            continue
        # 内腔的向内壳面可能是有意设计，逐件翻转会填实空腔。
        if any(other is not part and (part.volume < 0 or other.volume < 0)
               and (other.bounds[0] <= part.bounds[0]).all() and (other.bounds[1] >= part.bounds[1]).all()
               for other in components):
            raise ValueError("nested inward shell; cavity orientation needs manual inspection")
        part = part.copy()
        part.merge_vertices()
        part.remove_unreferenced_vertices()
        if not len(part.faces):
            raise ValueError(f"component {index + 1} has no valid triangles")
        trimesh.repair.fix_winding(part)
        trimesh.repair.fill_holes(part)
        trimesh.repair.fix_normals(part)
        roundtrip = part.vertices.astype(np.float32).astype(float)
        if np.abs(part.vertices - roundtrip).max() > max(1e-7, max(part.extents)*2e-7):
            raise ValueError("binary STL precision would change local geometry; move a copy nearer the origin")
        kept.append(part)
    return trimesh.util.concatenate(kept), len(kept)


def repair_mesh(mesh: trimesh.Trimesh, min_component_ratio: float | None = None,
                *, keep_largest: bool = False) -> trimesh.Trimesh:
    """Select components only on request; repair their winding and simple holes."""
    result, _ = _repair(mesh, min_component_ratio, keep_largest, {"filtered": []})
    return result


def check_destination(source: Path, output: Path):
    if source.resolve() == output.resolve() or (output.exists() and source.samefile(output)):
        raise ValueError("input and output are the same file")
    if os.path.lexists(output):
        raise FileExistsError(f"output already exists: {output}")
    if output.suffix.lower() != ".stl":
        raise ValueError("output filename must end in .stl")


def repair_file(source, output, ratio, largest, report):
    check_destination(source, output)
    original = load_mesh(source)
    report["before"] = mesh_report(original, source)
    mesh, expected_components = _repair(original, ratio, largest, report)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix=".tmp.stl", delete=False) as stream:
        temp = Path(stream.name)
    try:
        mesh.export(temp, file_type="stl")
        actual = load_mesh(temp)
        stats = mesh_report(actual, output)
        report["after"] = stats
        solids = actual.split(only_watertight=False, repair=False)
        if (not actual.is_volume or len(solids) != expected_components or stats["degenerate_faces"]
                or not all(p.is_volume and np.isfinite(p.volume) for p in solids)):
            raise ValueError("readback failed: expected intact, watertight, consistently wound positive-volume components")
        # 校验后才公布。两种操作都在目标被另一进程抢先创建时失败。
        if os.name == "nt":
            os.rename(temp, output)
        else:
            os.link(temp, output)
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path, help="new path; existing files and input aliases are refused")
    filters = parser.add_mutually_exclusive_group()
    filters.add_argument("--keep-largest", action="store_true", help="keep one component with most faces (first tie)")
    filters.add_argument("--min-component-ratio", type=float, metavar="R",
                         help="keep face count >= R * largest; legacy R=1 keeps one largest; default keeps all")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable diagnostic report")
    args = parser.parse_args()
    if args.min_component_ratio is not None and not np.isfinite(args.min_component_ratio):
        parser.error("min-component-ratio must be finite and in [0, 1]")
    report = {"input": str(args.input), "output": str(args.output), "status": "FAIL",
              "before": None, "after": None, "filtered": [], "min_component_ratio": args.min_component_ratio,
              "keep_largest": args.keep_largest,
              "limitations": "Simple boundary repairs only. Self-intersections, missing design geometry and fit require separate inspection."}
    try:
        repair_file(args.input, args.output, args.min_component_ratio, args.keep_largest, report)
        report["status"] = "PASS"
    except (OSError, ValueError, ImportError, RuntimeError, IndexError) as exc:
        report["reason"] = str(exc)
    print(json.dumps(report, ensure_ascii=True, allow_nan=False, indent=None if args.json else 2))
    return int(report["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
