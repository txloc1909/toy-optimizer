from dataclasses import dataclass


@dataclass(eq=False)
class KnownBits:
    ones: int
    unknowns: int

    def __post_init__(self):
        assert self.is_well_formed()

    def is_well_formed(self) -> bool:
        # a bit cannot be both 1 and unknown
        return self.ones & self.unknowns == 0

    @classmethod 
    def from_constant(cls, const: int) -> "KnownBits":
        """All bits are known."""
        return cls(ones=const, unknowns=0)

    def is_constant(self) -> bool:
        return self.unknowns == 0

    @property
    def knowns(self) -> int:
        """return an int where the known bits are set"""
        return ~self.unknowns

    @property  
    def zeros(self) -> int:
        """return an int where places that are known zeros have a bit set"""
        return self.knowns & ~self.ones

    def contains(self, value: int) -> bool:
        """check whether this instance contains the concrete int `value`"""
        return value & self.knowns == self.ones

    def __repr__(self):
        if self.is_constant():
            return f"KnownBits.from_constant({self.ones})"
        return f"KnownBits({self.ones}, {self.unknowns})"

    def __str__(self):
        res = []
        ones, unknowns = self.ones, self.unknowns

        # construct from right to left
        while True:
            if not ones and not unknowns:
                break   # reached leading known 0s

            if ones == -1 and not unknowns:
                # -1 in two's complement -> all leading bits are 1
                res.append("1")
                res.append("...")
                break

            if unknowns == -1: 
                # -1 in two's complement -> all leading bits are unknown
                assert not ones
                res.append("?")
                res.append("...")
                break

            if unknowns & 1:
                res.append("?")
            elif ones & 1:
                res.append("1")
            else:
                res.append("0")

            ones >>= 1 
            unknowns >>= 1

        if len(res) == 0:
            res = ["0"]

        return "".join(reversed(res))
