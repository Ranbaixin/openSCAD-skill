"""Independent acceptance geometry for the 100 × 60 mm enclosure example."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass

import networkx as nx
import numpy as np
from trimesh.intersections import mesh_plane

HOLES = [(10, 10), (90, 10), (10, 50), (90, 50)]
BOUNDS = {"base": [[0, 0, 0], [100, 60, 16]], "lid": [[0, 0, 0], [100, 60, 2]],
          "pcb": [[5, 5, 6], [95, 55, 7.6]]}
DEPTHS = {"base": [0.5, 1.5, 4.5, 5.8], "lid": [0.25, 1, 1.75], "pcb": [6.2, 6.8, 7.4]}
LENGTH_TOL = 0.05
VOLUME_TOL = 0.01
BORE = 3.2


def xy_segments(mesh, depth):
    return mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, depth])[:, :, :2]


def hole_profiles(mesh, part, bosses=False):
    depths = list([4.5, 5.8] if bosses else DEPTHS[part])
    bottom, top = {"base": (0, 6), "lid": (0, 2), "pcb": (6, 7.6)}[part]
    if bosses:
        bottom = 2
    # 顶点高度划分实际产物中的几何变化区间，固定取样间的台阶孔也会被量到。
    levels = sorted({bottom, top, *(float(z) for z in mesh.vertices[:, 2] if bottom+1e-5 < z < top-1e-5)})
    for low, high in zip(levels, levels[1:]):
        inset = min(0.001, (high-low)/4)
        depths.extend([low+inset, (low+high)/2, high-inset])
    depths = sorted(set(depths))
    diameter = 6 if bosses else BORE
    records = [{"target_center_mm": center, "depths_mm": depths, "centers_mm": [],
                "diameter_ranges_mm": []} for center in HOLES]
    passed = True
    for z in depths:
        graph = nx.Graph()
        for start, end in xy_segments(mesh, z).round(5):
            if not np.array_equal(start, end):
                graph.add_edge(tuple(start), tuple(end))
        rings = []
        for nodes in nx.connected_components(graph):
            if len(nodes) < 3 or any(graph.degree[p] != 2 for p in nodes):
                continue
            points = np.asarray(list(nodes))
            center = (points.min(axis=0) + points.max(axis=0)) / 2
            radial_max = np.linalg.norm(points - center, axis=1).max()
            # 用线段的最近点测量内切直径，包含圆孔多边形化的误差。
            edges = np.asarray(list(graph.subgraph(nodes).edges()))
            a = edges[:, 0] - center
            v = edges[:, 1] - edges[:, 0]
            t = np.clip(-(a*v).sum(axis=1) / (v*v).sum(axis=1), 0, 1)
            radial_min = np.linalg.norm(a + t[:, None]*v, axis=1).min()
            rings.append((center, [2*radial_min, 2*radial_max]))
        for p, record in zip(HOLES, records):
            nearby = [(c, d) for c, d in rings if np.linalg.norm(c-p) < 4]
            if not nearby:
                record["centers_mm"].append(None)
                record["diameter_ranges_mm"].append(None)
                passed = False
                continue
            c, diam = min(nearby, key=lambda ring: abs(ring[1][1] - diameter))
            record["centers_mm"].append(c.tolist())
            record["diameter_ranges_mm"].append(diam)
            passed &= bool(np.linalg.norm(c-p) <= LENGTH_TOL and max(abs(v-diameter) for v in diam) <= LENGTH_TOL)
    return bool(passed), records


def line_hits(segments, axis, midpoint):
    other = 1-axis
    a, b = segments[:, 0], segments[:, 1]
    crossed = (a[:, other] > midpoint) != (b[:, other] > midpoint)
    a, b = a[crossed], b[crossed]
    t = (midpoint - a[:, other]) / (b[:, other] - a[:, other])
    return np.unique(np.round(a[:, axis] + t * (b[:, axis]-a[:, axis]), 5))


def wall_widths(mesh):
    segments = xy_segments(mesh, 10)
    result = []
    for axis, midpoint in [(0, 30), (1, 50)]:
        hits = line_hits(segments, axis, midpoint)
        if len(hits) != 4:
            return []
        result.extend([float(hits[1]-hits[0]), float(hits[3]-hits[2])])
    return result


def floor_widths(mesh):
    result = []
    for y in (20, 40):
        cut = mesh_plane(mesh, plane_normal=[0,1,0], plane_origin=[0,y,0])[:, :, [0,2]]
        for x in (35,65):
            hits = line_hits(cut, 1, x)
            if len(hits) != 2:
                return []
            result.append(float(hits[1]-hits[0]))
    return result


def place(xyz, geometry):
    return f"translate({json.dumps(xyz)}) {geometry}"


def box(origin, dims):
    return place(origin, f"cube({json.dumps(dims)});")


def csg(operation, *solids):
    return operation + "() {" + "\n".join(solids) + "}"


def pins(diameter, z, height):
    return csg("union", *(place([x, y, z], f"cylinder(d={diameter},h={height},$fn=64);") for x, y in HOLES))


def sidewalls(wall):
    return csg("difference", box([0,0,2], [100,60,14]),
               box([wall,wall,1], [100-2*wall,60-2*wall,16]))


def gauges(wall):
    # 独立于被测模型。支柱顶环与盖底允许面贴合，其余区域要求净空。
    under_board = csg("difference", box([5,5,5.9], [90,50,0.1]), pins(6,5.8,0.3))
    under_lid = box([wall,wall,15.9], [100-2*wall,60-2*wall,0.1])
    return {
        "pcb_space": box([4.5,4.5,6], [91,51,5.6]),
        "contact_clearance": csg("union", under_board, under_lid),
        "through": pins(3.15/math.cos(math.pi/64), -0.1, 18.2),
    }


def material_gauges(wall):
    def rim(z):
        return csg("difference", box([0,0,z], [100,60,0.05]),
                   box([wall,wall,z-0.05], [100-2*wall,60-2*wall,0.15]))

    def supports(z):
        return csg("difference", pins(5.8,z,0.05), pins(3.4,z-0.05,0.15))

    # 内缩 0.001 mm 避免检测体端盖与 STL 共面。另有全长通规和端面接触检查。
    sleeves = {part:csg("difference", pins(4.5,z+0.001,h-0.002),
                        pins(BORE+3*LENGTH_TOL,z-0.05,h+0.1))
               for part,z,h in [("base",0,6), ("pcb",6,1.6), ("lid",16,2)]}
    return {"rim_contact": {"base": rim(15.95), "lid": rim(16)},
            "support_contact": {"base": supports(5.95), "pcb": supports(6)},
            "hole_material": sleeves}


@dataclass
class Solid:
    expression: str
    volume: float
