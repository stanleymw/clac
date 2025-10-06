def sqrt(n: int) -> int:
    def sqrt_inner(n: int, i: int) -> int:
        if n < (i + 1) ** 2:
            return i
        else:
            return sqrt_inner(n, i+1)
    
    return sqrt_inner(n, 0)