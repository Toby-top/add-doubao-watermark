from __future__ import annotations

import json
import re
import threading
import urllib.error
import urllib.request
import webbrowser
from importlib import metadata
from tkinter import Tk, messagebox

# NOTE:
# - Do not call any Tk APIs from background threads.
# - Keep this module dependency-free (no requests), so it works in packaged apps.

DEFAULT_REPO = "Toby-top/add-doubao-watermark"
REPO_URL = "https://github.com/Toby-top/add-doubao-watermark"
API_URL = f"https://api.github.com/repos/{DEFAULT_REPO}/releases/latest"

_VERSION_PART_RE = re.compile(r"(\d+)")


def _parse_version_tuple(version: str) -> tuple[int, ...] | None:
    raw = (version or "").strip()
    if not raw:
        return None
    if raw.startswith(("v", "V")):
        raw = raw[1:]
    parts = []
    for seg in raw.split("."):
        m = _VERSION_PART_RE.search(seg)
        if not m:
            break
        parts.append(int(m.group(1)))
    return tuple(parts) if parts else None


def _is_newer(latest: str, current: str) -> bool:
    latest_t = _parse_version_tuple(latest)
    current_t = _parse_version_tuple(current)
    if latest_t is None or current_t is None:
        return (latest or "").strip() != (current or "").strip()
    n = max(len(latest_t), len(current_t))
    latest_t = latest_t + (0,) * (n - len(latest_t))
    current_t = current_t + (0,) * (n - len(current_t))
    return latest_t > current_t


def get_current_version(package_name: str = "add-doubao-watermark") -> str:
    try:
        return metadata.version(package_name)
    except Exception:
        # Fallback: allow running from source tree without installed dist metadata.
        try:
            from . import __version__  # type: ignore

            return str(__version__)
        except Exception:
            return "0.0.0"


def fetch_latest_release_tag(api_url: str = API_URL, timeout: float = 5.0) -> str | None:
    req = urllib.request.Request(
        api_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "add-doubao-watermark-update-checker",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tag = data.get("tag_name")
            return str(tag) if tag else None
    except urllib.error.HTTPError as e:
        # Common cases: 404 (no releases), 403 (rate limit).
        print(f"检查更新失败: HTTP {e.code}")
        return None
    except Exception as e:
        print(f"检查更新失败: {e}")
        return None


def check_for_updates(
    *,
    parent: Tk | None = None,
    current_version: str | None = None,
    api_url: str = API_URL,
    repo_url: str = REPO_URL,
    timeout: float = 5.0,
) -> bool:
    """Check for updates and optionally prompt to open the release page.

    Returns True if a newer version is available, else False.
    """
    current = (current_version or get_current_version()).strip()
    latest = fetch_latest_release_tag(api_url=api_url, timeout=timeout)
    if not latest:
        return False

    if not _is_newer(latest, current):
        return False

    user_decision = messagebox.askyesno(
        "发现新版本",
        f"当前版本: {current}\n最新版本: {latest}\n\n是否前往下载更新？",
        parent=parent,
    )
    if user_decision:
        webbrowser.open(f"{repo_url}/releases/latest")
    return True


def check_for_updates_async(
    root: Tk,
    *,
    current_version: str | None = None,
    api_url: str = API_URL,
    repo_url: str = REPO_URL,
    timeout: float = 5.0,
) -> None:
    """Run network check in a background thread and show Tk prompt on the UI thread."""

    current = (current_version or get_current_version()).strip()

    def worker() -> None:
        latest = fetch_latest_release_tag(api_url=api_url, timeout=timeout)
        if not latest or not _is_newer(latest, current):
            return

        def prompt() -> None:
            user_decision = messagebox.askyesno(
                "发现新版本",
                f"当前版本: {current}\n最新版本: {latest}\n\n是否前往下载更新？",
                parent=root,
            )
            if user_decision:
                webbrowser.open(f"{repo_url}/releases/latest")

        root.after(0, prompt)

    threading.Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    # For manual testing: python -m add_doubao_watermark.requirements
    check_for_updates(parent=None)
