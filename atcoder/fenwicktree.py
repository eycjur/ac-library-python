import typing


class FenwickTree:
    """フェニック木(Binary Indexed Tree, BIT)を実装したクラス。

    このクラスは、長さ N の配列に対して以下の操作を効率的に行います
    - 単一点の更新
    - 任意区間の要素の総和の計算

    Args:
        n (int): 配列の長さ。

    Attributes:
        _n (int): 配列の長さ。
        data (List[int]): 内部的に管理されるフェニック木の配列。

    Methods:
        add(p, x):
            指定した位置に値を加算します。
        sum(left, right):
            [left, right) の区間の総和を計算します。

    Examples:
        >>> fw = FenwickTree(5)  # 長さ5のフェニック木を作成
        >>> fw
        [0, 0, 0, 0, 0]
        >>> fw.add(1, 3)         # a[1] += 3
        >>> fw.add(3, 5)         # a[3] += 5
        >>> fw
        [0, 3, 0, 5, 0]
        >>> fw.sum(1, 4)         # a[1] + a[2] + a[3]
        8
    """

    def __init__(self, n: int = 0) -> None:
        self._n = n
        self.data = [0] * n

    def add(self, p: int, x: typing.Any) -> None:
        """指定した位置に値を加算します。

        Args:
            p (int): 更新する位置(0-indexed)。
            x (Any): 加算する値。

        計算量: O(log n)
        """
        assert 0 <= p < self._n

        p += 1
        while p <= self._n:
            self.data[p - 1] += x
            p += p & -p

    def sum(self, left: int, right: int) -> typing.Any:
        """[left, right) の区間の総和を計算します。

        Args:
            left (int): 区間の開始位置(0-indexed)
            right (int): 区間の終了位置(0-indexed)

        Returns:
            Any: 指定区間の総和。

        計算量: O(log n)
        """
        assert 0 <= left <= right <= self._n

        return self._sum(right) - self._sum(left)

    def _sum(self, r: int) -> typing.Any:
        """内部的に使用される累積和計算

        Args:
            r (int): 累積和の終了位置(0-indexed, 終了位置を含まない）。

        Returns:
            Any: 累積和。

        計算量: O(log n)
        """
        s = 0
        while r > 0:
            s += self.data[r - 1]
            r -= r & -r

        return s

    def __str__(self) -> str:
        return str([self.sum(i, i + 1) for i in range(self._n)])
