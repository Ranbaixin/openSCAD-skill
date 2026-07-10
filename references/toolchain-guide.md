# 工具链和 CI/CD 配置

OpenSCAD 开发的编辑器、格式化器和自动化流水线配置。

## VS Code 扩展

| 扩展 | 作者 | 特点 | 推荐度 |
|------|------|------|--------|
| **OpenSCAD Language Support** | Leathong | LSP 支持、自动完成、定义跳转、悬停文档、格式化 | ⭐⭐⭐ |
| **OpenSCAD for VS Code** | Antyos | 一键预览/导出、自动命名、内置速查表 | ⭐⭐⭐ |
| **Carve — Live Preview** | Carve3D | WebAssembly 实时预览（无需安装 OpenSCAD） | ⭐⭐ |
| **OpenSCAD Renderer** | luizbon | AI 代理（`/create`, `/debug`, `/optimize`）、实时 STL 渲染 | ⭐⭐ |

**推荐组合**: `OpenSCAD Language Support` + `OpenSCAD for VS Code`

## 代码格式化

### SCADFormat (Go)

```bash
# 安装
go install github.com/hugheaves/scadformat@latest

# 使用
scadformat -w file.scad
```

### Topiary (Rust, tree-sitter)

最新选项，被 OpenSCAD Language Support 扩展内置使用:

```bash
# 安装
cargo install topiary

# 使用
topiary format file.scad
```

### openscad-format (npm)

```bash
npm install -g openscad-format

# 配置 .openscad-format
{
    "IndentWidth": 4,
    "UseTab": false
}

# 使用
openscad-format file.scad
```

## CI/CD — GitHub Actions

### 基础模型验证流水线

```yaml
# .github/workflows/validate.yml
name: Validate SCAD Models

on:
  push:
    paths: ['**/*.scad']
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        backend: [manifold]
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true

      - name: Install OpenSCAD
        run: |
          sudo apt-get update
          sudo apt-get install -y openscad

      - name: Validate examples
        run: |
          failed=0
          for f in examples/**/*.scad; do
            echo "::group::Checking $f"
            if openscad --backend ${{ matrix.backend }} \
                -o /tmp/out.stl \
                --export-format binstl \
                "$f" 2>&1; then
              echo "✅ PASS"
            else
              echo "❌ FAIL"
              ((failed++))
            fi
            echo "::endgroup::"
          done
          exit $failed
```

### 多文件项目 CI

对于使用 `OPENSCADPATH` 的项目:

```yaml
- name: Validate all parts
  run: |
    export OPENSCADPATH="./libs:./modules"
    failed=0
    for part in base cover bracket; do
      openscad -o stl/$part.stl \
        -D "show=\"$part\"" \
        assembly.scad || ((failed++))
    done
    exit $failed
```

## 本地预检脚本

```bash
#!/bin/bash
# tests/verify-examples.sh
set -e

OPENSCAD=$(command -v openscad)
if [ -z "$OPENSCAD" ]; then
    echo "❌ openscad not found in PATH"
    echo "   Install from: https://openscad.org/downloads.html"
    exit 1
fi

echo "OpenSCAD: $($OPENSCAD --version 2>&1 | head -1)"
echo "---"

failed=0
total=0

for scad_file in examples/**/*.scad; do
    [ -f "$scad_file" ] || continue
    ((total++))
    printf "%-50s " "$scad_file"
    if "$OPENSCAD" -o /dev/null --export-format binstl "$scad_file" > /dev/null 2>&1; then
        echo "✅"
    else
        echo "❌"
        ((failed++))
    fi
done

echo "---"
echo "Results: $((total - failed))/$total passed, $failed failed"
exit $failed
```

## 编辑器设置

### .editorconfig

```ini
root = true

[*.scad]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
indent_style = space
indent_size = 2
trim_trailing_whitespace = false
```

## 推荐工作流

```
开发时:
  1. VS Code + OpenSCAD Language Support (自动完成、错误提示)
  2. 用小 $fn 快速迭代 (F5 preview)
  3. 用 # 和 % 调试辅助符验证位置

提交前:
  1. 格式化: scadformat -w *.scad
  2. 本地验证: ./tests/verify-examples.sh
  3. 渲染检查: openscad --render -o /dev/null file.scad

CI (自动):
  1. Push → GitHub Actions 验证所有 SCAD
  2. PR → CI 通过才能合并
```
