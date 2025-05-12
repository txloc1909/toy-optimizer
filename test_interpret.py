from ir import Block, Operation, Constant, Value
from ir import bb_to_str
from abstract_interpret import Parity, TOP, BOTTOM, EVEN, ODD
from abstract_interpret import _analyze_parity, simplify


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


def test_parity_simplify():
    bb = Block()
    v0 = bb.getarg(0)
    v1 = bb.getarg(1)
    v2 = bb.lshift(v0, 1)
    v3 = bb.lshift(v1, 1)
    v4 = bb.add(v2, v3)
    v5 = bb.bitand(v4, 1)
    v6 = bb.dummy(v5)

    opt_bb = simplify(bb)

    # the bitand should be removed
    expected = """\
optvar0 = getarg(0)
optvar1 = getarg(1)
optvar2 = lshift(optvar0, 1)
optvar3 = lshift(optvar1, 1)
optvar4 = add(optvar2, optvar3)
optvar5 = dummy(0)
    """

    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()

