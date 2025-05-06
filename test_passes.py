import pytest

from ir import Value, Constant, Operation, Block
from ir import bb_to_str
from passes import constfold, cse, strength_reduce
from passes import alloc_removal
from interpret import interpret


def test_constfold_simple():
    # TODO: parametrize this test on different ops
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


def test_cse_simple():
    # TODO: parametrize this test on different ops
    bb = Block()
    a = bb.getarg(0)
    b = bb.getarg(1)
    var1 = bb.add(b, 17)
    var2 = bb.mul(a, var1)
    var3 = bb.add(b, 17)    # var3 and var1 are the same
    var4 = bb.add(var2, var3)

    opt_bb = cse(bb)
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = getarg(1)
optvar2 = add(optvar1, 17)
optvar3 = mul(optvar0, optvar2)
optvar4 = add(optvar3, optvar2)"""


def test_strength_reduce():
    # TODO: parametrize this test on different ops
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(var0, var0)

    opt_bb = strength_reduce(bb)
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = lshift(optvar0, 1)"""


def test_remove_unused_allocation_1():
    bb = Block()
    var0 = bb.getarg(0)
    obj = bb.alloc()        
    sto = bb.store(obj, 0, var0)
    var1 = bb.load(obj, 0) 
    bb.print(var1)

    opt_bb = alloc_removal(bb)
    assert interpret(bb, 42) == interpret(opt_bb, 42)
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = print(optvar0)"""


def test_remove_multiple_nested_allocations():
    bb = Block()
    var0 = bb.getarg(0)
    obj1 = bb.alloc()        
    obj2 = bb.alloc()        
    obj3 = bb.alloc()
    sto1 = bb.store(obj1, 0, var0)
    sto2 = bb.store(obj2, 0, obj1)
    sto2 = bb.store(obj3, 0, obj2)
    var1 = bb.load(obj3, 0) 
    var2 = bb.load(var1, 0) 
    var3 = bb.load(var2, 0)
    bb.print(var3)

    opt_bb = alloc_removal(bb)
    assert interpret(bb, 42) == interpret(opt_bb, 42)
    assert bb_to_str(opt_bb, "optvar") == """\
optvar0 = getarg(0)
optvar1 = print(optvar0)"""
