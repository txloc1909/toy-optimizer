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
        return BOTTOM

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


def _analyze(bb: Block):
    parity = {v: BOTTOM for v in bb}
    parity_of = lambda value: Parity.const(value) if isinstance(value, Constant) \
        else parity[value]

    for op in bb:
        transfer = getattr(Parity, op.name)
        args = [parity_of(arg.find()) for arg in op.args]
        parity[op] = transfer(*args)

    return parity


if __name__ == "__main__":
    bb = Block()
    v0 = bb.getarg(0)
    v1 = bb.getarg(1)
    v2 = bb.lshift(v0, 1)
    v3 = bb.lshift(v1, 1)
    v4 = bb.add(v2, v3)
    v5 = bb.dummy(v4)

    parity = _analyze(bb)
    assert parity[v0] is BOTTOM
    assert parity[v1] is BOTTOM
    assert parity[v2] is EVEN
    assert parity[v3] is EVEN
    assert parity[v4] is EVEN
    assert parity[v5] is TOP
