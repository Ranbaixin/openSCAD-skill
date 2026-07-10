# OpenSCAD 项目结构约定

良好的项目结构能显著提升团队协作和长期维护性。以下约定综合了社区最佳实践。

## 推荐目录布局

```
my-project/
├── assembly.scad            # 主装配文件 (所有模块的组合视图)
├── config/
│   └── settings.scad        # 全局常量、材料参数、公差
├── modules/                 # 可复用的几何模块
│   ├── rounded-plate.scad
│   ├── screw-boss.scad
│   └── snap-joint.scad
├── parts/                   # 各独立零件
│   ├── base.scad            # 每个文件一个 module，一个 module 调用
│   ├── cover.scad
│   └── bracket.scad
├── assemblies/              # 子装配体
│   └── hinge-assy.scad
├── libs/                    # 外部库 (git submodule)
│   ├── BOSL2/
│   └── NopSCADlib/
├── stl/                     # 导出的 STL 文件 (.gitignore)
├── images/                  # 预览 PNG (.gitignore)
├── tests/
│   └── validate.scad        # 尺寸和干涉检查
├── Makefile                 # 构建自动化
├── .gitignore
└── README.md
```

## use vs include

这是 OpenSCAD 中最容易被误解的机制:

| 命令 | 行为 | 使用场景 |
|------|------|---------|
| `use <file.scad>` | 导入模块/函数，**不执行**顶层代码 | 库文件（BOSL2、工具模块） |
| `include <file.scad>` | 全部导入并**执行**顶层代码 | 共享变量/数据文件 |

```openscad
// ✅ 正确: 用 use 导入库
use <libs/BOSL2/std.scad>    // 只导入模块，不执行几何体
use <modules/rounded-plate.scad>

// ✅ 正确: 用 include 共享配置
include <config/settings.scad>  // 执行顶层变量定义

// ❌ 错误: 用 include 导入库 — 会执行库文件的所有顶层代码!
```

## Assembly 控制模式

一个文件控制所有版本，通过变量切换:

```openscad
// assembly.scad
show = "assembly";  // 默认显示装配视图

// 导出单个零件: openscad assembly.scad -D 'show="base"' -o base.stl

if (show == "base") {
    base();
} else if (show == "cover") {
    cover();
} else if (show == "bracket") {
    bracket();
} else if (show == "exploded") {
    // 爆炸视图 — 各零件偏移
    translate([0, 0, 0]) base();
    translate([0, 0, 15]) cover();
    translate([20, 0, 5]) bracket();
} else {
    // assembly — 正常装配位置
    base();
    translate([0, 0, 3]) cover();
    translate([10, 0, 0]) bracket();
}
```

## 变量命名约定

```openscad
// 尺寸: 带单位的描述性名称
plate_w = 80;        // 板宽 (width)
plate_d = 50;        // 板深 (depth)
plate_h = 3;         // 板高 (height)
wall_t = 2;          // 壁厚 (thickness)

// 孔位
hole_d = 3.2;        // 孔径 (diameter)
hole_spacing = 25;   // 孔间距
hole_margin = 5;     // 孔到边缘距离

// 圆角/倒角
corner_r = 4;        // 圆角半径 (radius)
chamfer = 1;         // 倒角尺寸

// 公差
clearance_xy = 0.2;  // XY 平面间隙
clearance_z = 0.1;   // Z 方向间隙

// 开关
$fn = 64;            // 圆柱面数 (全局)
show = "assembly";   // 显示模式
```

## 库管理

**推荐: Git submodule + OPENSCADPATH**

```bash
# 添加依赖
git submodule add https://github.com/BelfrySCAD/BOSL2.git libs/BOSL2

# 设置搜索路径 (在 Makefile 或 shell profile 中)
export OPENSCADPATH="./libs:./modules:$OPENSCADPATH"

# 在 .scad 文件中
use <BOSL2/std.scad>          // 通过 OPENSCADPATH 找到
use <rounded-plate.scad>      // 通过 OPENSCADPATH 找到
```

**不推荐**: 全局安装到 OpenSCAD 库目录 — 不同项目需要不同版本的库时会产生冲突。

## Makefile 模板

```makefile
OPENSCAD ?= openscad
OPENSCADPATH := ./libs:./modules:$(OPENSCADPATH)

PARTS := base cover bracket
STLS := $(addprefix stl/,$(addsuffix .stl,$(PARTS)))

all: $(STLS)

stl/%.stl: assembly.scad
	$(OPENSCAD) -o $@ -D 'show="$*"' $<

preview:
	$(OPENSCAD) --render -o images/assembly.png \
		--imgsize=1920,1080 --viewall --autocenter \
		assembly.scad

clean:
	rm -f stl/*.stl images/*.png

.PHONY: all preview clean
```
