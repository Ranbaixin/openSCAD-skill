# NopSCADlib 标准件 (Vitamins)

[NopSCADlib](https://github.com/nophead/NopSCADlib) 是一套专注于**真实零件**（vitamins — 非打印的市购件）的 OpenSCAD 库。提供螺丝、螺母、垫圈、PCB、电机、铝型材等现成零件的精确模型。

## 为什么用 NopSCADlib

- 螺丝/螺母模型包含真实螺纹和尺寸
- PCB 模型可直接从 KiCad/Eagle 数据生成
- 挤出铝型材（2020/2040/3030 等）
- 同步带轮、步进电机、风扇等传动件
- Python 工具链：BOM 生成、STL 批量导出、装配图

## 安装

```bash
# Git submodule（推荐）
cd your-project
git submodule add https://github.com/nophead/NopSCADlib.git libs/NopSCADlib

# 设置 OPENSCADPATH
export OPENSCADPATH="./libs/NopSCADlib:./libs/BOSL2:$OPENSCADPATH"
```

> ⚠️ NopSCADlib 依赖自身 Python 工具链。完整的 BOM/装配图功能仅在有 Python 环境时可用。

## 常用零件速查

### 螺丝

```openscad
include <NopSCADlib/lib.scad>

// M3 沉头螺丝 x 12mm 长
screw(M3_cs_cap_screw, 12);

// M3 内六角螺丝
screw(M3_cap_screw, 16);

// M3 半圆头螺丝
screw(M3_pan_screw, 8);
```

### 螺母

```openscad
include <NopSCADlib/lib.scad>

// M3 普通螺母
nut(M3_hex_nut);

// M3 尼龙锁紧螺母
nut(M3_nyloc_nut);

// M3 方形螺母（用于挤出铝型材 T 型槽）
nut(M3_square_nut);
```

### 垫圈

```openscad
washer(M3_washer);          // 普通平垫圈
washer(M3_penny_washer);    // 大平垫圈 (M3 x 12mm)
```

### PCB

```openscad
// 从 KiCad 导出后
pcb(MyPCB);
```

### 铝型材

```openscad
extrusion(E2020, 300);   // 2020 型材 300mm
extrusion(E2040, 200);   // 2040 型材 200mm
extrusion(E3030, 150);   // 3030 型材 150mm
```

### 电机和电子元件

```openscad
NEMA17_48;       // NEMA17 步进电机 (48mm 长)
NEMA17_40;       // NEMA17 步进电机 (40mm 长)
arduino(Uno);    // Arduino Uno
Raspberry_Pi4;   // 树莓派 4
```

## NopSCADlib 项目结构约定

NopSCADlib 影响了 OpenSCAD 社区的最佳项目结构:

```
project/
├── assembly.scad            # 总装配
├── printed/                 # 打印件 (各部件单个文件)
│   ├── base.scad
│   └── cover.scad
├── assemblies/              # 子装配体
├── vitamins/ -> lib/NopSCADlib/  # 链接到库
├── stl/                     # 导出目录
├── dxf/                     # DXF 导出
├── bom.py                   # BOM 生成脚本
└── Makefile
```

## 注意事项

- NopSCADlib 体量较大（~200MB），首次 clone 需等待
- 部分维生素模型对渲染性能要求高（尤其是显示螺纹的螺丝）
- 建议在预览时用 `$explode = 1;` 显示爆炸视图
- Python 工具链需要 `pip install colorama` 等依赖
- 与 BOSL2 可共存使用 — NopSCADlib 管实体零件，BOSL2 管几何操作
