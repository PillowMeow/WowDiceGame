"""Action // 플레이어가 직접 하는 행동(선언) 모음

네트워크로 오가는 건 Action뿐이다. 변환은 game/net/protocol.py
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    """Action의 기반 클래스"""

    pid: str


@dataclass(frozen=True)
class RollDice(Action):
    """주사위 굴림 선언. ROLL phase에서만"""


@dataclass(frozen=True)
class UseActive(Action):
    """액티브 효과 격발 선언. effect_index는 die.effects의 번호"""

    effect_index: int
    target: str | int | None = None


@dataclass(frozen=True)
class Buy(Action):
    """상점에서 주사위 구매 선언. ACTION phase에서만. 가격은 registry.SHOP"""

    die_id: str


@dataclass(frozen=True)
class EndTurn(Action):
    """턴 종료 선언. ACTION phase에서만"""
