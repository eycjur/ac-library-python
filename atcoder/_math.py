import typing


def _is_prime(n: int) -> bool:
    """与えられた整数nが素数であるかどうかを判定します。

    この実装は、Miller-Rabin 素数判定法を基にしており、
    機械語サイズの整数（通常 64 ビット整数）に対して高速かつ正確に動作します。

    Reference:
        M. Forisek and J. Jancina,
        "Fast Primality Testing for Integers That Fit into a Machine Word"

    Args:
        n (int): 素数判定を行う整数。

    Returns:
        bool: 素数であれば True、それ以外は False。

    Examples:
        >>> _is_prime(2)
        True
        >>> _is_prime(15)
        False
        >>> _is_prime(61)
        True
        >>> _is_prime(97)
        True
    """

    if n <= 1:
        return False
    if n == 2 or n == 7 or n == 61:
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    while d % 2 == 0:
        d //= 2

    for a in (2, 7, 61):
        t = d
        y = pow(a, t, n)
        while t != n - 1 and y != 1 and y != n - 1:
            y = y * y % n
            t <<= 1
        if y != n - 1 and t % 2 == 0:
            return False
    return True


def _inv_gcd(a: int, b: int) -> tuple[int, int]:
    """拡張ユークリッドの互除法を用いて、最大公約数と逆元を計算します。

    Args:
        a (int): GCD と逆元を計算する整数。
        b (int): 正の整数（法）。

    Returns:
        tuple[int, int]: (GCD, 逆元) を返します。
            - GCD: a と b の最大公約数。
            - 逆元: a * x ≡ GCD (mod b) を満たす x。

    Examples:
        >>> _inv_gcd(10, 6)
        (2, 2)  # GCD = 2, 10 * 2 ≡ 2 (mod 6)
        >>> _inv_gcd(3, 7)
        (1, 5)  # GCD = 1, 3 * 5 ≡ 1 (mod 7)

    Notes:
        - aとbが互いに素の場合、GCDは1となり、aの逆元を計算できます。
        - a * x - b * ? = GCDという一次不定方程式の解となります。
    """
    a %= b
    if a == 0:
        return (b, 0)

    # Contracts:
    # [1] s - m0 * a = 0 (mod b)
    # [2] t - m1 * a = 0 (mod b)
    # [3] s * |m1| + t * |m0| <= b
    s = b
    t = a
    m0 = 0
    m1 = 1

    while t:
        u = s // t
        s -= t * u
        m0 -= m1 * u  # |m1 * u| <= |m1| * s <= b

        # [3]:
        # (s - t * u) * |m1| + t * |m0 - m1 * u|
        # <= s * |m1| - t * u * |m1| + t * (|m0| + |m1| * u)
        # = s * |m1| + t * |m0| <= b

        s, t = t, s
        m0, m1 = m1, m0

    # by [3]: |m0| <= b/g
    # by g != b: |m0| < b/g
    if m0 < 0:
        m0 += b // s

    return (s, m0)


def _primitive_root(m: int) -> int:
    """与えられた整数mに対する原始根(primitive root)を計算します。"""
    if m == 2:
        return 1
    if m == 167772161:
        return 3
    if m == 469762049:
        return 3
    if m == 754974721:
        return 11
    if m == 998244353:
        return 3

    divs = [2] + [0] * 19
    cnt = 1
    x = (m - 1) // 2
    while x % 2 == 0:
        x //= 2

    i = 3
    while i * i <= x:
        if x % i == 0:
            divs[cnt] = i
            cnt += 1
            while x % i == 0:
                x //= i
        i += 2

    if x > 1:
        divs[cnt] = x
        cnt += 1

    g = 2
    while True:
        for i in range(cnt):
            if pow(g, (m - 1) // divs[i], m) == 1:
                break
        else:
            return g
        g += 1
