// simple-bracket.scad
// 入门级示例: L 型支架 + 孔位
// 演示 rotate() + translate() + difference() 组合

/* [Dimensions] */
leg1_l = 50;           // 水平腿长 (mm)
leg2_l = 40;           // 垂直腿长 (mm)
width   = 30;          // 支架宽度 (mm)
thickness = 4;         // 壁厚 (mm)
corner_r = 4;          // 外角半径 (mm)

/* [Holes] */
hole_d = 3.2;          // 孔直径 (mm) — M3 标准
hole_count = 2;        // 每条腿上的孔数
hole_margin = 6;       // 孔到边缘/弯折线的距离 (mm)

/* [Quality] */
$fn = 64;


module L_bracket() {
    // L 型主体: 用两个 cube + 圆角过渡
    union() {
        // 水平腿 (沿 X 轴)
        cube([leg1_l, width, thickness]);

        // 垂直腿 (沿 Y 面，向上延伸)
        translate([0, 0, thickness])
            rotate([0, 90, 0])
                cube([leg2_l, width, thickness]);

        // 弯折处加强: 三棱柱简化三角支撑
        translate([0, 0, thickness])
            rotate([0, 90, 0])
                rotate([0, 0, 90])
                    linear_extrude(width)
                        polygon(points = [
                            [0, 0],
                            [thickness * 2, 0],
                            [0, thickness * 2]
                        ]);
    }
}

module mounting_holes() {
    // 水平腿上的孔
    spacing_1 = (leg1_l - 2 * hole_margin) / (hole_count - 1);
    for (i = [0 : hole_count - 1])
        translate([hole_margin + i * spacing_1, width / 2, -1])
            cylinder(h = thickness + 2, d = hole_d);

    // 垂直腿上的孔
    spacing_2 = (leg2_l - 2 * hole_margin) / (hole_count - 1);
    for (i = [0 : hole_count - 1])
        translate([thickness, width / 2,
                   thickness + hole_margin + i * spacing_2])
            rotate([0, 90, 0])
                cylinder(h = thickness + 2, d = hole_d);
}

module main() {
    difference() {
        L_bracket();
        mounting_holes();
    }
}

main();

// 导出示例:
// openscad simple-bracket.scad -D "leg1_l=60" -D "leg2_l=50" -o bracket.stl
