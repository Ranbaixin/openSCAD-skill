// rounded-plate.scad
// 入门级示例: 参数化圆角板 + 穿孔阵列
// 演示 hull() 圆角板模式 + difference() 穿孔

/* [Plate Dimensions] */
plate_w = 80;          // 板宽 (mm)
plate_d = 50;          // 板深 (mm)
plate_h = 3;           // 板厚 (mm)
corner_r = 5;          // 圆角半径 (mm)

/* [Hole Pattern] */
hole_d = 3.2;          // 孔径 (mm) — M3 标准孔
hole_count_x = 4;      // X 方向孔数
hole_count_y = 2;      // Y 方向孔数
hole_margin = 8;       // 孔到边缘距离 (mm)

/* [Quality] */
$fn = 64;              // 圆柱面数


module rounded_plate(w, d, h, r) {
    // 用 hull 围绕四角的圆柱生成圆角板
    hull()
    for (x = [r, w - r])
        for (y = [r, d - r])
            translate([x, y, 0])
                cylinder(h = h, r = r);
}

module hole_grid(w, d, margin, count_x, count_y, hole_d) {
    // 生成均匀分布的穿孔
    spacing_x = (w - 2 * margin) / (count_x - 1);
    spacing_y = (d - 2 * margin) / (count_y - 1);

    for (ix = [0 : count_x - 1])
        for (iy = [0 : count_y - 1])
            translate([margin + ix * spacing_x,
                       margin + iy * spacing_y,
                       -1])
                cylinder(h = plate_h + 2, d = hole_d);
}

module main() {
    difference() {
        rounded_plate(plate_w, plate_d, plate_h, corner_r);
        hole_grid(plate_w, plate_d, hole_margin,
                  hole_count_x, hole_count_y, hole_d);
    }
}

main();

// 导出示例:
// openscad rounded-plate.scad -D "plate_h=5" -D "hole_d=4.3" -o plate-5mm-m4.stl
