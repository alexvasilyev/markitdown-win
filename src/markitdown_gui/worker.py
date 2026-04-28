from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRunnable, Signal, Slot


@dataclass
class ConversionResult:
    source: Path
    output: Optional[Path]
    error: Optional[str]


class WorkerSignals(QObject):
    progress = Signal(int, int, str)        # current_index, total, source_path
    finished_one = Signal(object)           # ConversionResult
    all_finished = Signal()


class ConvertJob(QRunnable):
    """Run markitdown over a list of source files. One MarkItDown instance is
    reused across files so converter setup cost is paid once."""

    def __init__(self, sources: list[Path], output_dir: Optional[Path]):
        super().__init__()
        self.sources = sources
        self.output_dir = output_dir
        self.signals = WorkerSignals()
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @Slot()
    def run(self) -> None:
        # Import lazily so the UI starts even if markitdown's optional deps
        # are not yet installed.
        from markitdown import MarkItDown

        md = MarkItDown()
        total = len(self.sources)
        for idx, source in enumerate(self.sources, 1):
            if self._cancelled:
                break
            self.signals.progress.emit(idx, total, str(source))
            result = self._convert_one(md, source)
            self.signals.finished_one.emit(result)
        self.signals.all_finished.emit()

    def _convert_one(self, md, source: Path) -> ConversionResult:
        try:
            converted = md.convert(str(source))
            out_dir = self.output_dir or source.parent
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = out_dir / (source.stem + ".md")
            output_path.write_text(converted.text_content, encoding="utf-8")
            return ConversionResult(source=source, output=output_path, error=None)
        except Exception as exc:
            return ConversionResult(source=source, output=None, error=str(exc))
