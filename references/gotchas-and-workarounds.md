# 常见陷阱和工作区方案

OpenSCAD 开发中反复出现的问题及其解决方案。

## 🔴 中文路径 / 非 ASCII 路径

**问题**: `import()` 中文路径下的文件崩溃或静默失败。

**解决方案**:
- 项目路径只用 ASCII（英文/数字/下划线/连字符）
- 用户名含中文时，将项目放在 `C:\Users\Public\` 或 `C:\projects\` 下
- STL 导出路径同样避免中文

## 🔴 CGAL 渲染崩溃

**问题**: 模型在 preview (F5) 正常，但 render (F6) 时闪退或报错 "CGAL error"。

**原因**: CGAL 对非流形 (non-manifold) 几何体的容忍度极低。

**解决方案**:
1. 改用 Manifold 后端: `openscad --backend manifold`
2. 检查 `difference()` 是否有重合面 — 将被减体延伸 0.01mm
3. 避免 `polyhedron()` 的自交面
4. 减小 `$fn` 看是否是精度问题
5. 将复杂模型拆分为多个小文件分别渲染

## 🟡 重合面 (Coincident Faces)

**问题**: `difference()` 中被减体的面与基体的面完全重合，导致渲染闪烁或空洞。

**解决方案**: 让被减体比基体多伸出一点:
```openscad
module clearance_hole_through(d) {
    // 上下各多伸出 1mm 避免重合面
    cylinder(h = 200, d = d, center = true);
}

difference() {
    cube([50, 50, 5]);
    // ❌ cylinder(h = 5, d = 3);         // 面和面重合!
    // ✅
    translate([25, 25, -1])               // 底部多 1mm
        cylinder(h = 7, d = 3);           // 高度多 2mm
}
```

## 🟡 projection() 失败

**问题**: `projection(cut = true)` 在复杂 STL 上返回空结果。

**解决方案**: 用 `intersection()` 切薄片替代:
```openscad
// ❌ projection(cut = true) import("complex.stl");
// ✅
intersection() {
    import("complex.stl");
    translate([0, 0, cut_height])
        cube([200, 200, 0.01], center = true);
}
```

## 🟡 $fn 性能问题

**问题**: `$fn = 360` 导致渲染极慢。

**建议值**:
| 场景 | $fn 值 | 说明 |
|------|--------|------|
| 快速预览 | 24 | 开发时用 |
| 小圆柱 (<5mm) | 32 | 孔/小螺丝 |
| 中等圆柱 | 64 | 一般零件 |
| 外观面 | 128 | 最终导出 |
| 展示级 | 256 | 渲染图/视频 |

对于动态控制精度的场景，推荐用 `$fa` + `$fs`:
```openscad
$fa = 1;    // 最小角度步进 (度) — 越小越圆
$fs = 0.4;  // 最小边长度 (mm) — 越小越圆
```

## 🟡 preview vs render 行为差异

**问题**: F5 (preview) 显示正常，F6 (render) 什么都没出现。

**原因**: 顶层只有一个 `difference()` 时，preview 中的 "negative" 部分是透明的，render 中完全减去后可能为空。

**检查**:
- 确保被减体在正确位置
- 使用 `#` 和 `%` 调试辅助符检查位置
- 用 `!` 独立显示单个模块确认

## 🟡 导入 STL 位置偏移

**问题**: `import("file.stl")` 导入的网格位置不在原点。

**解决方案**:
```python
# 用 Python 检查 STL 包围盒中心
import trimesh
m = trimesh.load('file.stl')
center = m.bounds.mean(axis = 0)
print(f"Center offset: {-center}")  # 用这个值 translate 回原点
```

## 🟢 3MF vs STL 选择

| 格式 | 优点 | 缺点 |
|------|------|------|
| STL | 通用，所有切片软件支持 | 无颜色/材质，文件大 |
| 3MF | 支持多颜色/多材质/元数据，文件小 | 兼容性不如 STL，偶有导出 bug |

**建议**: 默认用 STL (ASCII)，需要多材质时用 3MF。

## 🟢 调试技巧

```openscad
// # 号: 透明高亮，用于检查被减体的位置
// % 号: 半透明，用于显示参考物体
// ! 号: 只显示当前模块，用于隔离检查
// * 号: 禁用该节点

difference() {
    cube([50, 50, 5]);
    #translate([25, 25, 0]) cylinder(h = 5, d = 10);  // 高亮孔位
    %translate([0, 0, 10]) cube([50, 50, 3]);          // 半透明参考
}
// !cube([50, 50, 5]);  // 只显示 cube
```

## 🟢 检查是否安装了 OpenSCAD

```bash
# 检查版本
openscad --version

# 检查后端
openscad --info 2>&1 | grep -i backend
```
