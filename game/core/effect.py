"""
게임에서 발생하는 여러 효과를 정의함
다른 효과를 만드려면 이걸 상속해서 구현하면 됨 (content/effects.py 참고)
이때 이하를 참고할 것
1) 상태는 Game의 효과용 API(add_coins, move, replace_die, add_log)로만 바꿀 것
2) Player나 Board 필드를 직접 대입 ㄴㄴ
3) 난수는 g.rng만 써야 함 (p2p니까 난수가 서로 다 다르면 개망함)
4) 게임 중 기억할 값은 self.state에. 전역 변수, 클래스 변수 ㄴㄴ
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from game.core.game import Game
    from game.core.state import Player

ParamValue = int | str | bool


class Effect:
    id: ClassVar[str] = ""
    """마크처럼 namespace:name로 둘 것"""
    name: ClassVar[str] = ""
    """UI 버튼·설명에 보일 짧은 이름"""
    desc: ClassVar[str] = ""
    """UI에 보일 한 줄 설명"""

    def __init__(self, **params: ParamValue) -> None:
        self.params: dict[str, ParamValue] = dict(params)
        """주사위 함수에서 넘겨주는 값. 예: CoinOnEven(amount=2)
        이게 없으면 "코인 +1" "코인 +2" "코인 +3" 효과를 따로 만들어야 해서 귀찮음
        대신 "코인 +amount" 하나로 숫자만 바꿔 쓴다."""
        self.state: dict[str, int] = {}
        """effect 내부에서 맘대로 쓸 수 있는 메모장용 딕셔너리"""

    def int_param(self, key: str) -> int:
        value = self.params[key]
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{self.id}: param {key!r} must be int")
        return value

    def on_turn_start(self, g: Game, owner: Player) -> None:
        """그 플레이어의 턴 시작"""

    def modify_roll(self, g: Game, owner: Player, value: int) -> int:
        """그 플레이어의 주사위 굴림 직후. 바꾼 값을 리턴하면 그 값으로 이동함"""
        return value

    def on_pass(self, g: Game, owner: Player, tile: int) -> None:
        """이 칸을 지나갔을 때 (멈춘 칸 제외)"""

    def on_land(self, g: Game, owner: Player, tile: int) -> None:
        """이 칸에서 멈췄을 때"""

    def on_turn_end(self, g: Game, owner: Player) -> None:
        """그 플레이어의 턴 종료"""

    def targets(self, g: Game, owner: Player) -> list[str | int | None]:
        """액티브 선택지.
        지금 쓸 수 있으면 가능한 대상 목록을 반환. 쓸 수 없으면 빈 배열 반환.
        대상이 필요 없는 효과는 [None]을 반환하는걸로
        """
        return []

    def use(self, g: Game, owner: Player, target: str | int | None) -> None:
        """액티브 격발. targets()가 반환한 대상 중 하나로 호출된다."""


class TileKind:
    """칸 종류. 플레이어가 이 칸에 멈추면 그 플레이어의 효과 on_land 다음에 호출된다."""

    id: ClassVar[str] = ""

    def on_land(self, g: Game, player: Player) -> None:
        """기본은 아무 일도 없음"""
