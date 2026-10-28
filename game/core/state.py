from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.effect import Effect


@dataclass
class Side:
    value: int
    effects: list[Effect]
    """이 면이 나온 굴림의 modify_roll에서 호출하는 effect"""


@dataclass
class Die:  # 죽는거 아님
    id: str
    """주사위 템플릿 id. namespace:id로 적음"""
    sides: list[Side]
    """면 목록 (6개 아니어도 됨)"""
    effects: list[Effect]
    """주사위 자체 효과"""


@dataclass
class Tile:
    kind: str
    """TileKind id. namespace:id로 적음"""
    pos: tuple[int, int]
    """지금 이 타일이 어느 위치에 있는가"""


@dataclass
class Board:
    tiles: list[Tile]
    """일단 일직선이라고 가정. 0이 시작 마지막이 도착"""

    @property
    def goal(self) -> int:
        return len(self.tiles) - 1


@dataclass
class Player:
    pid: str
    """플레이어마다 고유한 primary key id"""
    nickname: str
    coins: int
    pos: int
    """Board.tiles에서의 인덱스"""
    die: Die


class Phase(Enum):
    ROLL = "roll"
    ACTION = "action"
    END = "end"
