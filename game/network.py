"""네트워크

host 모든 플레이어의 행동을 모아서 같은 순서로 전원에게 다시 보내는 구조
"""

from multiprocessing.connection import Client

from game.core.actions import Action

PORT = 47321
KEY = b"wowdice"  # 우리 게임끼리만 접속되게 하는 암호


class Host:
    """방장. 다른 사람들이 다 들어올 때까지 기다렸다가 게임을 시작한다."""

    my_pid: str
    seed: int
    players: list[tuple[str, str]]  # (pid, 닉네임)

    def __init__(self, name: str, player_count: int) -> None:
        """
        1. Listener(("", PORT), authkey=KEY)로 접속을 받는다
        2. player_count명이 될 때까지 accept → 닉네임 recv. 방장은 p1, 들어온 순서대로 p2, p3로 할당
        3. random.getrandbits(63)를 호출해 seed를 정하고 각 참가자에게 (pid, seed, players)를 send함
        """
        raise NotImplementedError

    def send(self, action: Action) -> None:
        """방장 자신의 행동. 바로 보내지 말고 대기 목록에 넣어둔다"""
        raise NotImplementedError

    def receive(self) -> list[Action]:
        """참가자들이 보낸 행동을 poll/recv로 모아 대기 목록에 더하고,
        대기 목록 전체를 모든 참가자에게 send한 뒤 반환함"""
        raise NotImplementedError


class Guest:
    """참가자. 내 행동은 방장에게 보내고, 방장이 돌려준 것만 적용한다."""

    my_pid: str
    seed: int
    players: list[tuple[str, str]]

    def __init__(self, name: str, address: str) -> None:
        self.conn = Client((address, PORT), authkey=KEY)
        self.conn.send(name)
        self.my_pid, self.seed, self.players = self.conn.recv()

    def send(self, action: Action) -> None:
        self.conn.send(action)

    def receive(self) -> list[Action]:
        actions: list[Action] = []
        while self.conn.poll():
            actions.append(self.conn.recv())
        return actions
