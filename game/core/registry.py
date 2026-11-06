from collections.abc import Callable

from game.content.boards import basic_board
from game.content.dice import basic_d6, lucky_d6
from game.content.tiles import CoinTile, NormalTile
from game.core.effect import TileKind
from game.core.state import Board, Die

DICE: dict[str, Callable[[], Die]] = {
    "basic_d6": basic_d6,
    "lucky_d6": lucky_d6,
}

BOARDS: dict[str, Callable[[], Board]] = {
    "basic": basic_board,
}

TILE_KINDS: dict[str, TileKind] = {
    NormalTile.id: NormalTile(),
    CoinTile.id: CoinTile(),
}

SHOP: dict[str, int] = {
    "lucky_d6": 5,
}
"""상점에서 파는 주사위 id → 가격"""
