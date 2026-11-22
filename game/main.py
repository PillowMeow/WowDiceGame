# python -m game.main host p1 2
# python -m game.main join p2 127.0.0.1
import sys
import time

from game.core.actions import Action, Buy, EndTurn, RollDice, UseActive
from game.core.game import Game, IllegalAction
from game.network import Guest, Host


def describe(game: Game, action: Action) -> str:
    if isinstance(action, RollDice):
        return "주사위 굴리기"
    if isinstance(action, EndTurn):
        return "턴 엔드"
    if isinstance(action, Buy):
        return f"{action.die_id} 업그레이드"
    if isinstance(action, UseActive):
        effect = game.current_player().die.effects[action.effect_index]
        return f"{effect.name} 효과 사용"
    return str(action)


def print_state(game: Game) -> None:
    for p in game.players:
        print(f"  {p.nickname} / {p.pos}번 칸 / 코인 {p.coins} / 주사위 {p.die.id}")


def main() -> None:
    net: Host | Guest
    if sys.argv[1] == "host":
        net = Host(sys.argv[2], int(sys.argv[3]))
    else:
        net = Guest(sys.argv[2], sys.argv[3])

    game = Game.new(net.seed, net.players, "basic", "basic_d6", start_coins=3)
    waiting = False

    while True:
        received = net.receive()
        for action in received:
            try:
                game.apply(action)
            except IllegalAction:
                pass
        if received:
            waiting = False

        if game.winner is not None:
            print(f"{game.winner} 승리")
            break

        actions = game.legal_actions(net.my_pid)
        if not actions or waiting:
            time.sleep(0.1)
            continue

        print_state(game)
        for i, action in enumerate(actions):
            print(f"{i}: {describe(game, action)}")
        text = input("번호")
        if not text.isdigit() or int(text) >= len(actions):
            continue
        net.send(actions[int(text)])
        waiting = True


if __name__ == "__main__":
    main()
