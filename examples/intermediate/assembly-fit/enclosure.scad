// 合成装配示例，单位 mm。原点在底盒外部左前下角，开口朝 +Z。
// 侧壁向内增厚；底板、孔轴、支柱顶面和 PCB 的装配位置固定。
part = "base";             // [base,lid,pcb,assembly]
wall = 2;
outer_xy = [100, 60];
base_height = 16;
floor_thickness = 2;
lid_thickness = 2;
hole_centers = [[10,10], [90,10], [10,50], [90,50]];
hole_diameter = 3.2;
boss_diameter = 6;
board_origin = [5,5,6];
board_size = [90,50,1.6];
cut_extra = 0.2;
$fn = 64;

module bores(centers, bottom, height) {
    for (p = centers)
        translate([p.x, p.y, bottom - cut_extra])
            cylinder(h = height + 2*cut_extra, d = hole_diameter);
}

module base(thickness = wall, centers = hole_centers) {
    assert(thickness > 0 && 2*thickness < min(outer_xy));
    difference() {
        union() {
            difference() {
                cube([outer_xy.x, outer_xy.y, base_height]);
                translate([thickness, thickness, floor_thickness])
                    cube([outer_xy.x-2*thickness, outer_xy.y-2*thickness, base_height]);
            }
            for (p = hole_centers)
                translate([p.x, p.y, 0]) cylinder(h = board_origin.z, d = boss_diameter);
        }
        bores(centers, 0, base_height);
    }
}

module lid() {
    difference() {
        cube([outer_xy.x, outer_xy.y, lid_thickness]);
        bores(hole_centers, 0, lid_thickness);
    }
}

module pcb() {
    difference() {
        translate(board_origin) cube(board_size);
        bores(hole_centers, board_origin.z, board_size.z);
    }
}

if (part == "base") base(wall);
else if (part == "lid") lid();
else if (part == "pcb") pcb();
else if (part == "assembly") {
    base(wall);
    color("green") pcb();
    color("silver", 0.5) translate([0,0,base_height]) lid();
} else assert(false, str("unknown part: ", part));

// 仓库根目录运行 python scripts/verify_assembly.py --wall 3 --out evidence
