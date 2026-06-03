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


def test_store_to_same_object_offset_doesnt_invalidates_load():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.load(var0, 0)
    var2 = bb.store(var0, 3, 5)
    var3 = bb.load(var0, 0)
    bb.escape(var1)
    bb.escape(var3)

    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = load(var0, 0)
var2 = store(var0, 3, 5)
var3 = escape(var1)
var4 = escape(var1)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()


def test_load_after_store_removed():
    bb = Block()
    var0 = bb.getarg(0)
    bb.store(var0, 0, 5)
    var1 = bb.load(var0, 0)         # var1 is equivalent to var0
    var2 = bb.load(var0, 1)
    bb.escape(var1)
    bb.escape(var2)
    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = store(var0, 0, 5)
var2 = load(var0, 1)
var3 = escape(5)
var4 = escape(var2)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()


def test_load_then_store():
    bb = Block()
    arg1 = bb.getarg(0)
    var1 = bb.load(arg1, 0)
    bb.store(arg1, 0, var1)
    bb.escape(var1)

    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = load(var0, 0)
var2 = escape(var1)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()


def test_store_after_store():
    bb = Block()
    arg1 = bb.getarg(0)
    bb.store(arg1, 0, 5)
    bb.store(arg1, 0, 5)

    opt_bb = optimize_load_store(bb)

    expected = """
var0 = getarg(0)
var1 = store(var0, 0, 5)
    """

    assert bb_to_str(opt_bb).strip() == expected.strip()
