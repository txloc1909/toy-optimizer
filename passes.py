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
