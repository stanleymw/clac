def fun(n):
    print(n)
    return

def loop(n):
    fun(n)
    if 0 < n:
        loop(n-1)
    else:
        pass
    return

loop(100)