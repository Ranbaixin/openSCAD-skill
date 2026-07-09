---
name: openscad-modeling
description: |
  OpenSCAD 参数化 3D 建模与导出。用于创建、修改、导出 3D 打印用 STL/3MF 文件。
  当用户请求以下操作时使用此技能:
  - 创建新的 3D 模型（板子、托盘、支架、外壳等）
  - 修改现有 OpenSCAD (.scad) 或 STL 文件
  - 导出 STL/3MF 用于 3D 打印
  - 合并多个 STL 模型
  - 在模型上添加孔、文字、延伸等特征
  - 读取分析 STL 文件尺寸和结构
---

# OpenSCAD 建模

## 环境

- **OpenSCAD**: `D:/openSCAD/openscad.exe`
- **模型目录**: `C:/Users/Ran-xin/3d-models/`
- **路径格式**: Unix 风格 `C:/Users/Ran-xin/...`

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

常用模式：
```openscad
// 圆角板
module rounded_plate(w, d, h, r) {
    hull()
    for (x = [r, w-r]) for (y = [r, d-r])
        translate([x, y, 0])
            cylinder(h = h, r = r);
}

// M3 贯穿孔
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
"D:/openSCAD/openscad.exe" "model.scad" -o "model.stl"
```

### 4. 验证模型

用 Python 解析 STL 验证尺寸：
```bash
python -c "
import re
with open('model.stl', 'r') as f:
    content = f.read()
verts = re.findall(r'vertex\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)', content)
xs = [float(v[0]) for v in verts]
ys = [float(v[1]) for v in verts]
zs = [float(v[2]) for v in verts]
print(f'X: {min(xs):.1f}~{max(xs):.1f} ({max(xs)-min(xs):.1f}mm)')
print(f'Y: {min(ys):.1f}~{max(ys):.1f} ({max(ys)-min(ys):.1f}mm)')
print(f'Z: {min(zs):.1f}~{max(zs):.1f} ({max(zs)-min(zs):.1f}mm)')
"
```

### 5. 参数化导出（多版本）

通过 `-D` 传参批量生成不同厚度的版本：
```bash
openscad model.scad -D "plate_h=3" -o model-3mm.stl
openscad model.scad -D "plate_h=5" -o model-5mm.stl
```

## 常用参数参考

| 螺丝 | 通孔直径 | 螺母对边 |
|------|---------|---------|
| M2   | 2.2mm   | 4mm     |
| M3   | 3.2mm   | 5.5mm   |
| M4   | 4.3mm   | 7mm     |
| M5   | 5.3mm   | 8mm     |

## DXF 导入

如需从 DXF 读取 PCB 等轮廓，用 Python 解析：
```python
import re
with open('file.dxf', 'r') as f:
    content = f.read()
# 查找 LWPOLYLINE 实体获取顶点坐标
# 查找 HATCH 边界获取圆孔位置
```

## PNG 预览

```bash
openscad model.scad -o preview.png --render --imgsize=1024,768 --viewall --autocenter --colorscheme=Metallic
```

## 合并 STL

当 OpenSCAD CGAL 报错时，用 Python trimesh 合并：
```python
import trimesh
a = trimesh.load('file1.stl')
b = trimesh.load('file2.stl')
combined = trimesh.util.concatenate([a, b])
combined.export('merged.stl')
```

## 注意事项

- STL 路径避免中文字符（OpenSCAD import 不支持中文路径）
- 复杂 STL 的投影（projection）可能失败，改用 intersection 切薄片
- 导出前确认孔是否贯穿：cylinder 高度 > 板厚
- 托盘/外壳类模型注意壁厚 ≥ 2mm 保证强度
