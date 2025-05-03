from ir import Value, Constant, Operation, Block
from ir import bb_to_str


def test_construct_example():
    # first we need something to represent
    # "a" and "b". In our limited view, we don't
    # know where they come from, so we will define
    # them with a pseudo-operation called "getarg"
    # which takes a number n as an argument and
    # returns the n-th input argument. The proper
    # SSA way to do this would be phi-nodes.

    a = Operation("getarg", [Constant(0)])
    b = Operation("getarg", [Constant(1)])
    # var1 = add(b, 17)
    var1 = Operation("add", [b, Constant(17)])
    # var2 = mul(a, var1)
    var2 = Operation("mul", [a, var1])
    # var3 = add(b, 17)
    var3 = Operation("add", [b, Constant(17)])
    # var4 = add(var2, var3)
    var4 = Operation("add", [var2, var3])

    sequence = [a, b, var1, var2, var3, var4]
    # nothing to test really, it shouldn't crash


def test_convencience_block_construction():
    bb = Block()
    # a again with getarg, the following line
    # defines the Operation instance and
    # immediately adds it to the basic block bb
    a = bb.getarg(0)
    assert len(bb) == 1
    assert bb[0].name == "getarg"

    # it's a Constant
    assert bb[0].args[0].value == 0

    # b with getarg
    b = bb.getarg(1)
    # var1 = add(b, 17)
    var1 = bb.add(b, 17)
    # var2 = mul(a, var1)
    var2 = bb.mul(a, var1)
    # var3 = add(b, 17)
    var3 = bb.add(b, 17)
    # var4 = add(var2, var3)
    var4 = bb.add(var2, var3)
    assert len(bb) == 6


def test_basicblock_to_str():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(5, 4)
    var2 = bb.add(var1, var0)

    assert bb_to_str(bb) == """\
var0 = getarg(0)
var1 = add(5, 4)
var2 = add(var1, var0)"""

    # with a different prefix for the invented
    # variable names:
    assert bb_to_str(bb, "x") == """\
x0 = getarg(0)
x1 = add(5, 4)
x2 = add(x1, x0)"""

    # and our running example:
    bb = Block()
    a = bb.getarg(0)
    b = bb.getarg(1)
    var1 = bb.add(b, 17)
    var2 = bb.mul(a, var1)
    var3 = bb.add(b, 17)
    var4 = bb.add(var2, var3)

    assert bb_to_str(bb, "v") == """\
v0 = getarg(0)
v1 = getarg(1)
v2 = add(v1, 17)
v3 = mul(v0, v2)
v4 = add(v1, 17)
v5 = add(v3, v4)"""
    # Note the re-numbering of the variables! We
    # don't attach names to Operations at all, so
    # the printing will just number them in
    # sequence, can sometimes be a source of
    # confusion.
