from collections.abc import Callable

from game.core.effect import TileKind
from game.core.state import Board, Die

DICE: dict[str, Callable[[], Die]] = {}
BOARDS: dict[str, Callable[[], Board]] = {}
TILE_KINDS: dict[str, TileKind] = {}

from game.content.effects import lucky_d6

DICE["lucky_d6"] = lucky_d6
