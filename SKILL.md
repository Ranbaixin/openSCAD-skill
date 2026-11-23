---
name: openscad-modeling
license: MIT
description: >-
  Create parametric OpenSCAD parts, change existing SCAD dimensions while preserving mechanical
  interfaces, and inspect or conservatively repair STL meshes. Use for enclosures, mounts,
  multi-part exports, dimensional regression, PCB clearance, and mesh diagnostics.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# OpenSCAD 建模与网格处理

| 用户输入 | 工作流 |
|---|---|
| 新建参数化模型 | 参数化建模时记录单位、坐标、功能尺寸、孔轴与装配姿态，集中定义参数，为各打印件提供独立导出入口。 |
| 已有 SCAD 改尺寸 | 先读原模型，冻结外形、孔位、配合面和保留空间，另存改版。分别导出基线和变体，对照独立基准测量最终几何。 |
| 已有 STL 诊断或修复 | 先运行 `scripts/inspect_stl.py INPUT --json`。仅在用户要求修复时运行 `scripts/repair_stl.py INPUT NEW.stl --json`。默认保留全部组件，筛选须经明确授权。 |

## 确认与输入保护

- 最多一轮集中确认。能从输入文件或上下文确定的信息不要提问。用户已提供或批准实施方案时直接执行。
- 低风险遗漏采用可逆默认值并在交付时注明。只有歧义会改变尺寸、孔位、装配方向或主体轮廓时才集中提问，回答后直接执行，不再进行第二次确认。
- ASCII 草图仅用于检查现有坐标后仍有歧义的空间关系。
- 不覆盖用户原始文件。保留每轮产物和原件；多个合法组件可属于同一份交付。STL 的三角面或 `import()` 引用无法恢复原有的参数历史。

## 几何验证与交付

- 使用 `scripts/validate_scad.py` 的工具发现与后端探测。缺少 OpenSCAD 时可交付 SCAD，显式标注**未渲染**；缺少 Python 几何依赖时标注受影响的项目**未验证**。
- 简单件检查导出诊断、可解析性、尺寸、组件数、闭合和有符号体积。机械接口还要在实际产物上测孔心、孔径、贯穿与孔周材料，并按固定装配姿态检查保留空间。
- 指定允许的贴合面、净距和实体重叠阈值。渲染错误、无法解析或缺失的布尔产物应报告无法判定。必需项失败或无法判定时返回非零。
- 交付可编辑源、独立打印件、参考体标识、参数和可复跑命令，报告实测、期望、公差、工具版本及未验证项。分别说明几何验证、插入路径、打印精度、承载与实物装配的证据范围。

## 按需参考

- [壁厚修改实测案例](examples/intermediate/assembly-fit/README.md)与[复杂装配流程](references/complex-assembly-workflow.md)
- [STL 诊断、修复范围和筛选](references/stl-workflow.md)
- [DXF 导入](references/dxf-import-guide.md)、[项目组织](references/project-conventions.md)与[常见兼容问题](references/gotchas-and-workarounds.md)
- 标准件可查[螺丝规格](references/screw-sizes.md)、[BOSL2](references/bosl2-patterns.md)和[NopSCADlib](references/nopscadlib-vitamins.md)。
