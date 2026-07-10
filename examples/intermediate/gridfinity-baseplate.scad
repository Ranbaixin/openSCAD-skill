// gridfinity-baseplate.scad
// 中级示例: Gridfinity 兼容底板 (2x3 网格)
// 演示规范标准实现 + 磁铁孔 + 螺丝安装孔
// Gridfinity 规范: 42mm 网格, 底板高 4.6mm, 磁铁孔直径 6.5mm

/* [Grid Dimensions] */
grid_x = 2;            // X 方向网格数
grid_y = 3;            // Y 方向网格数

/* [Gridfinity Standard] */
grid_size = 42;        // 单格尺寸 (mm)
base_h = 4.6;          // 底板高度 (mm)
lip_h = 0.8;           // 底板唇高 (mm)
corner_r = 4;          // 外角半径 (mm)

/* [Magnet Holes] */
magnet_hole_d = 6.5;   // 磁铁孔径 (mm) — 适配 6x2mm 磁铁
magnet_hole_h = 2.4;   // 磁铁孔深度 (mm) — 略大于磁铁厚度
magnet_offset = 11;    // 磁铁到角距离 (mm)

/* [Screw Holes] */
screw_hole_d = 3.2;    // 螺丝安装孔径 (mm) — M3 沉头
screw_counterbore_d = 6;// 沉头直径 (mm)
screw_counterbore_h = 2;// 沉头深度 (mm)

/* [Quality] */
$fn = 64;


module baseplate() {
    total_w = grid_x * grid_size;
    total_d = grid_y * grid_size;

    difference() {
        // 底板主体
        hull()
        for (x = [corner_r, total_w - corner_r])
            for (y = [corner_r, total_d - corner_r])
                translate([x, y, 0])
                    cylinder(h = base_h, r = corner_r);
    }
}

module grid_lip() {
    // 网格凸棱 — 帮助上层的 Gridfinity 模块定位
    total_w = grid_x * grid_size;
    total_d = grid_y * grid_size;

    for (ix = [0 : grid_x - 1])
        for (iy = [0 : grid_y - 1]) {
            // X 方向棱
            translate([ix * grid_size + 2, iy * grid_size + 2, base_h])
                cube([grid_size - 4, 2, lip_h]);
            translate([ix * grid_size + 2, (iy + 1) * grid_size - 4, base_h])
                cube([grid_size - 4, 2, lip_h]);
            // Y 方向棱
            translate([ix * grid_size + 2, iy * grid_size + 2, base_h])
                cube([2, grid_size - 4, lip_h]);
            translate([(ix + 1) * grid_size - 4, iy * grid_size + 2, base_h])
                cube([2, grid_size - 4, lip_h]);
        }
}

module magnet_holes() {
    // 每个网格单元的磁铁孔
    total_w = grid_x * grid_size;
    total_d = grid_y * grid_size;

    for (ix = [0 : grid_x - 1])
        for (iy = [0 : grid_y - 1])
            for (x = [magnet_offset,
                      grid_size - magnet_offset])
                for (y = [magnet_offset,
                          grid_size - magnet_offset])
                    translate([ix * grid_size + x,
                               iy * grid_size + y,
                               base_h - magnet_hole_h + 0.1])
                        cylinder(h = magnet_hole_h + 1, d = magnet_hole_d);
}

module screw_holes() {
    // 底板四周的螺丝安装孔 (沉头)
    total_w = grid_x * grid_size;
    total_d = grid_y * grid_size;
    screw_margin = 10;

    for (x = [screw_margin, total_w - screw_margin])
        for (y = [screw_margin, total_d - screw_margin])
            translate([x, y, -0.1]) {
                // 沉头
                cylinder(h = screw_counterbore_h + 0.1,
                         d = screw_counterbore_d);
                // 通孔
                cylinder(h = base_h + 0.2,
                         d = screw_hole_d);
            }
}


module main() {
    difference() {
        union() {
            baseplate();
            grid_lip();
        }
        magnet_holes();
        screw_holes();
    }
}

main();

// 导出:
// openscad gridfinity-baseplate.scad \
//   -D "grid_x=3" -D "grid_y=4" \
//   -o gridfinity-3x4.stl
//
// Gridfinity 参考: https://gridfinity.xyz/
