def check(a):
    res = 0
    if a < 10:
        res = 123123
    else:
        res = check(a+1)
    return res