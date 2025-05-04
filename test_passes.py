import pytest

from ir import Value, Constant, Operation, Block
from ir import bb_to_str
from passes import constfold


def test_constfold_simple():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(5, 4)
    var2 = bb.add(var1, var0)

    opt_bb = constfold(bb)
    print(bb_to_str(opt_bb, "optvar"))
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = add(9, optvar0)"""


def test_constfold_multifold():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(5, 4)     # this is folded
    var2 = bb.add(var1, 10) # this should be folded, too
    var3 = bb.add(var2, var0)

    opt_bb = constfold(bb)
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = add(19, optvar0)"""
