def double(x: tuple) -> int:
    print(x[0])
    print(x[1])
    return x[0]

def main() -> None:
    print(double((2,3)))