import ast
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

print("Seirea CLAC Compiler")

source2 = """
"""

source3 = """
def add(a,b):
    return a+b, b-a

print(1+2)
x = 69
"""

tree = ast.parse(source3)
print(ast.dump(tree, indent=4))

class QueueInstruction():
    pass

class IntValue(QueueInstruction):
    value: int = 0
    def __init__(self, val):
        self.value = val

class FuncValue(QueueInstruction):
    value: str = ""
    def __init__(self, val):
        self.value = val

class ClacVisitor(ast.NodeVisitor):
    variables: dict[str, QueueInstruction] = {
        "print": FuncValue("1 pick print")
    }
    current_stack_position = 0
    generated = ""

    def visit_FunctionDef(self, node):
        print(f"Found function: {node.name}")
        self.generated += f": {node.name} "
        # Important: Continue traversing child nodes
        self.generic_visit(node)
        self.generated += " ; \n"

    def visit_Assign(self, node):
        assert(len(node.targets)==1)
        assert(node.targets[0].ctx.__class__ == ast.Store)

        print(f"Found assign: {node.targets[0].id}")
        # Important: Continue traversing child nodes
        self.generic_visit(node)
        self.variables[node.targets[0].id] = IntValue(self.current_stack_position)

    def visit_Name(self, node):
        match node.ctx.__class__:
          case ast.Load:
              print(f"Loading {node.id}")
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
        self.generic_visit(node)

        # FIXME: every defined function needs to report how much they change the stack position
        # REQUIREMENT FOR FUNCTIONS: THE STACK SIZE MUST NOT CHANGE
        self.generated += f" {self.variables[node.func.id].value} "

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

        print(f"binop: {opname}")
        self.generic_visit(node)
        self.generated += f" {binops[opname]} "
        self.current_stack_position -= 1

cv = ClacVisitor()
cv.visit(tree)
print(cv.generated)
print([(i,v.value) for (i,v) in cv.variables.items()])
print("Stack pos:", cv.current_stack_position)
