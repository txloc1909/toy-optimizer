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
