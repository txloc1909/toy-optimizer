from dataclasses import dataclass


@dataclass
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

    def __repr__(self) -> str:
        if self.is_constant():
            return f"KnownBits.from_constant({self.ones})"
        return f"KnownBits({self.ones}, {self.unknowns})"

    def __str__(self) -> str:
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

    @classmethod 
    def from_str(cls, s: str) -> "KnownBits":
        """Construct instance from string
        String starting with ...1 means all higher bits are 1, 
        or ...? means all higher bits are unknowns.
        Otherwise, assume higher bits are all 0.
        """
        if s.startswith("...?"):
            ones, unknowns, start = 0, -1, 4
        elif s.startswith("...1"):
            ones, unknowns, start = -1, 0, 4
        else: 
            ones, unknowns, start = 0, 0, 0

        for char in s[start:]:
            ones <<= 1
            unknowns <<= 1

            if char == "1":
                ones |= 1
            elif char == "?":
                unknowns |= 1
            else:
                assert char == "0"
                pass # do nothing

        return cls(ones=ones, unknowns=unknowns)

    @classmethod
    def all_unknown(cls) -> "KnownBits":
        """Convenient constructor for 'all bits unknown' abstract value"""
        return cls.from_str("...?")

    def __eq__(self, other: "KnownBits") -> bool:
        return self.ones == other.ones and self.unknowns == other.unknowns 

    def __invert__(self):
        return KnownBits(ones=self.zeros, unknowns=self.unknowns)

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __add__(self, other):
        raise NotImplementedError

    def __sub__(self, other):
        raise NotImplementedError
