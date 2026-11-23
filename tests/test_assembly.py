import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts import verify_assembly
from scripts.inspect_stl import load_mesh

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "examples/intermediate/assembly-fit/enclosure.scad"


def run_case(tmp_path, model=None):
    out = tmp_path / "装配 📐 evidence"
    args = [sys.executable, "-X", "utf8", str(ROOT / "scripts/verify_assembly.py"), "--out", str(out)]
    if model:
        args.extend(["--model", str(model)])
    result = subprocess.run(args, cwd=ROOT, capture_output=True, encoding="utf-8", timeout=360)
    reports = list(out.glob("*/report.json"))
    assert len(reports) == 1, result.stderr + result.stdout
    evidence = json.loads(reports[0].read_text(encoding="utf-8"))
    checks = {row["name"]: row for row in evidence["checks"]}
    assert len(checks) == len(evidence["checks"])
    return result, checks, reports[0]


def test_wall_variants_preserve_assembly(tmp_path):
    result, checks, path = run_case(tmp_path)
    problems = [(r["name"], r["reason"]) for r in checks.values() if r["status"] in ("FAIL", "INDETERMINATE")]
    assert result.returncode == 0, (path, problems)
    for prefix, thickness in (("baseline", 2), ("variant", 3)):
        assert checks[f"{prefix}.base.wall"]["measured"] == pytest.approx([thickness] * 4)
        for part in ("base", "lid", "pcb"):
            assert checks[f"{prefix}.{part}.holes"]["status"] == "PASS"
        for probe in ("pcb_space", "lid_fit", "through", "hole_material", "contact_clearance",
                      "rim_contact", "support_contact", "base.floor", "base.bosses"):
            assert checks[f"{prefix}.{probe}"]["status"] == "PASS"
    assert checks["comparison.base"]["status"] == "PASS"
    assert checks["comparison.lid"]["status"] == checks["comparison.pcb"]["status"] == "PASS"


def test_publish_mesh_when_volume_has_no_usable_short_path(tmp_path, monkeypatch):
    destination = tmp_path / "装配 📐"
    destination.mkdir()
    original = verify_assembly.renderer_path
    monkeypatch.setattr(verify_assembly, "renderer_path",
                        lambda path: None if path == destination else original(path))
    cad = verify_assembly.OpenSCAD.probe(verify_assembly.find_openscad())
    with verify_assembly.render_directory(destination) as working:
        assert working != destination
        result = cad.render(None, working / "cube.stl", expression="cube(2);")
        assert "error" not in result, result
        joined = cad.render(None, working / "pair.stl",
                            expression='union(){import("cube.stl");translate([3,0,0]) cube(1);}')
        assert "error" not in joined, joined
    assert not working.exists()
    assert load_mesh(destination / "pair.stl").volume == pytest.approx(9)


@pytest.mark.parametrize("fault,expression,check", [
    ("hole", "base(wall, [[11,10],[90,10],[10,50],[90,50]]);", "base.holes"),
    ("pcb", "union(){base(wall); translate([48,28,1]) cube([4,4,7]);}", "pcb_space"),
    ("extra", "union(){base(wall); translate([40,25,9]) cube(2);}", "base.mesh"),
    ("plug", "union(){base(wall); translate([10,10,3.1]) cylinder(d=4,h=0.2);}", "through"),
    ("wide", "difference(){base(wall); translate([10,10,2.1]) cylinder(d=3.55,h=2,$fn=64);}", "hole_material"),
    ("contact", "union(){base(wall); translate([48,28,1]) cube([2,2,5]);}", "contact_clearance"),
])
def test_real_geometry_fault(tmp_path, fault, expression, check):
    shutil.copyfile(MODEL, tmp_path / "normal.scad")
    model = tmp_path / f"{fault}.scad"
    model.write_text(
        'use <normal.scad>;\npart="base"; wall=2;\n'
        'if (part=="base") { if (wall==2) base(wall); else ' + expression + ' }\n'
        'else if (part=="lid") lid(); else if (part=="pcb") pcb();\n', encoding="utf-8")
    result, checks, report = run_case(tmp_path, model)
    assert result.returncode != 0, report
    row = checks[f"variant.{check}"]
    assert row["status"] == "FAIL" and row["reason"], (row, report)
    if fault == "hole":
        assert row["measured"][0]["centers_mm"][0] == pytest.approx([11,10], abs=0.05)
    if fault == "pcb":
        assert row["measured"] == pytest.approx(32, abs=0.01)
    if fault == "extra":
        assert row["measured"]["component_count"] == 2


@pytest.mark.parametrize("scad,diagnostic", [
    ("cube(;", "parser"), ("intersection(){cube(1);translate([2,0,0])cube(1);}", "empty"),
    ('union(){cube(1);import("missing-fixture.stl");}', "import"),
])
def test_failed_export_never_clears_space(tmp_path, scad, diagnostic):
    model = tmp_path / "bad.scad"
    model.write_text(scad, encoding="utf-8")
    result, checks, path = run_case(tmp_path, model)
    assert result.returncode != 0
    assert checks["baseline.base.export"]["status"] == "FAIL"
    assert diagnostic in checks["baseline.base.export"]["reason"].lower(), path
    assert checks["baseline.pcb_space"]["status"] == "NOT_RUN"


def test_both_versions_can_share_the_same_fault(tmp_path):
    text = MODEL.read_text(encoding="utf-8").replace("floor_thickness = 2;", "floor_thickness = 3;")
    text = text.replace("boss_diameter = 6;", "boss_diameter = 4.6;")
    text = text.replace('else if (part == "lid") lid();', '''
else if (part == "lid") difference(){
    lid();
    difference(){cube([100,60,0.65]); translate([4,4,-1]) cube([92,52,3]);}
}''')
    model = tmp_path/"shared-fault.scad"
    model.write_text(text, encoding="utf-8")
    result, checks, report = run_case(tmp_path, model)
    assert result.returncode != 0, report
    for role in ("baseline", "variant"):
        for name in ("base.floor", "base.bosses", "rim_contact"):
            assert checks[f"{role}.{name}"]["status"] == "FAIL", report
        assert checks[f"{role}.base.floor"]["measured"] == pytest.approx([3]*4)
