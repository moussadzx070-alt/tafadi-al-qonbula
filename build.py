from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = ["bomb.svg", "icons/play.svg", "icons/settings.svg", "icons/maximize-2.svg", "icons/arrow-left.svg", "icons/check.svg"]


def main() -> int:
    missing = [p for p in REQUIRED if not (ROOT / "assets" / p).exists()]
    if missing:
        raise SystemExit("Assets missing: " + ", ".join(missing))
    for folder in (ROOT / "build", ROOT / "dist"):
        if folder.exists(): shutil.rmtree(folder)
    spec = ROOT / "tafadi-al-qonbula.spec"
    if spec.exists(): spec.unlink()
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--name", "تفادي القنبلة", "--add-data", f"assets{';' if sys.platform == 'win32' else ':'}assets", "main.py"]
    if (ROOT / "assets" / "app.ico").exists(): command[7:7] = ["--icon", str(ROOT / "assets" / "app.ico")]
    subprocess.run(command, cwd=ROOT, check=True)
    print("Build completed: dist/تفادي القنبلة.exe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
