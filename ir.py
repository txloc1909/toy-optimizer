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
            return super().__eq__(other)

        return self.value == other.value

    def find(self):
        return self

    def _set_forwarded(self, value: Value):
        # if we found out that an Operation is
        # equal to a constant, it's a compiler bug
        # to find out that it's equal to another
        # constant
        assert isinstance(value, Constant) and \
            value.value == self.value


class Operation(Value):
    def __init__(self, name: str, args: list[Value]):
        self.name: str = name
        self.args: list[Value] = args
        self._forwarded: Optional[Value] = None
        self.info: Any = None

    def __repr__(self):
        return f"Operation({self.name}, {self.args}, {self._forwarded}, {self.info})"

    def __hash__(self):
        # NOTE: this is not so clean
        return hash((self.name, id(self.args), self._forwarded))

    def find(self) -> Value:
        op: Value = self 
        while isinstance(op, Operation):
            if op._forwarded is None:
                return op
            op = op._forwarded

        return op

    def _set_forwarded(self, value: Value):
        self._forwarded = value

    def arg(self, index: int):
        return self.args[index].find()

    def make_equal_to(self, value: Value):
        # this is "union" in the union-find sense,
        # but the direction is important! The
        # representative of the union of Operations
        # must be either a Constant or an operation
        # that we know for sure is not optimized
        # away.
        self.find()._set_forwarded(value)


class Block(list):

    @staticmethod
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

    add = opbuilder("add")
    mul = opbuilder("mul")
    getarg = opbuilder("getarg")
    dummy = opbuilder("dummy")
    lshift = opbuilder("lshift")
    alloc = opbuilder("alloc")
    load = opbuilder("load")
    store = opbuilder("store")
    print = opbuilder("print")


def bb_to_str(bb: Block, varprefix: str = "var") -> str:
    def arg_to_str(arg: Value):
        if isinstance(arg, Constant):
            return str(arg.value)
        else:
            assert arg in varnames, "Basic block not valid"
            return varnames[arg]

    varnames: dict[Value, str] = {}
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


def check_dominance(bb: Block) -> bool:
    """Definition of a variable must dominate its usage"""
    # TODO: test this

    defined = set()
    for op in bb:
        for j in len(op.args):
            arg = op.arg(j)
            if arg.find() not in defined: 
                return False

        defined.add(op.find())

    return True


def check_single_definition(bb: Block) -> bool:
    """Each variable is defined exactly once"""
    # TODO: test this

    defined = set()
    for op in bb:
        var = op.find()
        if var in defined:
            return False

        defined.add(var)

    return True
