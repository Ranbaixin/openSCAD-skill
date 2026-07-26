#!/usr/bin/env python3
"""Inspect ASCII or binary STL meshes and print actionable geometry facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import trimesh


def load_mesh(path: str | Path) -> trimesh.Trimesh:
    """Load any mesh format supported by trimesh and combine scene geometry."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    loaded = trimesh.load(source, force="scene")
    if isinstance(loaded, trimesh.Scene):
        if not loaded.geometry:
            raise ValueError(f"No mesh geometry found in {source}")
        mesh = loaded.to_mesh()
    else:
        mesh = loaded
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise ValueError(f"No triangular mesh found in {source}")
    return mesh


def mesh_report(mesh: trimesh.Trimesh, source: str | Path | None = None) -> dict[str, Any]:
    """Return JSON-serializable mesh diagnostics."""
    components = mesh.split(only_watertight=False)
    return {
        "path": str(source) if source is not None else None,
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds_min_mm": [float(v) for v in mesh.bounds[0]],
        "bounds_max_mm": [float(v) for v in mesh.bounds[1]],
        "extents_mm": [float(v) for v in mesh.extents],
        "volume_mm3": float(abs(mesh.volume)),
        "surface_area_mm2": float(mesh.area),
        "component_count": int(len(components)),
        "component_face_counts": sorted((int(len(c.faces)) for c in components), reverse=True),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "broken_face_count": int(len(trimesh.repair.broken_faces(mesh))),
        "euler_number": int(mesh.euler_number),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    try:
        report = mesh_report(load_mesh(args.input), args.input)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"file: {report['path']}")
        print(f"size_mm: {report['extents_mm']}")
        print(f"volume_mm3: {report['volume_mm3']:.3f}")
        print(f"components: {report['component_count']}  watertight: {report['watertight']}")
        print(f"broken_faces: {report['broken_face_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
