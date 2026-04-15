from __future__ import annotations

import sys


def enable_windows_dpi_awareness() -> None:
    """
    Make the process DPI-aware on Windows to avoid blurry UI under high-DPI scaling.

    Must be called before creating any Tk windows.
    """
    if sys.platform != "win32":
        return

    try:
        import ctypes
    except Exception:
        return

    # Prefer Per-Monitor v2 when available (Windows 10+).
    try:
        set_ctx = ctypes.windll.user32.SetProcessDpiAwarenessContext
        # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = (HANDLE)-4
        if set_ctx(ctypes.c_void_p(-4)):
            return
    except Exception:
        pass

    # Fallback: Per-monitor (Windows 8.1+).
    try:
        set_awareness = ctypes.windll.shcore.SetProcessDpiAwareness
        # PROCESS_PER_MONITOR_DPI_AWARE = 2
        set_awareness(2)
        return
    except Exception:
        pass

    # Fallback: System DPI aware (Vista+).
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

