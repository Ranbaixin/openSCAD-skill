# openSCAD-skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Validate](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml)

**Cross-platform OpenSCAD skill for Codex and Claude** — AI-assisted CAD and STL tooling for 3D printing.

📖 [中文完整文档 →](README_zh.md)

## First run from the repository root

Install OpenSCAD and Python 3.11. The example uses built-in OpenSCAD geometry. Install the Python mesh tools in a virtual environment.

**Windows PowerShell**

```powershell
py -3.11 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe scripts/verify_assembly.py --out "$env:TEMP\CAD fit"
```

**macOS or Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/verify_assembly.py --out "${TMPDIR:-/tmp}/CAD fit"
```

The command prints the path to a fresh `run-*/report.json`. Each of `baseline/` and `variant/` contains printable `base.stl` and `lid.stl`, plus a reference PCB under `reference/`. Read the first failed or indeterminate check for its measurements, target, tolerance and renderer diagnostics. A required check without a pass gives a nonzero exit. Physical fit and strength require separate evidence. [Example and coordinates](examples/intermediate/assembly-fit/README.md)

Keep the input and write each revision to a new path. For STL diagnosis use `scripts/inspect_stl.py INPUT --json`. Repair preserves all components by default and rejects existing outputs. Without OpenSCAD a source delivery is **unrendered**. Missing Python geometry dependencies leave the corresponding measurements **unverified**. [STL repair](references/stl-workflow.md) · [Agent evaluation](evals/README.md)

## Who Is This For?

This skill is designed for a broad range of users — from beginners to experienced makers:

| User | Why it helps |
|------|--------------|
| 🎓 **3D Printing Beginners** | Start from an editable example and use the first-run command to render STL files and read their measurements. |
| 🔧 **Makers & Hobbyists** | Iterate on enclosures, brackets and mounting plates with named hole positions and measured clearances. |
| 🛠️ **Engineers & Hardware Devs** | Integrate with EDA tools (KiCad/Eagle → DXF → mounting plate). Batch-export multi-version parts with `-D` parameter overrides. BOSL2 and NopSCADlib patterns included. |
| 🤖 **AI/LLM Enthusiasts** | Run paired skill-on and skill-off tasks and score their files, tool calls and reports. |
| 📐 **OpenSCAD Learners** | Graded examples with Chinese annotations cover standard parts, assembly and inspection. |

### Typical Use Cases

- "I need a 100×60×3mm rounded plate with M3 mounting holes in a 4×2 grid" → parameterized SCAD with an STL export
- "Design an enclosure for this 85×55mm PCB with USB cutout" → parametric enclosure generated
- "Modify this existing STL — add 4mm mounting holes at the corners" → edits applied via OpenSCAD
- "Convert this KiCad PCB DXF into a 3D-printable mounting plate" → DXF parsed, plate with standoffs generated
- "Batch export the same bracket at 3mm, 5mm, and 8mm thickness" → three STLs from one command
- "Merge these two STL files into one printable model" → trimesh concatenation
- "Inspect or repair this binary STL" → deterministic mesh report and conservative repair script

### Scope & Limitations

**✅ Well-suited for:**
- Parametric mechanical parts (plates, brackets, enclosures, mounts, spacers)
- Grid-based designs (Gridfinity, honeycomb storage wall, pegboard accessories)
- Functional 3D prints with precise hole patterns and fasteners
- PCB mounting solutions and electronics enclosures
- Multi-part assemblies with fit tolerances

**⚠️ Less suited for:**
- Organic/artistic sculpting (use Blender or ZBrush instead)
- Complex curved surfaces and sweeps (OpenSCAD's CSG paradigm is not ideal)
- Models requiring constraint-based sketching (use Fusion 360 / FreeCAD)
- Rendering/visualization-focused work (OpenSCAD has basic preview only)

### Platforms & Tools

| Platform | Support |
|----------|---------|
| **Codex / Claude Code** (CLI) | Install the skill directory, then request a modeling task or invoke the skill by name. |
| **Claude Code** (VS Code / JetBrains) | ✅ Via IDE extensions |
| **Claude.ai** (Web chat) | ⚠️ Limited — file operations available but no local OpenSCAD execution |
| **Other AI tools** | 📖 Reference-only — SKILL.md and examples are educational resources |
| **Codewhale** | ✅ Compatible — install to `~/.codewhale/skills/` |
| **Any OpenSCAD user** | ✅ Standalone — examples and references work independent of Claude Code |

## Quick Install

```bash
# Clone as a Codex/Claude skill
git clone https://github.com/Ranbaixin/openSCAD-skill.git \
  ~/.claude/skills/openscad-modeling/

