---
name: openscad-modeling
version: "1.0.0"
license: MIT
description: >
  OpenSCAD 参数化 3D 建模与导出技能。用于创建、修改、导出 3D 打印用 STL/3MF 文件，
  包含圆角板、螺丝孔、托盘、外壳、支架等常用建模模式，支持 DXF 导入和 STL 合并。

  This skill should be used when the user asks to create parametric 3D models,
  modify .scad or .stl files, export STL/3MF for 3D printing, merge STL models,
  add holes/text/extensions to models, or analyze STL file dimensions.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
paths: "**/*.scad, **/*.stl, **/*.3mf, **/*.dxf"
disable-model-invocation: false
compatibility: "requires OpenSCAD CLI (stable or nightly); Python 3.8+ optional for STL tools"
---

# OpenSCAD 建模

## 环境发现

OpenSCAD CLI 需要可在命令行调用。按以下顺序自动发现:
1. 检查 `openscad` 是否在 PATH 中: `command -v openscad`
2. Windows: 检查 `C:\Program Files\OpenSCAD\openscad.exe` 和 `C:\Program Files (x86)\OpenSCAD\openscad.exe`
3. Mac: 检查 `/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD`
4. Linux: 已通过包管理器安装时通常已在 PATH 中
5. 若找不到，提示用户安装: https://openscad.org/downloads.html

模型文件默认存放在当前工作目录。用户可指定输出目录。

## 工作流程

### 1. 需求分析

用户描述需求后，先确认关键参数：
- 尺寸（长宽高、壁厚、孔径等）
- 孔位布局（位置、间距、数量）
- 特殊结构（凸起、凹槽、加强筋等）
- 输出格式（STL、3MF、PNG 预览）

对于不明确的地方，**主动画 ASCII 图确认**而非猜测。

### 2. 编写 SCAD 文件

原则：
- 参数化设计 — 所有尺寸定义为变量，方便修改
- 模块化 — 用 `module` 封装可复用组件
- 使用 `$fn` 控制圆角/圆柱面数
- 圆角板用 `hull()` + 四角 `cylinder()`
- 孔用 `difference()` 减去 `cylinder()`
- 壁/托盘用 `difference()` 掏空

核心模式：
```openscad
// 圆角板 (rounded plate via hull)
module rounded_plate(w, d, h, r) {
    hull()
    for (x = [r, w-r]) for (y = [r, d-r])
        translate([x, y, 0])
            cylinder(h = h, r = r);
}

// M3 贯穿孔 (M3 clearance hole)
module m3_clearance() {
    cylinder(h = 100, d = 3.2, center = true);  // 做大一点确保穿透
}

// M4 孔
module m4_clearance() {
    cylinder(h = 100, d = 4.3, center = true);
}
```

### 3. 导出 STL

```bash
openscad model.scad -o model.stl
```

### 4. 参数化导出（多版本）

通过 `-D` 传参批量生成:
```bash
openscad model.scad -D "plate_h=3" -o model-3mm.stl
openscad model.scad -D "plate_h=5" -o model-5mm.stl
```

### 5. PNG 预览

```bash
openscad model.scad -o preview.png --render --imgsize=1024,768 --viewall --autocenter --colorscheme=Metallic
```

## 参考文档

以下详细信息在对应 `references/` 文件中，按需加载:

- **[references/screw-sizes.md](references/screw-sizes.md)** — 完整螺丝/螺母/热熔螺母规格表。需要查螺丝尺寸时打开。
- **[references/bosl2-patterns.md](references/bosl2-patterns.md)** — BOSL2 库的 anchor/spin/attach 模式。使用 BOSL2 时打开。
- **[references/nopscadlib-vitamins.md](references/nopscadlib-vitamins.md)** — NopSCADlib 标准件库。需要螺母/螺丝/PCB 等真实零件模型时打开。
- **[references/project-conventions.md](references/project-conventions.md)** — 推荐项目结构和 use vs include 约定。组织多文件项目时打开。
- **[references/gotchas-and-workarounds.md](references/gotchas-and-workarounds.md)** — 常见陷阱和工作区方案。遇到渲染错误或异常行为时打开。
- **[references/toolchain-guide.md](references/toolchain-guide.md)** — VS Code 扩展、格式化器和 CI/CD 配置。设置开发环境时打开。
- **[references/dxf-import-guide.md](references/dxf-import-guide.md)** — DXF 导入完整工作流。需要从 PCB 设计生成安装板时打开。

## 常用参数速查

| 螺丝 | 通孔直径 | 螺母对边 |
|------|---------|---------|
| M2   | 2.2mm   | 4mm     |
| M3   | 3.2mm   | 5.5mm   |
| M4   | 4.3mm   | 7mm     |
| M5   | 5.3mm   | 8mm     |

> 完整规格表见 **[references/screw-sizes.md](references/screw-sizes.md)**

## 模型验证与 STL 工具

**验证 STL 尺寸**（Python 包围盒检查）:
```bash
python -c "import re; f=open('model.stl').read(); v=re.findall(r'vertex\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)',f); xs=[float(x[0])for x in v]; ys=[float(x[1])for x in v]; zs=[float(x[2])for x in v]; print(f'X:{min(xs):.1f}~{max(xs):.1f}({max(xs)-min(xs):.1f}mm) Y:{min(ys):.1f}~{max(ys):.1f}({max(ys)-min(ys):.1f}mm) Z:{min(zs):.1f}~{max(zs):.1f}({max(zs)-min(zs):.1f}mm)')"
```

**合并 STL**（CGAL 报错时备用）:
```python
import trimesh; combined = trimesh.util.concatenate([trimesh.load(f) for f in ['a.stl','b.stl']]); combined.export('merged.stl')
```

**DXF 导入**: 用 Python 正则解析 LWPOLYLINE/CIRCLE 实体。完整代码见 [references/dxf-import-guide.md](references/dxf-import-guide.md)

## 注意事项

- ⚠️ STL 路径避免中文字符（OpenSCAD import 不支持）
- 复杂 STL 的 projection 可能失败 → 改用 `intersection()` 切薄片
- 导出前确认孔贯穿: cylinder 高度 > 板厚
- 托盘/外壳壁厚 ≥ 2mm
- 更多陷阱 → **[references/gotchas-and-workarounds.md](references/gotchas-and-workarounds.md)**

## 示例

`examples/` 目录包含三级难度示例:
- **[examples/basic/](examples/basic/)** — 圆角板、L 型支架、扣合盖（零依赖）
- **[examples/intermediate/](examples/intermediate/)** — 参数化外壳、打印铰链、Gridfinity 底板
- **[examples/advanced/](examples/advanced/)** — BOSL2 螺纹紧固件、多零件装配、DXF 到安装板
