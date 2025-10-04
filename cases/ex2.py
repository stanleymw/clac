def increment_both(a,b):
    return a+1, b+1

def pass_through(x,y):
    return increment_both(x, y)

def add_together(c,d):
    return c+d

print(add_together(pass_through(67,67)))