from game.content.effects import Boost, CoinOnEven
from game.core.state import Die, Side


def basic_d6() -> Die:
    """기본 주사위. 1~6, 효과 없음. 게임 시작 주사위"""
    return Die(id="basic_d6", sides=[Side(v, []) for v in range(1, 7)], effects=[])


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
