// parametric-enclosure.scad
// 中级示例: 参数化电子外壳
// 演示 for 循环阵列、PCB 支柱、通风槽、USB 开口

/* [Box Dimensions] */
outer_w = 100;         // 外壳外宽 (mm)
outer_d = 70;          // 外壳外深 (mm)
outer_h = 30;          // 外壳外高 (mm)
wall_t = 2.5;          // 壁厚 (mm)

/* [PCB Mounting] */
pcb_w = 85;            // PCB 宽度 (mm)
pcb_d = 55;            // PCB 深度 (mm)
pcb_hole_d = 3.2;      // PCB 安装孔径 (mm) — M3
standoff_h = 6;        // 支柱高度 (mm)
standoff_od = 6;       // 支柱外径 (mm)
pcb_z_offset = 5;      // PCB 离底面距离 (mm)

/* [Ventilation] */
vent_l = 15;           // 通风槽长度 (mm)
vent_w = 2;            // 通风槽宽度 (mm)
vent_spacing = 6;      // 通风槽间距 (mm)
vent_count = 8;        // 每侧通风槽数

/* [USB Cutout] */
usb_w = 9;             // USB 口宽度 (mm)
usb_h = 5;             // USB 口高度 (mm)
usb_z = 10;            // USB 口距底面高度 (mm)

/* [Quality] */
$fn = 64;


module enclosure_body() {
    // 外壳主体 (无盖)
    difference() {
        cube([outer_w, outer_d, outer_h]);

        // 掏空内部
        translate([wall_t, wall_t, wall_t])
            cube([outer_w - 2 * wall_t,
                  outer_d - 2 * wall_t,
                  outer_h - wall_t + 1]);
    }
}

module pcb_standoffs() {
    // 四个角的 PCB 支柱
    pcb_margin = (outer_w - pcb_w) / 2;
    pcb_margin_d = (outer_d - pcb_d) / 2;

    standoff_h_total = pcb_z_offset + standoff_h;

    for (x = [pcb_margin, outer_w - pcb_margin])
        for (y = [pcb_margin_d, outer_d - pcb_margin_d])
            translate([x, y, wall_t])
                difference() {
                    // 支柱圆柱
                    cylinder(h = standoff_h_total, d = standoff_od);
                    // 螺丝孔
                    translate([0, 0, -0.1])
                        cylinder(h = standoff_h_total + 0.2,
                                 d = pcb_hole_d);
                }
}

module ventilation_slots() {
    // 两侧通风槽
    slot_start = (outer_d - (vent_count * vent_w +
                  (vent_count - 1) * vent_spacing)) / 2;

    // 左侧
    for (i = [0 : vent_count - 1])
        translate([-0.5,
                   slot_start + i * (vent_w + vent_spacing),
                   outer_h * 0.5])
            cube([wall_t + 1, vent_w, vent_l + 1]);  // +1 避免重合面

    // 右侧
    for (i = [0 : vent_count - 1])
        translate([outer_w - wall_t - 0.5,
                   slot_start + i * (vent_w + vent_spacing),
                   outer_h * 0.5])
            cube([wall_t + 1, vent_w, vent_l + 1]);  // +1 避免重合面
}

module usb_cutout() {
    // 前侧 USB 开口
    translate([-0.5, outer_d - wall_t - 0.5, usb_z])
        cube([wall_t + 1, wall_t + 1, usb_h]);
}


module main() {
    difference() {
        union() {
            enclosure_body();
            pcb_standoffs();
        }
        ventilation_slots();
        usb_cutout();
    }

    // 半透明 PCB 示意
    %translate([(outer_w - pcb_w) / 2,
                (outer_d - pcb_d) / 2,
                wall_t + pcb_z_offset + standoff_h])
        cube([pcb_w, pcb_d, 1.6]);
}

main();

// 导出:
// openscad parametric-enclosure.scad \
//   -D "pcb_w=100" -D "pcb_d=65" \
//   -D "outer_w=110" -D "outer_d=75" \
//   -o enclosure.stl
