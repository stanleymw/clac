#!/bin/python3
import ast
import sys
import types
from dataclasses import dataclass
from abc import ABC, abstractmethod

# a b
# a+b

# PUSH: <const> | ss+=1
# CALLS: <func> | ss+=(#ret-#arguments)

# Binary Operators: <binop> | ss -= 1

# Drop | ss -= 1
# Swap | ss X
# Rot | ss X
# If | ss -= 1
# Pick | ss X
# Skip | ss -= 1

@dataclass
class ClacExpression:
    pass

# all possible value types 
@dataclass
class ClacInt:
    val: int
    position: int

@dataclass
class PyTuple:
    a: ClacInt
    b: ClacInt

class OpCode(ABC):
    @abstractmethod
    def stack_delta(self):
        raise Exception()

@dataclass
class ClacFunc:
    arg_count: int
    ret_count: int

    code: list[OpCode]
    children: list #list of clacfuncs

ClacValue = ClacInt | PyTuple | ClacFunc

@dataclass
class If(OpCode):
    body: ClacExpression
    orelse: ClacExpression

    def stack_delta(self):
        return -1

class Swap(OpCode):
    def stack_delta(self):
        return 0

class Rot(OpCode):
    def stack_delta(self):
        return 0

class Pick(OpCode):
    offset: int
    def stack_delta(self):
        return 0

class Skip(OpCode):
    def stack_delta(self):
        return -1
    
class Drop(OpCode):
    def stack_delta(self):
        return -1

@dataclass
class Push(OpCode):
    value: ClacInt | PyTuple
    def stack_delta(self):
        match (self.value):
            case ClacInt():
                return 1
            case PyTuple():
                return 2

@dataclass
class Call:
    func: ClacFunc

@dataclass
class BinOp:
    operator: str


binops = {
    "Add": BinOp("+"),
    "Sub": BinOp("-"),
    "Mult": BinOp("*"),
    "Mod": BinOp("%"),
    "FloorDiv": BinOp("/"),
    "Pow": BinOp("**"),
}

compares = {
    "Lt": "<",
}

if (len(sys.argv) < 2):
    print("Usage: ./main.py <file.py>")
    exit()

print("Seirea CLAC Compiler v0.1.0")
with open(sys.argv[1], "r") as f:
    tree = ast.parse(f.read())
# tree = ast.parse(source5)
print(ast.dump(tree, indent=4))

preamble = """
: dup 1 pick ;
: noop ;
"""

class FunctionReturnAmountFinder(ast.NodeVisitor):
    def __init__(self, fun: ast.FunctionDef):
        self.argcount = None
        self.fun = fun

    def find(self):
        self.generic_visit(self.fun)

        return self.argcount

    def visit_Return(self, node: ast.Return):
        raise Exception(node.value)


# ClacCompile should be created for all FunctionDef
class FunctionCompiler(ast.NodeVisitor):
    # given a FunctionDef, and names, the function compiler should be able to compile this function and all of it's children
    def __init__(self, fun: ast.FunctionDef, names: dict[str, ClacValue], stack_size = 0):
        self.func: ast.FunctionDef = fun

        args = self.func.args.args

        self.parent_stack_size = stack_size
        self.stack_size = stack_size + len(args)
        # stack_size should be the size of parent stack + # args (assume that the caller always puts those args onto the parent stack)

        # we have access to whatever was in our parent function, as well as our local variables
        self.names = names

        # assume that caller put these args on the stack in the correct order
        for i in range(len(args)):
            arg = args[i]
            self.names[arg.arg] = self.parent_stack_size + i

        self.queue: list[OpCode] = []
        self.children_functions: list[ClacFunc] = []

    def add_opcode_to_queue(self, opcode: OpCode):
        self.queue.append(opcode)
        self.stack_size += opcode.stack_delta()

    def compile(self) -> ClacFunc:
        self.generic_visit(self.func)
        return ClacFunc(len(self.func.args.args), self.stack_size - self.parent_stack_size, self.queue, self.children_functions)

    def visit_FunctionDef(self, node):
        raise Exception()

    def visit_Return(self, node):
        raise Exception()

    def visit_Assign(self, node):
        raise Exception()

    def visit_Name(self, node: ast.Name) -> ast.Any:
        match node.ctx:
            case ast.Load():
                assert node.id in self.names, f"Variable/identifier not found: {node.id} | Line {node.lineno}"

                val = self.names[node.id]
                match val:
                    case ClacInt() | PyTuple():
                        self.add_opcode_to_queue(Push(val))
                    case ClacFunc:
                        pass
            case ast.Store():
                # raise Exception()
                print("storing", node.id)
            case _:
                raise Exception()

    def visit_If(self, node):
        raise Exception()

    def visit_Constant(self, node):
        raise Exception()

    def visit_Call(self, node):
        raise Exception()

    def visit_Expr(self, node):
        raise Exception()

    def visit_If(self, node):
        raise Exception()

    def visit_BinOp(self, node):
        raise Exception()

    def visit_Compare(self, node):
        raise Exception()

# def create_block(gen: str) -> str:
#     id = len(if_blocks)
#     name = get_block_name_from_id(id)
#     if_blocks.append(f": {name} {gen} ;")
#     return name

# def get_block_name_from_id(id: int) -> str:
#     return f"__CLACC_IF_BLOCK_{id}_"

for i in tree.body:
    if isinstance(i, ast.FunctionDef):
        c = FunctionCompiler(i, {"print": ClacFunc(1, 0, [], [])}, 0)
        print(c.compile())

# cv = ClacCompile(0, "")
# compiled = cv.compile(tree)
# if_blocks += "\n"
# res = preamble + "\n".join([i for i in if_blocks]) + compiled
# print(res)
# print([(i,v.value) for (i,v) in cv.variables.items()])
# print("Stack pos:", cv.current_stack_position)
# with open("output.clac", "w") as w:
#     w.write(res)
