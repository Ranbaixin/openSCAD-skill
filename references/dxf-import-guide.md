# DXF 导入完整工作流

从 PCB DXF 或机械图纸自动生成安装板/外壳。

## 流程概览

```
PCB 设计 (KiCad/Eagle)
    ↓ 导出 DXF
DXF 文件
    ↓ Python 解析 → 提取轮廓和孔位
参数数据
    ↓ 生成 → SCAD 安装板
STL 模型
```

## DXF 文件结构

DXF 是 AutoCAD 的文本格式。关键实体:

| 实体 | 用途 | 关键参数 |
|------|------|---------|
| LWPOLYLINE | 2D 多段线（PCB 外形） | 顶点坐标 (10, 20, 30) |
| CIRCLE | 圆（安装孔） | 中心 (10, 20), 半径 (40) |
| HATCH | 填充/槽孔 | 边界路径 |
| ARC | 弧线 | 中心、半径、角度 |

## Python 解析 LWPOLYLINE 和 CIRCLE

```python
import re
import math
from typing import List, Tuple

def parse_dxf_vertices(filepath: str) -> List[List[Tuple[float, float]]]:
    """Extract all LWPOLYLINE vertex sequences from DXF."""
    with open(filepath, 'r') as f:
        content = f.read()

    polylines = []
    for entity in content.split('LWPOLYLINE')[1:]:
        # Extract 2D vertices: group code 10 = X, 20 = Y
        xs = [float(m) for m in re.findall(r'^\s*10\n([\d.e+-]+)', entity, re.M)]
        ys = [float(m) for m in re.findall(r'^\s*20\n([\d.e+-]+)', entity, re.M)]
        if xs and ys:
            polylines.append(list(zip(xs, ys)))
    return polylines


def parse_dxf_circles(filepath: str) -> List[Tuple[float, float, float]]:
    """Extract CIRCLE entities: returns [(cx, cy, r), ...]."""
    with open(filepath, 'r') as f:
        content = f.read()

    circles = []
    for entity in content.split('CIRCLE')[1:]:
        cx_match = re.search(r'^\s*10\n([\d.e+-]+)', entity, re.M)
        cy_match = re.search(r'^\s*20\n([\d.e+-]+)', entity, re.M)
        r_match  = re.search(r'^\s*40\n([\d.e+-]+)', entity, re.M)
        if cx_match and cy_match and r_match:
            circles.append(
                (float(cx_match.group(1)),
                 float(cy_match.group(1)),
                 float(r_match.group(1)))
            )
    return circles
```

## 生成 SCAD 安装板

```python
def generate_mounting_plate(
    outline_verts: List[Tuple[float, float]],
    holes: List[Tuple[float, float, float]],
    plate_thickness: float = 3,
    margin: float = 5,
    output_path: str = "mounting_plate.scad"
):
    """Generate a SCAD file for a PCB mounting plate."""

    # Compute bounding box
    xs = [v[0] for v in outline_verts]
    ys = [v[1] for v in outline_verts]
    plate_w = max(xs) - min(xs) + 2 * margin
    plate_d = max(ys) - min(ys) + 2 * margin
    center_x = (max(xs) + min(xs)) / 2
    center_y = (max(ys) + min(ys)) / 2

    with open(output_path, 'w') as f:
        f.write(f"""// Auto-generated mounting plate from DXF
// PCB bounding box: {max(xs)-min(xs):.1f} x {max(ys)-min(ys):.1f} mm

plate_w = {plate_w:.1f};
plate_d = {plate_d:.1f};
plate_h = {plate_thickness};
corner_r = 3;
margin = {margin};
$fn = 64;

module rounded_plate(w, d, h, r) {{
    hull()
    for (x = [r, w-r])
        for (y = [r, d-r])
            translate([x, y, 0])
                cylinder(h = h, r = r);
}}

module mounting_plate() {{
    difference() {{
        // Base plate
        rounded_plate(plate_w, plate_d, plate_h, corner_r);

        // Mounting holes
""")
        for i, (cx, cy, r) in enumerate(holes):
            dx = cx - center_x
            dy = cy - center_y
            # Map DXF Y-up to SCAD Y
            scad_x = plate_w/2 + dx
            scad_y = plate_d/2 - dy
            f.write(f"""        // Hole {i+1}
        translate([{scad_x:.1f}, {scad_y:.1f}, -1])
            cylinder(h = plate_h + 2, d = {2*r:.1f});
""")

        f.write("""    }
}

mounting_plate();
""")
    print(f"Generated: {output_path}")
```

## 在 SCAD 中使用 DXF 直接导入

OpenSCAD 也可以直接导入 DXF 2D 图层:

```openscad
// 导入 DXF 的特定图层
linear_extrude(height = 3) {
    import("pcb_outline.dxf", layer = "Edge.Cuts");
    import("pcb_outline.dxf", layer = "Edge.Panel");
}

// 减去安装孔
difference() {
    linear_extrude(height = 3)
        import("pcb_outline.dxf", layer = "Edge.Cuts");

    // M3 安装孔 (需要知道具体位置)
    linear_extrude(height = 10, center = true)
        import("pcb_outline.dxf", layer = "Mounting.Holes");
}
```

> ⚠️ OpenSCAD 的 DXF 导入功能有限制 — 确保 DXF 保存为 **DXF R12** 格式以获得最佳兼容性。

## 常用技巧

1. **KiCad 导出 DXF**: File → Plot → DXF → 选择图层 (Edge.Cuts, 自定义 Mounting 图层)
2. **单位转换**: DXF 通常用 mm，但某些工具用 inch — 检查 `$INSUNITS` 头变量
3. **圆角 PCB**: DXF 导入后手动添加 corner radius — 导入的轮廓可能只有直角
4. **验证尺寸**: 导入后用 Python 验证包围盒是否与预期 PCB 尺寸一致
