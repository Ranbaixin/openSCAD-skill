# AGENTS.md

This is an OpenSCAD skill for Claude Code. When working in this repository:

## Language
- **Primary documentation**: Simplified Chinese (中文为主, `README_zh.md` is authoritative)
- **Code comments**: Chinese (变量名和 API 名称保持英文)
- **README.md**: English overview for public GitHub display

## Skill Conventions
- `SKILL.md` is the core skill file — keep it under 120 lines / ~2000 words
- Use **progressive disclosure**: metadata → SKILL.md body → `references/` files
- Extended reference material goes in `references/` — load on demand
- Reusable scripts go in `scripts/` — never inline large code blocks in SKILL.md

## Example SCAD Files
- Live in `examples/` at three levels: `basic/`, `intermediate/`, `advanced/`
- Every example must be **parameterized** — all dimensions as named variables at file top
- Every example must be **independently renderable** — use only built-in OpenSCAD for basic/intermediate
- Header comment explaining what the example teaches
- Advanced examples may require BOSL2 (documented in comments)
- Verification: `openscad -o /dev/null example.scad` must exit 0

## Git
- Commit messages in Chinese or English
- Never commit `.stl`, `.3mf`, or `.png` files (they are build artifacts)
- Follow [Conventional Commits](https://www.conventionalcommits.org/) when possible
