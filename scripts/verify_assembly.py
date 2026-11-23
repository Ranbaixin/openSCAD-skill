#!/usr/bin/env python3
"""Export and measure both wall variants of the synthetic enclosure in a fresh run directory."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from .validate_scad import OpenSCAD, configure_console, find_openscad, renderer_path
else:
    from validate_scad import OpenSCAD, configure_console, find_openscad, renderer_path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "examples/intermediate/assembly-fit/enclosure.scad"
PARTS = ("base", "lid", "pcb")


@contextmanager
def render_directory(output):
    writable_path = renderer_path(output)
    if writable_path is not None:
        yield writable_path
        return
    # 部分 Windows 卷禁用短文件名。所有相对 import 必须在同一目录树中解析。
    with tempfile.TemporaryDirectory(prefix="openscad-fit-") as scratch:
        working = renderer_path(Path(scratch))
        if working is None:
            raise ValueError("Windows OpenSCAD cannot read the temporary path; point TEMP and TMP "
                             "to a writable ASCII directory and rerun")
        try:
            yield working
        finally:
            shutil.copytree(scratch, output, dirs_exist_ok=True)


def planned_checks():
    targets = {"environment": "OpenSCAD, numpy, trimesh and networkx available",
               "controls": "known disjoint, touching and overlapping solids"}
    for role in ("baseline", "variant"):
        for part in PARTS:
            for check, target in (("export", "exit 0, no render diagnostics, complete binary STL"),
                                  ("mesh", "one closed, outward-oriented solid with specified bounds"),
                                  ("holes", "four specified circular bores at all inspection depths")):
                targets[f"{role}.{part}.{check}"] = target
        targets[f"{role}.base.wall"] = "requested sidewall thickness at four locations (mm)"
        targets[f"{role}.base.floor"] = {"floor_mm": [2]*4}
        targets[f"{role}.base.bosses"] = {"outside_diameter_mm": 6, "count": 4}
        for check in ("rim_contact", "support_contact", "lid_fit", "pcb_fit", "pcb_space",
                      "through", "contact_clearance", "hole_material"):
            targets[f"{role}.{check}"] = "volume residual within tolerance"
    for part in PARTS:
        targets[f"comparison.{part}"] = "symmetric difference within tolerance after allowed sidewall change"
    return {key: {"name": key, "status": "NOT_RUN", "reason": "prerequisite did not pass",
                  "measured": None, "expected": goal, "tolerance": None} for key, goal in targets.items()}


class Measurements:
    def __init__(self, run, model, wall):
        self.run = run
        self.model = model
        self.wall = wall
        self.rows = planned_checks()
        self.report = {"schema_version": 1, "status": "INDETERMINATE", "model": str(model),
                       "parameters_mm": {"baseline": 2, "variant": wall}, "units": "mm",
                       "scope": "Final static pose only. Printing accuracy, insertion path and strength untested.",
                       "assembly_translation_mm": {"base": [0,0,0], "lid": [0,0,16], "pcb": [0,0,0]},
                       "platform": platform.platform(), "python": sys.version, "packages": {},
                       "openscad": {}, "checks": list(self.rows.values()), "renders": [], "artifacts": {}}
        self.diagnostics = run / "diagnostics"
        self.diagnostics.mkdir()

    def record(self, name, passed, measured, expected, tolerance=None, reason=None):
        self.rows[name].update(status="PASS" if passed else "FAIL", measured=measured, expected=expected,
                               tolerance=tolerance, reason=reason or ("within specification" if passed else "outside specification"))

    def unknown(self, name, error):
        self.rows[name].update(status="INDETERMINATE", reason=str(error))

    def render(self, target, **options):
        target.parent.mkdir(parents=True, exist_ok=True)
        event = self.cad.render(self.model, target, **options)
        event["output"] = target.relative_to(self.run).as_posix()
        self.report["renders"].append(event)
        if "union()" in (options.get("expression") or "") and event.get("backend_observed"):
            self.report["openscad"]["backend_actual"] = event["backend_observed"]
        if "error" in event:
            raise ValueError(event["error"])

    def solid(self, path, mesh):
        rel = Path(os.path.relpath(path, self.diagnostics)).as_posix()
        return self.geo.Solid(f"import({json.dumps(rel)});", float(mesh.volume))

    def boolean_solid(self, name, expression):
        path = self.diagnostics / (name + ".stl")
        self.render(path, expression=expression)
        mesh = self.load_mesh(path)
        if not mesh.is_volume or not math.isfinite(mesh.volume) or not mesh.nondegenerate_faces().all():
            raise ValueError(f"{name}: invalid boolean result, volume={mesh.volume}, closed={mesh.is_watertight}")
        return self.solid(path, mesh)

    def residual(self, name, a, b, mode):
        g = self.geo
        joined = self.boolean_solid(name + ".union", g.csg("union", a.expression, b.expression))
        if mode == "overlap":
            value = a.volume + b.volume - joined.volume
        elif mode == "missing":
            value = joined.volume - a.volume
        else:
            value = 2*joined.volume - a.volume - b.volume
        if value < -g.VOLUME_TOL or not math.isfinite(value):
            raise ValueError(f"inconsistent {mode} volume: {value} mm3")
        return joined, value

    def volume_check(self, name, a, b, mode="overlap", target=0):
        g = self.geo
        try:
            joined, value = self.residual(name, a, b, mode)
            passed = abs(value-target) <= g.VOLUME_TOL
            self.record(name, passed, value, {mode + "_mm3": target}, g.VOLUME_TOL,
                        "volume within tolerance" if passed else f"{mode} volume exceeds tolerance")
            self.rows[name]["operand_and_union_volumes_mm3"] = [a.volume, b.volume, joined.volume]
            return joined
        except (ValueError, OSError, RuntimeError) as exc:
            self.unknown(name, exc)
            return None

    def controls(self):
        g = self.geo
        measured = []
        try:
            unit = self.boolean_solid("control.cube", "cube(1);")
            for label, x in (("disjoint", 2), ("touch", 1), ("overlap", 0.5)):
                joined = self.boolean_solid("control." + label, g.csg("union", unit.expression,
                                                                    g.place([x,0,0], unit.expression)))
                measured.append(2*unit.volume - joined.volume)
            targets = [0, 0, 0.5]
            passed = abs(unit.volume-1) <= g.VOLUME_TOL and all(
                abs(actual-target) <= g.VOLUME_TOL for actual, target in zip(measured, targets))
            self.record("controls", passed, measured, targets, g.VOLUME_TOL)
            return passed
        except (ValueError, OSError, RuntimeError) as exc:
            self.unknown("controls", exc)
            return False

    def part(self, role, part, thickness):
        g = self.geo
        name = role + "." + part
        folder = self.run / role
        if part == "pcb":
            folder = folder / "reference"
        path = folder / (part + ".stl")
        try:
            self.render(path, defines={"wall": thickness, "part": part})
        except (ValueError, OSError) as exc:
            self.record(name+".export", False, self.report["renders"][-1] if self.report["renders"] else None,
                        "successful OpenSCAD binary STL export", reason=str(exc))
            return None
        self.record(name+".export", True, {"bytes": path.stat().st_size, "exit_code": 0},
                    "successful OpenSCAD binary STL export")
        self.report["artifacts"][name] = {"path": path.relative_to(self.run).as_posix(),
                                        "role": "reference" if part == "pcb" else "print",
                                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        key = name + ".mesh"
        try:
            mesh = self.load_mesh(path)
            facts = self.mesh_report(mesh, str(path.relative_to(self.run)))
            expected = {"bounds_mm": g.BOUNDS[part], "component_count": 1, "watertight": True,
                        "winding_consistent": True, "signed_volume_mm3": "> 0", "degenerate_faces": 0}
            delta = abs(mesh.bounds - g.BOUNDS[part]).max()
            valid = (mesh.is_volume and math.isfinite(mesh.volume) and facts["component_count"] == 1
                     and facts["degenerate_faces"] == 0 and delta <= g.LENGTH_TOL)
            differences = [str(field) for field in ("component_count","watertight","winding_consistent","degenerate_faces")
                           if facts[field] != expected[field]]
            if delta > g.LENGTH_TOL:
                differences.append("bounds_mm")
            if not mesh.is_volume or not math.isfinite(mesh.volume):
                differences.append("valid positive volume")
            self.record(key, valid, facts, expected, {"bounds_mm": g.LENGTH_TOL},
                        reason="mesh meets print/reference contract" if valid else "mesh mismatch: " + ", ".join(differences))
            if not valid:
                return None
            key = name + ".holes"
            passed, profiles = g.hole_profiles(mesh, part)
            self.record(key, passed, profiles, {"centers_mm": g.HOLES, "diameter_mm": g.BORE,
                                               "fixed_depths_mm": g.DEPTHS[part]}, g.LENGTH_TOL,
                        reason="all measured hole profiles match" if passed else "missing, shifted or out-of-size bore; see profiles by center and depth")
            if part == "base":
                key = name + ".floor"
                floor = g.floor_widths(mesh)
                self.record(key, len(floor)==4 and all(abs(x-2) <= g.LENGTH_TOL for x in floor),
                            floor, [2]*4, g.LENGTH_TOL)
                key = name + ".bosses"
                passed, bosses = g.hole_profiles(mesh, part, bosses=True)
                self.record(key, passed, bosses, {"centers_mm":g.HOLES, "outside_diameter_mm":6,
                                                  "depths_mm":[4.5,5.8]}, g.LENGTH_TOL)
                key = name + ".wall"
                widths = g.wall_widths(mesh)
                self.record(key, len(widths) == 4 and all(abs(x-thickness) <= g.LENGTH_TOL for x in widths),
                            widths, [thickness]*4, g.LENGTH_TOL)
            return self.solid(path, mesh)
        except (ValueError, OSError, RuntimeError, IndexError) as exc:
            self.unknown(key, exc)
            return None

    def assembly(self, role, parts, thickness):
        g = self.geo
        base, lid, pcb = (parts[p] for p in PARTS)
        lid = g.Solid(g.place([0,0,16], lid.expression), lid.volume)
        placed = {"base":base, "lid":lid, "pcb":pcb}
        for label, halves in g.material_gauges(thickness).items():
            key = role + "." + label
            try:
                missing = {}
                for owner, expression in halves.items():
                    name = key + "." + owner
                    gauge = self.boolean_solid(name + ".gauge", expression)
                    _, missing[owner] = self.residual(name, placed[owner], gauge, "missing")
                self.record(key, all(abs(v) <= g.VOLUME_TOL for v in missing.values()),
                            missing, {"missing_volume_mm3":dict.fromkeys(halves, 0)}, g.VOLUME_TOL)
            except (ValueError, OSError, RuntimeError) as exc:
                self.unknown(key, exc)
        case = self.volume_check(role+".lid_fit", base, lid)
        if not case:
            return
        assembled = self.volume_check(role+".pcb_fit", case, pcb)
        for label, expression in g.gauges(thickness).items():
            key = role+"."+label
            subject = case if label in ("pcb_space", "contact_clearance") else assembled
            if subject:
                try:
                    gauge = self.boolean_solid(key+".gauge", expression)
                    self.volume_check(key, subject, gauge)
                except (ValueError, OSError, RuntimeError) as exc:
                    self.unknown(key, exc)

    def execute(self, backend):
        try:
            if __package__:
                from . import assembly_geometry as g
                from .inspect_stl import load_mesh, mesh_report
            else:
                import assembly_geometry as g
                from inspect_stl import load_mesh, mesh_report
            self.geo, self.load_mesh, self.mesh_report = g, load_mesh, mesh_report
            self.report["packages"] = {p: importlib.metadata.version(p) for p in ("trimesh","numpy","networkx")}
        except ImportError as exc:
            raise ValueError(f"geometry dependencies unavailable ({exc}); install with python -m pip install -r requirements.txt") from exc
        executable = find_openscad()
        if not executable:
            raise ValueError("OpenSCAD not found; set OPENSCAD to its executable or install OpenSCAD")
        self.cad = OpenSCAD.probe(executable, backend)
        self.report["openscad"] = {"path": executable, "version": self.cad.version, "backend_requested": backend,
                                   "backend_option_sent": self.cad.backend_option, "backend_actual": None}
        self.report["model_sha256"] = hashlib.sha256(self.model.read_bytes()).hexdigest()
        self.record("environment", True, self.report["openscad"], "OpenSCAD and geometry dependencies available")
        calibrated = self.controls()
        versions = []
        for role, thickness in (("baseline", 2), ("variant", self.wall)):
            parts = {p: self.part(role, p, thickness) for p in PARTS}
            versions.append(parts)
            if calibrated and all(parts.values()):
                self.assembly(role, parts, thickness)
        if not calibrated:
            return
        original, changed = versions
        for part in PARTS:
            nominal = original[part]
            if not nominal or not changed[part]:
                continue
            key = "comparison." + part
            try:
                if part == "base":
                    if self.wall >= 2:
                        expected = g.csg("union", nominal.expression, g.sidewalls(self.wall))
                    else:
                        removed = g.csg("difference", g.sidewalls(2), g.sidewalls(self.wall))
                        expected = g.csg("difference", nominal.expression, removed)
                    nominal = self.boolean_solid("expected.base", expected)
                self.volume_check(key, nominal, changed[part], "symmetric_difference")
            except (ValueError, OSError, RuntimeError) as exc:
                self.unknown(key, exc)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wall", type=float, default=3, help="variant sidewall thickness in mm (baseline is always 2)")
    parser.add_argument("--out", type=Path, required=True, help="parent for a new run-* directory on every invocation")
    parser.add_argument("--model", type=Path, default=MODEL, help="SCAD implementing part and wall selectors")
    parser.add_argument("--backend", choices=("manifold", "CGAL"), default="manifold")
    args = parser.parse_args()
    if not math.isfinite(args.wall) or not 0 < args.wall < 30:
        parser.error("wall must be finite, positive and leave an inner cavity (< 30 mm)")
    args.out.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=args.out.resolve()))
    model = args.model.resolve()
    check = None
    try:
        with render_directory(run) as working:
            check = Measurements(working, model, args.wall)
            check.report.update(render_directory=str(working), output_directory=str(run))
            check.execute(args.backend)
    except (ValueError, OSError, RuntimeError, ImportError, subprocess.SubprocessError) as exc:
        if check is None:
            check = Measurements(run, model, args.wall)
        if check.rows["environment"]["status"] == "NOT_RUN":
            check.unknown("environment", exc)
        check.report["error"] = str(exc)
        print(str(exc), file=sys.stderr)
    states = {row["status"] for row in check.rows.values()}
    status = "PASS" if states == {"PASS"} and "error" not in check.report else (
        "FAIL" if "FAIL" in states else "INDETERMINATE")
    check.report["status"] = status
    path = run / "report.json"
    path.write_text(json.dumps(check.report, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(f"{status} {path}")
    return int(status != "PASS")


if __name__ == "__main__":
    configure_console()
    raise SystemExit(main())
