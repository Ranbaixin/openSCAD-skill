# BOSL2 模式参考

[BOSL2](https://github.com/BelfrySCAD/BOSL2) 是 OpenSCAD 的事实标准扩展库，提供 anchoring、spin、attachability 等高级定位系统。

## 安装

```bash
# 方式 1: Git submodule（推荐 — 项目级可复现）
cd your-project
git submodule add https://github.com/BelfrySCAD/BOSL2.git libs/BOSL2

# 方式 2: 全局安装到 OpenSCAD 库目录
# Windows: %USERPROFILE%\Documents\OpenSCAD\libraries\BOSL2\
# Mac:     ~/Documents/OpenSCAD/libraries/BOSL2/
# Linux:   ~/.local/share/OpenSCAD/libraries/BOSL2/

# 使用: 设置 OPENSCADPATH 或直接在代码中 include
```

## 核心概念

### Anchor（锚点）

BOSL2 形状有命名锚点，取代手动 `translate()`:

```openscad
include <BOSL2/std.scad>

// 原生方式: 需要手动计算 translate
cube([10, 10, 10]);
translate([5, 5, 10]) cylinder(h = 5, d = 3);

// BOSL2 方式: 用 anchor 定位
cuboid([10, 10, 10]);
cuboid([10, 10, 10]) {
    attach(TOP) cyl(h = 5, d = 3);
}
```

锚点方向:
| 锚点名 | 方向 | 等价位置 |
|--------|------|---------|
| LEFT   | -X   | 左侧中心 |
| RIGHT  | +X   | 右侧中心 |
| FRONT  | -Y   | 前方中心 |
| BACK   | +Y   | 后方中心 |
| BOTTOM | -Z   | 底部中心 |
| TOP    | +Z   | 顶部中心 |
| CENTER | —    | 几何中心 |

组合锚点: `TOP+LEFT`, `BOTTOM+FRONT+RIGHT` 等。

### Spin（旋转）

绕锚点旋转对象:

```openscad
cuboid([20, 10, 5]) {
    attach(TOP, spin = 45)  // 绕 Z 轴旋转 45°
        cyl(h = 10, d = 3);
    attach(TOP, spin = 90, orient = FRONT)  // 面向前方
        cyl(h = 15, d = 3);
}
```

### Orient（朝向）

控制子对象的朝向:

```openscad
// 让螺丝从顶部指向右前角
cuboid([30, 20, 5]) {
  attach(TOP, orient = UP + RIGHT + FRONT)
    cyl(h = 20, d = 4);
}
```

## 常用形状对照

| 原生 OpenSCAD | BOSL2 替代 | 优势 |
|--------------|-----------|------|
| `cube([w,d,h])` | `cuboid([w,d,h])` | 可 anchor/spin/attach，支持圆角 `rounding=` |
| `cylinder(h, d)` | `cyl(h, d)` | 可 anchor/spin/attach，支持 chamfer |
| `sphere(d)` | `spheroid(d)` | 可 anchor |
| `linear_extrude()` | `linear_sweep()` | 更好的 2D→3D 控制 |
| — | `prismoid()` | 梯形棱柱 |
| — | `tube()` | 管道/套管 |

## BOSL2 螺丝/螺纹

```openscad
include <BOSL2/std.scad>
include <BOSL2/screws.scad>

// 外螺纹
screw("M3", length = 10, head = "socket cap", thread = true);

// 内螺纹孔
nut("M3", thickness = 3);

// 使用 attach 组装
screw("M3x10", head = "socket cap") {
    attach(TOP) nut("M3");
}
```

## 何时用 BOSL2 vs 原生

| 场景 | 推荐 |
|------|------|
| 简单矩形/圆柱 + translate | 原生 — 足够简洁 |
| 多锚点精确装配 | BOSL2 — attach 比 translate 直观 |
| 需要圆角/倒角 | BOSL2 — cuboid(rounding=) > hull 模式 |
| 标准螺纹 | BOSL2 — screw() 比手写准确 |
| $fn/$fa 控制 | 原生 — 够用 |
| 单文件简单零件 | 原生 — 无需引入依赖 |

## 性能注意事项

- BOSL2 的 `$fn` 默认值较高（72 vs 原生的 12），在预览时可能较慢
- 开发时用 `$fn = 24;` 预览，导出时恢复到默认值
- `screw()` 的 `thread=true` 渲染很慢 — 预览时关掉，只对最终导出开启
