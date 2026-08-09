from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

from PySide6.QtGui import QIcon, QPixmap


class Assets:
    """Centralized, cached resource access for source runs and PyInstaller bundles."""

    _pixmaps: Dict[str, QPixmap] = {}
    _icons: Dict[str, QIcon] = {}

    @staticmethod
    def root() -> Path:
        if getattr(sys, "frozen", False):
            return Path(sys._MEIPASS) / "assets"
        return Path(__file__).resolve().parent / "assets"

    @classmethod
    def path(cls, relative: str) -> Path:
        return cls.root() / relative

    @classmethod
    def pixmap(cls, relative: str, width: int = 0, height: int = 0) -> QPixmap:
        key = f"{relative}:{width}:{height}"
        if key not in cls._pixmaps:
            pixmap = QPixmap(str(cls.path(relative)))
            if width or height:
                pixmap = pixmap.scaled(width or pixmap.width(), height or pixmap.height())
            cls._pixmaps[key] = pixmap
        return cls._pixmaps[key]

    @classmethod
    def icon(cls, relative: str) -> QIcon:
        if relative not in cls._icons:
            cls._icons[relative] = QIcon(str(cls.path(relative)))
        return cls._icons[relative]

    @classmethod
    def sound_path(cls, name: str) -> Path:
        return cls.path(f"sounds/{name}.wav")
