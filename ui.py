from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame,
    QGraphicsOpacityEffect, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QScrollArea, QSizePolicy, QSlider, QSpinBox,
    QStackedWidget, QVBoxLayout, QWidget,
)

from assets import Assets
from game import Decision, GameEngine, GameState, Player


STYLE = """
QWidget { color:#F6F7FB; font-family:'Segoe UI','Tahoma'; font-size:14px; }
QMainWindow, QDialog { background:#080D18; }
QFrame#panel { background:#111A2A; border:1px solid #26354E; border-radius:18px; }
QFrame#card { background:#172238; border:1px solid #2B3D5B; border-radius:16px; }
QFrame#card[dead="true"] { background:#101522; border-color:#242B38; }
QLabel#title { font-size:44px; font-weight:800; color:#FFFFFF; }
QLabel#subtitle { font-size:18px; color:#AAB6CB; }
QLabel#section { font-size:20px; font-weight:700; color:#FFFFFF; }
QLabel#muted { color:#96A4BB; }
QPushButton { background:#202E47; border:1px solid #344A6C; border-radius:11px; padding:12px 18px; color:#FFF; font-weight:600; }
QPushButton:hover { background:#2A3D5D; border-color:#D8A84E; }
QPushButton:pressed { background:#172238; }
QPushButton#primary { background:#B52D3C; border-color:#E0535F; font-size:16px; padding:15px 25px; }
QPushButton#primary:hover { background:#D13A4A; }
QPushButton#danger { background:#7D1F2B; border-color:#D34755; }
QComboBox, QSpinBox { background:#0E1727; border:1px solid #344A6C; border-radius:9px; padding:10px; }
QScrollArea { border:0; background:transparent; }
QSlider::groove:horizontal { height:5px; background:#26354E; }
QSlider::handle:horizontal { width:16px; margin:-6px 0; border-radius:8px; background:#D8A84E; }
"""


def icon(name: str) -> QIcon:
    return Assets.icon(f"icons/{name}.svg")


class AudioSystem:
    def __init__(self):
        self.enabled = True
        self.effects = True

    def play(self, name: str) -> None:
        if not (self.enabled and self.effects):
            return
        path = Assets.sound_path(name)
        if path.exists():
            from PySide6.QtMultimedia import QSoundEffect
            effect = QSoundEffect()
            effect.setSource(path.as_uri())
            effect.setVolume(0.35)
            effect.play()


class PlayerCard(QFrame):
    def __init__(self, player: Player):
        super().__init__()
        self.setObjectName("card")
        self.setProperty("dead", "true" if not player.alive else "false")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 14, 15, 14)
        badge = QLabel(str(player.player_id + 1).zfill(2))
        badge.setStyleSheet("color:#D8A84E;font-size:22px;font-weight:800;")
        name = QLabel(player.name)
        name.setStyleSheet("font-weight:700;font-size:16px;")
        status = QLabel("حي" if player.alive else "مستبعد")
        status.setObjectName("muted")
        layout.addWidget(badge, alignment=Qt.AlignRight)
        layout.addWidget(name, alignment=Qt.AlignRight)
        layout.addWidget(status, alignment=Qt.AlignRight)


class StartScreen(QWidget):
    start_requested = Signal()
    settings_requested = Signal()
    about_requested = Signal()

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.addStretch()
        panel = QFrame(); panel.setObjectName("panel")
        box = QVBoxLayout(panel); box.setContentsMargins(45, 45, 45, 45); box.setSpacing(18)
        emblem = QLabel(); emblem.setPixmap(Assets.pixmap("bomb.svg", 112, 112)); emblem.setAlignment(Qt.AlignCenter)
        title = QLabel("تفادي القنبلة"); title.setObjectName("title"); title.setAlignment(Qt.AlignCenter)
        sub = QLabel("لعبة جماعية تعتمد على الذكاء والحظ"); sub.setObjectName("subtitle"); sub.setAlignment(Qt.AlignCenter)
        box.addWidget(emblem); box.addWidget(title); box.addWidget(sub); box.addSpacing(12)
        play = QPushButton(icon("play"), "ابدأ اللعبة"); play.setObjectName("primary"); play.clicked.connect(self.start_requested.emit)
        settings = QPushButton(icon("settings"), "الإعدادات"); settings.clicked.connect(self.settings_requested.emit)
        about = QPushButton("حول اللعبة"); about.clicked.connect(self.about_requested.emit)
        for b in (play, settings, about): box.addWidget(b)
        root.addWidget(panel, alignment=Qt.AlignCenter); root.addStretch()


