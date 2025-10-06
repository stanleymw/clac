def loop(n):
    if n % 2:
        # n%2 != 0
        pass
    else:
        # n%2 == 0
        print(n)

    if 32 < n:
        pass
    else:
        loop(n+1)
    return

loop(0)