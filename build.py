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
    # التحقق من ملفات assets المطلوبة
    missing = [
        path
        for path in REQUIRED
        if not (ROOT / "assets" / path).exists()
    ]

    if missing:
        raise SystemExit(
            "Assets missing: " + ", ".join(missing)
        )

    # حذف نتائج البناء السابقة
    for folder in (ROOT / "build", ROOT / "dist"):
        if folder.exists():
            shutil.rmtree(folder)

    # حذف ملف spec السابق
    spec = ROOT / "tafadi-al-qonbula.spec"
    if spec.exists():
        spec.unlink()

    # إعداد assets
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
        "--onefile",
        "--name",
        "tafadi-al-qonbula",
        "--add-data",
        add_data,
    ]

    # إضافة الأيقونة
    icon = ROOT / "assets" / "app.ico"

    if icon.exists():
        command.extend([
            "--icon",
            str(icon),
        ])

    # الملف الرئيسي
    command.append("main.py")

    print("Building Windows EXE...")
    print()

    subprocess.run(
        command,
        cwd=ROOT,
        check=True,
    )

    # الملف النهائي المتوقع
    exe = ROOT / "dist" / "tafadi-al-qonbula.exe"

    if not exe.exists():
        raise SystemExit(
            f"Build completed but EXE was not found: {exe}"
        )

    print()
    print("=" * 60)
    print("BUILD SUCCESSFUL")
    print("=" * 60)
    print(f"EXE: {exe}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
