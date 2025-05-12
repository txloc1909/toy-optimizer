from ir import Block, Operation, Constant, Value
from abstract_interpret import Parity, TOP, BOTTOM, EVEN, ODD
from abstract_interpret import _analyze_parity


def test_analyze_parity_simple():
    bb = Block()
    v0 = bb.getarg(0)
    v1 = bb.getarg(1)
    v2 = bb.lshift(v0, 1)
    v3 = bb.lshift(v1, 1)
    v4 = bb.add(v2, v3)
    v5 = bb.dummy(v4)

    parity = _analyze_parity(bb)

    assert parity[v0] == TOP
    assert parity[v1] == TOP
    assert parity[v2] == EVEN
    assert parity[v3] == EVEN
    assert parity[v4] == EVEN
    assert parity[v5] == TOP
