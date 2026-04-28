# MarkItDown GUI

A desktop GUI for Microsoft's [`markitdown`](https://github.com/microsoft/markitdown) — convert PDF, Office documents, HTML, and more into Markdown. Drag files in, hit Convert, get `.md` next to the source (or in a folder of your choice).

Built with **Python 3.10+** and **PySide6 (Qt 6)**. Packaged with **PyInstaller**; the Windows installer is built with **Inno Setup**.

## Run from source

```bash
python -m venv .venv
source .venv/bin/activate            # macOS / Linux
.venv\Scripts\activate                # Windows (cmd / PowerShell)

pip install -e .
python -m markitdown_gui
```

By default the install pulls doc-focused `markitdown` extras (PDF, DOCX, PPTX, XLSX, XLS, Outlook MSG). To also handle audio transcription, YouTube, and OCR, edit `pyproject.toml` and replace the `markitdown[...]` line with `markitdown[all]` — note that this pulls multi-GB ML dependencies (PyTorch).

## Build a Windows .exe and installer

From a Windows machine, in your activated venv:

```powershell
pip install pyinstaller
pyinstaller packaging\markitdown_gui.spec
```

This produces `dist\MarkItDownGUI\MarkItDownGUI.exe` plus its support files. To wrap it in an installer:

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Open `packaging\installer.iss` in the Inno Setup IDE and click **Build → Compile**, or run `iscc packaging\installer.iss`.
3. The signed-ready installer lands in `dist\installer\`.

Update `MyAppPublisher` and the `AppId` GUID in `installer.iss` before shipping.

## Build a macOS .app and .dmg

```bash
pip install pyinstaller
pyinstaller packaging/markitdown_gui.spec
# Result: dist/MarkItDown GUI.app

hdiutil create -volname "MarkItDown GUI" \
  -srcfolder "dist/MarkItDown GUI.app" \
  -ov -format UDZO \
  "dist/MarkItDownGUI-0.1.0.dmg"
```

For distribution outside the Mac App Store you'll need to codesign and notarize the `.app` with an Apple Developer ID certificate.

## Project layout

```
src/markitdown_gui/
  app.py           entry point; QApplication + MainWindow
  main_window.py   Qt UI: file list, drag-and-drop, output picker, progress
  worker.py        QRunnable that calls markitdown off the UI thread
packaging/
  markitdown_gui.spec   PyInstaller config
  installer.iss         Inno Setup script
```
