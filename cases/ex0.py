def const() -> tuple:
    x = 66
    def lol() -> tuple:
        return x + 1, 0
    
    def g(x: int) -> None:
        print(x)

    g(5)
    a = lol()[0]
    b = (2, 1234)[1]
    return a,b
print(const())
# def tuple_double(x: tuple):
#     return x[0] * 2, x[1] * 2

# def double(x: int):
#     if (x):
#         return x * 2
#     else:
#         return x + 67

# def main():
#     return 1