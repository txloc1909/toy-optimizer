from ir import Block
from ir import bb_to_str
from passes import optimize_load_store


def test_two_loads():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.load(var0, 0)
    var2 = bb.load(var0, 0)
    bb.escape(var1)
    bb.escape(var2)

    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = load(var0, 0)
var2 = escape(var1)
var3 = escape(var1)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()
