"""
게임에서 발생하는 여러 효과를 정의함
다른 효과를 만드려면 이걸 상속해서 구현하면 됨 (content/effects.py 참고)
이때 이하를 참고할 것
1) 상태는 Game의 public한 필드 / 메서드만 건들 것 (딱보면 퍼블릭인지 아닌지 앎)
2) Player나 Board 필드를 직접 대입 ㄴㄴ
3) 난수는 g.rng만 써야 함 (p2p니까 난수가 서로 다 다르면 개망함)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from game.core.game import Game
    from game.core.state import Player

ParamValue = int | str | bool


class Effect:
    id: ClassVar[str] = ""
    """"마크처럼 namespace:name로 둘 것"""

    def __init__(self, **params: ParamValue) -> None:
        self.params: dict[str, ParamValue] = dict(params)
        """주사위 템플릿 같은 곳에서 받는 호출값.
        이게 없으면 "이 면을 띄우면 코인 +1" "이 면을 띄우면 코인 +2" "이 면을 띄우면 코인 +3" 이런 효과 만들때 Effect를 3개 만들어야 해서 겁나 귀찮음
        대신 "이면을 띄우면 코인 +n"(3) 이런 식으로 쓸 수 있게 해준다.
        패러미터는 int, str, bool의 딕셔너리로 받을 수 있다

        아마 테스트는 안 해봤지만 그 Effect에서 원하는 이름의 필드를 안 주면 에러가 뜰거같은데 고치려면 굉장히 귀찮은 타이핑을 해야 하니까 그냥 잘 보고 쓸 것"""
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
        """그 플레이어의 주사위 굴림 직후. 값을 적용하기 전에 호출됨. 이때 이 함수로 그 값을 바꿔서 리턴하면 바뀐 값으로 적용됨"""
        return value

    def on_pass(self, g: Game, owner: Player, tile: int) -> None:
        """이 타일을 지나갔을 때"""

    def on_land(self, g: Game, owner: Player, tile: int) -> None:
        """이 타일에서 멈췄을 때"""

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
