# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-07-10

### Added

- Core skill: `openscad-modeling` for OpenSCAD parametric 3D modeling
- Cross-platform OpenSCAD CLI discovery (`scripts/find-openscad.sh`, `scripts/find-openscad.ps1`)
- Progressive disclosure architecture with 7 reference files:
  - `references/screw-sizes.md` — Complete M1.6–M8 fastener reference table
  - `references/bosl2-patterns.md` — BOSL2 anchor/spin/attach patterns
  - `references/nopscadlib-vitamins.md` — NopSCADlib real-world parts guide
  - `references/project-conventions.md` — Project structure and conventions
  - `references/gotchas-and-workarounds.md` — Common pitfalls catalog
  - `references/toolchain-guide.md` — Editor, formatter, and CI/CD setup
  - `references/dxf-import-guide.md` — DXF to SCAD workflow
- 9 parameterized example SCAD files across 3 difficulty levels:
  - **Basic**: rounded plate, L-bracket, snap-fit lid
  - **Intermediate**: enclosure, print-in-place hinge, Gridfinity baseplate
  - **Advanced**: BOSL2 threaded fasteners, multi-part assembly, DXF mounting plate
- GitHub Actions CI pipeline to validate all examples render correctly
- Local verification script (`tests/verify-examples.sh`)
- MIT License
- Chinese and English documentation (`README.md`, `README_zh.md`)
- Contribution guide (`CONTRIBUTING.md`)
- AGENTS.md with repository conventions for Claude Code agents

### Changed

- De-hardcoded all platform-specific paths from SKILL.md
- Updated frontmatter with `version`, `license`, `allowed-tools`, `paths`, `compatibility` fields

### Fixed

- Description format updated to third-person convention for Claude Code skill discovery
