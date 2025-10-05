import sys
sys.setrecursionlimit(99999)


def prec() -> int:
    return 1000

def delta() -> tuple:
    return 10, prec()

# integers are stored as the value and scaling factor: tuple[int,int]

# you can only return tuples and numbers

def add(n1: tuple, n2: tuple) -> tuple:
    # assuming that s1 and s2 are the same, otherwise we must convert res = lcm(s1,s2)
    return n1[0] + n2[0], n1[1]

# 'p/q' + 'a/q' = '(p+a)/q'

def sub(n1: tuple, n2: tuple) -> tuple:
    # assuming that s1 and s2 are the same, otherwise we must convert res = lcm(s1,s2)
    return n1[0] - n2[0], n1[1]

def mul_trunc(n1: tuple, n2: tuple) -> tuple:
    return (n1[0]*n2[0]) // n1[1], n1[1]
    # 'a/b * c/d = ac/bd = (ac * (1/d))/(bd * 1/d) = ac/b'
    # print(f"{n1[0]/n1[1]} * {n2[0]/n2[1]} ~= {res[0]/res[1]}")

def make_fixed(n: int) -> tuple:
    return n*prec(), prec()

def f(x: tuple) -> tuple:
    # return add(add(mul_trunc(x,x),mul_trunc(make_fixed(2), x)), make_fixed(1))
    return mul_trunc(x,x)

def update(x: tuple, sum: tuple, lim: tuple) -> tuple:
    # print(f"x: {x} | sum: {sum} | lim: {lim}")
    d = delta()

    sum2 = add(sum, mul_trunc(f(x), d))
    x2 = add(x, d)

    dif = sub(x2, lim)[0] 

    if (dif < 0):
        # x2 < lim
        return update(x2, sum2, lim)
    else:
        # x >= lim
        return sum2

def integrate(lower: tuple, upper: tuple) -> tuple:
    return update(lower, (0,prec()), upper)

def run() -> None:
    x = integrate(make_fixed(0), make_fixed(5))
    print(x[0])
    print(x[1])

run()