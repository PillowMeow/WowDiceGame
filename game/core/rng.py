from collections.abc import Sequence

_MASK = (1 << 64) - 1


class Rng:
    def __init__(self, seed: int) -> None:
        self.state = seed & _MASK

    def next_u64(self) -> int:
        self.state = (self.state + 0x9E3779B97F4A7C15) & _MASK
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
        return z ^ (z >> 31)

    def randbelow(self, n: int) -> int:
        if n <= 0:
            raise ValueError("N은 정수여야 함")
        limit = (1 << 64) - ((1 << 64) % n)
        while True:
            x = self.next_u64()
            if x < limit:
                return x % n

    def choice[T](self, seq: Sequence[T]) -> T:
        return seq[self.randbelow(len(seq))]
