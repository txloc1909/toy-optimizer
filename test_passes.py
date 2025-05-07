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
    expected = """
optvar0 = getarg(0)
optvar1 = add(9, optvar0)
    """
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


def test_constfold_multifold():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(5, 4)     # this is folded
    var2 = bb.add(var1, 10) # this should be folded, too
    var3 = bb.add(var2, var0)

    opt_bb = constfold(bb)
    expected = """
optvar0 = getarg(0)
optvar1 = add(19, optvar0)
    """
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


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
    expected = """
optvar0 = getarg(0)
optvar1 = getarg(1)
optvar2 = add(optvar1, 17)
optvar3 = mul(optvar0, optvar2)
optvar4 = add(optvar3, optvar2)
    """

    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


def test_strength_reduce():
    # TODO: parametrize this test on different ops
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.add(var0, var0)

    opt_bb = strength_reduce(bb)

    expected = """
optvar0 = getarg(0)
optvar1 = lshift(optvar0, 1)
    """
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


def test_remove_unused_allocation():
    bb = Block()
    var0 = bb.getarg(0)
    obj = bb.alloc()        
    sto = bb.store(obj, 0, var0)
    var1 = bb.load(obj, 0) 
    bb.print(var1)

    opt_bb = alloc_removal(bb)
    expected = """
optvar0 = getarg(0)
optvar1 = print(optvar0)
    """
    assert interpret(bb, 42) == interpret(opt_bb, 42)
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


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
    expected = """
optvar0 = getarg(0)
optvar1 = print(optvar0)
    """

    assert interpret(bb, 42) == interpret(opt_bb, 42)
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


def test_materialize():
    bb = Block()
    var0 = bb.getarg(0)
    obj = bb.alloc()        
    sto = bb.store(var0, 0, obj)

    opt_bb = alloc_removal(bb)

    # allocation of obj should be kept
    assert bb_to_str(opt_bb, "optvar") == bb_to_str(bb, "optvar")


def test_dont_materialize_twice():
    bb = Block()
    var0 = bb.getarg(0)
    obj = bb.alloc()
    sto0 = bb.store(var0, 0, obj)
    sto1 = bb.store(var0, 0, obj)

    opt_bb = alloc_removal(bb)

    # obj should be materialized only once
    expected = """\
optvar0 = getarg(0)
optvar1 = alloc()
optvar2 = store(optvar0, 0, optvar1)
optvar3 = store(optvar0, 0, optvar1)
    """
    assert bb_to_str(opt_bb, "optvar").strip() == expected.strip()


def test_materialize_non_virtuals():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.getarg(1)
    sto = bb.store(var0, 0, var1)

    opt_bb = alloc_removal(bb)

    # both var0 and var1 are not virtuals,
    # so there should be no materialization
    assert bb_to_str(opt_bb, "optvar") == bb_to_str(bb, "optvar")


def test_materialize_constant():
    bb = Block()
    var0 = bb.getarg(0)
    sto = bb.store(var0, 0, Constant(42))

    opt_bb = alloc_removal(bb)

    expected = bb_to_str(bb, "optvar")
    result = bb_to_str(opt_bb, "optvar")
    assert result == expected


def test_materialize_fields():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.getarg(1)
    obj = bb.alloc()
    field1 = bb.store(obj, 0, Constant(42))
    field2 = bb.store(obj, 1, var1)
    sto = bb.store(var0, 0, obj)

    opt_bb = alloc_removal(bb)

    # the two stores to obj should be kept
    assert bb_to_str(opt_bb, "optvar") == bb_to_str(bb, "optvar")


def test_materialize_chained_objs():
    bb = Block()
    var0 = bb.getarg(0)
    obj0 = bb.alloc()
    obj1 = bb.alloc()
    contents = bb.store(obj0, 0, obj1)
    const = bb.store(obj1, 0, 1337)
    sto = bb.store(var0, 0, obj0)

    opt_bb = alloc_removal(bb)
    print(bb_to_str(opt_bb, "optvar"))

    expected = """\
optvar0 = getarg(0)
optvar1 = alloc()
optvar2 = alloc()
optvar3 = store(optvar2, 0, 1337)
optvar4 = store(optvar1, 0, optvar2)
optvar5 = store(optvar0, 0, optvar1)
    """
    assert bb_to_str(opt_bb, "optvar") == expected.strip()


def test_materialize_obj_cycle():
    bb = Block()
    var0 = bb.getarg(0)
    var1 = bb.alloc()
    var2 = bb.store(var1, 0, var1) # cycle!
    var3 = bb.store(var0, 1, var1)

    opt_bb = alloc_removal(bb)

    # var1 mustn't escape
    assert bb_to_str(opt_bb, "optvar") == bb_to_str(bb, "optvar")
