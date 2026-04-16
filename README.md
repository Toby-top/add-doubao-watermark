# 豆印 - 为图片批量添加豆包水印
你是否会遇到这种情况：看见一张图片，诡异得像是 AI 生成的，但是四处寻找都不能找到 AI 水印😭。 ~~这时天空一声巨响，豆印响亮登场~~ -- 豆印可以批量为图片添加 “豆包 AI 生成”水印，帮你弥补这一遗憾...
当然也可以用来为一些错误找藉口。

## Introductions

一个离线小工具：给图片批量添加“豆包AI生成”水印。支持 **GUI** 和 **命令行**，适合把一批图快速处理成带水印的版本。

支持格式：`jpg/jpeg/png/webp/bmp/tif/tiff`  
默认输出：  
- 处理单张图片：生成 `*.watermarked.*`  
- 处理目录：在输入目录旁生成 `out/`，并保持目录结构

示例（仓库自带样例图）：

| 原图 | 处理后 |
| --- | --- |
| ![sample](sample.jpg) | ![sample watermarked](sample.watermarked.jpg) |

---

## 下载安装（推荐：直接用打包好的程序）

1. 打开本仓库的 [Release](https://github.com/Toby-top/add-doubao-watermark/releases "") 页面，下载与你系统匹配的可执行文件(macOS ARM64/Windows x86_64)
2. 解压后你会看到两个程序：
   - `doubao-watermark` / `doubao-watermark.exe`：命令行工具
   - `doubao-watermark-gui.app` / `doubao-watermark-gui.exe`：图形界面工具

### macOS 打不开的解决方式

若提示“来自未识别开发者/无法打开”，按 macOS 版本通常有两种方式：

- **系统设置 → 隐私与安全性**：在提示处允许打开
- 或在终端执行（对解压目录按需替换路径）：

```bash
xattr -dr com.apple.quarantine ./doubao-watermark-gui.app
```

---

## 使用方法（GUI）

1. 打开 `doubao-watermark-gui`（macOS 为 `doubao-watermark-gui.app`）。
2. 点击「选择图片…」或「选择目录…」。
3. （可选）点击「选择输出目录…」；不选则：
   - 单张图片输出为 `*.watermarked.*`
   - 目录输出到输入目录旁的 `out/`
4. 调整参数（可选）：
   - 位置：`bottom-right / bottom-left / top-right / top-left / center`
   - 不透明度：0–255
   - PNG 宽度比例、边距比例
   - 勾选「叠加自定义文字」并输入文字（不勾选则不叠加文字）
5. 点击「开始处理」。

---

## 使用方法（CLI）

解压后，进入解压目录：

- macOS：在终端执行

```bash
./doubao-watermark <input>
```

 - Windows：在 PowerShell 执行

```powershell
.\doubao-watermark.exe <input>
```

常用示例：

```bash
# 处理一个目录（递归），输出到 <input>/out/
./doubao-watermark ./images

# 处理一张图片（输出为 *.watermarked.*）
./doubao-watermark ./a.jpg

# 指定输出目录
./doubao-watermark ./images -o ./out

# 调整位置/不透明度
./doubao-watermark ./a.jpg --position top-left --opacity 180

# 叠加一行自定义文字
./doubao-watermark ./a.jpg --text "自定义文字"
```

查看完整参数：

```bash
./doubao-watermark --help
```

---

## 自定义/替换水印 PNG（可选）

默认会使用程序内置的水印 PNG；如果你想替换成自己提取的“真实豆包水印 PNG”，有两种方式：

1. **CLI 指定外部 PNG**（推荐）：

```bash
./doubao-watermark ./a.jpg --watermark-png /path/to/your/watermark.png
```

2. **从源码运行/自行打包时替换内置 PNG**：把 PNG 放到  
`src/add_doubao_watermark/assets/`，命名为 `doubao_watermark.png`（或 `doubao-watermark.png`）。

---

## 从源码运行（For Developers）

环境：Python 3.9+。

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

运行 CLI：

```bash
doubao-watermark <input>
```

运行 GUI：

```bash
doubao-watermark-gui
```

---

## 常见问题

### 1) 为什么输出目录里也会有子目录？
当输入是一个目录时，会递归处理，并在输出目录中 **保持原始目录结构**，方便对照与回滚。

### 2) 我只想处理某几张图？
用 GUI 的「选择图片…」；或 CLI 直接传单个文件路径（也可以多次执行）。

---

## To do.

- 适配更多平台（macOS x86_64/Linux/Android...）

- 设计一个有意思的应用图标

> 有任何改进建议，欢迎 PR 或发起 issue 和 discussion。

---

## 免责声明

本项目为非官方工具，仅供学习与个人使用。请确保你对待处理图片与水印使用方式拥有合法权利，并遵守相关平台/服务条款。

## License

MIT License（见 `LICENSE`）。
