from typing import Optional, Any


class Value:
    pass


class Constant(Value):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"


class Operation(Value):
    def __init__(self, name: str, args: list[Value]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"Operation({self.name}, {self.args})"

    def arg(self, index: int):
        return self.args[index]


class Block(list):
    def opbuilder(opname):

        def wraparg(arg):
            if not isinstance(arg, Value):
                arg = Constant(arg)
            return arg

        def build(self, *args):
            # construct an Operation, wrap the
            # arguments in Constants if necessary
            op = Operation(opname,
                [wraparg(arg) for arg in args])
            # add it to self, the basic block
            self.append(op)
            return op

        return build

    # a bunch of operations we support
    add = opbuilder("add")
    mul = opbuilder("mul")
    getarg = opbuilder("getarg")
    dummy = opbuilder("dummy")
    lshift = opbuilder("lshift")


def bb_to_str(bb: Block, varprefix: str = "var"):
    def arg_to_str(arg: Value):
        nonlocal varnames
        if isinstance(arg, Constant):
            return str(arg.value)
        else:
            # the key must exist, otherwise it's
            # not a valid SSA basic block:
            # the variable must be defined before
            # its first use
            assert arg in varnames
            return varnames[arg]

    varnames = {}
    res = []
    for index, op in enumerate(bb):
        # give the operation a name used while
        # printing:
        var = f"{varprefix}{index}"
        varnames[op] = var
        arguments = ", ".join(
            arg_to_str(op.arg(i))
                for i in range(len(op.args))
        )
        strop = f"{var} = {op.name}({arguments})"
        res.append(strop)
    return "\n".join(res)

