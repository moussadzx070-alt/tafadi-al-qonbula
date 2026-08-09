from __future__ import annotations

import logging
import sys
import os

# فرض استخدام Software Rendering للأجهزة التي لا تملك تعريفات رسومية
os.environ["QT_OPENGL"] = "software"
os.environ["QT_QUICK_BACKEND"] = "software"
os.environ["QT_QPA_PLATFORM"] = "windows" # ضمان استقرار العرض على أنظمة ويندوز القديمة

from PySide6.QtCore import QLocale, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from ui import MainWindow, STYLE

def main() -> int:
    logging.basicConfig(filename="tafadi.log", level=logging.INFO, encoding="utf-8")
    app = QApplication(sys.argv)
    
    # تحسين التوافق مع الشاشات المتنوعة
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
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
    QMessageBox.critical(None, "خطأ غير متوقع", f"حدث خطأ غير متوقع:\n{exc_value}\n\nراجع ملف tafadi.log للتفاصيل.")

if __name__ == "__main__":
    sys.excepthook = excepthook
    sys.exit(main())
