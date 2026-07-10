# openSCAD-skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Validate](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml)

**Claude Code skill for OpenSCAD parametric 3D modeling** — AI-assisted CAD for 3D printing.

📖 [中文完整文档 →](README_zh.md)

## Who Is This For?

This skill is designed for a broad range of users — from beginners to experienced makers:

| User | Why it helps |
|------|--------------|
| 🎓 **3D Printing Beginners** | Start with parametric templates — skip the steep OpenSCAD learning curve. Describe your idea in natural language, get working SCAD code and STL output. |
| 🔧 **Makers & Hobbyists** | Rapidly iterate on enclosures, brackets, mounting plates. No need to manually calculate hole positions or clearance tolerances — the skill handles it. |
| 🛠️ **Engineers & Hardware Devs** | Integrate with EDA tools (KiCad/Eagle → DXF → mounting plate). Batch-export multi-version parts with `-D` parameter overrides. BOSL2 and NopSCADlib patterns included. |
| 🤖 **AI/LLM Enthusiasts** | A reference implementation of a well-structured Claude Code skill: progressive disclosure, `references/` architecture, `paths` scoping, CI/CD validation. |
| 📐 **OpenSCAD Learners** | 9 graded example files (basic → intermediate → advanced) with Chinese annotations. Reference guides cover screw specs, BOSL2 patterns, and real-world gotchas. |

### Typical Use Cases

- "I need a 100×60×3mm rounded plate with M3 mounting holes in a 4×2 grid" → working STL in seconds
- "Design an enclosure for this 85×55mm PCB with USB cutout" → parametric enclosure generated
- "Modify this existing STL — add 4mm mounting holes at the corners" → edits applied via OpenSCAD
- "Convert this KiCad PCB DXF into a 3D-printable mounting plate" → DXF parsed, plate with standoffs generated
- "Batch export the same bracket at 3mm, 5mm, and 8mm thickness" → three STLs from one command
- "Merge these two STL files into one printable model" → trimesh concatenation

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
| **Claude Code** (CLI) | ✅ Native — skill auto-activates on SCAD/STL/3MF/DXF files |
| **Claude Code** (VS Code / JetBrains) | ✅ Via IDE extensions |
| **Claude.ai** (Web chat) | ⚠️ Limited — file operations available but no local OpenSCAD execution |
| **Other AI tools** | 📖 Reference-only — SKILL.md and examples are educational resources |
| **Codewhale** | ✅ Compatible — install to `~/.codewhale/skills/` |
| **Any OpenSCAD user** | ✅ Standalone — examples and references work independent of Claude Code |

## Quick Install

```bash
# Clone as a Claude Code skill
git clone https://github.com/Ranbaixin/openSCAD-skill.git \
  ~/.claude/skills/openscad-modeling/

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

## Examples

Nine progressively complex, production-ready SCAD examples included:

| Level | Examples | Skills Demonstrated |
|-------|----------|---------------------|
| **Basic** | Rounded plate, L-bracket, Snap-fit lid | `hull()`, `difference()`, parametric design, tolerances |
| **Intermediate** | Enclosure, Print-in-place hinge, Gridfinity | `for` loops, standoffs, ventilation, standard compliance |
| **Advanced** | BOSL2 fasteners, Multi-part assembly, DXF import | `use<>` patterns, `anchor/spin/attach`, DXF workflow |

See **[examples/](examples/)** for all files.

## Requirements

- **OpenSCAD** (latest stable or nightly) — [download](https://openscad.org/downloads.html)
- **Python 3.8+** (optional) — for STL validation/merging and DXF parsing
- **BOSL2** (optional) — for advanced examples; install via `git submodule add`

## Documentation

| File | Content |
|------|---------|
| [SKILL.md](SKILL.md) | Core skill definition (Chinese) |
| [README_zh.md](README_zh.md) | Full Chinese documentation |
| [references/](references/) | Progressive disclosure references — loaded on demand by Claude |
| [examples/](examples/) | 9 parameterized SCAD examples at 3 levels |

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

*Made for [Claude Code](https://claude.ai/code) — the AI-powered CLI for developers.*
