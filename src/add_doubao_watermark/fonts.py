from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FontCandidate:
    name: str
    path: Path


def default_macos_chinese_fonts() -> list[FontCandidate]:
    # Prefer system fonts that can render Chinese. These paths exist on most macOS installs.
    return [
        FontCandidate("PingFang SC (TTC)", Path("/System/Library/Fonts/PingFang.ttc")),
        FontCandidate("Heiti SC (TTC)", Path("/System/Library/Fonts/STHeiti Medium.ttc")),
        FontCandidate("Songti SC (TTC)", Path("/System/Library/Fonts/Supplemental/Songti.ttc")),
    ]


def find_default_font_path(user_font: str | None) -> Path | None:
    if user_font:
        p = Path(user_font).expanduser()
        return p if p.exists() else None

    for candidate in default_macos_chinese_fonts():
        if candidate.path.exists():
            return candidate.path
    return None

