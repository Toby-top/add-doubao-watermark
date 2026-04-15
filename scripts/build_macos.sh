#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYINSTALLER_CONFIG_DIR="${ROOT}/.pyinstaller"
mkdir -p "${PYINSTALLER_CONFIG_DIR}"

rm -rf build dist
pyinstaller -F pyinstaller_entry.py -n doubao-watermark --clean --paths src --add-data "src/add_doubao_watermark/assets:add_doubao_watermark/assets"
pyinstaller pyinstaller_gui_entry.py -n doubao-watermark-gui --clean --paths src --add-data "src/add_doubao_watermark/assets:add_doubao_watermark/assets" -w

ARCH="$(uname -m)"
VERSION="$(PYTHONPATH=src python3 -c "import add_doubao_watermark as p; print(p.__version__)")"
OUT="dist/doubao-watermark-${VERSION}-macos-${ARCH}.zip"

(cd dist && /usr/bin/zip -r "../${OUT}" "doubao-watermark" "doubao-watermark-gui.app" >/dev/null)
echo "Built: ${OUT}"
