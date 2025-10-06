# def const() -> tuple:
#     x = 66
#     def lol() -> tuple:
#         return x + 1, 0
    
#     def g(x: int) -> None:
#         print(x)

#     a = lol()[0]
#     b = (2, 1234)[1]
#     g(a)
#     return a,b

# def tuple_double(x: tuple) -> tuple:
#     return x[0] * 2, x[1] * 2

# def fib(x: int, y: int) -> int:
#     print(x)
#     return fib(x+y, x)

def double(x: int) -> int:
    if (x):
        return x * 2
    else:
        return 1

def main() -> int:
    return 1