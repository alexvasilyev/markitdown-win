import sys

from PySide6.QtWidgets import QApplication

from markitdown_gui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("MarkItDown GUI")
    app.setOrganizationName("MarkItDown GUI")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
