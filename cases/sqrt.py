def sqrt(n: int):
    def sqrt_inner(i):
        if n < (i + 1) * (i + 1):
            return i
        else:
            return sqrt_inner(i+1)
    
    return sqrt_inner(0)