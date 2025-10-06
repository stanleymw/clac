def increment_both(c: tuple, a: int, b: int):
    return c[0] + a, c[1] + b

def pass_through(x: int, y: int):
    return increment_both((x,y), 1,2)

def add_together(c: int, d: int):
    return c+d

def main():
    v = pass_through(67,67)
    print(add_together(v[0],v[1]))