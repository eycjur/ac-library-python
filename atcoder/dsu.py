import typing


class DSU:
    """Disjoint Set Union (Union-Find) を実装したクラス。

    無向グラフの連結成分を管理するためのデータ構造です。以下の操作を効率的に行います：
    - 頂点間の連結クエリ (同じ連結成分に属するかの判定)
    - 頂点間の連結成分の統合 (Union 操作)
    - 各連結成分のサイズや構造の取得

    Args:
        n (int): 頂点の数。

    Attributes:
        _n (int): 頂点の数。
        parent_or_size (List[int]): 各頂点の親またはサイズを管理する配列。
            - 負の値の場合、その頂点が連結成分の代表元であり、値の絶対値は成分サイズ(要素数)を示す。
            - 正の値の場合、その頂点の親のインデックスを示す。

    Methods:
        merge(a, b):
            辺 (a, b) を追加し、2つの連結成分を統合します。
        same(a, b):
            頂点 a と b が同じ連結成分に属するかを判定します。
        leader(a):
            頂点 a の属する連結成分の代表元を返します。
        size(a):
            頂点 a の属する連結成分のサイズ(要素数)を返します。
        groups():
            現在のグラフを連結成分ごとに分けた結果を返します。

    Examples:
        >>> uf = UnionFind(5)  # 頂点数5のグラフを作成
        >>> uf              # 連結成分ごとの頂点番号のリストを取得
        [[0], [1], [2], [3], [4]]
        >>> uf.merge(1, 2)  # 辺 (1, 2) を追加
        >>> uf              # 連結成分ごとの頂点番号のリストを取得
        [[0], [1, 2], [3], [4]]
        >>> uf.same(1, 2)   # 頂点 1 と 2 が連結かを判定
        True
        >>> uf.same(1, 3)   # 頂点 1 と 3  が連結かを判定
        False
        >>> uf.size(1)      # 頂点 1 の属する連結成分のサイズを取得
        2
    """

    def __init__(self, n: int = 0) -> None:
        self._n = n
        self.parent_or_size = [-1] * n

    def merge(self, a: int, b: int) -> int:
        """辺 (a, b) を追加し、2つの連結成分を統合します。

        Args:
            a (int): 辺の一方の頂点。
            b (int): 辺の他方の頂点。

        Returns:
            int: 新たな連結成分の代表元。

        Notes:
            - すでに連結な場合は、変更せず現在の代表元を返します。

        計算量: ならしO(alpha(n))
        """
        assert 0 <= a < self._n
        assert 0 <= b < self._n

        x = self.leader(a)
        y = self.leader(b)

        if x == y:
            return x

        if -self.parent_or_size[x] < -self.parent_or_size[y]:
            x, y = y, x

        self.parent_or_size[x] += self.parent_or_size[y]
        self.parent_or_size[y] = x

        return x

    def same(self, a: int, b: int) -> bool:
        """頂点 a と b が同じ連結成分に属するかを判定します。

        Args:
            a (int): 判定する一方の頂点。
            b (int): 判定する他方の頂点。

        Returns:
            bool: 同じ連結成分に属する場合は True、それ以外は False。

        計算量: ならし O(alpha(n))
        """
        assert 0 <= a < self._n
        assert 0 <= b < self._n

        return self.leader(a) == self.leader(b)

    def leader(self, a: int) -> int:
        """頂点 a の属する連結成分の代表元を返します。

        Args:
            a (int): 対象の頂点。

        Returns:
            int: 連結成分の代表元。

        計算量: ならし O(alpha(n))
        """
        assert 0 <= a < self._n

        parent = self.parent_or_size[a]
        while parent >= 0:
            if self.parent_or_size[parent] < 0:
                return parent
            self.parent_or_size[a], a, parent = (
                self.parent_or_size[parent],
                self.parent_or_size[parent],
                self.parent_or_size[self.parent_or_size[parent]]
            )

        return a

    def size(self, a: int) -> int:
        """頂点 a の属する連結成分のサイズ(要素数)を返します。

        Args:
            a (int): 対象の頂点。

        Returns:
            int: 連結成分のサイズ。

        計算量: ならし O(alpha(n))
        """
        assert 0 <= a < self._n

        return -self.parent_or_size[self.leader(a)]

    def groups(self) -> typing.List[typing.List[int]]:
        """現在のグラフを連結成分ごとに分けた結果を返します。

        Returns:
            List[List[int]]: 各連結成分の頂点番号のリスト。

        計算量: ならし O(n)
        """
        leader_buf = [self.leader(i) for i in range(self._n)]

        result: typing.List[typing.List[int]] = [[] for _ in range(self._n)]
        for i in range(self._n):
            result[leader_buf[i]].append(i)

        return list(filter(lambda r: r, result))

    def __str__(self) -> str:
        return str(self.groups())
