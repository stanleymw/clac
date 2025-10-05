#!/bin/python3
import ast
import sys
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
class ClacVoid:
    pass

@dataclass
class ClacInt:
    # val: int
    position: int

# a pytuple is just two ClacInts right next to each other
@dataclass
class PyTuple:
    position: int

class OpCode(ABC):
    @abstractmethod
    def stack_delta(self) -> int:
        raise Exception()
    
    @abstractmethod
    def assemble(self) -> str:
        raise Exception()

@dataclass
class ClacFunc:
    name: str
    arg_count: int
    ret_count: int

    code: list[OpCode]
    children: list #list of clacfuncs

ClacValue = ClacVoid | ClacInt | PyTuple | ClacFunc

@dataclass
class If(OpCode):
    body: ClacExpression
    orelse: ClacExpression

    def stack_delta(self):
        return -1

class Swap(OpCode):
    def stack_delta(self):
        return 0
    
    def assemble(self):
        return "swap"

class Rot(OpCode):
    def stack_delta(self):
        return 0
    
    def assemble(self):
        return "rot"

@dataclass
class Pick(OpCode):
    def stack_delta(self):
        return 0
    def assemble(self):
        return "pick"

class Skip(OpCode):
    def stack_delta(self):
        return -1

    def assemble(self):
        return "skip"

    
class Drop(OpCode):
    def stack_delta(self):
        return -1

    def assemble(self):
        return "drop"

@dataclass
class Push(OpCode):
    value: int
    def stack_delta(self):
        # match (self.value):
        #     case int():
        #         return 1
        return 1

    def assemble(self):
        return f"{self.value}"

@dataclass
class Call(OpCode):
    func: ClacFunc

    def assemble(self):
        return f"{self.func.name}"

@dataclass
class BinOp(OpCode):
    operator: str
    def stack_delta(self):
        return -1

    def assemble(self):
        return f"{self.operator}"

def match_operator_to_BinOp(op: ast.operator) -> BinOp:
    match (op):
        case ast.Add():
            return BinOp("+")
        case ast.Sub():
            return BinOp("-")
        case ast.Mult():
            return BinOp("*")
        case ast.Mod():
            return BinOp("%")
        case ast.FloorDiv():
            return BinOp("/")
        case ast.Pow():
            return BinOp("**")
        case _:
            raise Exception(f"Non-existent BinOp: {op}")

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

def generate_error_message(message: str, node: ast.expr | ast.stmt):
    return f"{message} | Line {node.lineno} Col {node.col_offset}"

