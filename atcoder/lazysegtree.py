import typing

import atcoder._bit


class LazySegTree:
    """
    遅延セグメントツリー (Lazy Segment Tree) を実装したクラス。

    このクラスは、モノイドと写像を用いた区間更新および区間クエリを効率的に処理します。
    主な機能は以下の通りです：
    - 区間に対して写像を適用（例: 加算、値の一括更新など）
    - 区間に対する二項演算結果の取得（例: 区間和、区間最小値など）
    - 配列全体や区間内で条件を満たす最大/最小の位置の探索（二分探索）

    Args:
        op (Callable[[Any, Any], Any]): モノイドの二項演算を行う関数(min, operator.add など)
        e (Any): モノイドの単位元(例：区間和なら 0、区間最小値なら正の無限大)
        mapping (Callable[[Any, Any], Any]): 写像を適用する関数(ex. operator.add)
        composition (Callable[[Any, Any], Any]): 写像の合成を行う関数(ex. operator.add)
        id_ (Any): 写像の単位元(例：加算なら 0、乗算なら 1)
        v (Union[int, List[Any]]): 初期化用の配列または配列の長さ。
            - 配列の場合、その内容が初期値となります。
            - 整数の場合、長さがその整数で単位元で初期化された配列として扱います。

    Attributes:
        _op (Callable): モノイドの二項演算関数。
        _e (Any): モノイドの単位元。
        _mapping (Callable): 写像の適用関数。
        _composition (Callable): 写像の合成関数。
        _id (Any): 写像の単位元。
        _n (int): 配列の長さ。
        _log (int): セグメントツリーの高さ。
        _size (int): セグメントツリーのノード数(2の冪乗)=葉ノードの開始位置。
        _d (List[Any]): セグメントツリーのデータ配列(_d[1]が根)
        _lz (List[Any]): 遅延用の写像配列。

    Methods:
        set(p, x): 指定位置の値を更新します。
        get(p): 指定位置の値を取得します。
        prod(left, right): 指定した区間の要素に対する二項演算結果を返します。
        all_prod(): 配列全体の要素に対する二項演算結果を返します。
        apply(left, right, f): 区間または単一点に写像を適用します。
        max_right(left, g): 条件を満たす最大の右端を二分探索で求めます。
        min_left(right, g): 条件を満たす最小の左端を二分探索で求めます。

    Examples:
        >>> op = min  # 区間最小値
        >>> e = float('inf')  # 単位元
        >>> mapping = lambda f, x: f + x
        >>> composition = lambda f, g: f + g
        >>> id_ = 0  # 恒等写像
        >>> seg = LazySegTree(op, e, mapping, composition, id_, [5, 3, 7, 9, 6])
        >>> seg
        [Segment Tree]
        |                      3                      |
        |          3           |           6          |
        |    3     |     7     |     6     |     e    |
        | 5  |  3  |  7  |  9  |  6  |  e  |  e  |  e |

        [Lazy Propagation]
        |         id          |
        |   id     |    id    |
        |id  | id  | id  | id |
        >>> seg.values
        [5, 3, 7, 9, 6]
        >>> seg.prod(1, 4)  # 区間最小値
        3
        >>> seg.apply(2, 5, 1)  # 区間に 1 を加算
        >>> seg
        [Segment Tree]
        |                      3                      |
        |          3           |           7          |
        |    3     |     8     |     7     |     e    |
        | 5  |  3  |  7  |  9  |  7  |  e  |  e  |  e |

        [Lazy Propagation]
        |         id          |
        |   id     |    id    |
        |id  |  1  | id  | id |
        >>> seg.values  # このとき、lazy配列も反映される
        [5, 3, 8, 10, 7]
        >>> seg.prod(1, 4)  # 更新後の区間最小値
        3
        >>> seg.get(2)  # 要素の取得
        8
    """

    def __init__(
        self,
        op: typing.Callable[[typing.Any, typing.Any], typing.Any],
        e: typing.Any,
        mapping: typing.Callable[[typing.Any, typing.Any], typing.Any],
        composition: typing.Callable[[typing.Any, typing.Any], typing.Any],
        id_: typing.Any,
        v: typing.Union[int, typing.List[typing.Any]]
    ) -> None:
        self._op = op
        self._e = e
        self._mapping = mapping
        self._composition = composition
        self._id = id_

        if isinstance(v, int):
            v = [e] * v

        self._n = len(v)
        self._log = atcoder._bit._ceil_pow2(self._n)
        self._size = 1 << self._log
        self._d = [e] * (2 * self._size)
        self._lz = [self._id] * self._size
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
        for i in range(self._log, 0, -1):
            self._push(p >> i)
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

        p += self._size
        for i in range(self._log, 0, -1):
            self._push(p >> i)
        return self._d[p]

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

        if left == right:
            return self._e

        left += self._size
        right += self._size

        for i in range(self._log, 0, -1):
            if ((left >> i) << i) != left:
                self._push(left >> i)
            if ((right >> i) << i) != right:
                self._push((right - 1) >> i)

        sml = self._e
        smr = self._e
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

    def apply(
        self, left: int,
        right: typing.Optional[int] = None,
        f: typing.Optional[typing.Any] = None
    ) -> None:
        """区間[left, right)に写像を適用します。

        Args:
            left (int): 区間の開始位置(0-indexed)。
            right (Optional[int]): 区間の終了位置(0-indexed, 開始位置を含み終了位置を含まない）。
                None の場合は単一点に適用します。
            f (Any): 適用する写像(x = mapping(f, x)のように更新される)

        Time Complexity:
            O(log n): ツリーの高さに比例します。
        """
        assert f is not None

        if right is None:
            p = left
            assert 0 <= left < self._n

            p += self._size
            for i in range(self._log, 0, -1):
                self._push(p >> i)
            self._d[p] = self._mapping(f, self._d[p])
            for i in range(1, self._log + 1):
                self._update(p >> i)
        else:
            assert 0 <= left <= right <= self._n
            if left == right:
                return

            left += self._size
            right += self._size

            for i in range(self._log, 0, -1):
                if ((left >> i) << i) != left:
                    self._push(left >> i)
                if ((right >> i) << i) != right:
                    self._push((right - 1) >> i)

            l2 = left
            r2 = right
            while left < right:
                if left & 1:
                    self._all_apply(left, f)
                    left += 1
                if right & 1:
                    right -= 1
                    self._all_apply(right, f)
                left >>= 1
                right >>= 1
            left = l2
            right = r2

            for i in range(1, self._log + 1):
                if ((left >> i) << i) != left:
                    self._update(left >> i)
                if ((right >> i) << i) != right:
                    self._update((right - 1) >> i)

    def max_right(
        self, left: int, g: typing.Callable[[typing.Any], bool]
    ) -> int:
        """op([left, max_right))で関数gを満たすmax_rightを返します(二分探索)、max_rightはfを満たさないことに注意

        Args:
            left (int): 探索区間の左端(0-indexed)
            g (Callable[[Any], bool]): 条件を満たすかどうかを判定する関数

        Returns:
            int: max_right

        計算量: O(logN)
        """
        assert 0 <= left <= self._n
        assert g(self._e)

        if left == self._n:
            return self._n

        left += self._size
        for i in range(self._log, 0, -1):
            self._push(left >> i)

        sm = self._e
        first = True
        while first or (left & -left) != left:
            first = False
            while left % 2 == 0:
                left >>= 1
            if not g(self._op(sm, self._d[left])):
                while left < self._size:
                    self._push(left)
                    left *= 2
                    if g(self._op(sm, self._d[left])):
                        sm = self._op(sm, self._d[left])
                        left += 1
                return left - self._size
            sm = self._op(sm, self._d[left])
            left += 1

        return self._n

    def min_left(self, right: int, g: typing.Callable[[typing.Any], bool]) -> int:
        """op([min_left, right))で関数gを満たすmin_leftを返します(二分探索)、min_leftはfを満たすことに注意

        Args:
            right (int): 探索区間の右端(0-indexed)
            g (Callable[[Any], bool]): 条件を満たすかどうかを判定する関数

        Returns:
            int: min_left

        計算量: O(logN)
        """
        assert 0 <= right <= self._n
        assert g(self._e)

        if right == 0:
            return 0

        right += self._size
        for i in range(self._log, 0, -1):
            self._push((right - 1) >> i)

        sm = self._e
        first = True
        while first or (right & -right) != right:
            first = False
            right -= 1
            while right > 1 and right % 2:
                right >>= 1
            if not g(self._op(self._d[right], sm)):
                while right < self._size:
                    self._push(right)
                    right = 2 * right + 1
                    if g(self._op(self._d[right], sm)):
                        sm = self._op(self._d[right], sm)
                        right -= 1
                return right + 1 - self._size
            sm = self._op(self._d[right], sm)

        return 0

    def _update(self, k: int) -> None:
        """内部ノードの値を子ノードの値を元に更新します。

        Args:
            k (int): 更新対象のノードの位置(0-indexed)。

        Notes:
            この関数は、子ノードの値から親ノードの値を計算するために使用されます。

        Time Complexity:
            O(1): 定数時間で動作します。
        """
        self._d[k] = self._op(self._d[2 * k], self._d[2 * k + 1])

    def _all_apply(self, k: int, f: typing.Any) -> None:
        """指定したノードに写像を適用し、遅延配列に反映します。

        Args:
            k (int): 適用対象のノードの位置(0-indexed)。
            f (Any): 適用する写像。

        Notes:
            この関数は、指定ノードに即座に写像を適用し、遅延情報も更新します。

        Time Complexity:
            O(1): 定数時間で動作します。
        """
        self._d[k] = self._mapping(f, self._d[k])
        if k < self._size:
            self._lz[k] = self._composition(f, self._lz[k])

    def _push(self, k: int) -> None:
        """指定したノードの遅延情報を子ノードに伝播させます。

        Args:
            k (int): 遅延情報を伝播するノードの位置(0-indexed)。

        Notes:
            遅延配列 `_lz` の値を子ノードに反映し、現在のノードの遅延情報をリセットします。

        Time Complexity:
            O(1): 定数時間で動作します。
        """
        self._all_apply(2 * k, self._lz[k])
        self._all_apply(2 * k + 1, self._lz[k])
        self._lz[k] = self._id

    @property
    def values(self) -> typing.List[typing.Any]:
        """セグメントツリーの値をリストで返します

        Returns:
            List[Any]: セグメントツリーの値

        計算量: O(N)
        """
        return [self.get(i) for i in range(self._n)]

    def __str__(self) -> str:
        """
        遅延セグメントツリーを階層構造で可視化します。

        Returns:
            str: セグメントツリーと遅延配列の文字列表現。
        """
        levels = []
        level_start = 1
        while level_start < len(self._d):
            levels.append(self._d[level_start:level_start * 2])
            level_start *= 2

        result = ["[Segment Tree]"]
        max_width = max(len(str(item)) for item in self._d if item != self._e) if self._d else 1
        max_width = max(max_width, 2)
        max_width = max_width // 2 * 2 + 1  # 奇数にする

        for i, level in enumerate(levels):
            padding = " " * ((2 ** (len(levels) - i - 1)) - 1) * max_width
            line = padding
            len_spacing = ((2 ** (len(levels) - i)) - 1) * max_width
            spacing = " " * (len_spacing // 2) + "|" + " " * (len_spacing // 2)
            line += spacing.join(f"{str(item):^{max_width}}" if item != self._e else f"{'e':^{max_width}}" for item in level)
            line += padding
            result.append(f"|{line}|")

        result.append("\n[Lazy Propagation]")
        lazy_levels = []
        level_start = 1
        while level_start < len(self._lz):
            lazy_levels.append(self._lz[level_start:level_start * 2])
            level_start *= 2

        for i, level in enumerate(lazy_levels):
            padding = " " * ((2 ** (len(lazy_levels) - i - 1)) - 1) * max_width
            line = padding
            len_spacing = ((2 ** (len(lazy_levels) - i)) - 1) * max_width
            spacing = " " * (len_spacing // 2) + "|" + " " * (len_spacing // 2)
            line += spacing.join(f"{str(item):^{max_width}}" if item != self._id else f"{'id':^{max_width}}" for item in level)
            line += padding
            result.append(f"|{line}|")

        return "\n".join(result)