# For Codex, place the same folder under:
# %CODEX_HOME%/skills/openscad-modeling/  (Windows)
# or ~/.codex/skills/openscad-modeling/   (macOS/Linux)

# Or add as a git submodule to your project
git submodule add https://github.com/Ranbaixin/openSCAD-skill.git \
  .claude/skills/openscad-modeling/
```

## What This Skill Does

This skill teaches Claude how to:
- **Create** parametric 3D models — plates, brackets, enclosures, hinges, snap-fit lids
- **Modify** existing `.scad` and `.stl` files
- **Export** STL/3MF for 3D printing, with multi-version batch export
- **Analyze** STL dimensions and structure
- **Import** DXF files (from KiCad/Eagle PCB designs) to generate mounting plates
- **Merge** multiple STL models via Python trimesh
- **Inspect and repair** ASCII/binary STL, including isolated components and simple boundary defects
- **Validate** SCAD renders without leaving build artifacts in the repository

## Examples

The examples progress from individual parts to assemblies.

| Level | Examples | Skills Demonstrated |
|-------|----------|---------------------|
| **Basic** | Rounded plate, L-bracket, Snap-fit lid | `hull()`, `difference()`, parametric design, tolerances |
| **Intermediate** | Enclosure, print-in-place hinge, Gridfinity, enclosure wall change | Standoffs, ventilation, fixed hole positions and measured PCB clearance |
| **Advanced** | BOSL2 fasteners, Multi-part assembly, DXF import | `use<>` patterns, `anchor/spin/attach`, DXF workflow |

See **[examples/](examples/)** for all files.

## Requirements

- **OpenSCAD** (latest stable or nightly) — [download](https://openscad.org/downloads.html)
- **Python 3.11** is the CI version for geometry verification. Rendering a single SCAD directly only needs OpenSCAD.
  ```bash
  python -m pip install -r requirements.txt pytest
  ```
- **BOSL2** (optional) — for advanced examples; install via `git submodule add`

## Documentation

| File | Content |
|------|---------|
| [SKILL.md](SKILL.md) | Core skill definition (Chinese) |
| [README_zh.md](README_zh.md) | Full Chinese documentation |
| [references/](references/) | Progressive disclosure references — loaded on demand by Claude |
| [scripts/](scripts/) | Cross-platform OpenSCAD discovery, STL inspection/repair, and SCAD validation |
| [examples/](examples/) | Parameterized examples at three levels |

### Reference Guides

- [Screw sizes](references/screw-sizes.md) — M1.6–M8 holes, nuts, heat-set inserts
- [BOSL2 patterns](references/bosl2-patterns.md) — Anchor, spin, orient, attach, threading
- [NopSCADlib](references/nopscadlib-vitamins.md) — Real-world parts library
- [Project conventions](references/project-conventions.md) — Layout, `use` vs `include`, Makefile
- [Gotchas](references/gotchas-and-workarounds.md) — Common pitfalls and workarounds
- [Toolchain](references/toolchain-guide.md) — Editors, formatters, CI/CD setup
- [DXF import](references/dxf-import-guide.md) — PCB DXF to mounting plate workflow

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding examples, references, or improvements.

## License

MIT — see [LICENSE](LICENSE).

---

*Designed for [Codex](https://openai.com/codex/) and [Claude Code](https://claude.ai/code) — AI-assisted CAD workflows for developers.*
