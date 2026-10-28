"""ACtion // 플레이어가 직접 하는 행동(선언) 모음"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """Action의 기반 클래스"""

    pid: str


@dataclass(frozen=True)
class RollDice(Action):
    """주사위 굴림 선언"""


@dataclass(frozen=True)
class UseActive(Action):
    """액티브 효과 격발 선언"""

    effect_index: int
    target: str | int | None = None


@dataclass(frozen=True)
class EndTurn(Action):
    """턴 종료 선언"""
