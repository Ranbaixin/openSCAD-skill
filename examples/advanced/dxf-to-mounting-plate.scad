// dxf-to-mounting-plate.scad
// 高级示例: PCB DXF → 安装板全流程
// 演示 DXF 导入 + 安装孔自动生成
// 配合 Python 脚本自动提取 DXF 中的孔位

/* [Import Path] */
dxf_file = "pcb_outline.dxf";    // DXF 文件路径
dxf_outline_layer = "Edge.Cuts";  // PCB 外形图层
dxf_holes_layer = "Mounting";     // 安装孔图层 (需在 KiCad 中自定义)

/* [Plate Parameters] */
margin = 5;             // 板边超出 PCB 的距离 (mm)
plate_h = 3;            // 安装板厚度 (mm)
corner_r = 4;           // 安装板圆角 (mm)

/* [Standoff Bosses] */
boss_od = 6;            // 支柱外径 (mm)
boss_h = 5;             // 支柱高度 (mm)
boss_hole_d = 3.2;      // 支柱孔直径 (mm)

/* [Quality] */
$fn = 64;


// 因 DXF 导入尺寸未知, 我们先定义 PCB 预期尺寸
// 实际项目中由 Python 脚本解析 DXF 后替换这些值

module pcb_mockup() {
    // 模拟 PCB 外形 (50x35mm) 作为参考
    // 正式使用时用 import() 替代
    %translate([margin, margin, plate_h + boss_h])
        cube([50, 35, 1.6]);
}


module mounting_plate() {
    // 安装板需比 PCB 大一圈
    // 简化版: 基于模拟 PCB 尺寸
    pcb_w = 50;
    pcb_d = 35;
    plate_w = pcb_w + 2 * margin;
    plate_d = pcb_d + 2 * margin;

    difference() {
        // 圆角板主体
        hull()
        for (x = [corner_r, plate_w - corner_r])
            for (y = [corner_r, plate_d - corner_r])
                translate([x, y, 0])
                    cylinder(h = plate_h, r = corner_r);

        // 用 DXF 外形做沉台 (PCB 嵌入式定位)
        translate([margin, margin, plate_h - 0.5])
            linear_extrude(height = 1)
                square([pcb_w, pcb_d]);
    }
}

module standoffs() {
    // PCB 安装支柱 — 位置由 DXF 孔位决定
    // 示例: 四角各一个 M3 支柱
    pcb_w = 50;
    pcb_d = 35;
    hole_margin = 4;

    hole_positions = [
        [hole_margin, hole_margin],
        [pcb_w - hole_margin, hole_margin],
        [hole_margin, pcb_d - hole_margin],
        [pcb_w - hole_margin, pcb_d - hole_margin],
    ];

    for (pos = hole_positions)
        translate([margin + pos[0], margin + pos[1], plate_h])
            difference() {
                cylinder(h = boss_h, d = boss_od);
                translate([0, 0, -0.1])
                    cylinder(h = boss_h + 0.2, d = boss_hole_d);
            }
}

// 对 PCB 安装板的简化: 直接导入 DXF 层
module dxf_based_plate() {
    // 如果 DXF 文件存在, 用它替代:
    // linear_extrude(height = plate_h)
    //     import(dxf_file, layer = dxf_outline_layer);

    // 否则用手动计算的尺寸:
    mounting_plate();
}


module main() {
    dxf_based_plate();
    standoffs();
    pcb_mockup();
}

main();

// 完整 DXF 工作流:
// 1. 从 KiCad 导出 DXF: File → Plot → DXF
// 2. Python 解析 DXF 提取 PCB 轮廓和安装孔位
// 3. 将解析出的尺寸填入本文件的变量
// 4. 生成安装板 STL
//
// Python 解析脚本示例见 references/dxf-import-guide.md
