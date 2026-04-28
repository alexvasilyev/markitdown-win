# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A desktop GUI wrapper around Microsoft's [`markitdown`](https://github.com/microsoft/markitdown) Python library. The user-facing artefact is a Windows installer (Inno Setup) and/or a macOS `.app`/`.dmg`. Python + PySide6 was chosen over alternatives (Electron + Python sidecar, Tauri + sidecar, native C++/Qt) so the conversion library and the UI run in one process with no IPC.

## Common commands

Dev loop (run from project root in an activated venv):

```bash
pip install -e .
python -m markitdown_gui
```

Build a frozen bundle (Windows or macOS, run on the matching OS):

```bash
pip install pyinstaller
pyinstaller packaging/markitdown_gui.spec
# Windows -> dist/MarkItDownGUI/MarkItDownGUI.exe
# macOS   -> dist/MarkItDown GUI.app
```

Build the Windows installer (after the PyInstaller step):

```powershell
iscc packaging\installer.iss
# -> dist\installer\MarkItDownGUI-Setup-<ver>.exe
```

There is no test suite and no linter wired up yet.

## Architecture

Three files do the work; everything else is config or packaging.

- `src/markitdown_gui/app.py` — creates `QApplication`, instantiates `MainWindow`, runs the event loop.
- `src/markitdown_gui/main_window.py` — all UI: file list with drag-and-drop, file/output pickers, progress bar, status bar. Owns a `QThreadPool` and dispatches a `ConvertJob` per Convert click.
- `src/markitdown_gui/worker.py` — `ConvertJob(QRunnable)` runs on the thread pool. It instantiates **one** `MarkItDown()` and reuses it across all files in the batch (converter setup is non-trivial). It emits three Qt signals: `progress(current, total, source)`, `finished_one(ConversionResult)`, and `all_finished()`.

Threading rule: the worker never touches Qt widgets directly. It only emits signals. The main window's slots, running on the UI thread, mutate widgets. Keep it that way — Qt widgets are not thread-safe.

The UI list shows each path; once a file finishes, its row is rewritten in place to `<path>  [OK -> name.md]` or `<path>  [ERROR: ...]`. `FileListWidget.all_paths()` strips that suffix when collecting paths for a new run.

## Packaging notes that matter

`markitdown` discovers converters at import time and lazy-imports format-specific deps (`pypdf`, `python-docx`, `python-pptx`, `openpyxl`, …) inside try/except. PyInstaller's static analysis can't see those, which breaks the frozen build for some formats. The spec file calls `collect_all("markitdown")` to grab its data files and submodules; if a specific format works in `pip install -e .` but fails in the bundled `.exe` with an `ImportError`, add the missing top-level package to `EXTRA_HIDDEN_PACKAGES` in `packaging/markitdown_gui.spec`.

The default install in `pyproject.toml` uses `markitdown[pdf,docx,pptx,xlsx,xls,outlook]`. The `[all]` extra also enables audio transcription, YouTube, and OCR but pulls multi-GB ML deps (PyTorch). Don't switch to `[all]` casually — bundle size and build time both balloon.

`installer.iss` has placeholder values (`AppId` GUID, `MyAppPublisher`) that must be updated before any real release.
