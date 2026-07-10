# openSCAD-skill — 中文完整文档

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Claude Code 的 OpenSCAD 参数化 3D 建模技能** — AI 辅助 CAD，面向 3D 打印。

## 适用范围

### 适合谁用？

| 用户 | 为什么适合 |
|------|-----------|
| 🎓 **3D 打印新手** | 从参数化模板开始，跳过 OpenSCAD 陡峭的学习曲线。用自然语言描述想法，直接得到可用的 SCAD 代码和 STL 文件。 |
| 🔧 **创客 & 爱好者** | 快速迭代外壳、支架、安装板。无需手工计算孔位和间隙公差 — 技能自动处理。 |
| 🛠️ **工程师 & 硬件开发者** | 与 EDA 工具集成（KiCad/Eagle → DXF → 安装板）。通过 `-D` 参数批量导出多版本零件。内置 BOSL2 和 NopSCADlib 模式。 |
| 🤖 **AI/LLM 爱好者** | Claude Code 技能的结构化参考实现：渐进式加载、`references/` 架构、`paths` 作用域、CI/CD 验证。 |
| 📐 **OpenSCAD 学习者** | 9 个分级示例（入门→中级→高级），中文注释。参考文档涵盖螺丝规格、BOSL2 模式和实战陷阱。 |

### 典型使用场景

- 「我需要一块 100×60×3mm 的圆角板，上面 4×2 排列 M3 安装孔」→ 秒出 STL
- 「给这块 85×55mm 的 PCB 设计一个外壳，带 USB 开孔」→ 自动生成参数化外壳
- 「修改这个 STL 文件 — 在四角加 4mm 安装孔」→ OpenSCAD 直接编辑
- 「把 KiCad 的 PCB DXF 转成 3D 打印安装板」→ DXF 解析 + 自动生成支柱
- 「同一个支架导出 3mm、5mm、8mm 三个版本」→ 一条命令批量输出
- 「把两个 STL 合并成一个可打印的模型」→ trimesh 拼接

### 适用范围 & 局限

**✅ 擅长:**
- 参数化机械零件（板、支架、外壳、安装座、垫片）
- 网格类设计（Gridfinity、蜂巢收纳墙、洞洞板配件）
- 需要精确孔位和紧固件的功能性 3D 打印件
- PCB 安装方案和电子外壳
- 带配合公差的多零件装配体

**⚠️ 不擅长:**
- 有机/艺术造型（建议用 Blender 或 ZBrush）
- 复杂曲面和扫描（OpenSCAD 的 CSG 范式不适合）
- 需要约束草图的设计（建议用 Fusion 360 / FreeCAD）
- 渲染/可视化为主的工作（OpenSCAD 只有基础预览）

### 平台 & 工具支持

| 平台 | 支持程度 |
|------|---------|
| **Claude Code** (CLI) | ✅ 原生 — 技能在 SCAD/STL/3MF/DXF 文件上自动激活 |
| **Claude Code** (VS Code / JetBrains) | ✅ 通过 IDE 扩展 |
| **Claude.ai** (网页对话) | ⚠️ 有限 — 可执行文件操作但不能本地渲染 OpenSCAD |
| **其他 AI 工具** | 📖 仅参考 — SKILL.md 和示例可作为教育资源 |
| **Codewhale** | ✅ 兼容 — 安装到 `~/.codewhale/skills/` |
| **任何 OpenSCAD 用户** | ✅ 独立使用 — 示例和参考文档不依赖 Claude Code |

## 安装

### 方式 1: git clone（推荐）

```bash
git clone https://github.com/Ranbaixin/openSCAD-skill.git \
  ~/.claude/skills/openscad-modeling/
```

### 方式 2: 项目内 submodule

```bash
git submodule add https://github.com/Ranbaixin/openSCAD-skill.git \
  .claude/skills/openscad-modeling/
```

### 方式 3: 手动复制

将本仓库的 `SKILL.md` 复制到 `%USERPROFILE%\.claude\skills\openscad-modeling\SKILL.md`（Windows）或 `~/.claude/skills/openscad-modeling/SKILL.md`（Mac/Linux）。

### 验证安装

在 Claude Code 中发送任意建模相关请求，技能应自动触发。也可通过 `/openscad-modeling` 手动调用。

## 功能概览

通过此技能，Claude 能够:

- **创建**参数化 3D 模型 — 圆角板、支架、外壳、铰链、扣合盖
- **修改**现有的 `.scad` 和 `.stl` 文件
- **导出** STL/3MF 用于 3D 打印，支持多版本批量导出
- **分析** STL 文件尺寸和结构（Python 包围盒检查）
- **导入** DXF 文件（KiCad/Eagle PCB 设计）并生成安装板
- **合并**多个 STL 模型（Python trimesh）

## 示例

9 个渐进式示例，全部参数化、独立可渲染:

### 入门级 (`examples/basic/`)

| 示例 | 文件 | 知识点 |
|------|------|--------|
| 圆角板 + 穿孔阵列 | `rounded-plate.scad` | `hull()` 圆角 + `difference()` + 孔网格 |
| L 型支架 | `simple-bracket.scad` | `rotate()` + `translate()` 组合 + 多面孔 |
| 扣合式盒盖 | `snap-fit-lid.scad` | 公差设计 + 凹凸配合结构 |

