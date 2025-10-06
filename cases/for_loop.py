def fun(n: int) -> None:
    print(n)

    return

def loop(n: int) -> None:
    fun(n)
    if 0 < n:
        loop(n-1)
    else:
        pass

    return