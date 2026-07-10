# openSCAD-skill

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Validate](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Ranbaixin/openSCAD-skill/actions/workflows/validate.yml)

**Claude Code skill for OpenSCAD parametric 3D modeling** — AI-assisted CAD for 3D printing.

📖 [中文完整文档 →](README_zh.md)

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
