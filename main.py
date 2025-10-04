#!/bin/python3

import ast
import sys
import types

binops = {
    "Add": "+",
    "Sub": "-",
    "Mult": "*",
    "Mod": "%",
    "FloorDiv": "/",
    "Pow": "**",
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
    assert isinstance(ret, ast.Return), f"not return, {ret}"
    match ret.value.__class__:
        case ast.Tuple:
            assert len(ret.value.elts) == 2, "Invalid multi-return amount"
            return 2
        case ast.Name | ast.Constant | ast.BinOp:
            return 1
        case ast.Call:
            return len(ret.value.args)
        case types.NoneType:
            return 0
        case _:
            raise Exception(f"Unknown return type {ret.value}")
        

if_blocks = [

]

preamble = """
: dup 1 pick ;
: noop ;
"""

class ClacCompile(ast.NodeVisitor):
    def __init__(self, current_stack_position, generated):
        self.variables: dict[str, QueueInstruction] = {
            "print": FuncValue("print", 1, 0),
        }
        self.current_stack_position = current_stack_position
        self.generated = generated

    def compile(self, node):
        print(self,"variables:", self.variables)
        self.visit(node)
        
        return self.generated

    def visit_FunctionDef(self, node):
        print(f"Found function def: {node.name}")
        self.generated += f": {node.name} "

        args = node.args.args
        new_compile = ClacCompile(len(args), "")

        # export this function to our current compiler
        
        found_ret = None


        def body_has_type(data_list, target_type):
            for obj in data_list:
                if isinstance(obj, target_type):
                    return True
            return False
        
        def well_defined_if(if_node):
            # check body
            body_ret = False
            orelse_ret = False
            if (not body_has_type(if_node.body, ast.If)):
                # no ifs in body, so the last element should be return
                assert not body_has_type(if_node.body[:-1], ast.Return), "only the last element in the if should be return"
                body_ret = isinstance(if_node.body[-1], ast.Return)
            else:
                # we do have ifs, so all of them must be well defined
                for expr in if_node.body:
                    if isinstance(expr, ast.If) and not well_defined_if(expr):
                        return False

            if (not body_has_type(if_node.orelse, ast.If)):
                # no ifs in body, so the last element should be return
                assert not body_has_type(if_node.orelse[:-1], ast.Return), "only the last element in the if should be return"
                orelse_ret = isinstance(if_node.orelse[-1], ast.Return)
            else:
                # we do have ifs, so both of those should be good
                for expr in if_node.body:
                    if isinstance(expr, ast.If) and not well_defined_if(expr):
                        return False

            # check orelse
            return (body_ret and orelse_ret) or (not body_ret and not orelse_ret)
        

        if not (body_has_type(node.body, ast.If)):
            # do naive check for true (it should just be the last element)
            found_ret = node.body[-1]
        else:
            found_ret = well_defined_if()
            # recursively check all ifs. If one of the ifs has a return, then the other must have as well


        # def return_in_block(if_node):
            
        self.variables[node.name] = FuncValue(node.name, len(args), get_return_amount(found_ret))

        # print("(0) parent vars:", self.variables, "child vars:", new_compile.variables)
        # give local variables to function
        for i in range(len(args)):
            new_compile.variables[args[i].arg] = IntValue(i + 1)

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
        # assert return_amount == 2 or return_amount == 1, "Invalid return amount (v2)"
        match return_amount:
            case 2:
                while (self.current_stack_position > 2):
                    self.generated += " rot drop "
                    self.current_stack_position -= 1
            case 1:
                while (self.current_stack_position > 1):
                    self.generated += " swap drop "
                    self.current_stack_position -= 1
            case 0:
                while (self.current_stack_position > 0):
                    self.generated += " drop "
                    self.current_stack_position -= 1
            case _:
                raise Exception("Invalid return amount (v2)")

        print("RETURNING", self, node.value)

    def visit_Assign(self, node):
        # print("MY VARIABLES:", self.variables, self)
        assert len(node.targets)==1, "can only assign to one variable"
        assert node.targets[0].ctx.__class__ == ast.Store, "must be storing variable"

        print(f"Found assign: {node.targets[0].id}")
        # Important: Continue traversing child nodes
        before_assign_stack = self.current_stack_position
        self.generic_visit(node)
        assert self.current_stack_position > before_assign_stack, "stack should be larger when assigning! (sanity check)"
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

        assert len(node.args) == func.num_args, "called function with wrong number of args"
        prev_stack_len = self.current_stack_position
        self.generic_visit(node)
        new_stack_len = self.current_stack_position
        assert new_stack_len == prev_stack_len + len(node.args), "args were not properly pushed onto the stack. Perhaps, not existent args"

        # FIXME: every defined function needs to report how much they change the stack position
        # REQUIREMENT FOR FUNCTIONS: THE STACK SIZE MUST NOT CHANGE

        self.generated += f" {self.variables[node.func.id].value} "

        self.current_stack_position += func.num_returns - func.num_args

        # stack offset modify should be #RETURN_VALUES - #ARGUMENTS

        # S a,b => f(a,b)_1, f(a,b)_2, f(a,b)_3, etc

    def visit_Expr(self, node):
        self.generic_visit(node)

    def visit_If(self, node):
        print("If detected:", node)

        self.visit(node.test)

        self.current_stack_position -= 1

        compiled, nsl = self.compile_expr_as_block(node.body)
        body_block = create_if_block(compiled)

        compiled_else, nsl_e = self.compile_expr_as_block(node.orelse)
        else_block = create_if_block(compiled_else)

        assert nsl == nsl_e, "both sides of if statement must result in consistent stack behavior"
        self.current_stack_position = nsl

        # assert new_compile.current_stack_position == self.current_stack_position, "if statement blocks must not affect the stack"

        self.generated += f" if {body_block} 1 skip {else_block} "

    def visit_BinOp(self, node):
        # is_valid = False
        # for i in BINOPS:
        #     is_valid |= isinstance(node.op, i)
        # assert(is_valid)
        opname = (node.op.__class__.__name__)
        assert opname in binops.keys(), "invalid binop"

        print(f"BINOP {self}: {opname}")
        self.generic_visit(node)
        self.generated += f" {binops[opname]} "
        self.current_stack_position -= 1

    def visit_Compare(self, node):
        # is_valid = False
        # for i in BINOPS:
        #     is_valid |= isinstance(node.op, i)
        # assert(is_valid)
        assert len(node.ops) == 1, "can only compare one thing"
        assert len(node.comparators) == 1, "should only use one comparator"
        opname = (node.ops[0].__class__.__name__)
        assert opname in compares.keys(), "invalid comparator"

        print(f"COMPARE {self}: {opname}")
        self.generic_visit(node)
        self.generated += f" {compares[opname]} "
        self.current_stack_position -= 1

    def compile_expr_as_block(self, expr) -> str:
        new_compile = ClacCompile(self.current_stack_position, "")

        # give our state to the compiler
        new_compile.variables = self.variables.copy()

        for stmt in expr:
            # print(f"  Body Statement: {type(stmt).__name__}, Code: {ast.unparse(stmt).strip()}")
            new_compile.visit(stmt)

        # required to not mess up the if statement
        # assert new_compile.current_stack_position == self.current_stack_position, "if statement blocks must not affect the stack"
        return new_compile.generated, new_compile.current_stack_position
    
def create_if_block(gen: str) -> str:
    id = len(if_blocks)
    name = get_block_name_from_id(id)
    if_blocks.append(f": {name} {gen} ;")
    return name

def get_block_name_from_id(id: int) -> str:
    return f"__CLACC_IF_BLOCK_{id}_"

cv = ClacCompile(0, "")
compiled = cv.compile(tree)
if_blocks += "\n"
res = preamble + "\n".join([i for i in if_blocks]) + compiled
print(res)
print([(i,v.value) for (i,v) in cv.variables.items()])
print("Stack pos:", cv.current_stack_position)
with open("output.clac", "w") as w:
    w.write(res)
