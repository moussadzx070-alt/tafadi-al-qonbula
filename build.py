from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

REQUIRED = [
    "bomb.svg",
    "icons/play.svg",
    "icons/settings.svg",
    "icons/maximize-2.svg",
    "icons/arrow-left.svg",
    "icons/check.svg",
]


def main() -> int:
    # التحقق من وجود الملفات المطلوبة
    missing = [
        path for path in REQUIRED
        if not (ROOT / "assets" / path).exists()
    ]

    if missing:
        raise SystemExit(
            "Assets missing: " + ", ".join(missing)
        )

    # حذف مجلدات البناء القديمة
    for folder in (ROOT / "build", ROOT / "dist"):
        if folder.exists():
            shutil.rmtree(folder)

    # حذف ملف spec القديم
    spec = ROOT / "tafadi-al-qonbula.spec"
    if spec.exists():
        spec.unlink()

    # إعداد مسار assets حسب نظام التشغيل
    separator = ";" if sys.platform == "win32" else ":"
    add_data = f"assets{separator}assets"

    # أمر PyInstaller
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "tafadi-al-qonbula",
        "--add-data",
        add_data,
    ]

    # إضافة الأيقونة إذا كانت موجودة
    icon = ROOT / "assets" / "app.ico"

    if icon.exists():
        command.extend([
            "--icon",
            str(icon),
        ])

    # الملف الرئيسي
    command.append("main.py")

    print("Building Windows executable...")
    print("Command:")
    print(" ".join(f'"{arg}"' if " " in arg else arg for arg in command))

    # تنفيذ PyInstaller
    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )

    exe = ROOT / "dist" / "tafadi-al-qonbula.exe"

    if not exe.exists():
        raise SystemExit(
            "Build failed: EXE file was not created."
        )

    print()
    print("=" * 50)
    print("Build completed successfully!")
    print(f"EXE: {exe}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
