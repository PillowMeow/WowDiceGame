"""예시 효과

이런 식으로 새 효과를 만들고 싶으면 Effect를 상속해서 필요한 함수만 오버라이딩하면 됩니당
만든 효과는 content/dice.py의 주사위 함수 안에서 쓰면 됨 (따로 등록할 필요 없음)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.effect import Effect

if TYPE_CHECKING:
    from game.core.game import Game
    from game.core.state import Player


class CoinOnEven(Effect):
    """패시브 // 짝수가 나오면 코인 amount만큼 얻음"""

    id = "core:coin_on_even"
    name = "짝수 보너스"
    desc = "짝수가 나오면 코인을 얻는다"

    def modify_roll(self, g: Game, owner: Player, value: int) -> int:
        if value % 2 == 0:
            g.add_coins(owner, self.int_param("amount"))
        return value


class Boost(Effect):
    """액티브 // 턴당 1회 제한으로 코인 cost를 내고 다음 굴림 amount 증가"""

    id = "core:boost"
    name = "부스트"
    desc = "턴당 1회, 코인을 내고 다음 굴림의 눈금 수를 늘린다"

    def on_turn_start(self, g: Game, owner: Player) -> None:
        self.state["used"] = 0  # armed는 다음 굴림까지 유지

    def targets(self, g: Game, owner: Player) -> list[str | int | None]:
        if self.state.get("used", 0) == 0 and owner.coins >= self.int_param("cost"):
            return [None]
        return []

    def use(self, g: Game, owner: Player, target: str | int | None) -> None:
        g.add_coins(owner, -self.int_param("cost"))
        self.state["used"] = 1
        self.state["armed"] = 1

    def modify_roll(self, g: Game, owner: Player, value: int) -> int:
        if self.state.get("armed", 0):
            self.state["armed"] = 0
            return value + self.int_param("amount")
        return value
