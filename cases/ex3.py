def mul(x: int, y: int) -> int:
    # if x:
    #     return 1
    # else:
    #     if y:
    #         return 2
    #     else:
    #         return x*y
    return x * y

def main():
    x = (4//2) * 5
    y = x + 1
    z = mul(x,y)

    print(z)

    a = x + y + z
    print(a)