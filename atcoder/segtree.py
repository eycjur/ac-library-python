import typing

import atcoder._bit


class SegTree:
    """セグメントツリーを実装したクラス

    以下の操作を効率的に行います
    - 要素の更新
    - 任意区間の要素に対する二項演算（例: 区間和、区間最小値など）
    - 配列全体や区間内での条件を満たす最大/最小の位置の探索（二分探索）

    Args:
        op (Callable[[Any, Any], Any]): モノイドの二項演算を行う関数(min, operator.add など)
        e (Any): モノイドの単位元(例：区間和なら 0、区間最小値なら正の無限大)
        v (Union[int, List[Any]]): 初期化用の配列または配列の長さ。
            - 配列の場合、その内容を初期値とします。
            - 整数の場合、長さがその整数で単位元で初期化された配列として扱います。

    Attributes:
        _op (Callable): 二項演算の関数。
        _e (Any): モノイドの単位元。
        _n (int): 配列の要素数。
        _log (int): セグメントツリーの高さ。
        _size (int): セグメントツリーのノード数(2の冪乗)=葉ノードの開始位置
        _d (List[Any]): セグメントツリーの内部配列(_d[1]が根)。

    Methods:
        set(p, x):
            指定位置の要素を更新します(0-indexed)。
        get(p):
            指定位置の要素を取得します(0-indexed)。
        prod(left, right):
            指定した区間[left, right) の要素に対する二項演算結果を返します。
        all_prod():
            配列全体の要素に対する二項演算結果を返します。
        max_right(left, f):
            op([left, max_right))で関数fを満たすmax_rightを返します(二分探索)、max_rightはfを満たさないことに注意
        min_left(right, f):
            op([min_left, right))で関数fを満たすmin_leftを返します(二分探索)、min_leftはfを満たすことに注意
        values:
            要素を配列形式で文字列化して返します。
        __str__():
            セグメントツリーの内部配列を木形式で文字列化して返します。

    Examples:
        >>> op = min  # 区間最小値
        >>> e = float('inf')  # 単位元（正の無限大）
        >>> seg = SegTree(op, e, [5, 3, 7, 9, 6])
        >>> str(seg)
        |                      3                      |
        |          3           |           6          |
        |    3     |     7     |     6     |     e    |
        | 5  |  3  |  7  |  9  |  6  |  e  |  e  |  e |
        >>> seg.values
        [5, 3, 7, 9, 6]
        >>> seg.prod(1, 4)  # 区間最小値
        3
        >>> seg.set(1, 1)  # 要素の更新
        >>> seg.values
        [5, 1, 7, 9, 6]
        >>> seg.prod(1, 4)  # 更新後の区間最小値
        1
        >>> seg.get(1)  # 要素の取得
        1
        >>> seg.all_prod()  # 配列全体の最小値
        1
        >>> seg.max_right(2, lambda x: x >= 7)  # 条件を満たす最大右端+1
        4
        >>> seg.min_left(4, lambda x: x >= 7)  # 条件を満たす最小左端
        2
    """

    def __init__(self,
                 op: typing.Callable[[typing.Any, typing.Any], typing.Any],
                 e: typing.Any,
                 v: typing.Union[int, typing.List[typing.Any]]) -> None:
        self._op = op
        self._e = e

        if isinstance(v, int):
            v = [e] * v

        self._n = len(v)
        self._log = atcoder._bit._ceil_pow2(self._n)
        self._size = 1 << self._log
        self._d = [e] * (2 * self._size)

        for i in range(self._n):
            self._d[self._size + i] = v[i]
        for i in range(self._size - 1, 0, -1):
            self._update(i)

    def set(self, p: int, x: typing.Any) -> None:
        """指定位置の要素を更新します(0-indexed)

        Args:
            p (int): 更新する位置(0-indexed)
            x (Any): 更新する値

        計算量: O(logN)
        """
        assert 0 <= p < self._n

        p += self._size
        self._d[p] = x
        for i in range(1, self._log + 1):
            self._update(p >> i)

    def get(self, p: int) -> typing.Any:
        """指定位置の要素を取得します(0-indexed)

        Args:
            p (int): 取得する位置(0-indexed)

        Returns:
            Any: 指定位置の要素

        計算量: O(1)
        """
        assert 0 <= p < self._n

        return self._d[p + self._size]

    def prod(self, left: int, right: int) -> typing.Any:
        """指定した区間[left, right) の要素に対する二項演算結果を返します

        Args:
            left (int): 区間の左端(0-indexed)
            right (int): 区間の右端(0-indexed)

        Returns:
            Any: 演算結果

        計算量: O(logN)
        """
        assert 0 <= left <= right <= self._n
        sml = self._e
        smr = self._e
        left += self._size
        right += self._size

        while left < right:
            if left & 1:
                sml = self._op(sml, self._d[left])
                left += 1
            if right & 1:
                right -= 1
                smr = self._op(self._d[right], smr)
            left >>= 1
            right >>= 1

        return self._op(sml, smr)

    def all_prod(self) -> typing.Any:
        """配列全体の要素に対する二項演算結果を返します

        Returns:
            Any: 演算結果

        計算量: O(1)
        """
        return self._d[1]

    def max_right(self, left: int, f: typing.Callable[[typing.Any], bool]) -> int:
        """op([left, max_right))で関数fを満たすmax_rightを返します(二分探索)、max_rightはfを満たさないことに注意

        Args:
            left (int): 探索区間の左端(0-indexed)
            f (Callable[[Any], bool]): 条件を満たすかどうかを判定する関数

        Returns:
            int: max_right

        計算量: O(logN)
        """
        assert 0 <= left <= self._n
        assert f(self._e)

        if left == self._n:
            return self._n

        left += self._size
        sm = self._e

        first = True
        while first or (left & -left) != left:
            first = False
            while left % 2 == 0:
                left >>= 1
            if not f(self._op(sm, self._d[left])):
                while left < self._size:
                    left *= 2
                    if f(self._op(sm, self._d[left])):
                        sm = self._op(sm, self._d[left])
                        left += 1
                return left - self._size
            sm = self._op(sm, self._d[left])
            left += 1

        return self._n

    def min_left(self, right: int, f: typing.Callable[[typing.Any], bool]) -> int:
        """op([min_left, right))で関数fを満たすmin_leftを返します(二分探索)、min_leftはfを満たすことに注意

        Args:
            right (int): 探索区間の右端(0-indexed)
            f (Callable[[Any], bool]): 条件を満たすかどうかを判定する関数

        Returns:
            int: min_left

        計算量: O(logN)
        """
        assert 0 <= right <= self._n
        assert f(self._e)

        if right == 0:
            return 0

        right += self._size
        sm = self._e

        first = True
        while first or (right & -right) != right:
            first = False
            right -= 1
            while right > 1 and right % 2:
                right >>= 1
            if not f(self._op(self._d[right], sm)):
                while right < self._size:
                    right = 2 * right + 1
                    if f(self._op(self._d[right], sm)):
                        sm = self._op(self._d[right], sm)
                        right -= 1
                return right + 1 - self._size
            sm = self._op(self._d[right], sm)

        return 0

    def _update(self, k: int) -> None:
        self._d[k] = self._op(self._d[2 * k], self._d[2 * k + 1])

    @property
    def values(self) -> typing.List[typing.Any]:
        return self._d[self._size:self._size + self._n]

    def __str__(self) -> str:
        levels = []
        level_start = 1
        while level_start < len(self._d):
            levels.append(self._d[level_start:level_start * 2])
            level_start *= 2

        result = []
        max_width = len("{}".format(max(self._d, key=lambda x: len(str(x)) if x != self._e else 1, default=self._e)))
        max_width = max_width // 2 * 2 + 1  # 奇数にする
        for i, level in enumerate(levels):
            padding = " " * ((2 ** (len(levels) - i - 1)) - 1) * max_width
            line = padding
            len_spacing = ((2 ** (len(levels) - i)) - 1) * max_width
            spacing = " " * (len_spacing // 2) + "|" + " " * (len_spacing // 2)
            line += spacing.join(f"{str(item):^{max_width}}" if item != self._e else f"{'e':^{max_width}}" for item in level)
            line += padding
            result.append(f"|{line}|")
        return "\n".join(result)
