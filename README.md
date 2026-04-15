# add-doubao-watermark

一个在 macOS 上开发/打包的图片水印工具：给图片批量添加“豆包AI生成”文字水印（默认右下角）。

## 功能

- 支持单张图片或目录批量处理（递归）
- 支持 `jpg/jpeg/png/webp/bmp/tif/tiff`
- 可配置位置、透明度、颜色、描边、字体大小/边距比例
- 支持 PyInstaller 打包成可分发的 macOS 可执行文件（CLI）

## 本地开发（不安装也能跑）

```bash
PYTHONPATH=src python3 -m add_doubao_watermark.cli <input>
```

例如：

```bash
PYTHONPATH=src python3 -m add_doubao_watermark.cli ./images
PYTHONPATH=src python3 -m add_doubao_watermark.cli ./a.jpg --position bottom-right --opacity 160
```

## 安装（可选）

如果你希望使用命令 `doubao-watermark`：

```bash
python3 -m pip install -e . --no-build-isolation
doubao-watermark ./images
```

## 使用说明

```bash
doubao-watermark <input> [--output <path>] [--text <text>] [--position <pos>] [--opacity 0-255]
```

- `<input>`：图片文件或目录（目录会递归处理）
- `--output/-o`：
  - 输入是单文件：可传输出文件路径，或输出目录（自动生成 `<name>.watermarked<ext>`）
  - 输入是目录：默认输出到 `<input>/out/`，并保持目录结构
- `--font`：指定字体文件路径（中文需要可用中文字体）。默认会尝试系统字体（如 `PingFang`）。

## 打包（macOS）

产物是一个单文件 CLI 可执行程序（放在 `dist/`）：

```bash
./scripts/build_macos.sh
```

生成：

- `dist/doubao-watermark`
- `dist/doubao-watermark-<version>-macos-<arch>.zip`

## GitHub Release（推荐流程）

仓库包含一个 workflow：当你 push tag（例如 `v0.1.0`）时，会在 GitHub Actions 上构建 macOS 包并上传到 Release。

```bash
git tag v0.1.0
git push origin v0.1.0
```

