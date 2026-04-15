# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pyinstaller_gui_entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/add_doubao_watermark/assets', 'add_doubao_watermark/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='doubao-watermark-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='doubao-watermark-gui',
)
app = BUNDLE(
    coll,
    name='doubao-watermark-gui.app',
    icon=None,
    bundle_identifier=None,
)
