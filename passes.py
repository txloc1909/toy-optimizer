from ir import Value, Constant, Operation, Block
from interpret import Obj, VirtualObj, get_num, argval


def constfold(bb: Block) -> Block:
    opt_bb = Block()

    for op in bb:
        match op.name:
            case "add":
                arg0, arg1 = op.arg(0), op.arg(1)
                if isinstance(arg0, Constant) and isinstance(arg1, Constant):
                    op.make_equal_to(Constant(arg0.value + arg1.value))
                    continue
                else: 
                    opt_bb.append(op)
            case "mul":
                arg0, arg1 = op.arg(0), op.arg(1)
                if isinstance(arg0, Constant) and isinstance(arg1, Constant):
                    op.make_equal_to(Constant(arg0.value * arg1.value))
                    continue
                else: 
                    opt_bb.append(op)
            case "lshift":
                arg0, arg1 = op.arg(0), op.arg(1) 
                if isinstance(arg0, Constant) and isinstance(arg1, Constant):
                    op.make_equal_to(Constant(arg0.value << arg1.value))
                    continue
                else: 
                    opt_bb.append(op)
            case _: # TODO: handle other ops
                opt_bb.append(op)

    return opt_bb




def cse(bb: Block) -> Block:
    """Common Subexpression Elimination"""
    opt_bb = Block()

    def _find_prev_op(op_name, arg0, arg1, bb):
        for op in bb:
            if op.name != op_name:
                continue
            if (op.arg(0) == arg0 and op.arg(1) == arg1) or \
               (op.arg(0) == arg1 and op.arg(1) == arg0):
                return op
        return None
    
    for op in bb: 
        match op.name:
            case "add" | "mul" | "lshift":
                arg0, arg1 = op.arg(0), op.arg(1)
                prev_op = _find_prev_op(op.name, arg0, arg1, opt_bb)
                if prev_op is not None:
                    op.make_equal_to(prev_op)
                    continue
                else:
                    opt_bb.append(op)
            case _: # TODO: handle other ops
                opt_bb.append(op)

    return opt_bb


def strength_reduce(bb: Block) -> Block:
    opt_bb = Block()

    for op in bb:
        match op.name:
            case "add":
                arg0, arg1 = op.arg(0), op.arg(1)
                if arg0 is arg1:
                    new_op = opt_bb.lshift(arg0, 1)
                    op.make_equal_to(new_op)
                    continue
                else:
                    opt_bb.append(op)
            case "mul":
                # TODO: multiply by power of 2 -> left shift
                opt_bb.append(op)
            case _: # TODO: handle other ops
                opt_bb.append(op)

    return opt_bb


def _materialize(bb: Block, value) -> Block:
    if isinstance(value, Constant):
        return

    assert isinstance(value, Operation)
    info = value.info
    if info is None: # already materialized
        return 

    bb.append(value)
    for i, val in info.content.items():
        bb.store(value, i, val)
    value.info = None


def alloc_removal(bb: Block) -> Block:
    opt_bb = Block()

    for op in bb:
        match op.name:
            case "alloc":
                op.info = VirtualObj()
            case "load":
                info = op.arg(0).info
                field = get_num(op, 1)
                op.make_equal_to(info.load(field))
            case "store":
                info = op.arg(0).info
                if info is not None: # virtual object
                    field = get_num(op, 1)
                    value = op.arg(2)
                    info.store(field, value)
                else:
                    _materialize(opt_bb, op.arg(2))
                    opt_bb.append(op)
            case _:
                opt_bb.append(op)

    return opt_bb
