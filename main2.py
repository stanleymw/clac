#!/bin/python3

import ast
import sys
from enum import Enum
from typing import List, Union

binops = {
        "Add": "+",
        "Sub": "-",
        "Mult": "*",
        "Mod": "%",
        "FloorDiv": "/",
        "Pow": "**",
}

if (len(sys.argv) < 2):
    print("Usage: ./main.py <file.py>")
    exit()

print("Seirea CLAC Compiler v0.1.0")
with open(sys.argv[1], "r") as f:
    tree = ast.parse(f.read())
# tree = ast.parse(source5)
print(ast.dump(tree, indent=4))

class QueueInstruction():
    pass

class IntValue(QueueInstruction):
    value: int = 0
    def __init__(self, val):
        self.value = val

class FuncValue(QueueInstruction):
    value: str = ""
    num_args: int = 0
    num_returns: int = 0
    def __init__(self, val, num_args, num_returns):
        self.value = val
        self.num_args = num_args
        self.num_returns = num_returns

def get_return_amount(ret: ast.Return):
    match ret.value.__class__:
        case ast.Tuple:
            assert(len(ret.value.elts) == 2)
            return 2
        case ast.Name | ast.Constant | ast.BinOp:
            return 1
        case ast.Call:
            return len(ret.value.args)
        case _:
            raise Exception("Unknown return type")

class ClacCompile(ast.NodeVisitor):
    def __init__(self):
        self.variables: dict[str, QueueInstruction] = {
            "print": FuncValue("print", 1, 0)
        }
        self.current_stack_position = 0
        self.generated = ""

    def compile(self, node):
        print(self,"variables:", self.variables)
        self.visit(node)
        
        return self.generated

    def visit_FunctionDef(self, node):
        print(f"Found function def: {node.name}")
        self.generated += f": {node.name} "

        new_compile = ClacCompile()
        args = node.args.args

        # export this function to our current compiler
        self.variables[node.name] = FuncValue(node.name, len(args), get_return_amount(node.body[-1]))

        # print("(0) parent vars:", self.variables, "child vars:", new_compile.variables)
        # give local variables to function
        for i in range(len(args)):
            new_compile.variables[args[i].arg] = IntValue(i + 1)

        # set function stack pos (after the local variables)
        new_compile.current_stack_position = len(args)

        # give the function itself to the function
        new_compile.variables[node.name] = self.variables[node.name]

        # give our functions to the compiler
        for i,v in self.variables.items():
            if (v.__class__ == FuncValue):
                new_compile.variables[v.value] = v

        # print("parent:", self, "child:", new_compile)
        # print("(1) parent vars:", self.variables, "child vars:", new_compile.variables)
        new_compile.generic_visit(node)
        # print("(2) parent vars:", self.variables, "child vars:", new_compile.variables)

        self.generated +=  new_compile.generated

        print("{node.name} generated:", new_compile.generated, "\nret count:", new_compile.current_stack_position)


        # Important: Continue traversing child nodes
        self.generated += " ; \n"

    def visit_Return(self, node):
        self.generic_visit(node)

        return_amount = get_return_amount(node)
        # asd asd asd a b
        assert(return_amount == 2 or return_amount == 1)
        if return_amount == 2:
            # assert(len(node.value.elts) == 2)

            while (self.current_stack_position > 2):
                self.generated += " rot drop "
                self.current_stack_position -= 1
        else:
            # should be one item
            while (self.current_stack_position > 1):
                self.generated += " swap drop "
                self.current_stack_position -= 1
        print("RETURNING", self, node.value)

    def visit_Assign(self, node):
        # print("MY VARIABLES:", self.variables, self)
        assert(len(node.targets)==1)
        assert(node.targets[0].ctx.__class__ == ast.Store)

        print(f"Found assign: {node.targets[0].id}")
        # Important: Continue traversing child nodes
        self.generic_visit(node)
        self.variables[node.targets[0].id] = IntValue(self.current_stack_position)

    def visit_Name(self, node):
        match node.ctx.__class__:
          case ast.Load:
              print(self,f"Loading {node.id}")
              val = self.variables[node.id]
              match val.__class__.__name__:
                  case "IntValue":
                      self.generated += f" {self.current_stack_position - val.value + 1} pick "
                      self.current_stack_position += 1
                  case "FuncValue":
                      # self.generated += f" {val.value} "
                      pass
                  case _:
                      raise Exception("Unknown value")
          case ast.Store:
              print(f"Storing {node.id}")
          case _:
              raise Exception("Unknown name op")

        self.generic_visit(node)

    def visit_If(self, node):
        print(f"Found if: {node.test}")
        # Important: Continue traversing child nodes
        self.generic_visit(node)

    def visit_Constant(self, node):
        self.generated += f" {node.value} "
        self.current_stack_position += 1

        self.generic_visit(node)

    def visit_Call(self, node):
        func = self.variables[node.func.id]

        assert(len(node.args) == func.num_args)
        self.generic_visit(node)

        # FIXME: every defined function needs to report how much they change the stack position
        # REQUIREMENT FOR FUNCTIONS: THE STACK SIZE MUST NOT CHANGE

        self.generated += f" {self.variables[node.func.id].value} "

        self.current_stack_position += func.num_returns - func.num_args

        # stack offset modify should be #RETURN_VALUES - #ARGUMENTS

        # S a,b => f(a,b)_1, f(a,b)_2, f(a,b)_3, etc

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_BinOp(self, node):
        # is_valid = False
        # for i in BINOPS:
        #     is_valid |= isinstance(node.op, i)
        # assert(is_valid)
        opname = (node.op.__class__.__name__)
        assert(opname in binops.keys())

        print(f"BINOP {self}: {opname}")
        self.generic_visit(node)
        self.generated += f" {binops[opname]} "
        self.current_stack_position -= 1

cv = ClacCompile()
res = cv.compile(tree)
print(res)
print([(i,v.value) for (i,v) in cv.variables.items()])
print("Stack pos:", cv.current_stack_position)
with open("output.clac", "w") as w:
    w.write(res)
