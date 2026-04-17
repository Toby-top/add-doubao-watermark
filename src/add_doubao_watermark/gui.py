from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path
from tkinter import BooleanVar, DoubleVar, IntVar, StringVar, Tk, ttk, filedialog, messagebox

from PIL import Image

from .win_dpi import enable_windows_dpi_awareness
from .watermark import (
    PngWatermarkStyle,
    WatermarkStyle,
    add_png_watermark_image,
    add_text_watermark,
    load_default_watermark_png,
    save_image_like_input,
)


SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def _iter_images(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for input_path in inputs:
        if input_path.is_file():
            if input_path.suffix.lower() in SUPPORTED_EXTS:
                paths.append(input_path)
            continue
        for p in input_path.rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
                paths.append(p)
    return sorted(set(paths))


def _compute_output_path(
    input_root: Path, src: Path, output_dir: Path | None
) -> Path:
    if input_root.is_file():
        if output_dir is None:
            return src.with_name(f"{src.stem}.watermarked{src.suffix}")
        if output_dir.suffix:
            return output_dir
        return output_dir / f"{src.stem}.watermarked{src.suffix}"

    out_dir = output_dir if output_dir is not None else input_root / "out"
    rel = src.relative_to(input_root)
    return out_dir / rel


@dataclass(frozen=True)
class GuiJob:
    inputs: list[Path]
    output_dir: Path | None
    position: str
    opacity: int
    png_width_ratio: float
    margin_ratio: float
    add_text: bool
    text: str


class App:
    def __init__(self, root: Tk) -> None:
        self.root = root
        root.title("豆印")
        root.geometry("640x360")

        self.input_paths: list[Path] = []
        self.output_dir: Path | None = None

        self.position = StringVar(value="bottom-right")
        self.opacity = IntVar(value=int(255 * 0.95))
        self.png_width_ratio = DoubleVar(value=0.22)
        self.margin_ratio = DoubleVar(value=0.02)
        self.add_text = BooleanVar(value=False)
        self.text = StringVar(value="")

        self.status = StringVar(value="就绪")
        self.progress = IntVar(value=0)

        self._build_ui()

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        row1 = ttk.Frame(main)
        row1.pack(fill="x")
        ttk.Button(row1, text="选择图片…", command=self.pick_files).pack(side="left")
        ttk.Button(row1, text="选择目录…", command=self.pick_folder).pack(side="left", padx=8)
        ttk.Button(row1, text="选择输出目录…", command=self.pick_output).pack(side="left")
        ttk.Button(row1, text="清空", command=self.clear_inputs).pack(side="right")

        self.inputs_label = ttk.Label(main, text="未选择输入")
        self.inputs_label.pack(fill="x", pady=(10, 0))

        self.output_label = ttk.Label(main, text="输出：默认（输入旁边 out/ 或 *.watermarked）")
        self.output_label.pack(fill="x")

        opts = ttk.LabelFrame(main, text="参数", padding=10)
        opts.pack(fill="x", pady=10)

        r = 0
        ttk.Label(opts, text="位置").grid(row=r, column=0, sticky="w")
        ttk.Combobox(
            opts,
            textvariable=self.position,
            values=["bottom-right", "bottom-left", "top-right", "top-left", "center"],
            state="readonly",
            width=14,
        ).grid(row=r, column=1, sticky="w", padx=(8, 18))

        ttk.Label(opts, text="不透明度").grid(row=r, column=2, sticky="w")
        ttk.Scale(opts, from_=0, to=255, variable=self.opacity, orient="horizontal").grid(
            row=r, column=3, sticky="ew", padx=(8, 0)
        )
        opts.columnconfigure(3, weight=1)

        r += 1
        ttk.Label(opts, text="PNG宽度比例").grid(row=r, column=0, sticky="w", pady=(8, 0))
        ttk.Scale(
            opts, from_=0.05, to=0.6, variable=self.png_width_ratio, orient="horizontal"
        ).grid(row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(8, 0))

        r += 1
        ttk.Label(opts, text="边距比例").grid(row=r, column=0, sticky="w", pady=(8, 0))
        ttk.Scale(opts, from_=0.0, to=0.1, variable=self.margin_ratio, orient="horizontal").grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(8, 0)
        )

        r += 1
        ttk.Checkbutton(opts, text="叠加自定义文字", variable=self.add_text).grid(
            row=r, column=0, sticky="w", pady=(10, 0)
        )
        ttk.Entry(opts, textvariable=self.text).grid(
            row=r, column=1, columnspan=3, sticky="ew", padx=(8, 0), pady=(10, 0)
        )

        bottom = ttk.Frame(main)
        bottom.pack(fill="x", pady=(10, 0))
        ttk.Button(bottom, text="开始处理", command=self.start).pack(side="left")
        ttk.Progressbar(bottom, maximum=100, variable=self.progress).pack(
            side="left", fill="x", expand=True, padx=10
        )
        ttk.Label(bottom, textvariable=self.status).pack(side="right")

    def pick_files(self) -> None:
        files = filedialog.askopenfilenames(
            title="选择图片", filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tif *.tiff")]
        )
        if not files:
            return
        self.input_paths = [Path(p) for p in files]
        self._refresh_labels()

    def pick_folder(self) -> None:
        d = filedialog.askdirectory(title="选择目录")
        if not d:
            return
        self.input_paths = [Path(d)]
        self._refresh_labels()

    def pick_output(self) -> None:
        d = filedialog.askdirectory(title="选择输出目录")
        if not d:
            return
        self.output_dir = Path(d)
        self._refresh_labels()

    def clear_inputs(self) -> None:
        self.input_paths = []
        self.output_dir = None
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        if not self.input_paths:
            self.inputs_label.configure(text="未选择输入")
        else:
            shown = ", ".join(str(p) for p in self.input_paths[:3])
            if len(self.input_paths) > 3:
                shown += f" … (+{len(self.input_paths)-3})"
            self.inputs_label.configure(text=f"输入：{shown}")

        if self.output_dir is None:
            self.output_label.configure(text="输出：默认（输入旁边 out/ 或 *.watermarked）")
        else:
            self.output_label.configure(text=f"输出：{self.output_dir}")

    def start(self) -> None:
        if not self.input_paths:
            messagebox.showerror("错误", "请先选择图片或目录")
            return

        watermark = load_default_watermark_png()
        if watermark is None:
            messagebox.showerror(
                "错误",
                "未找到内置水印PNG：src/add_doubao_watermark/assets/doubao_watermark.png（或 doubao-watermark.png）",
            )
            return

        job = GuiJob(
            inputs=self.input_paths,
            output_dir=self.output_dir,
            position=self.position.get(),
            opacity=int(self.opacity.get()),
            png_width_ratio=float(self.png_width_ratio.get()),
            margin_ratio=float(self.margin_ratio.get()),
            add_text=bool(self.add_text.get()),
            text=self.text.get().strip(),
        )

        self.root.title("豆印 - 处理中…")
        self.progress.set(0)
        self.status.set("处理中…")

        t = threading.Thread(target=self._run_job, args=(job, watermark), daemon=True)
        t.start()

        self.root.title("豆印")

    def _run_job(self, job: GuiJob, watermark: Image.Image) -> None:
        try:
            images = _iter_images(job.inputs)
            if not images:
                raise RuntimeError("未找到可处理的图片")

            png_style = PngWatermarkStyle(
                position=job.position,
                opacity=job.opacity,
                margin_ratio=job.margin_ratio,
                width_ratio=job.png_width_ratio,
            )
            text_style = WatermarkStyle(
                text=job.text,
                position=job.position,
                opacity=job.opacity,
                margin_ratio=job.margin_ratio,
            )

            total = len(images)
            for i, src in enumerate(images, start=1):
                # Choose a root for output path computation
                root = job.inputs[0] if len(job.inputs) == 1 else src
                out_path = _compute_output_path(root, src, job.output_dir)
                with Image.open(src) as img:
                    out = add_png_watermark_image(img, watermark, png_style)
                    if job.add_text and job.text:
                        out = add_text_watermark(out, text_style)
                    save_image_like_input(out, src, out_path)

                self.root.after(
                    0,
                    lambda pct=int(i * 100 / total): self.progress.set(pct),
                )

            self.root.after(0, lambda: self.status.set(f"完成（{total}张）"))
            self.root.after(0, lambda: messagebox.showinfo("完成", f"处理完成：{total} 张"))
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.status.set("失败"))
            self.root.after(0, lambda msg=error_msg: messagebox.showerror("失败", msg))


def main() -> int:
    enable_windows_dpi_awareness()
    root = Tk()
    root.title("豆印 - 为图片加上豆包水印")
    try:
        ttk.Style().theme_use("aqua")
    except Exception:
        pass
    App(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())