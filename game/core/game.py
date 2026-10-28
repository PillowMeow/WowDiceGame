from __future__ import annotations

from collections.abc import Sequence

from game.core.actions import Action
from game.core.rng import Rng
from game.core.state import Board, Phase, Player


class IllegalAction(Exception): ...


class Game:
    board: Board
    players: list[Player]  # 2~4명 / 이 리스트의 플레이어 순서가 턴 순서
    turn: int  # 1부터 세고 모든 플레이어가 턴을 가질 때마다 +1
    current: int  # 지금 턴을 가지고 있는 플레이어의 인덱스
    phase: Phase  # 현재 턴 진행 상태
    rng: Rng  # 게임 전체에서 들고있는 랜덤함수 하나
    winner: str | None

    @classmethod
    def new(
        cls,
        seed: int,
        players: Sequence[tuple[str, str]],
        board_id: str,
        die_id: str,
        start_coins: int = 0,
    ) -> Game:
        """새 게임을 만들고 턴 루프를 시작함

        1) players: (pid, nickname) 2~4개.
        2) 모든 플레이어가 die_id 템플릿으로 만든 주사위를 받음
        3) seed는 호스트가 정해서 모든 피어에 같은 값을 줘야 함
        """
        raise NotImplementedError

    def add_coins(self, p: Player, amount: int) -> None:
        """그 플레이어의 코인 증가/감소. 0 미만으로 감소하지 않음"""
        raise NotImplementedError

    def move(self, p: Player, steps: int, is_teleport: bool = False) -> None:
        """steps칸 전진 (steps <= 0이면 바로 return)

        한 칸씩 pos += 1 하면서 이하 효과 :
        1) 그 칸이 goal이면 win(p) 후 아무것도 안 보고 즉시 return
        2) 마지막 칸이 아니고 is_teleport가 아니라면 p의 효과들 on_pass(tile)
        3) 마지막 칸이면 p의 효과들 on_land(tile), 그다음 그 칸 TileKind.on_land 호출
        """
        raise NotImplementedError

    def replace_die(self, p: Player, die_id: str) -> None:
        """die_id 템플릿으로 새 주사위를 만들어 교체함"""
        raise NotImplementedError

    def legal_actions(self, pid: str) -> list[Action]:
        """pid가 지금 보낼 수 있는 Action 목록 리턴

        지금 턴을 가진 플레이어가 아니면 빈 배열 리턴
        아니라면, phase에 따라 이하의 배열 리턴
        ROLL) RollDice + UseActive들
        ACTION) UseActive들 + EndTurn
        END) []
        """
        raise NotImplementedError

    def apply(self, action: Action) -> None:
        """Action 하나를 처리함

        RollDice
        1) 주사위의 면 하나를 랜덤하게 고름
        2) 주사위의 면 값을 die.effects에서 그 면의 effects에 우선순위 순서대로 modify_roll에 통과시킨 값을 얻음
        3) 그 값만큼 move 호출
        UseActive
        1) die.effects[effect_index].use(self, p, target)
        EndTurn:
        1) 그 플레이어가 가진 모든 효과들 on_turn_end 호출
        2) 다음 플레이어로 턴 넘김
        """
        raise NotImplementedError

    # ── 내부 ──

    def win(self, p: Player) -> None:
        """게임 끝 처리"""
        raise NotImplementedError