# ClacCompile should be created for all FunctionDef
class FunctionCompiler(ast.NodeVisitor):
    # given a FunctionDef, and names, the function compiler should be able to compile this function and all of it's children
    def __init__(self, fun: ast.FunctionDef, names: dict[str, ClacValue], stack_size = 0):
        self.func: ast.FunctionDef = fun

        args = self.func.args.args

        self.parent_stack_size = stack_size
        self.stack_size = stack_size
        # stack_size should be the size of parent stack + # args (assume that the caller always puts those args onto the parent stack)

        # we have access to whatever was in our parent function, as well as our local variables
        self.names = names

        # assume that caller put these args on the stack in the correct order
        offset: int = 0
        for arg in args:
            assert arg.annotation, f"All function arguments must be type annotated | Line {arg.lineno}"
            assert isinstance(arg.annotation, ast.Name), generate_error_message("All function arguments must be type annotated with Name", arg.annotation)
            match arg.annotation.id:
                case "int":
                    self.stack_size += 1
                    self.names[arg.arg] = ClacInt(self.stack_size)
                case "tuple":
                    self.stack_size += 2
                    self.names[arg.arg] = PyTuple(self.stack_size-1)
                case _:
                    raise Exception(f"Unknown Type! Expecting int or tuple | Line {arg.lineno}")

        self.queue: list[OpCode] = []
        self.children_functions: list[ClacFunc] = []

    def visit_arguments(self, node: ast.arguments):
        print("Already visited args in function def")

    def add_opcode_to_queue(self, opcode: OpCode):
        self.queue.append(opcode)
        self.stack_size += opcode.stack_delta()

    def eval_expression_and_get_type(self, expr: ast.expr) -> type[ClacValue]:
        old_size = self.stack_size
        self.visit(expr)
        expr_size: int = self.stack_size - old_size

        assert 0 <= expr_size <= 2, generate_error_message("0 <= expression_size <= 2 must hold", expr)

        match expr_size:
            case 0:
                return ClacVoid
            case 1:
                return ClacInt
            case 2:
                return PyTuple
            case _:
                raise Exception(generate_error_message("Unknown expresion type", expr))

    def compile(self) -> ClacFunc:
        self.generic_visit(self.func)
        print("{self.func.name}-> final names:", self.names)
        return ClacFunc(self.func.name, len(self.func.args.args), self.stack_size - self.parent_stack_size, self.queue, self.children_functions)
    
    def visit_Constant(self, node: ast.Constant):
        # node.value
        assert isinstance(node.value, int), generate_error_message("All constant values must be integers!", node)
        self.add_opcode_to_queue(Push(node.value))

    def visit_FunctionDef(self, node):
        raise Exception()

    def visit_Return(self, node: ast.Return):
        # visit all of this node's children
        if node.value is None:
            expr_type: type[ClacValue] = ClacVoid
        else:
            expr_type: type[ClacValue] = self.eval_expression_and_get_type(node.value)

        match expr_type:
            case cls if cls is ClacVoid:
                while (self.stack_size > self.parent_stack_size):
                    self.add_opcode_to_queue(Drop())

            case cls if cls is ClacInt:
                while (self.stack_size > self.parent_stack_size + 1):
                    self.add_opcode_to_queue(Swap())
                    self.add_opcode_to_queue(Drop())

            case cls if cls is PyTuple:
                while (self.stack_size > self.parent_stack_size + 2):
                    self.add_opcode_to_queue(Rot())
                    self.add_opcode_to_queue(Drop())
            case _:
                raise Exception()

    def visit_Assign(self, node: ast.Assign):
        assert len(node.targets) == 1, generate_error_message("Can only assign to one variable", node)
        name = node.targets[0]
        assert isinstance(name, ast.Name), generate_error_message("Must assign to name", node)

        expr_type = self.eval_expression_and_get_type(node.value)
        print(f"{name.id} :: {expr_type}")
        match expr_type:
            case cls if cls is ClacVoid:
                raise Exception()
            case cls if cls is ClacInt:
                self.names[name.id] = ClacInt(self.stack_size)
            case cls if cls is PyTuple:
                self.names[name.id] = PyTuple(self.stack_size - 1)
            case _:
                raise Exception()
    
    def visit_Subscript(self, node: ast.Subscript):
        assert isinstance(node.ctx, ast.Load), generate_error_message("Can only use subscript to access elements", node)
        # we should load whatever is at value first

        val = self.eval_expression_and_get_type(node.value)
        assert val == PyTuple, generate_error_message("val must be tuple", node)

        # match node.value:
        #     case ast.Tuple():
        #         pass
        #     case ast.Name():
        #         assert node.value.id in self.names, generate_error_message("Trying to subscript an undefined value", node)
        #         assert isinstance(self.names[node.value.id], PyTuple), generate_error_message("Can only subscript a tuple", node)
        #     case _:
        #         raise Exception("Trying to subscript an invalid object", node)

        self.add_opcode_to_queue(Push(2))

        subscript = self.eval_expression_and_get_type(node.slice)
        assert subscript == ClacInt, generate_error_message("subscript must be ClacInt", node)

        # val[0] val[1] subscript
        # TODO: statically verify that subscript is within bounds
        self.add_opcode_to_queue(match_operator_to_BinOp(ast.Sub()))
        self.add_opcode_to_queue(Pick())

        # val[0] val[1] val[subscript]
        self.add_opcode_to_queue(Rot())
        self.add_opcode_to_queue(Rot())

        self.add_opcode_to_queue(Drop())
        self.add_opcode_to_queue(Drop())

    def absolute_pos_relative_pick_offset(self, pos: int):
        return self.stack_size - pos + 1

    def visit_Name(self, node: ast.Name):
        match node.ctx:
            case ast.Load():
                assert node.id in self.names, f"Variable/identifier not found: {node.id} | Line {node.lineno}"

                val = self.names[node.id]
                match val:
                    case ClacInt():
                        self.add_opcode_to_queue(Push(self.absolute_pos_relative_pick_offset(val.position)))
                        self.add_opcode_to_queue(Pick())
                    case PyTuple():
                        self.add_opcode_to_queue(Push(self.absolute_pos_relative_pick_offset(val.position)))
                        self.add_opcode_to_queue(Pick())

                        self.add_opcode_to_queue(Push(self.absolute_pos_relative_pick_offset(val.position + 1)))
                        self.add_opcode_to_queue(Pick())
                    case ClacFunc:
                        pass
            case ast.Store():
                # raise Exception()
                print("storing", node.id)
            case _:
                raise Exception()

    def visit_Call(self, node: ast.Call):
        raise Exception()

    def visit_Expr(self, node):
        raise Exception()

    def visit_If(self, node):
        raise Exception()

    def visit_BinOp(self, node: ast.BinOp):
        # load all of the binop children onto the stack
        # FIXME: this could break with tuples
        self.generic_visit(node)
        self.add_opcode_to_queue(match_operator_to_BinOp(node.op))

    def visit_Compare(self, node):
        raise Exception()

# def create_block(gen: str) -> str:
#     id = len(if_blocks)
#     name = get_block_name_from_id(id)
#     if_blocks.append(f": {name} {gen} ;")
#     return name

# def get_block_name_from_id(id: int) -> str:
#     return f"__CLACC_IF_BLOCK_{id}_"

def assemble(func: ClacFunc) -> list[list[str]]:
    out: list[list[str]] = []
    
    # assemble itself
    out.append([])

    out[0].append(":")
    out[0].append(func.name)

    for i in func.code:
        out[0].append(i.assemble())

    out[0].append(";")

    for i in func.children:
        for child_function in assemble(i):
            out.append(child_function)

    return out


for i in tree.body:
    if isinstance(i, ast.FunctionDef):
        c = FunctionCompiler(i, {"print": ClacFunc("print", 1, 0, [], [])}, 0)
        compiled = (c.compile())
        assembled = assemble(compiled)

        print(f"Compiled: {compiled} \n Assembled: {assembled}")
        for i in assembled:
            print(" ".join(i))

# cv = ClacCompile(0, "")
# compiled = cv.compile(tree)
# if_blocks += "\n"
# res = preamble + "\n".join([i for i in if_blocks]) + compiled
# print(res)
# print([(i,v.value) for (i,v) in cv.variables.items()])
# print("Stack pos:", cv.current_stack_position)
# with open("output.clac", "w") as w:
#     w.write(res)
