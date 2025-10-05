def fib(x: int, y: int) -> int:
    print(x)
    if 1000 < x:
        return y
    else:
        return fib(x+y, x)