# STL 工作流

## 1. 检查

使用 `scripts/inspect_stl.py input.stl --json`。重点查看：

- `extents_mm`：包围盒尺寸和单位是否合理。
- `component_count`：大于 1 时先确认是否为装配体或孤立碎片。
- `watertight`：切片前通常应为 `true`。
- `broken_face_count`：非零表示存在边界破损风险。
- `component_face_counts`：用于判断最大主体与小组件的比例。

不要通过 `re.findall(r"vertex ...")` 读取 STL；那只覆盖 ASCII STL，二进制 STL 会得到错误或空结果。

## 2. 保守修复

```bash
python scripts/repair_stl.py input.stl repaired.stl
```

默认策略：

1. 读取 ASCII 或 binary STL。
2. 按面数选择最大连通组件，删除独立小组件。
3. 合并重复顶点，删除退化面和重复面。
4. 修正反转面、绕序和法线。
5. 尝试填补 trimesh 能识别的简单边界。
6. 写出新 STL，并在输出仍非 watertight 时以非零状态退出。

如果装配体需要保留多个组件，可使用较小的 `--min-component-ratio`，然后人工检查输出报告。不要在不知道组件用途时默认合并或删除所有组件。

## 3. 不能自动猜测的情况

以下情况不应被脚本伪装成“已修复”：

- 缺少大面积几何，而不是简单边界孔洞。
- 扫描网格中的自交、非流形边和严重重叠面。
- 需要保持精确配合面的复杂 CAD 逆向工程。

这时报告诊断结果，并选择 FreeCAD、Blender、MeshLab 或基于截面的参数化重建。

## 4. SCAD 对应关系

新模型优先直接生成参数化 SCAD，再由 OpenSCAD 导出 STL。对于无法合理参数化的现有 STL，可生成：

```openscad
// Keep this file next to repaired_model.stl or use an ASCII-only absolute path.
import("repaired_model.stl", convexity = 10);
```

这种 SCAD 是对应引用，不是可编辑的参数模型；交付时必须明确这一点。
