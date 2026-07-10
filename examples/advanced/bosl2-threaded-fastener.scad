// bosl2-threaded-fastener.scad
// 高级示例: BOSL2 螺丝/螺母 + attach 装配
// 需要 BOSL2 库! 安装: git submodule add https://github.com/BelfrySCAD/BOSL2.git libs/BOSL2
// 预览时关闭螺纹以加速: 设置 thread = false

include <BOSL2/std.scad>
include <BOSL2/screws.scad>

/* [Plate] */
plate_w = 60;
plate_d = 40;
plate_h = 5;
corner_r = 4;
hole_spacing = 40;     // 对角孔间距 (mm)

/* [Fastener] */
screw_size = "M3";     // 螺丝规格
screw_len = 12;        // 螺丝长度 (mm)
head_type = "socket cap"; // 螺丝头型: "socket cap", "countersunk", "pan"
show_threads = false;  // true = 渲染螺纹 (慢), false = 简化预览

/* [Quality] */
$fn = 64;


module mounting_plate() {
    // 圆角安装板 + 4 个对角孔
    difference() {
        cuboid([plate_w, plate_d, plate_h], rounding = corner_r,
                edges = "Z", except = []);
        // M3 通孔在四角
        grid_copies(spacing = hole_spacing, n = 2) {
            tag("remove")
                cyl(h = plate_h + 2, d = 3.4, anchor = CENTER);
        }
    }
}

module assembled_bracket() {
    // 装配展示: 板 + 4 颗螺丝从下往上, 螺母在上
    // 使用 BOSL2 的 attach() 自动定位

    mounting_plate();

    // 四颗螺丝从底部穿上, 螺母在顶部
    grid_copies(spacing = hole_spacing, n = 2) {
        // 螺丝: 头部在下 (BOTTOM), 螺杆穿过板
        // BOSL2 的 screw() 头部默认在 anchor=TOP, 我们反转
        down(plate_h / 2 + screw_len - 8)
            screw(str(screw_size, "x", screw_len),
                  head = head_type,
                  thread = show_threads,
                  anchor = BOTTOM,
                  orient = DOWN);

        // 螺母在顶部
        up(plate_h / 2 + 1)
            nut(screw_size,
                thickness = 2.4,
                anchor = BOTTOM,
                orient = DOWN);
    }
}

module main() {
    assembled_bracket();
}

main();

// 导出单个零件示例:
// 板:        openscad -D 'show="plate"' bosl2-threaded-fastener.scad -o plate.stl
// 爆炸视图:  在 assembled_bracket 中加入 translate 偏移各零件
// 渲染螺纹:  openscad -D "show_threads=true" bosl2-threaded-fastener.scad -o threaded.stl
