from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

REQUIRED_ASSETS = [
    "bomb.svg",
    "icons/play.svg",
    "icons/settings.svg",
    "icons/arrow-left.svg",
    "icons/check.svg",
]


def check_assets() -> None:
    missing = []

    for relative in REQUIRED_ASSETS:
        path = ASSETS / relative
        if not path.exists():
            missing.append(relative)

    if missing:
        print("ERROR: Missing assets:")
        for item in missing:
            print(f"  - {item}")
        raise SystemExit(1)


def clean_build() -> None:
    for folder in (
        ROOT / "build",
        ROOT / "dist",
    ):
        if folder.exists():
            print(f"Removing: {folder}")
            shutil.rmtree(folder)

    spec = ROOT / "tafadi-al-qonbula.spec"
    if spec.exists():
        print(f"Removing: {spec}")
        spec.unlink()


def build() -> int:
    print("Checking assets...")
    check_assets()

    print("Cleaning old build...")
    clean_build()

    print("Building Windows executable...")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",

        "--noconfirm",
        "--clean",

        # IMPORTANT:
        # Create ONE standalone EXE.
        "--onefile",

        # No console window.
        "--windowed",

        # Safe ASCII internal executable name.
        "--name",
        "tafadi-al-qonbula",

        # Include all assets.
        "--add-data",
        f"{ASSETS}{';'}assets",
    ]

    # Add icon only if app.ico exists.
    app_icon = ASSETS / "app.ico"

    if app_icon.exists():
        command.extend([
            "--icon",
            str(app_icon),
        ])

    # PySide6 imports Qt modules dynamically.
    # These options make the bundle more robust.
    command.extend([
        "--collect-all",
        "PySide6",

        "--collect-all",
        "shiboken6",

        "main.py",
    ])

    print("Command:")
    print(" ".join(f'"{x}"' if " " in x else x for x in command))
    print()

    try:
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        print()
        print(f"Build failed with exit code {exc.returncode}.")
        return exc.returncode

    # PyInstaller --onefile creates exactly this file.
    exe = ROOT / "dist" / "tafadi-al-qonbula.exe"

    if not exe.exists():
        print()
        print("ERROR: EXE file was not created.")
        print(f"Expected: {exe}")
        return 1

    print()
    print("=" * 60)
    print("BUILD SUCCESSFUL")
    print("=" * 60)
    print(f"EXE: {exe}")
    print(f"Size: {exe.stat().st_size / (1024 * 1024):.2f} MB")
    print()
    print("The executable is standalone.")
    print("You can copy this EXE to another Windows computer.")
    print("=" * 60)

    return 0


def main() -> int:
    return build()


if __name__ == "__main__":
    raise SystemExit(main())
