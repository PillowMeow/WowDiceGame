from game.core.state import Board, Tile


# 예시 보스
def basic_board() -> Board:
    tiles: list[Tile] = []
    for i in range(30):
        kind = "core:coin" if i % 5 == 4 else "core:normal"
        row = i // 10
        col = i % 10 if row % 2 == 0 else 9 - i % 10
        tiles.append(Tile(kind, (col, row)))
    return Board(tiles)
