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
2. 在副本上清除退化面和重复面，再按面邻接识别组件，默认全部保留。面数与零件用途无直接对应关系。
3. 合并重复顶点，删除退化面和重复面。
4. 修正反转面、绕序和法线。
5. 尝试填补 trimesh 能识别的简单边界。
6. 在目标同目录写二进制临时 STL，重新读取，核对整网格及组件闭合、绕序、正体积、组件数和退化面，通过后发布到新路径。已有目标、输入别名、无法可靠保留的内壳朝向或精度损失均报错。POSIX 发布使用同文件系统硬链接，文件系统不支持时会报告失败。

仅在已授权筛选时使用 `--keep-largest` 或 `--min-component-ratio R`，两者互斥。前者保留面数最多的一件，并列取首件。显式 `R=1` 沿用相同行为；`0 ≤ R < 1` 保留面数大于等于最大面数乘 R 的组件。添加 `--json` 可记录修复前后包围盒、组件数、闭合和被过滤组件的面数。需要再试参数时换一个输出文件名。

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
