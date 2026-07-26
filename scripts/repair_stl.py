#!/usr/bin/env python3
"""Repair common STL issues without silently changing the largest component."""

from __future__ import annotations

import argparse
from pathlib import Path

import trimesh

try:  # Support both `python -m scripts.repair_stl` and direct execution.
    from .inspect_stl import load_mesh, mesh_report
except ImportError:  # pragma: no cover - exercised by the direct CLI form.
    from inspect_stl import load_mesh, mesh_report


def repair_mesh(mesh: trimesh.Trimesh, min_component_ratio: float = 1.0) -> trimesh.Trimesh:
    """Keep the main component and apply conservative trimesh repairs."""
    if not 0 <= min_component_ratio <= 1:
        raise ValueError("min_component_ratio must be between 0 and 1")
    components = sorted(mesh.split(only_watertight=False), key=lambda item: len(item.faces), reverse=True)
    if not components:
        raise ValueError("Input contains no mesh components")
    largest = components[0]
    if min_component_ratio >= 1.0:
        selected = [largest]
    else:
        threshold = len(largest.faces) * min_component_ratio
        selected = [part for part in components if len(part.faces) >= threshold]
    result = selected[0] if len(selected) == 1 else trimesh.util.concatenate(selected)
    result = result.copy()
    result.merge_vertices()
    result.remove_unreferenced_vertices()
    result.update_faces(result.nondegenerate_faces())
    result.update_faces(result.unique_faces())
    trimesh.repair.fix_inversion(result, multibody=True)
    trimesh.repair.fix_winding(result)
    trimesh.repair.fill_holes(result)
    trimesh.repair.fix_normals(result, multibody=True)
    result.remove_unreferenced_vertices()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--min-component-ratio", type=float, default=1.0)
    args = parser.parse_args()
    source = load_mesh(args.input)
    repaired = repair_mesh(source, args.min_component_ratio)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    repaired.export(args.output)
    print("before:")
    print(mesh_report(source, args.input))
    print("after:")
    print(mesh_report(repaired, args.output))
    if not repaired.is_watertight:
        raise SystemExit("Repair completed but output is still not watertight; inspect the report before printing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
