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


def test_store_to_the_same_object_offset_invalidates_load():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.load(var0, 0)
    var2 = bb.store(var0, 0, 5)
    var3 = bb.load(var0, 0)
    bb.escape(var1)
    bb.escape(var3)

    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = load(var0, 0)
var2 = store(var0, 0, 5)
var3 = load(var0, 0)
var4 = escape(var1)
var5 = escape(var3)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()
