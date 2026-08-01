---
name: openscad-modeling
license: MIT
description: >
  Cross-platform OpenSCAD and mesh-modeling workflow for creating parametric SCAD,
  analyzing and repairing ASCII/binary STL, inspecting 3MF, importing DXF,
  merging meshes, and exporting verified STL/3MF/PNG files. Use when Codex or
  Claude needs to create or modify 3D-printable mechanical parts, diagnose mesh
  defects, convert between CAD/mesh formats, or batch-export model variants.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# OpenSCAD 建模与网格处理

## 选择工作流

先判断输入和目标，不要把 STL 机械地“转换”为假参数化 SCAD：

| 情况 | 工作流 |
|---|---|
| 新零件、规则孔位、外壳、支架 | 先写参数化 SCAD，再由 OpenSCAD 导出 STL |
| 已有 SCAD 需要改尺寸 | 读取参数和模块，最小修改后重新渲染 |
| 已有 ASCII/binary STL 需要诊断 | 运行 `scripts/inspect_stl.py` |
| STL 有孤立组件、重复顶点、法线或简单孔洞问题 | 运行 `scripts/repair_stl.py`，检查修复报告 |
| STL 是扫描/自由曲面，不能合理参数化 | 保留修复后的 STL；SCAD 只用 `import()` 作为对应引用 |
| 需要从 DXF/PCB 生成安装板 | 先读 `references/dxf-import-guide.md` |
| 需要螺丝、螺母、PCB 标准件 | 按需读 BOSL2 或 NopSCADlib 参考 |
| 多轮迭代的 L 形支架、托盘或分件装配 | 先读 `references/complex-assembly-workflow.md` |

## 交互与确认

- 每个任务最多一轮集中确认；需求完整时直接执行。
- 能从输入文件或上下文确定的信息不要提问，先检查现有模型、坐标和历史要求。
- 用户已提供或批准实施方案，或明确要求继续、生成、执行时，视为已确认并直接执行。
- 低风险遗漏采用保守默认值并在交付时说明，不为此提问。
- 只有歧义会改变尺寸、孔位、装配方向或主体轮廓时，才一次性汇总所有关键问题。
- 收到该轮回答后直接执行，不再进行第二次确认；剩余次要不确定性采用可逆、保守方案。
- ASCII 草图仅用于检查模型和坐标后仍无法澄清的空间关系。
- 默认创建新文件且不覆盖原文件；完成建模后直接验证和报告，不询问是否验证或导出。

## 标准流程

1. **分析需求**：记录长宽高、壁厚、孔径、孔位、配合间隙、特殊结构和输出格式。
2. **检查环境**：运行 `scripts/find-openscad.ps1`（Windows）或 `scripts/find-openscad.sh`（macOS/Linux）；也可设置 `OPENSCAD` 指向可执行文件。
3. **选择实现**：优先使用参数化 SCAD；仅在原始网格无法合理重建时使用 STL 修复或 `import()` SCAD。
4. **参数化建模**：把尺寸放在文件顶部，用 `module` 封装重复结构；孔必须用足够高的 cylinder 确保贯穿。
5. **渲染导出**：使用 `openscad --backend manifold model.scad -o model.stl`；必要时用 `-D` 批量导出。
6. **几何验证**：用 `scripts/validate_scad.py` 验证 SCAD 渲染，再用 `scripts/inspect_stl.py --json` 检查输出尺寸、组件数和 watertight 状态。
7. **交付说明**：列出生成文件、关键尺寸、验证结果和已知限制；不覆盖用户原始文件。

对于需要与现有模型对接、包含孔位继承、分件螺钉连接或大悬臂加强的零件，先建立坐标/接口表，再开始建模；完整流程见 `references/complex-assembly-workflow.md`。

## 参数化 OpenSCAD 原则

- 所有可调整尺寸都定义为变量，避免把关键数字散落在几何表达式中。
- 重复件使用 `module` 和 `for`，圆柱/圆角质量用 `$fn` 控制（默认 48–64）。
- 圆角板优先使用 `hull()` + 四角 cylinder；孔用 `difference()` 减去贯穿 cylinder。
- 托盘和外壳先定义外体，再用 `difference()` 掏空；打印壁厚通常不低于 2 mm，除非用户指定。
- 多文件组合优先 `use <file.scad>`，避免 `include` 意外复制顶层几何；参见 `references/project-conventions.md`。

```openscad
module rounded_plate(w, d, h, r) {
    hull()
        for (x = [r, w-r]) for (y = [r, d-r])
            translate([x, y, 0]) cylinder(h = h, r = r);
}

module m3_clearance(h = 100) {
    cylinder(h = h, d = 3.2, center = true);
}
```

## STL/3MF 网格规则

- STL 可能是 ASCII 或 binary，不能用正则读取文本来判断尺寸；使用 `inspect_stl.py`。
- 修复前保存原始文件；`repair_stl.py` 默认只保留最大连通组件，适合删除孤立碎片，但不会猜测缺失的大块几何。
- 如果修复后仍非 watertight，必须报告失败并说明原因，不要把“删除碎片”误报成完整修复。
- 中文路径在部分 OpenSCAD `import()` 版本中不稳定；必要时把输入复制到 ASCII 临时目录，完成后再移动结果。
- 复杂扫描网格的参数化重建应明确标注为近似重建；不能承诺与原 STL 三角面完全一致。
- 需要详细修复策略时读取 `references/stl-workflow.md`。

## 命令速查

```powershell
& .\scripts\find-openscad.ps1
python scripts/inspect_stl.py input.stl --json
python scripts/repair_stl.py input.stl repaired.stl
python scripts/validate_scad.py examples/basic/rounded-plate.scad
openscad --backend manifold model.scad -o model.stl
openscad model.scad --render --viewall --autocenter --imgsize=1024,768 -o preview.png
```

```bash
# macOS/Linux
bash scripts/find-openscad.sh
python3 scripts/inspect_stl.py input.stl --json
python3 scripts/validate_scad.py examples/basic/rounded-plate.scad
```

## 参考资料

- `references/stl-workflow.md`：STL 检查、修复边界、组件筛选和验证决策。
- `references/screw-sizes.md`：M2–M8 通孔、螺母和热熔螺母规格。
- `references/bosl2-patterns.md`：BOSL2 anchor/spin/attach 模式。
- `references/nopscadlib-vitamins.md`：真实标准件、PCB 和装配模型。
- `references/project-conventions.md`：项目结构与 `use`/`include` 约定。
- `references/gotchas-and-workarounds.md`：CGAL、重合面、中文路径等问题。
- `references/dxf-import-guide.md`：DXF 到安装板工作流。
- `references/complex-assembly-workflow.md`：复杂装配、分件打印、孔位迁移与加强筋设计。

## 输出前检查清单

- [ ] 尺寸和单位明确，关键参数集中在顶部。
- [ ] SCAD 可独立渲染，或 `import()` 依赖路径已明确。
- [ ] 输出 STL 是单一实体，`watertight` 状态符合目标。
- [ ] 孔贯穿、壁厚和装配间隙已验证。
- [ ] 原始输入未被覆盖，输出文件路径清楚。
