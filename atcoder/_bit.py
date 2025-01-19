def _ceil_pow2(n: int) -> int:
    """nを超えない最小の2の累乗(2^x >= n)の指数xを計算します

    Args:
        n (int): 2 の累乗を計算するための正の整数

    Returns:
        int: 2^x >= nを満たす最小の整数x

    Examples:
        >>> _ceil_pow2(7)
        3  # 2^3 = 8 >= 7
        >>> _ceil_pow2(16)
        4  # 2^4 = 16 >= 16
    """
    x = 0
    while (1 << x) < n:
        x += 1

    return x


def _bsf(n: int) -> int:
    """整数nの最下位ビットが1である位置を計算します

    Args:
        n (int): 正の整数。

    Returns:
        int: 最下位ビットの位置(0-indexed)。

    Examples:
        >>> _bsf(8)
        3  # 8 = 1000(2), 最下位ビットの1の位置は3
        >>> _bsf(10)
        1  # 10 = 1010(2), 最下位ビットの1の位置は1
    """
    x = 0
    while n % 2 == 0:
        x += 1
        n //= 2

    return x
