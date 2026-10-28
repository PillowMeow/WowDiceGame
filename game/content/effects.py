"""예시 효과 (TDD같은걸 해보고 싶어서 짰는데 안될듯 그냥 이게 돌아가면 게임 완성인걸로)

이런 식으로 새 효과를 만들고 싶으면 Effect를 상속해서 함수를 오버로딩?오버라이딩?하면 됩니당
"""

from game.core.effect import Effect
from game.core.game import Game
from game.core.state import Die, Player, Side


class CoinOnEven(Effect):
    """패시브 // 짝수가 나오면 코인 amount만큼 얻음"""

    id = "core:coin_on_even"

    def modify_roll(self, g: Game, owner: Player, value: int) -> int:
        if value % 2 == 0:
            g.add_coins(owner, self.int_param("amount"))
        return value


class Boost(Effect):
    """액티브 // 턴당 1회 제한으로 코인 cost를 내고 다음 굴림 amount 증가"""

    id = "core:boost"

    def on_turn_start(self, g: Game, owner: Player) -> None:
        self.state["used"] = 0  # 다음 굴림까지 유지

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


def lucky_d6() -> Die:  # 개쩌는 주사위
    return Die(
        id="lucky_d6",
        sides=[
            Side(1, []),
            Side(2, [CoinOnEven(amount=1)]),
            Side(3, []),
            Side(4, [CoinOnEven(amount=1)]),
            Side(5, []),
            Side(6, [CoinOnEven(amount=1)]),
        ],
        effects=[Boost(cost=3, amount=2)],
    )
