import sys
sys.setrecursionlimit(99999)

FixedInt = tuple[int,int]

def prec():
    return 10000

def delta() -> FixedInt:
    return 100, prec()

# integers are stored as the value and scaling factor: tuple[int,int]

# you can only return tuples and numbers

def add(n1: FixedInt, n2: FixedInt):
    # assuming that s1 and s2 are the same, otherwise we must convert res = lcm(s1,s2)
    return n1[0] + n2[0], n1[1]

# 'p/q' + 'a/q' = '(p+a)/q'

def sub(n1: FixedInt, n2: FixedInt):
    # assuming that s1 and s2 are the same, otherwise we must convert res = lcm(s1,s2)
    return n1[0] - n2[0], n1[1]

def mul_trunc(n1: FixedInt, n2: FixedInt):
    return n1[0]*n2[0] // n1[1], n1[1]
    # 'a/b * c/d = ac/bd = (ac * (1/d))/(bd * 1/d) = ac/b'
    # print(f"{n1[0]/n1[1]} * {n2[0]/n2[1]} ~= {res[0]/res[1]}")

def f(x: FixedInt) -> FixedInt:
    return add(add(mul_trunc(x,x),mul_trunc(make_fixed(2), x)), make_fixed(1))

def update(x: FixedInt, sum: FixedInt, lim: FixedInt) -> FixedInt:
    # print(f"x: {x} | sum: {sum} | lim: {lim}")
    d = delta()

    sum2 = add(sum, mul_trunc(f(x), d))
    x2 = add(x, d)

    dif = sub(x2, lim)[0] 

    if (dif):
        # x != max
        return update(x2, sum2, lim)
    else:
        # x == max
        return sum2

def integrate(lower, upper):
    return update(lower, (0,prec()), upper)

def make_fixed(n: int) -> FixedInt:
    return int(n*prec()), prec()

res = integrate(make_fixed(-100), make_fixed(100))

print(res[0]/res[1])