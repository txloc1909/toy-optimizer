from typing import Any 

from ir import Block, Operation, Constant, Value


class Obj:
    """Runtime representation of heap-allocated objects."""

    def __init__(self):
        self.content: dict[int, Any] = {}

    def store(self, idx: int, value: Any):
        self.content[idx] = value

    def load(self, idx: int) -> Any:
        return self.content[idx]


class VirtualObj: 
    """Placeholder for objects whose allocation is removed"""

    def __init__(self):
        self.content: dict[int, Value] = {}

    def store(self, idx: int, value: Value):
        self.content[idx] = value

    def load(self, idx: int) -> Value:
        return self.content[idx]


def get_num(op, idx: int = 1) -> Any:
    assert isinstance(op.arg(idx), Constant)
    return op.arg(idx).value


def argval(op, i):
    arg = op.arg(i)
    if isinstance(arg, Constant):
        return arg.value
    else:
        assert isinstance(arg, Operation) 
        return arg.info


def interpret(bb: Block, *args) -> Any:
    for idx, op in enumerate(bb):
        match op.name:
            case "getarg":
                op.info = args[get_num(op, 0)]
            case "alloc":
                op.info = Obj()
            case "load":
                field_num = get_num(op)
                op.info = argval(op, 0).load(field_num)
            case "store":
                obj = argval(op, 0)
                field_num = get_num(op, 1)
                field_val = argval(op, 2)
                obj.store(field_num, field_val)
            case "print":
                res = argval(op, 0)
                print(res)
                return res
            case "add":
                op.info = argval(op, 0) + argval(op, 1)
            case "mul":
                op.info = argval(op, 0) * argval(op, 1)
            case "lshift":
                op.info = argval(op, 0) << argval(op, 1)
            case _:
                raise NotImplementedError(f"Operation {op.name} not implemented")


if __name__ == "__main__":
    bb = Block()
    var0 = bb.getarg(0)
    obj = bb.alloc()
    sto = bb.store(obj, 0, var0)
    var1 = bb.load(obj, 0)
    bb.print(var1)

    assert interpret(bb, 42) == 42