### 中级 (`examples/intermediate/`)

| 示例 | 文件 | 知识点 |
|------|------|--------|
| 参数化外壳 | `parametric-enclosure.scad` | `for` 循环阵列、PCB 支柱、通风槽、USB 开口 |
| 打印就位铰链 | `print-in-place-hinge.scad` | 0.3mm 打印间隙 + 互锁几何 |
| Gridfinity 底板 | `gridfinity-baseplate.scad` | 42mm 标准实现 + 磁铁孔 + 沉头螺丝孔 |

### 高级 (`examples/advanced/`)

| 示例 | 文件 | 知识点 |
|------|------|--------|
| BOSL2 螺纹紧固件 | `bosl2-threaded-fastener.scad` | `screw()` + `nut()` + `attach()` 装配 |
| 多零件装配 | `multi-part-assembly.scad` | `show` 控制变量 + `use<>` 多文件模式 + 颜色可视化 |
| DXF → 安装板 | `dxf-to-mounting-plate.scad` | DXF 导入 + 安装孔自动生成 |

### 运行示例

```bash
# 渲染单个示例
openscad examples/basic/rounded-plate.scad -o plate.stl

# 参数化导出不同厚度
openscad examples/basic/rounded-plate.scad \
  -D "plate_h=5" -D "hole_d=4.3" \
  -o plate-5mm-m4.stl
```

## 参考文档

7 份渐进式参考文件，Claude 按需加载:

| 参考 | 文件 | 内容 |
|------|------|------|
| 螺丝规格 | `references/screw-sizes.md` | M1.6–M8 通孔/螺母/沉头/热熔螺母/自攻螺丝完整表 |
| BOSL2 模式 | `references/bosl2-patterns.md` | anchor/spin/orient/attach 决策树 + 何时用 BOSL2 |
| NopSCADlib | `references/nopscadlib-vitamins.md` | 标准件库使用 + submodule 安装 |
| 项目结构 | `references/project-conventions.md` | 推荐目录布局 + `use` vs `include` + Makefile |
| 常见陷阱 | `references/gotchas-and-workarounds.md` | CGAL 崩溃、重合面、中文路径等 10+ 问题 |
| 工具链 | `references/toolchain-guide.md` | VS Code 配置 + 格式化器 + CI/CD 搭建 |
| DXF 导入 | `references/dxf-import-guide.md` | DXF 解析 Python 代码 + 安装板自动生成 |

## 环境要求

- **OpenSCAD** (最新稳定版或 nightly) — [下载](https://openscad.org/downloads.html)
- **Python 3.8+** (可选) — STL 验证和合并、DXF 解析
  ```bash
  pip install trimesh numpy
  ```
- **BOSL2** (可选，advanced 示例需要) — 安装方式见 [BOSL2 参考](references/bosl2-patterns.md)

## 项目结构

```
openSCAD-skill/
├── SKILL.md                     # 核心技能文件
├── README.md                    # 英文概览
├── README_zh.md                 # 中文完整文档（本文件）
├── LICENSE                      # MIT
├── AGENTS.md                    # Claude 代理指令
├── CONTRIBUTING.md              # 贡献指南
├── CHANGELOG.md                 # 版本历史
├── references/                  # 渐进式参考文件
├── scripts/                     # 跨平台工具发现脚本
├── examples/                    # 9 个分级 SCAD 示例
└── .github/workflows/           # CI/CD
```

## 常见问题

### Q: 技能不自动触发？

检查:
1. `SKILL.md` 是否在正确的目录（`~/.claude/skills/openscad-modeling/SKILL.md`）
2. 文件是否名为 `SKILL.md`（区分大小写）
3. 重启 Claude Code 会话

### Q: OpenSCAD 找不到？

技能会自动按以下顺序查找:
1. PATH 环境变量中的 `openscad`
2. 标准安装路径（Windows/Mac/Linux）
3. 如果都找不到，Claude 会提示你安装

也可以手动运行:
- Windows: `scripts/find-openscad.ps1`
- Mac/Linux: `scripts/find-openscad.sh`

### Q: CGAL 渲染错误怎么办？

1. 优先尝试 Manifold 后端: `openscad --backend manifold model.scad -o model.stl`
2. 检查 `difference()` 是否有重合面 — 将减去的 cylinder 高度多延伸 1mm
3. 降低 `$fn` 值排查是否是精度问题
4. 详细排查见 [常见陷阱参考](references/gotchas-and-workarounds.md)

### Q: 中文路径报错？

OpenSCAD 的 `import()` 不支持非 ASCII 路径。将项目放在纯英文路径下（如 `C:\projects\`）。

## 贡献

欢迎 PR！参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 致谢

- [OpenSCAD](https://openscad.org/) — 程序化 3D CAD 建模工具
- [BOSL2](https://github.com/BelfrySCAD/BOSL2) — OpenSCAD 标准增强库
- [NopSCADlib](https://github.com/nophead/NopSCADlib) — 标准件库
- [Anthropic Skills](https://github.com/anthropics/skills) — Claude Code 技能官方参考
