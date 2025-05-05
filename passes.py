from ir import Value, Constant, Operation, Block


def constfold(bb):
    opt_bb = Block()

    for op in bb:
        match op.name:
            case "add":
                arg0, arg1 = op.arg(0), op.arg(1)
                if isinstance(arg0, Constant) and isinstance(arg1, Constant):
                    # fold
                    value = arg0.value + arg1.value
                    op.make_equal_to(Constant(value))
                    continue
                else: 
                    opt_bb.append(op)
            case _: # TODO: handle other ops
                opt_bb.append(op)

    return opt_bb

def _find_prev_op(op_name, arg0, arg1, bb):
    # This is quite naive
    # TODO: optimize this

    for op in bb:
        if op.name != op_name:
            continue

        if (op.arg(0) == arg0 and op.arg(1) == arg1) or \
           (op.arg(0) == arg1 and op.arg(1) == arg0):
            return op

    return None


def cse(bb):
    """Common Subexpression Elimination"""
    opt_bb = Block()

    for op in bb: 
        match op.name:
            case "add":
                arg0, arg1 = op.arg(0), op.arg(1)
                prev_op = _find_prev_op("add", arg0, arg1, opt_bb)
                if prev_op is not None:
                    op.make_equal_to(prev_op)
                    continue
                else:
                    opt_bb.append(op)
            case _: # TODO: handle other ops
                opt_bb.append(op)

    return opt_bb
