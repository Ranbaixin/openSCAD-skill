// snap-fit-lid.scad
// 入门级示例: 扣合式盒子和盖子
// 演示公差设计 + 凹凸配合结构

/* [Box Dimensions] */
box_w = 60;            // 盒内宽 (mm)
box_d = 40;            // 盒内深 (mm)
box_inner_h = 20;      // 盒内高 (mm)
wall_t = 2.5;          // 壁厚 (mm)
floor_t = 2;           // 底厚 (mm)

/* [Tolerance] */
fit_clearance = 0.2;   // 盖子与盒体的配合间隙 (mm)
snap_w = 4;            // 卡扣宽度 (mm)
snap_d = 1;            // 卡扣突出量 (mm)

/* [Quality] */
$fn = 64;


module box_body() {
    // 盒子主体: difference 掏空
    outer_w = box_w + 2 * wall_t;
    outer_d = box_d + 2 * wall_t;
    outer_h = box_inner_h + floor_t;

    difference() {
        // 外轮廓
        cube([outer_w, outer_d, outer_h]);

        // 掏空内部
        translate([wall_t, wall_t, floor_t])
            cube([box_w, box_d, box_inner_h + 1]);
    }
}

module box_lid() {
    // 盖子: 倒扣结构 + 侧壁
    outer_w = box_w + 2 * wall_t;
    outer_d = box_d + 2 * wall_t;
    lid_h = 4;

    union() {
        // 盖顶板
        cube([outer_w + 2 * snap_d + 1,
              outer_d + 2 * snap_d + 1,
              wall_t]);

        // 侧壁 (外尺寸匹配盒子外尺寸)
        difference() {
            translate([snap_d + 0.5, snap_d + 0.5, wall_t])
                cube([outer_w, outer_d, lid_h]);

            // 掏空侧壁内部 (留壁厚)
            translate([snap_d + 0.5 + wall_t,
                       snap_d + 0.5 + wall_t,
                       wall_t - 0.5])
                cube([outer_w - 2 * wall_t,
                      outer_d - 2 * wall_t,
                      lid_h + 1]);
        }
    }
}


module main() {
    // 并排显示盒子 (左) 和盖子 (右)
    box_body();
    translate([box_w + 2 * wall_t + snap_d + 15, 0, 0])
        box_lid();
}

main();

// 导出单个零件:
// 盒子:  openscad snap-fit-lid.scad -o box.stl
//         (在 main 中只保留 box_body 调用)
//
// 盖子:  openscad snap-fit-lid.scad -o lid.stl
//         (在 main 中只保留 box_lid 调用)
