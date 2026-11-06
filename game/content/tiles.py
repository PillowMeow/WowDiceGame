"""칸 종류"""

from __future__ import annotations

from typing import TYPE_CHECKING

from game.core.effect import TileKind
from game.core.state import Player

if TYPE_CHECKING:
    from game.core.game import Game


class NormalTile(TileKind):
    """무효과 타일"""

    id = "core:normal"


class CoinTile(TileKind):
    """멈추면 코인 +2 하는 보너스 코인 타일"""

    id = "core:coin"

    def on_land(self, g: Game, player: Player) -> None:
        g.add_coins(player, 2)
