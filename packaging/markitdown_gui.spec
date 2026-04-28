# PyInstaller spec for MarkItDown GUI.
#
# Build from the project root:
#     pyinstaller packaging/markitdown_gui.spec
#
# Output:
#   - Windows / Linux: dist/MarkItDownGUI/  (folder bundle, plus .exe)
#   - macOS:           dist/MarkItDown GUI.app
#
# `collect_all("markitdown")` pulls in the package's data files and submodules
# so its converter registry works in a frozen build. Optional format deps
# (pypdf, python-docx, etc.) are resolved by the same call when they ship as
# Python packages — if a particular format fails at runtime in the bundled
# build, add the missing package to EXTRA_HIDDEN_PACKAGES below.

import sys
from PyInstaller.utils.hooks import collect_all

EXTRA_HIDDEN_PACKAGES: list[str] = [
    # Add e.g. "pypdf", "docx", "pptx", "openpyxl" here if frozen build can't
    # find them despite being installed in the build venv.
]

datas, binaries, hiddenimports = [], [], []

for pkg in ["markitdown", *EXTRA_HIDDEN_PACKAGES]:
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    ["../src/markitdown_gui/__main__.py"],
    pathex=["../src"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MarkItDownGUI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MarkItDownGUI",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="MarkItDown GUI.app",
        icon=None,
        bundle_identifier="com.example.markitdowngui",
    )
