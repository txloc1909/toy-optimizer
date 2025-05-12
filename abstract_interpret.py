from ir import Block, Operation, Constant, Value


class Parity: 
    """Lattice for parity analysis."""

    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

    @staticmethod
    def const(value: Constant) -> "Parity":
        if value.value % 2 == 0:
            return EVEN
        else:
            return ODD

    def getarg(self):
        return TOP

    def add(self, other):
        if self is BOTTOM or other is BOTTOM:
            return BOTTOM
        elif self is TOP or other is TOP:
            return TOP
        elif self is EVEN and other is EVEN:
            return EVEN
        elif self is ODD and other is ODD:
            return EVEN
        else:
            return ODD

    def lshift(self, other):
        if other is ODD:
            return EVEN
        return TOP

    def dummy(self):
        return TOP


TOP = Parity("TOP")
BOTTOM = Parity("BOTTOM")
EVEN = Parity("EVEN")
ODD = Parity("ODD")


def _analyze_parity(bb: Block):
    """Derive all parity information from the basic block."""
    parity = {v: BOTTOM for v in bb}
    parity_of = lambda value: Parity.const(value) if isinstance(value, Constant) \
        else parity[value]

    for op in bb:
        transfer = getattr(Parity, op.name)
        args = [parity_of(arg.find()) for arg in op.args]
        parity[op] = transfer(*args)

    return parity
