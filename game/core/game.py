from __future__ import annotations

from collections.abc import Sequence

from game.core.actions import Action, EndTurn, RollDice, UseActive  # 필요해서 자체적으로 추가
from game.core.registry import BOARDS
from game.core.rng import Rng
from game.core.state import Board, Die, Phase, Player  # Die 추가함


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
        # 1) players: (pid, nickname) 2~4개.
        # 2) 모든 플레이어가 die_id 템플릿으로 만든 주사위를 받음
        # 3) seed는 호스트가 정해서 모든 피어에 같은 값을 줘야 함"""
        game_instance = cls()
        game_instance.rng = Rng(seed)
        game_instance.board = BOARDS[board_id]()

        game_instance.players = [
            Player(
                pid=player_id,
                nickname=player_nickname,
                coins=start_coins,
                pos=0,
                die=Die(die_id, sides=[], effects=[]),
            )
            for player_id, player_nickname in players
        ]

        game_instance.turn = 1
        game_instance.current = 0
        game_instance.phase = Phase.ROLL
        game_instance.winner = None
        return game_instance

    def current_player(self) -> Player:  # 추가한 def
        return self.players[self.current]

    def add_coins(self, p: Player, amount: int) -> None:
        """그 플레이어의 코인 증가/감소. 0 미만으로 감소하지 않음"""
        p.coins = max(p.coins + amount, 0)

    def move(self, p: Player, steps: int, is_teleport: bool = False) -> None:
        """steps칸 전진 (steps <= 0이면 바로 return)

        한 칸씩 pos += 1 하면서 이하 효과 :
        1) 그 칸이 goal이면 win(p) 후 아무것도 안 보고 즉시 return
        2) 마지막 칸이 아니고 is_teleport가 아니라면 p의 효과들 on_pass(tile)
        3) 마지막 칸이면 p의 효과들 on_land(tile), 그다음 그 칸 TileKind.on_land 호출
        """
        if steps <= 0:
            return

        for i in range(steps):
            p.pos += 1

            is_last_tile = i == steps - 1  # i 활용하는 방식으로 수정

            if p.pos >= self.board.goal:
                p.pos = self.board.goal  # 이 부분도 수정
                break

            current_tile = self.board.get_tile(
                p.pos
            )  # state.py에서 Board 클래스에 get_tile정의 필요할듯

            if not is_last_tile and not is_teleport:
                for effect in p.effects:
                    effect.on_pass(self, p, current_tile)

        """final_tile = self.board.get_tile(p.pos) 의 부분"""

        """for effect in p.effects: #플레이어의 특수 이펙트들 중 effect로 해서 for 하려고 했으나 TODO
        effect.on_land(self, p, final_tile)
        """

        if p.pos == self.board.goal:
            self.win(p)
        else:
            final_tile = self.board.get_tile(p.pos)  # 로 이동하였으나 오류 그대로
            final_tile.kind.on_land(self, p)

    def replace_die(self, p: Player, die_id: str) -> None:
        """die_id 템플릿으로 새 주사위를 만들어 교체함"""
        new_die = Die(die_id, sides=[], effects=[])  # 일단 new_die로 잡았어요
        p.die = new_die

    def legal_actions(self, pid: str) -> list[Action]:
        """pid가 지금 보낼 수 있는 Action 목록 리턴

        지금 턴을 가진 플레이어가 아니면 빈 배열 리턴
        아니라면, phase에 따라 이하의 배열 리턴
        ROLL) RollDice + UseActive들
        ACTION) UseActive들 + EndTurn
        END) []
        """
        current_player = self.current_player()
        if current_player.pid != pid:
            return []

        actions: list[Action] = []  # actions = [] 의미. Action 계열 데이터 모아둘 리스트 명시했어요
        phase = self.phase

        if phase == Phase.ROLL:  # ROLL 페이즈
            actions.append(RollDice(current_player.pid))
            if current_player.die and current_player.die.effects:
                for effect_index, effect in enumerate(
                    current_player.die.effects
                ):  # enumerate추가 수정
                    actions.append(UseActive(current_player.pid, effect_index))

        elif phase == Phase.ACTION:  # ACTION 페이즈
            if current_player.die and current_player.die.effects:
                for effect in current_player.die.effects:
                    actions.append(UseActive(effect))
            actions.append(EndTurn(current_player.pid))

        elif phase == Phase.END:  # END 페이즈 [] 반환
            return []

        return actions

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
        p = self.players[self.current]

        if isinstance(action, RollDice):  # RollDice 액션 처리
            side = self.rng.choice(p.die.sides)
            value = side.value

            """ 모든 효과 리스트, 주사위 자체/선택 면 효과 추가. 우선순위 부분 - 시스템적으로 더 필요하다 함. TODO
            all_effects = []
            if p.die and p.die.effects:
                all_effects.extend(p.die.effects)
            if side and side.effects:
                all_effects.extend(side.effects)

            .sort() key 어떨지 모름
            이 부분 통째로 수정 가능


            for effect in all_effects:
                value = effect.modify_roll(self, p, value)
            """
            self.move(p, value)
            self.phase = Phase.ACTION

        elif isinstance(action, UseActive):  # UseActive 액션 처리
            if p.die and p.die.effects and 0 <= action.effect_index < len(p.die.effects):
                p.die.effects[action.effect_index].use(self, p, action.target)

        elif isinstance(action, EndTurn):  # EndTurn 액션 처리
            if p.die and p.die.effects:
                for effect in p.die.effects:
                    effect.on_turn_end(self, p)

            self.current = (self.current + 1) % len(self.players)

            if self.current == 0:
                self.turn += 1

            self.phase = Phase.ROLL

    # ── 내부 ──

    def win(self, p: Player) -> None:
        """게임 끝 처리"""
        """이긴 거 그냥 .winner로 처리? - ui """
        self.phase = Phase.END
        """승리하면 뭐 따로 출력 있는지.. - ui """
