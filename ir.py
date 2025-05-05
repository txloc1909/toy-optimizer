from typing import Optional, Any


class Value:
    def __eq__(self, other):
        return self is other

    def find(self):
        """Union-find"""
        raise NotImplementedError

    def _set_forwarded(self, value):
        raise NotImplementedError


class Constant(Value):
    def __init__(self, value: Any):
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"

    def __eq__(self, other):
        if not isinstance(other, Constant):
            return super().__eq__(self, other)

        return self.value == other.value

    def find(self):
        return self

    def _set_forwarded(self, value):
        # if we found out that an Operation is
        # equal to a constant, it's a compiler bug
        # to find out that it's equal to another
        # constant
        assert isinstance(value, Constant) and \
            value.value == self.value


class Operation(Value):
    def __init__(self, name: str, args: list[Value]):
        self.name = name
        self.args = args
        self._forwarded = None

    def __repr__(self):
        return f"Operation({self.name}, {self.args}, {self._forwarded})"

    def __hash__(self):
        # NOTE: this is not so clean
        return hash((self.name, id(self.args), self._forwarded))

    def find(self):
        op = self 
        while isinstance(op, Operation):
            if op._forwarded is None:
                return op
            op = op._forwarded

        return op

    def _set_forwarded(self, value):
        self._forwarded = value

    def arg(self, index: int):
        return self.args[index].find()

    def make_equal_to(self, value):
        # this is "union" in the union-find sense,
        # but the direction is important! The
        # representative of the union of Operations
        # must be either a Constant or an operation
        # that we know for sure is not optimized
        # away.
        self.find()._set_forwarded(value)


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
