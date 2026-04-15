from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PIL import Image, ImageColor, ImageDraw, ImageFont

from .fonts import find_default_font_path

Position = Literal[
    "bottom-right",
    "bottom-left",
    "top-right",
    "top-left",
    "center",
]


@dataclass(frozen=True)
class WatermarkStyle:
    text: str = "豆包AI生成"
    position: Position = "bottom-right"
    opacity: int = 128  # 0-255
    fill: str = "#FFFFFF"
    stroke_fill: str = "#000000"
    stroke_width: int = 2
    margin_ratio: float = 0.02  # margin relative to min(image_w, image_h)
    font_path: str | None = None
    font_size_ratio: float = 0.05  # font size relative to min(image_w, image_h)


def _clamp_int(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _load_font(font_path: str | None, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    resolved = find_default_font_path(font_path)
    if resolved is not None:
        try:
            return ImageFont.truetype(str(resolved), size=size)
        except Exception:
            pass
    return ImageFont.load_default()


def _compute_anchor_xy(
    image_w: int,
    image_h: int,
    text_w: int,
    text_h: int,
    margin: int,
    position: Position,
) -> tuple[int, int]:
    if position == "bottom-right":
        return image_w - text_w - margin, image_h - text_h - margin
    if position == "bottom-left":
        return margin, image_h - text_h - margin
    if position == "top-right":
        return image_w - text_w - margin, margin
    if position == "top-left":
        return margin, margin
    # center
    return (image_w - text_w) // 2, (image_h - text_h) // 2


def add_text_watermark(img: Image.Image, style: WatermarkStyle) -> Image.Image:
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")
    base = img.convert("RGBA")

    min_dim = max(1, min(base.size))
    font_size = max(12, int(min_dim * style.font_size_ratio))
    margin = max(4, int(min_dim * style.margin_ratio))
    opacity = _clamp_int(style.opacity, 0, 255)

    font = _load_font(style.font_path, size=font_size)

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Compute text bbox
    bbox = draw.textbbox((0, 0), style.text, font=font, stroke_width=style.stroke_width)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x, y = _compute_anchor_xy(base.size[0], base.size[1], text_w, text_h, margin, style.position)

    fill_rgb = ImageColor.getrgb(style.fill)
    stroke_rgb = ImageColor.getrgb(style.stroke_fill)
    fill_rgba = (*fill_rgb, opacity)
    stroke_rgba = (*stroke_rgb, opacity)

    draw.text(
        (x, y),
        style.text,
        font=font,
        fill=fill_rgba,
        stroke_fill=stroke_rgba,
        stroke_width=style.stroke_width,
    )

    return Image.alpha_composite(base, overlay)


def save_image_like_input(
    watermarked: Image.Image, input_path: Path, output_path: Path
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    suffix = input_path.suffix.lower()

    if suffix in (".jpg", ".jpeg"):
        watermarked.convert("RGB").save(output_path, quality=95, optimize=True)
        return
    if suffix == ".png":
        watermarked.save(output_path, optimize=True)
        return
    if suffix == ".webp":
        watermarked.save(output_path, quality=95, method=6)
        return
    # Fallback: let Pillow pick based on extension
    watermarked.save(output_path)

