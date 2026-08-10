from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["bomb.svg", "icons/play.svg", "icons/settings.svg", "icons/maximize-2.svg", "icons/arrow-left.svg", "icons/check.svg"]

# قائمة المكتبات الضخمة التي لا تحتاجها اللعبة لتقليص الحجم
EXCLUDED_MODULES = [
    "PySide6.QtWebEngine", "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtNetwork", "PySide6.QtSql",
    "PySide6.QtTest", "PySide6.QtXml", "PySide6.QtBluetooth", "PySide6.QtDesigner",
    "PySide6.QtSensors", "PySide6.QtPrintSupport", "PySide6.QtOpenGL", "PySide6.QtQuickWidgets"
]

def main() -> int:
    # إجبار مخرج النصوص على استخدام UTF-8 لتفادي أخطاء الترميز في بيئات Windows
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    missing = [p for p in REQUIRED if not (ROOT / "assets" / p).exists()]
    if missing:
        print("تنبيه: بعض الأصول مفقودة، لكن سيستمر البناء.")
    
    for folder in (ROOT / "build", ROOT / "dist"):
        if folder.exists(): 
            shutil.rmtree(folder)
            
    spec = ROOT / "tafadi-al-qonbula.spec"
    if spec.exists(): 
        spec.unlink()
        
    command = [
        sys.executable, "-m", "PyInstaller", 
        "--noconfirm", "--clean", "--windowed", 
        "--name", "تفادي القنبلة", 
        "--add-data", f"assets{';' if sys.platform == 'win32' else ':'}assets"
    ]
    
    # إضافة الاستبعادات لأمر البناء
    for mod in EXCLUDED_MODULES:
        command.extend(["--exclude-module", mod])
        
    if (ROOT / "assets" / "app.ico").exists(): 
        command.extend(["--icon", str(ROOT / "assets" / "app.ico")])
        
    command.append("main.py")
    
    subprocess.run(command, cwd=ROOT, check=True)
    
    # رسالة نجاح آمنة لتفادي أخطاء الترميز في شاشات الكونسول الأجنبية
    try:
        print("Build completed: dist/تفادي القنبلة.exe")
    except UnicodeEncodeError:
        print("Build completed successfully! Executable generated in 'dist' folder.")
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
