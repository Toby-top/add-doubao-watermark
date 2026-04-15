from __future__ import annotations

from add_doubao_watermark.win_dpi import enable_windows_dpi_awareness

enable_windows_dpi_awareness()

from add_doubao_watermark.gui import main

if __name__ == "__main__":
    raise SystemExit(main())
