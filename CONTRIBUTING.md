# 贡献指南

感谢你对 openSCAD-skill 的关注！以下是贡献流程和规范。

## 贡献类型

我们欢迎以下类型的贡献:

| 类型 | 描述 | 建议 |
|------|------|------|
| **新增 SCAD 示例** | `examples/` 目录中添加新的教学模型 | 见下方「SCAD 示例规范」 |
| **参考文档更新** | 修正/扩展 `references/` 中的内容 | 附上数据来源或实测验证 |
| **Bug 修复** | 修正现有代码或文档的错误 | 描述复现步骤 |
| **新功能/模式** | 添加新的建模模式或工作流 | 在 Issues 中先讨论 |

## SCAD 示例规范

新增示例需满足以下标准:

### 代码规范

- ✅ 所有尺寸定义为命名变量，放在文件顶部
- ✅ 变量名用英文描述（`plate_w`, `hole_d`, `corner_r`）
- ✅ 注释用中文，位于关键逻辑上方
- ✅ 使用 `module` 封装可复用组件
- ✅ `$fn` 作为可调变量（默认 64）
- ✅ 文件头注释说明示例教什么
- ✅ 文件尾注释给出导出命令示例

### 渲染要求

```bash
# 每个文件必须能独立渲染成功
openscad -o /dev/null example.scad  # 退出码 0
```

### 依赖层级

| 难度 | 依赖 | 规则 |
|------|------|------|
| Basic | 仅 OpenSCAD 内置 | 零外部依赖 |
| Intermediate | 仅 OpenSCAD 内置 | 鼓励用 for/hull/difference 等内置功能 |
| Advanced | 可引入 BOSL2 | 文件头注释必须注明依赖和安装方式 |

## 参考文档规范

- 内容必须有可靠来源（标准规范、官方文档、实测数据）
- 代码示例必须可运行
- 写清楚「何时打开这个文件」— 帮助 Claude 判断加载时机

## PR 流程

1. **Fork** 本仓库
2. **创建分支**: `feature/my-example` 或 `fix/screw-table`
3. **编写代码/文档**（遵循上述规范）
4. **本地验证**:
   ```bash
   # 验证所有示例可渲染
   bash tests/verify-examples.sh

   # 或者手动验证单个文件
   openscad -o /dev/null examples/basic/your-example.scad
   ```
5. **提交 PR**: 描述变更内容和动机

## Commit 规范

建议遵循 Conventional Commits:
```
feat: 新增圆角板带加强筋示例
fix: 修正 M4 沉头孔直径数据
docs: 补充 BOSL2 安装说明
```

## 代码风格参考

```openscad
// ✅ 推荐的风格
/* [Dimensions] */
plate_w = 80;          // 板宽 (mm) — 命名描述性, 带单位注释
plate_d = 50;
plate_h = 3;
corner_r = 5;
$fn = 64;

/* [Hole Pattern] */
hole_d = 3.2;          // M3 标准孔
hole_margin = 8;

module rounded_plate(w, d, h, r) {
    hull()
    for (x = [r, w - r])
        for (y = [r, d - r])
            translate([x, y, 0])
                cylinder(h = h, r = r);
}
```

```openscad
// ❌ 不推荐的风格
w=80;d=50;h=3;r=5;$fn=64;  // 变量无注释, 挤在一行

module rp(a,b,c,d){        // 无意义的缩写
    hull(){
        cylinder(h=c,r=d);  // 缺少 translate, 功能不正确
    }
}
```

## 交流

- 有问题或想法？在 [GitHub Issues](https://github.com/Ranbaixin/openSCAD-skill/issues) 中提出
