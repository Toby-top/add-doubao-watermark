from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from .watermark import (
    PngWatermarkStyle,
    WatermarkStyle,
    add_png_watermark,
    add_png_watermark_image,
    add_text_watermark,
    load_default_watermark_png,
    save_image_like_input,
)


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def _iter_images(input_path: Path) -> list[Path]:
    if input_path.is_file():
        return [input_path]

    paths: list[Path] = []
    for p in input_path.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            paths.append(p)
    return sorted(paths)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="doubao-watermark",
        description="给图片添加“豆包AI生成”文字水印（macOS / Python）。",
    )
    parser.add_argument("input", type=str, help="输入图片文件或目录")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="输出目录（默认: 在输入旁边创建 out/；单文件则输出为 <name>.watermarked<ext>）",
    )
    parser.add_argument("--text", type=str, default="豆包AI生成", help="水印文本")
    parser.add_argument(
        "--watermark-png",
        type=str,
        default=None,
        help="水印PNG路径（若不传，会尝试使用内置 assets/doubao_watermark.png；找不到则回退为文字水印）",
    )
    parser.add_argument(
        "--position",
        type=str,
        default="bottom-right",
        choices=["bottom-right", "bottom-left", "top-right", "top-left", "center"],
        help="水印位置",
    )
    parser.add_argument("--opacity", type=int, default=128, help="不透明度 0-255")
    parser.add_argument("--fill", type=str, default="#FFFFFF", help="文字颜色（例如 #FFFFFF）")
    parser.add_argument("--stroke-fill", type=str, default="#000000", help="描边颜色（例如 #000000）")
    parser.add_argument("--stroke-width", type=int, default=2, help="描边宽度（像素）")
    parser.add_argument(
        "--font",
        type=str,
        default=None,
        help="字体文件路径（默认尝试系统 PingFang 等字体；注意中文需要可用字体）",
    )
    parser.add_argument(
        "--font-size-ratio",
        type=float,
        default=0.05,
        help="字体大小比例（相对图片短边，默认 0.05）",
    )
    parser.add_argument(
        "--margin-ratio",
        type=float,
        default=0.02,
        help="边距比例（相对图片短边，默认 0.02）",
    )
    parser.add_argument(
        "--png-width-ratio",
        type=float,
        default=0.22,
        help="PNG 水印宽度比例（相对图片短边，默认 0.22）",
    )
    return parser


def _compute_output_path(input_root: Path, src: Path, output_arg: str | None) -> Path:
    if src.is_file() and input_root.is_file():
        if output_arg:
            out = Path(output_arg).expanduser()
            if out.suffix:
                return out
            return out / f"{src.stem}.watermarked{src.suffix}"
        return src.with_name(f"{src.stem}.watermarked{src.suffix}")

    out_dir = Path(output_arg).expanduser() if output_arg else input_root / "out"
    rel = src.relative_to(input_root)
    return out_dir / rel


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path = Path(args.input).expanduser()
    if not input_path.exists():
        parser.error(f"输入路径不存在: {input_path}")

    images = _iter_images(input_path)
    if not images:
        parser.error("未找到可处理的图片（支持: jpg/jpeg/png/webp/bmp/tif/tiff）")

    png_path: Path | None = None
    if args.watermark_png:
        png_path = Path(args.watermark_png).expanduser()
        if not png_path.exists():
            parser.error(f"水印PNG不存在: {png_path}")

    text_style = WatermarkStyle(
        text=args.text,
        position=args.position,
        opacity=args.opacity,
        fill=args.fill,
        stroke_fill=args.stroke_fill,
        stroke_width=args.stroke_width,
        font_path=args.font,
        font_size_ratio=float(args.font_size_ratio),
        margin_ratio=float(args.margin_ratio),
    )
    png_style = PngWatermarkStyle(
        position=args.position,
        opacity=args.opacity,
        margin_ratio=float(args.margin_ratio),
        width_ratio=float(args.png_width_ratio),
    )

    for src in images:
        out_path = _compute_output_path(input_path, src, args.output)
        with Image.open(src) as img:
            if png_path is not None:
                watermarked = add_png_watermark(img, png_path, png_style)
            else:
                built_in = load_default_watermark_png()
                if built_in is not None:
                    watermarked = add_png_watermark_image(img, built_in, png_style)
                else:
                    watermarked = add_text_watermark(img, text_style)
            save_image_like_input(watermarked, src, out_path)
        print(f"{src} -> {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
