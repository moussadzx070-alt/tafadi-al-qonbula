from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtCore import QLocale, Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QMessageBox

from assets import Assets
from ui import MainWindow, STYLE


def main() -> int:
    logging.basicConfig(filename="tafadi.log", level=logging.INFO, encoding="utf-8")
    app = QApplication(sys.argv)
    app.setApplicationName("تفادي القنبلة")
    app.setOrganizationName("Tafadi Al-Qonbula")
    app.setLayoutDirection(Qt.RightToLeft)
    app.setLocale(QLocale(QLocale.Arabic, QLocale.SaudiArabia))
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


def excepthook(exc_type, exc_value, exc_tb):
    logging.error("Unhandled error", exc_info=(exc_type, exc_value, exc_tb))
    QMessageBox.critical(None, "خطأ غير متوقع", "حدث خطأ غير متوقع. راجع ملف tafadi.log للتفاصيل.")


if __name__ == "__main__":
    sys.excepthook = excepthook
    sys.exit(main())
