from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

from game.core.actions import Action, Buy, EndTurn, RollDice, UseActive
from game.core.log import LogEntry
from game.core.registry import BOARDS, DICE, SHOP, TILE_KINDS
from game.core.rng import Rng
from game.core.state import Board, Phase, Player


class IllegalAction(Exception):
    """지금 할 수 없는 Action. 상태는 바뀌지 않음"""


class Game:
    board: Board
    players: list[Player]
    """2~4명. 이 리스트의 플레이어 순서가 턴 순서"""
    turn: int
    """1부터 세고 모든 플레이어가 한 번씩 하면 +1"""
    current: int
    """지금 턴을 가지고 있는 플레이어의 인덱스"""
    phase: Phase
    rng: Rng
    """게임 전체에서 들고 있는 난수 하나. 효과도 이것만 쓴다"""
    winner: str | None
    log: list[LogEntry]
    """UI 연출용 기록 (game/core/log.py 참고)"""

    @classmethod
    def new(
        cls,
        seed: int,
        players: Sequence[tuple[str, str]],
        board_id: str,
        die_id: str,
        start_coins: int = 0,
    ) -> Game:
        g = cls()
        g.rng = Rng(seed)
        g.board = BOARDS[board_id]()
        g.players = [
            Player(pid=pid, nickname=nickname, coins=start_coins, pos=0, die=DICE[die_id]())
            for pid, nickname in players
        ]
        g.turn = 1
        g.current = 0
        g.winner = None
        g.log = []
        g._start_turn()
        return g

    def current_player(self) -> Player:
        return self.players[self.current]

    def add_coins(self, p: Player, amount: int) -> None:
        """코인 증감. 0 미만으로 내려가지 않는다."""
        before = p.coins
        p.coins = max(p.coins + amount, 0)
        if p.coins != before:
            self.add_log("coins", p, delta=p.coins - before, total=p.coins)

    def move(self, p: Player, steps: int, is_teleport: bool = False) -> None:
        """steps칸 전진. steps <= 0이면 아무 일 없음.

        한 칸씩 전진하면서
        1) goal에 닿으면 즉시 승리 (훅 없음)
        2) 마지막 칸이 아니고 순간이동이 아니면 효과들 on_pass
        끝나면 도착 처리: 효과들 on_land → 그 칸 TileKind.on_land
        """
        if steps <= 0:
            return
        start = p.pos
        for i in range(steps):
            p.pos += 1
            if p.pos >= self.board.goal:
                p.pos = self.board.goal
                self.add_log("moved", p, start=start, end=p.pos, teleport=int(is_teleport))
                self.win(p)
                return
            if i < steps - 1 and not is_teleport:
                for effect in p.die.effects:
                    effect.on_pass(self, p, p.pos)
                if self.winner is not None:
                    return
        self.add_log("moved", p, start=start, end=p.pos, teleport=int(is_teleport))
        self._land(p)

    def replace_die(self, p: Player, die_id: str) -> None:
        """die_id 주사위로 통째로 교체. 옛 주사위 효과의 기록은 사라진다."""
        p.die = DICE[die_id]()
        self.add_log("die_replaced", p, die=die_id)

    def add_log(self, kind: str, p: Player | None = None, **data: int | str) -> None:
        """UI용 기록 추가. 효과가 자기 연출용 기록을 남길 때도 쓴다."""
        self.log.append(LogEntry(kind, p.pid if p is not None else None, dict(data)))

    def legal_actions(self, pid: str) -> list[Action]:
        """pid가 지금 보낼 수 있는 Action 전부. UI는 이 순서대로 버튼을 놓는다.

        내 턴이 아니거나 게임이 끝났으면 []
        ROLL: RollDice, UseActive들
        ACTION: UseActive들, Buy들, EndTurn
        """
        p = self.current_player()
        if p.pid != pid or self.phase == Phase.END:
            return []
        actions: list[Action] = []
        if self.phase == Phase.ROLL:
            actions.append(RollDice(pid))
        for i, effect in enumerate(p.die.effects):
            for target in effect.targets(self, p):
                actions.append(UseActive(pid, i, target))
        if self.phase == Phase.ACTION:
            for die_id, price in SHOP.items():
                if die_id != p.die.id and p.coins >= price:
                    actions.append(Buy(pid, die_id))
            actions.append(EndTurn(pid))
        return actions

    def apply(self, action: Action) -> None:
        """Action 하나를 끝까지 처리한다. legal_actions에 없으면 illegalaction"""
        if action not in self.legal_actions(action.pid):
            raise IllegalAction(action)
        p = self.current_player()

        if isinstance(action, RollDice):
            side = self.rng.choice(p.die.sides)
            value = side.value
            for effect in p.die.effects + side.effects:  # 주사위 효과 → 나온 면 효과 순
                value = effect.modify_roll(self, p, value)
            self.add_log("rolled", p, face=side.value, value=value)
            self.move(p, max(0, value))
            if self.winner is None:
                self.phase = Phase.ACTION

        elif isinstance(action, UseActive):
            effect = p.die.effects[action.effect_index]
            self.add_log("used", p, effect=effect.id)
            effect.use(self, p, action.target)

        elif isinstance(action, Buy):
            price = SHOP[action.die_id]
            self.add_coins(p, -price)
            self.replace_die(p, action.die_id)
            self.add_log("bought", p, die=action.die_id, price=price)

        elif isinstance(action, EndTurn):
            for effect in p.die.effects:
                effect.on_turn_end(self, p)
            self.add_log("turn_end", p, turn=self.turn)
            self.current = (self.current + 1) % len(self.players)
            if self.current == 0:
                self.turn += 1
            self._start_turn()

    def state_hash(self) -> str:
        """상태가 같은지 확인ㄴ만 함"""
        players: list[object] = []
        for p in self.players:
            effects = [[e.id, e.params, e.state] for e in p.die.effects]
            for side in p.die.sides:
                effects += [[e.id, e.params, e.state] for e in side.effects]
            players.append(
                {"pid": p.pid, "coins": p.coins, "pos": p.pos, "die": p.die.id, "effects": effects}
            )
        data = {
            "turn": self.turn,
            "current": self.current,
            "phase": self.phase.value,
            "rng": self.rng.state,
            "winner": self.winner,
            "players": players,
        }
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    # ── 내부 ──

    def _start_turn(self) -> None:
        self.phase = Phase.ROLL
        p = self.current_player()
        self.add_log("turn_start", p, turn=self.turn)
        for effect in p.die.effects:
            effect.on_turn_start(self, p)

    def _land(self, p: Player) -> None:
        self.add_log("landed", p, tile=p.pos)
        for effect in p.die.effects:
            effect.on_land(self, p, p.pos)
        if self.winner is not None:
            return
        tile = self.board.tiles[p.pos]
        TILE_KINDS[tile.kind].on_land(self, p)

    def win(self, p: Player) -> None:
        """승리 처리. 이거 이후에 모든 action을 무시해야 함"""
        self.winner = p.pid
        self.phase = Phase.END
        self.add_log("win", p)
