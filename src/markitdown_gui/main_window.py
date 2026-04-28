from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThreadPool
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from markitdown_gui.worker import ConversionResult, ConvertJob


class FileListWidget(QListWidget):
    """List widget that accepts dropped files."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QListWidget.ExtendedSelection)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        existing = {self.item(i).text() for i in range(self.count())}
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if local and local not in existing:
                self.addItem(local)
                existing.add(local)

    def all_paths(self) -> list[str]:
        return [self.item(i).text().split("  ", 1)[0] for i in range(self.count())]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MarkItDown GUI")
        self.resize(720, 480)

        self._thread_pool = QThreadPool.globalInstance()
        self._current_job: Optional[ConvertJob] = None
        self._output_dir: Optional[Path] = None

        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        instructions = QLabel(
            "Drop files here, or use 'Add files…'. "
            "Supported: PDF, DOCX, PPTX, XLSX, HTML, and more."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        self.file_list = FileListWidget()
        layout.addWidget(self.file_list, stretch=1)

        file_btns = QHBoxLayout()
        self.add_btn = QPushButton("Add files…")
        self.add_btn.clicked.connect(self._on_add_files)
        self.remove_btn = QPushButton("Remove selected")
        self.remove_btn.clicked.connect(self._on_remove_selected)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.file_list.clear)
        file_btns.addWidget(self.add_btn)
        file_btns.addWidget(self.remove_btn)
        file_btns.addWidget(self.clear_btn)
        file_btns.addStretch()
        layout.addLayout(file_btns)

        out_row = QHBoxLayout()
        self.same_dir_check = QCheckBox("Save next to source files")
        self.same_dir_check.setChecked(True)
        self.same_dir_check.toggled.connect(self._on_same_dir_toggled)
        self.choose_out_btn = QPushButton("Choose output folder…")
        self.choose_out_btn.clicked.connect(self._on_choose_output)
        self.choose_out_btn.setEnabled(False)
        self.out_label = QLabel("(beside source)")
        out_row.addWidget(self.same_dir_check)
        out_row.addWidget(self.choose_out_btn)
        out_row.addWidget(self.out_label, stretch=1)
        layout.addLayout(out_row)

        bottom = QHBoxLayout()
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.convert_btn = QPushButton("Convert")
        self.convert_btn.clicked.connect(self._on_convert)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setEnabled(False)
        bottom.addWidget(self.progress, stretch=1)
        bottom.addWidget(self.convert_btn)
        bottom.addWidget(self.cancel_btn)
        layout.addLayout(bottom)

        self.setCentralWidget(central)
        self.setStatusBar(QStatusBar())

    # ------------------------------------------------------------- Handlers

    def _on_add_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select files", "", "All files (*.*)"
        )
        existing = set(self.file_list.all_paths())
        for f in files:
            if f and f not in existing:
                self.file_list.addItem(f)
                existing.add(f)

    def _on_remove_selected(self) -> None:
        for item in self.file_list.selectedItems():
            self.file_list.takeItem(self.file_list.row(item))

    def _on_same_dir_toggled(self, checked: bool) -> None:
        self.choose_out_btn.setEnabled(not checked)
        if checked:
            self._output_dir = None
            self.out_label.setText("(beside source)")

    def _on_choose_output(self) -> None:
        d = QFileDialog.getExistingDirectory(self, "Choose output folder")
        if d:
            self._output_dir = Path(d)
            self.out_label.setText(d)

    def _on_convert(self) -> None:
        paths = [Path(p) for p in self.file_list.all_paths()]
        if not paths:
            QMessageBox.information(self, "No files", "Add files first.")
            return

        self._set_running(True)
        self.progress.setRange(0, len(paths))
        self.progress.setValue(0)

        job = ConvertJob(paths, self._output_dir)
        job.signals.progress.connect(self._on_progress)
        job.signals.finished_one.connect(self._on_one_done)
        job.signals.all_finished.connect(self._on_all_done)
        self._current_job = job
        self._thread_pool.start(job)

    def _on_cancel(self) -> None:
        if self._current_job is not None:
            self._current_job.cancel()
            self.statusBar().showMessage("Cancelling…")

    def _on_progress(self, current: int, total: int, source: str) -> None:
        self.statusBar().showMessage(f"[{current}/{total}] {source}")

    def _on_one_done(self, result: ConversionResult) -> None:
        self.progress.setValue(self.progress.value() + 1)
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            base = item.text().split("  ", 1)[0]
            if base == str(result.source):
                if result.error:
                    item.setText(f"{base}  [ERROR: {result.error}]")
                else:
                    item.setText(f"{base}  [OK -> {result.output.name}]")
                break

    def _on_all_done(self) -> None:
        self._set_running(False)
        self._current_job = None
        self.statusBar().showMessage("Done.", 5000)

    def _set_running(self, running: bool) -> None:
        self.convert_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
        self.add_btn.setEnabled(not running)
        self.remove_btn.setEnabled(not running)
        self.clear_btn.setEnabled(not running)
        self.progress.setVisible(running)
