from collections.abc import Mapping
from dataclasses import dataclass, field

from game.core.effect import ParamValue


@dataclass(frozen=True)
class EffectSpec:
    id: str
    params: Mapping[str, ParamValue] = field(default_factory=dict[str, ParamValue])


@dataclass(frozen=True)
class SideSpec:
    value: int
    effects: tuple[EffectSpec, ...] = ()


@dataclass(frozen=True)
class DieTemplate:
    id: str
    sides: tuple[SideSpec, ...]
    effects: tuple[EffectSpec, ...] = ()


@dataclass(frozen=True)
class TileSpec:
    kind: str
    pos: tuple[int, int]


@dataclass(frozen=True)
class BoardTemplate:
    id: str
    tiles: tuple[TileSpec, ...]
    """0번이 출발, 마지막이 도착. 최소 2칸."""
