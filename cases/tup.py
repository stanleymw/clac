def add(tup):
    return tup[0] + 1, tup[1] + 2


def main():
    one = 1
    cur = (6,7)
    res = add(cur)
    print(res)