from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
import random
from typing import Dict, List, Optional, Set


class Decision(Enum):
    STAY = auto()
    HOME = auto()
    MOVE_TO_PLAYER = auto()


class GameState(Enum):
    SETUP = auto()
    ROUND_1 = auto()
    ROUND_2 = auto()
    ROUND_3 = auto()
    READY_TO_REVEAL = auto()
    REVEALING = auto()
    ELIMINATION = auto()
    NEXT_CYCLE = auto()
    GAME_OVER = auto()


@dataclass
class Slot:
    number: int
    occupant_id: Optional[int] = None


@dataclass
class Player:
    player_id: int
    name: str
    home_slot: int
    current_slot: int
    alive: bool = True
    decision: Optional[Decision] = None
    target_player_id: Optional[int] = None


@dataclass
class Resolution:
    moved: Dict[int, int] = field(default_factory=dict)
    cancelled: Set[int] = field(default_factory=set)


class BombManager:
    def __init__(self, slot_count: int, rng: Optional[random.Random] = None):
        self.slot_count = slot_count
        self.rng = rng or random.Random()
        self.previous_slot: Optional[int] = None
        self.current_slot: Optional[int] = None

    def choose(self, available_slots: List[int]) -> int:
        choices = [s for s in available_slots if s != self.previous_slot] or available_slots
        self.current_slot = self.rng.choice(choices)
        self.previous_slot = self.current_slot
        return self.current_slot


class GameEngine:
    """GUI-independent rules engine. Decisions are collected, validated, resolved, then applied."""

    def __init__(self, player_names: List[str], rng: Optional[random.Random] = None):
        if not 2 <= len(player_names) <= 24:
            raise ValueError("عدد اللاعبين يجب أن يكون بين 2 و24")
        names = [name.strip() for name in player_names]
        if any(not name for name in names):
            raise ValueError("لا يمكن أن يكون اسم اللاعب فارغًا")
        self.players: Dict[int, Player] = {
            i: Player(i, name, i + 1, i + 1) for i, name in enumerate(names)
        }
        self.slots: Dict[int, Slot] = {i: Slot(i, i) for i in range(1, len(names) + 1)}
        self.bomb_manager = BombManager(len(names), rng)
        self.state = GameState.SETUP
        self.cycle = 0
        self.round_number = 0
        self.bomb_slot: Optional[int] = None
        self.last_resolution = Resolution()
        self.eliminated_player_id: Optional[int] = None

    @property
    def alive_players(self) -> List[Player]:
        return [p for p in self.players.values() if p.alive]

    @property
    def alive_count(self) -> int:
        return len(self.alive_players)

    def start_game(self) -> None:
        self.cycle = 1
        self.round_number = 1
        self.state = GameState.ROUND_1
        self._choose_bomb()

    def _choose_bomb(self) -> None:
        self.bomb_slot = self.bomb_manager.choose([p.current_slot for p in self.alive_players])
        for p in self.players.values():
            p.decision = None
            p.target_player_id = None

    def submit_decision(self, player_id: int, decision: Decision, target_player_id: Optional[int] = None) -> None:
        if self.state not in {GameState.ROUND_1, GameState.ROUND_2, GameState.ROUND_3}:
            raise ValueError("لا يمكن تسجيل قرار في هذه الحالة")
        player = self.players.get(player_id)
        if not player or not player.alive:
            raise ValueError("اللاعب غير متاح")
        if decision == Decision.MOVE_TO_PLAYER:
            target = self.players.get(-1 if target_player_id is None else target_player_id)
            if not target or not target.alive or target.player_id == player_id:
                raise ValueError("الهدف غير صالح")
        else:
            target_player_id = None
        player.decision = decision
        player.target_player_id = target_player_id

    def all_decisions_submitted(self) -> bool:
        return all(p.decision is not None for p in self.alive_players)

    def commit_round(self) -> Resolution:
        if not self.all_decisions_submitted():
            raise ValueError("لم تكتمل الاختيارات")
        self.last_resolution = self._resolve_conflicts()
        for player_id, destination in self.last_resolution.moved.items():
            self.players[player_id].current_slot = destination
        for slot in self.slots.values():
            slot.occupant_id = next((p.player_id for p in self.alive_players if p.current_slot == slot.number), None)
        self.round_number += 1
        self.state = {2: GameState.ROUND_2, 3: GameState.ROUND_3}.get(self.round_number, GameState.READY_TO_REVEAL)
        for p in self.alive_players:
            p.decision = None
            p.target_player_id = None
        return self.last_resolution

    def _resolve_conflicts(self) -> Resolution:
        desired: Dict[int, int] = {}
        for p in self.alive_players:
            if p.decision == Decision.STAY:
                desired[p.player_id] = p.current_slot
            elif p.decision == Decision.HOME:
                desired[p.player_id] = p.home_slot
            elif p.decision == Decision.MOVE_TO_PLAYER:
                target = self.players[p.target_player_id]  # validated on submission
                desired[p.player_id] = target.current_slot

        by_destination: Dict[int, List[int]] = {}
        for pid, destination in desired.items():
            by_destination.setdefault(destination, []).append(pid)
        cancelled: Set[int] = set()
        for ids in by_destination.values():
            if len(ids) > 1:
                cancelled.update(ids)

        # A directed cycle is valid only when each destination is uniquely claimed.
        moved = {pid: destination for pid, destination in desired.items() if pid not in cancelled}
        return Resolution(moved=moved, cancelled=cancelled)

    def reveal_bomb(self) -> Optional[Player]:
        if self.state != GameState.READY_TO_REVEAL:
            raise ValueError("القنبلة لا يمكن كشفها الآن")
        self.state = GameState.REVEALING
        victim = next((p for p in self.alive_players if p.current_slot == self.bomb_slot), None)
        self.eliminated_player_id = victim.player_id if victim else None
        self.state = GameState.ELIMINATION
        if victim:
            victim.alive = False
        return victim

    def start_next_cycle(self) -> None:
        if self.state != GameState.ELIMINATION:
            raise ValueError("لا يمكن بدء دورة جديدة الآن")
        if self.alive_count <= 1:
            self.state = GameState.GAME_OVER
            return
        self.cycle += 1
        self.round_number = 1
        self.state = GameState.NEXT_CYCLE
        self._choose_bomb()
        self.state = GameState.ROUND_1

    def get_winner(self) -> Optional[Player]:
        return next((p for p in self.players.values() if p.alive), None) if self.alive_count == 1 else None

    def player_status(self, player_id: int) -> str:
        player = self.players[player_id]
        return "حي" if player.alive else "مستبعد"

    def reset_decisions(self) -> None:
        for p in self.players.values():
            p.decision = None
            p.target_player_id = None
