# Cross-Platform OpenSCAD Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the OpenSCAD skill reliable on Ran-xin's Windows machine while remaining useful as a cross-platform, Codex/Claude-compatible open-source skill.

**Architecture:** Keep `SKILL.md` concise and workflow-focused. Move deterministic STL inspection/repair and OpenSCAD discovery into reusable scripts, expose UI metadata through `agents/openai.yaml`, and validate examples plus scripts in local and GitHub Actions checks.

**Tech Stack:** Markdown/YAML, Python 3.8+, `trimesh`/`numpy` (optional STL tooling), OpenSCAD CLI, POSIX shell, PowerShell, GitHub Actions.

## Global Constraints

- Preserve the existing OpenSCAD examples and reference files unless a documented compatibility fix is required.
- Never commit generated `.stl`, `.3mf`, or `.png` artifacts.
- Support Windows PowerShell, macOS, and Linux discovery paths.
- Keep `SKILL.md` under 500 lines and use progressive disclosure for detailed references.
- Scripts must fail with actionable messages when optional dependencies or OpenSCAD are missing.

---

### Task 1: Add deterministic STL inspection and repair tooling

**Files:**
- Create: `scripts/inspect_stl.py`
- Create: `scripts/repair_stl.py`
- Create: `tests/test_stl_tools.py`

**Interfaces:**
- `inspect_stl.py INPUT [--json]` prints bounds, extents, volume, area, component count, watertight state, broken-face count, and format-independent mesh statistics.
- `repair_stl.py INPUT OUTPUT [--min-component-ratio R]` keeps the largest connected component, merges duplicate vertices, fixes normals, attempts safe hole filling, writes the output, and prints a before/after report.
- Library functions are importable as `load_mesh()`, `mesh_report()`, and `repair_mesh()` for tests.

- [ ] Write tests that prove binary and ASCII STL inspection returns the same required fields, and that a fixture with an isolated component is reduced to one component.
- [ ] Run `python -m pytest tests/test_stl_tools.py -q` and confirm the new tests fail before implementation.
- [ ] Implement format detection through `trimesh.load`, largest-component selection, vertex merging, normal repair, and explicit output validation.
- [ ] Run the focused tests and then inspect a real STL from the user's model folder without modifying it.

### Task 2: Improve cross-platform OpenSCAD discovery and validation

**Files:**
- Modify: `scripts/find-openscad.ps1`
- Modify: `scripts/find-openscad.sh`
- Create: `scripts/validate_scad.py`
- Modify: `tests/verify-examples.sh`

**Interfaces:**
- Discovery scripts return a usable executable path and a non-zero status with install guidance when unavailable.
- `validate_scad.py FILE... [--backend manifold| CGAL]` renders each file to a temporary output and reports per-file status without leaving artifacts in the repository.

- [ ] Add tests for PATH lookup, standard Windows install paths, macOS bundle path, and Linux PATH lookup using mocked environments.
- [ ] Run the new discovery tests before implementation and record the failing cases.
- [ ] Implement platform-safe quoting, temporary-directory cleanup, and backend fallback behavior.
- [ ] Run all basic/intermediate examples locally with the installed Windows OpenSCAD CLI.

### Task 3: Rewrite the skill workflow and add Codex metadata

**Files:**
- Modify: `SKILL.md`
- Create: `agents/openai.yaml`
- Create: `references/stl-workflow.md`

**Interfaces:**
- Frontmatter description explicitly triggers for SCAD creation, STL/3MF analysis, STL repair, conversion, and export.
- The body routes detailed mesh operations to `references/stl-workflow.md` and deterministic commands to `scripts/`.

- [ ] Add a failing metadata validation check for missing `agents/openai.yaml` and incomplete trigger coverage.
- [ ] Implement concise platform-neutral workflow, Windows notes, ASCII temporary-path guidance, SCAD-vs-STL decision rules, and verification gates.
- [ ] Add UI metadata with deterministic display name, short description, and default prompt.
- [ ] Run the repository's skill validation and inspect the final file for duplicated or contradictory instructions.

### Task 4: Update documentation and CI for general use

**Files:**
- Modify: `README.md`
- Modify: `README_zh.md`
- Modify: `AGENTS.md`
- Modify: `.github/workflows/validate.yml`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Docs contain matching commands for Windows PowerShell, macOS/Linux shells, and Codex/Claude installation.
- CI validates SCAD examples and Python tooling on Windows, Ubuntu, and macOS without committing artifacts.

- [ ] Add CI matrix entries and a script test job before changing implementation, then validate the workflow YAML syntax.
- [ ] Update docs with real command examples for inspect, repair, SCAD render, and STL verification.
- [ ] Run local Markdown checks and the complete example/tool test suite.

### Task 5: Local acceptance, commit, and GitHub push

**Files:**
- No new source files; verify the complete diff and generated reports only in temporary directories.

- [ ] Run all Python tests, all SCAD example renders, metadata validation, and a real Windows end-to-end command.
- [ ] Confirm `git status` contains only intended source/docs changes and no generated mesh artifacts.
- [ ] Commit with `feat: harden cross-platform OpenSCAD skill`.
- [ ] Push `main` to `origin` only after verification succeeds and report the commit and remote result.
