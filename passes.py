from ir import Value, Constant, Operation, Block


def constfold(bb):
    opt_bb = Block()

    for op in bb:
        if op.name == "add":
            arg0, arg1 = op.args
            if isinstance(arg0, Constant) and isinstance(arg1, Constant):
                value = arg0.value + arg1.value
                op.make_equal_to(Constant(value))
                continue

        opt_bb.append(op)

    return opt_bb