class SetupScreen(QWidget):
    started = Signal(list)
    back_requested = Signal()

    def __init__(self):
        super().__init__(); self.inputs = []
        root = QVBoxLayout(self); root.setContentsMargins(32, 28, 32, 28)
        head = QHBoxLayout(); back = QPushButton(icon("arrow-left"), "رجوع"); back.clicked.connect(self.back_requested.emit)
        head.addWidget(back); head.addStretch(); title = QLabel("إعداد اللاعبين"); title.setObjectName("title"); head.addWidget(title); root.addLayout(head)
        form = QFrame(); form.setObjectName("panel"); fl = QVBoxLayout(form)
        row = QHBoxLayout(); row.addWidget(QLabel("عدد اللاعبين")); self.count = QSpinBox(); self.count.setRange(2, 24); self.count.setValue(4); self.count.valueChanged.connect(self._refresh); row.addWidget(self.count); row.addStretch(); fl.addLayout(row)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.names = QWidget(); self.grid = QGridLayout(self.names); self.scroll.setWidget(self.names); fl.addWidget(self.scroll)
        start = QPushButton(icon("play"), "ابدأ الدورة الأولى"); start.setObjectName("primary"); start.clicked.connect(self._submit); fl.addWidget(start)
        root.addWidget(form); self._refresh(4)

    def _refresh(self, count: int):
        while self.grid.count(): self.grid.takeAt(0).widget().deleteLater()
        self.inputs = []
        for i in range(count):
            label = QLabel(f"اللاعب {i+1}"); edit = QLineEdit(f"لاعب {i+1}"); edit.setPlaceholderText("اكتب اسم اللاعب")
            self.inputs.append(edit); self.grid.addWidget(label, i, 0); self.grid.addWidget(edit, i, 1)

    def _submit(self):
        names = [e.text().strip() for e in self.inputs]
        if any(not n for n in names): QMessageBox.warning(self, "بيانات ناقصة", "يرجى إدخال أسماء جميع اللاعبين."); return
        self.started.emit(names)


class GameScreen(QWidget):
    finished = Signal()
    home_requested = Signal()

    def __init__(self, engine: GameEngine, audio: AudioSystem):
        super().__init__(); self.engine = engine; self.audio = audio; self.current_player = 0; self.cards = []
        root = QVBoxLayout(self); root.setContentsMargins(24, 20, 24, 20); root.setSpacing(12)
        top = QHBoxLayout(); home = QPushButton(icon("arrow-left"), "الرئيسية"); home.clicked.connect(self.home_requested.emit); top.addWidget(home); top.addStretch()
        self.cycle_label = QLabel(); self.cycle_label.setObjectName("section"); top.addWidget(self.cycle_label); top.addStretch(); self.progress = QLabel(); top.addWidget(self.progress); root.addLayout(top)
        self.bomb_label = QLabel("موقع القنبلة مخفي"); self.bomb_label.setObjectName("muted"); self.bomb_label.setAlignment(Qt.AlignCenter); root.addWidget(self.bomb_label)
        self.grid = QGridLayout(); root.addLayout(self.grid, 1)
        self.action_panel = QFrame(); self.action_panel.setObjectName("panel"); self.actions = QHBoxLayout(self.action_panel); root.addWidget(self.action_panel)
        self.status = QLabel(); self.status.setObjectName("muted"); self.status.setAlignment(Qt.AlignCenter); root.addWidget(self.status)
        self._render()

    def _render(self):
        self.cycle_label.setText(f"الدورة {self.engine.cycle}  |  الجولة {min(self.engine.round_number, 3)} / 3")
        self.progress.setText(f"{sum(p.decision is not None for p in self.engine.alive_players)} / {self.engine.alive_count}")
        while self.grid.count(): self.grid.takeAt(0).widget().deleteLater()
        for i, p in enumerate(self.engine.players.values()):
            card = PlayerCard(p); self.grid.addWidget(card, i // 6, i % 6)
        while self.actions.count(): self.actions.takeAt(0).widget().deleteLater()
        if self.engine.state in {GameState.ROUND_1, GameState.ROUND_2, GameState.ROUND_3}:
            active = next((p for p in self.engine.alive_players if p.decision is None), None)
            if active:
                self.status.setText(f"دور الاختيار: {active.name} — القرار مخفي عن المشاهد")
                for text, decision in (("البقاء في مكاني", Decision.STAY), ("العودة إلى مكاني الأصلي", Decision.HOME)):
                    b = QPushButton(text); b.clicked.connect(lambda _, d=decision, pid=active.player_id: self._choose(pid, d)); self.actions.addWidget(b)
                move = QPushButton("أخذ مكان لاعب حي آخر"); move.clicked.connect(lambda: self._choose_target(active)); self.actions.addWidget(move)
            if self.engine.all_decisions_submitted(): self._add_commit()
        elif self.engine.state == GameState.READY_TO_REVEAL:
            self.status.setText("اكتملت الاختيارات. المشرف وحده يكشف القنبلة.")
            reveal = QPushButton("إظهار القنبلة"); reveal.setObjectName("danger"); reveal.clicked.connect(self._reveal); self.actions.addWidget(reveal)

    def _choose(self, pid, decision):
        self.engine.submit_decision(pid, decision); self.audio.play("decision"); self._render()

    def _choose_target(self, active):
        dialog = QDialog(self); dialog.setWindowTitle("اختر لاعبًا حيًا"); layout = QVBoxLayout(dialog); combo = QComboBox()
        for p in self.engine.alive_players:
            if p.player_id != active.player_id: combo.addItem(p.name, p.player_id)
        layout.addWidget(combo); buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec(): self._choose(active.player_id, Decision.MOVE_TO_PLAYER) if False else (self.engine.submit_decision(active.player_id, Decision.MOVE_TO_PLAYER, combo.currentData()), self.audio.play("decision"), self._render())

    def _add_commit(self):
        commit = QPushButton("تثبيت الجولة"); commit.setObjectName("primary"); commit.clicked.connect(lambda: (self.engine.commit_round(), self.audio.play("round"), self._render())); self.actions.addWidget(commit)

    def _reveal(self):
        self.setEnabled(False); self.bomb_label.setText("جاري كشف موقع القنبلة...")
        effect = QGraphicsOpacityEffect(self.bomb_label); self.bomb_label.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self); anim.setDuration(900); anim.setStartValue(0.15); anim.setEndValue(1.0); anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.finished.connect(self._finish_reveal); anim.start(); self._anim = anim

    def _finish_reveal(self):
        victim = self.engine.reveal_bomb(); self.bomb_label.setText(f"القنبلة كانت في المكان {self.engine.bomb_slot}")
        if victim: QMessageBox.warning(self, "انفجار", f"خرج اللاعب: {victim.name}")
        if self.engine.alive_count <= 1:
            winner = self.engine.get_winner(); self.setEnabled(True); QMessageBox.information(self, "الفائز", winner.name if winner else "لا يوجد فائز"); self.finished.emit(); return
        self.engine.start_next_cycle(); self.setEnabled(True); self._render()


