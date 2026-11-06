"""실행
방장: uv run python -m game.main host 닉네임 인원수
참가: uv run python -m game.main join 닉네임 방장IP
(한 컴퓨터에서 시험할 때는 터미널 두 개로 host와 join 닉네임 127.0.0.1)
"""


def main() -> None:
    """1. sys.argv를 보고 Host 또는 Guest를 만든다
    2. Game.new(net.seed, net.players, "basic", "basic_d6", start_coins=3)
    3. 반복:
       - net.receive()로 받은 행동을 순서대로 game.apply (IllegalAction이면 무시)
       - 화면을 그리고 버튼이 눌렸으면 net.send (TODO)
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
