from collections.abc import Sequence


class Rng:
    # LCG 같은거 쓸거같음
    def choice[T](self, seq: Sequence[T]) -> T: ...
