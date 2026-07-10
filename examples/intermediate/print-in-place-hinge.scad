// print-in-place-hinge.scad
// 中级示例: 一次打印铰链
// 演示打印就位间隙 + 互锁几何结构

/* [Hinge Dimensions] */
hinge_l = 40;          // 铰链总长 (mm)
barrel_od = 8;         // 铰链筒外径 (mm)
barrel_id = 3.2;       // 铰链筒内径 (mm) — M3 销轴
knuckle_count = 3;     // 关节数量 (奇数 — 两端在同一侧)
knuckle_gap = 0.3;     // 关节间隙 (mm) — 打印就位的关键公差!

/* [Mounting Flanges] */
flange_w = 25;         // 法兰宽度 (mm)
flange_t = 3;          // 法兰厚度 (mm)
flange_holes = 2;      // 每法兰孔数
flange_hole_d = 3.2;   // 安装孔径 (mm) — M3

/* [Quality] */
$fn = 64;


module knuckle(is_middle) {
    // 单个铰链关节
    // is_middle: true = 中间段 (属于 A 侧), false = 两端 (属于 B 侧)
    knuckle_l = (hinge_l / knuckle_count) - knuckle_gap;

    difference() {
        // 关节筒体
        rotate([90, 0, 0])
            cylinder(h = knuckle_l, d = barrel_od, center = true);

        // 销轴孔 (贯穿整个关节，center=true 与筒体对齐)
        rotate([90, 0, 0])
            cylinder(h = knuckle_l + 0.2, d = barrel_id, center = true);

        // 法兰连接面 (切除部分筒体让法兰平面贴合)
        if (is_middle) {
            translate([0, -knuckle_l / 2, -barrel_od / 2])
                cube([barrel_od + 1, knuckle_l + 0.2, barrel_od / 2]);
        }
    }
}

module flange_a() {
    // A 侧法兰 — 只连接两端关节
    difference() {
        union() {
            // 法兰平板
            cube([flange_w, hinge_l, flange_t]);

            // 两端关节 (center=true 时，关节中心在 y_pos)
            for (i = [0, knuckle_count - 1]) {
                y_pos = (i + 0.5) * (hinge_l / knuckle_count);
                translate([flange_w, y_pos, flange_t])
                    knuckle(false);
            }
        }

        // 法兰安装孔
        for (i = [0 : flange_holes - 1])
            translate([flange_w / (flange_holes + 1) * (i + 1),
                       hinge_l / 2,
                       -0.1])
                cylinder(h = flange_t + 0.2, d = flange_hole_d);
    }
}

module flange_b() {
    // B 侧法兰 — 连接所有关节
    difference() {
        union() {
            // 法兰平板
            cube([flange_w, hinge_l, flange_t]);

            // 中间关节 (center=true 时，关节中心在 y_pos)
            for (i = [1 : knuckle_count - 2]) {
                y_pos = (i + 0.5) * (hinge_l / knuckle_count);
                translate([0, y_pos, flange_t])
                    knuckle(true);
            }
        }

        // 法兰安装孔
        for (i = [0 : flange_holes - 1])
            translate([flange_w / (flange_holes + 1) * (i + 1),
                       hinge_l / 2,
                       -0.1])
                cylinder(h = flange_t + 0.2, d = flange_hole_d);
    }
}

module main() {
    // 并排显示 A 侧和 B 侧
    flange_a();
    translate([flange_w * 2 + 10, 0, 0])
        flange_b();

    // 销轴示意 (对齐关节中心)
    %color("Silver")
        translate([flange_w + 5, hinge_l / 2, flange_t + barrel_od / 2])
            rotate([90, 0, 0])
                cylinder(h = hinge_l + 10, d = barrel_id - 0.2, center = true);
}

main();

// 导出:
// openscad print-in-place-hinge.scad -o hinge.stl
// 打印后组装: 将 A 侧和 B 侧对齐, 插入 M3 螺丝作为销轴
// 关键: knuckle_gap = 0.3mm 提供打印就位所需的间隙
