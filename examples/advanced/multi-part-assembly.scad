// multi-part-assembly.scad
// 高级示例: 多零件装配模式
// 演示 use <> 多文件组合 + show 变量控制 + 颜色可视化
// 本文件是装配文件, 各零件定义在下方 module 中
// 更大的项目建议将每个 module 拆分到单独文件用 use <> 引入

/* [Show Mode] */
show = "assembly";     // "assembly" | "exploded" | "base" | "cover" | "switch"

/* [Dimensions] */
box_w = 80;
box_d = 50;
box_h = 30;
wall_t = 2.5;
lid_t = 2;

/* [Quality] */
$fn = 64;


module base_part() {
    // 底部盒体
    color("SteelBlue", 0.7)
    difference() {
        cube([box_w, box_d, box_h]);
        // 掏空
        translate([wall_t, wall_t, wall_t])
            cube([box_w - 2 * wall_t,
                  box_d - 2 * wall_t,
                  box_h - wall_t + 1]);

        // 前侧电源线开孔
        translate([box_w / 2 - 5, box_d - wall_t - 0.5, box_h / 2 + 3])
            cube([10, wall_t + 1, 8]);
    }
}

module cover_part() {
    // 上盖
    color("LightBlue", 0.5)
    translate([-2, -2, box_h])
    difference() {
        cube([box_w + 4, box_d + 4, lid_t]);

        // 与 base 配合的定位凹槽
        translate([1, 1, -0.1])
            cube([box_w - 2 * wall_t + 4,
                  box_d - 2 * wall_t + 4,
                  1.2]);
    }
}

module switch_bracket() {
    // 开关支架 (内部)
    color("Orange", 0.8)
    translate([wall_t, box_d / 2 - 8, wall_t])
    difference() {
        cube([15, 16, 20]);
        // 开关安装槽
        translate([-1, 4, 7])
            cube([15 + 2, 8, 6.5]);
    }
}

module assembly() {
    // 正常装配位置
    base_part();
    cover_part();
    switch_bracket();
}

module exploded() {
    // 爆炸视图 — 各零件拉开
    explode_z = 15;

    base_part();

    translate([0, 0, box_h + explode_z])
        cover_part();

    translate([30, 0, explode_z])
        switch_bracket();
}


if (show == "base") {
    base_part();
} else if (show == "cover") {
    cover_part();
} else if (show == "switch") {
    switch_bracket();
} else if (show == "exploded") {
    exploded();
} else {
    assembly();
}

// 导出:
// 全部装配: openscad multi-part-assembly.scad -o assembly.stl
// 只导出底座: openscad multi-part-assembly.scad -D 'show="base"' -o base.stl
// 只导出盖子: openscad multi-part-assembly.scad -D 'show="cover"' -o cover.stl
// 爆炸视图 (用于文档): openscad multi-part-assembly.scad -D 'show="exploded"' -o exploded.png --render