class SettingsDialog(QDialog):
    def __init__(self, audio: AudioSystem, parent=None):
        super().__init__(parent); self.setWindowTitle("الإعدادات"); self.audio = audio
        layout = QFormLayout(self); self.sound = QComboBox(); self.sound.addItems(["مفعّل", "متوقف"]); self.sound.setCurrentIndex(0 if audio.enabled else 1)
        self.effects = QComboBox(); self.effects.addItems(["مفعّلة", "متوقفة"]); self.effects.setCurrentIndex(0 if audio.effects else 1)
        layout.addRow("الصوت", self.sound); layout.addRow("المؤثرات", self.effects)
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel); buttons.accepted.connect(self._save); buttons.rejected.connect(self.reject); layout.addRow(buttons)
    def _save(self): self.audio.enabled = self.sound.currentIndex() == 0; self.audio.effects = self.effects.currentIndex() == 0; self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("تفادي القنبلة"); self.setWindowIcon(icon("bomb")); self.setMinimumSize(900, 620); self.audio = AudioSystem(); self.stack = QStackedWidget(); self.setCentralWidget(self.stack)
        self.start = StartScreen(); self.setup = SetupScreen(); self.stack.addWidget(self.start); self.stack.addWidget(self.setup)
        self.start.start_requested.connect(lambda: self.stack.setCurrentWidget(self.setup)); self.start.settings_requested.connect(self._settings); self.start.about_requested.connect(self._about); self.setup.back_requested.connect(lambda: self.stack.setCurrentWidget(self.start)); self.setup.started.connect(self._start_game)
    def _settings(self): SettingsDialog(self.audio, self).exec()
    def _about(self): QMessageBox.information(self, "حول اللعبة", "تفادي القنبلة\nلعبة جماعية عربية تعمل بالكامل دون اتصال بالإنترنت.")
    def _start_game(self, names):
        self.engine = GameEngine(names); self.engine.start_game(); self.game = GameScreen(self.engine, self.audio); self.stack.addWidget(self.game); self.stack.setCurrentWidget(self.game); self.game.home_requested.connect(lambda: self.stack.setCurrentWidget(self.start)); self.game.finished.connect(lambda: self.stack.setCurrentWidget(self.start))
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11: self.showNormal() if self.isFullScreen() else self.showFullScreen()
        else: super().keyPressEvent(event)
