"""
Построение m ярусов планарного графа l(v, g).

Параметры:
    m — число ярусов (положительное целое)
    v — степень вершин
    g — обхват графа

Алгоритм:
  Ярус 0: {0}.
  Ярус 1: вершины 1..v на окружности радиуса 1, соединённые с 0.
          У каждой свободных рёбер = v−1.
  Ярус k (k=2..m):
    Каждая вершина P предыдущего яруса порождает столько кандидатов,сколько у неё свободных рёбер. Кандидаты расположены в планарном порядке «слева направо» при взгляде наружу.
    Для каждой соседней пары родителей (P1, P2) из (k−1)-го яруса
    смотрим правого кандидата P1 и левого кандидата P2:
        d = dist(P1, P2) в уже построенном графе:
        если 2 + d == g  → слить эти две вершины в одну (цикл длины g);
        если 3 + d == g  → соединить их ребром (цикл длины g);
        иначе            → оставить независимыми.
    Граничная вершина получает v−2 свободных рёбер, остальные — v−1.
"""
from collections import defaultdict, deque

def _bfs_distance(src, dst, adj):
    if src == dst:
        return 0
    visited = {src}
    queue = deque([(src, 0)])
    while queue:
        u, d = queue.popleft()
        for w in adj[u]:
            if w == dst:
                return d + 1
            if w not in visited:
                visited.add(w)
                queue.append((w, d + 1))
    return None

def build_planar_graph(m, v, g):
    """Возвращает (tier_vertices, tier_edges) — списки вершин и рёбер,
    добавленных на каждом ярусе 0..m."""
    if m < 0:
        raise ValueError("m должно быть неотрицательным")
    if v < 2:
        raise ValueError("v должно быть >= 2")
    if g < 3:
        raise ValueError("g должно быть >= 3")

    all_edges = []
    tier_vertices = [[0]]
    tier_edges = [[]]
    tier_order = [[0]]          # циркулярный порядок каждого яруса
    free_edges = {0: v}         # счётчик свободных рёбер у каждой вершины
    next_id = 1

    # --- Ярус 1 ---
    if m >= 1:
        t1 = list(range(1, v + 1))
        tier_order.append(t1)
        edges_1 = [(0, vi) for vi in t1]
        for vi in t1:
            free_edges[vi] = v - 1
        free_edges[0] = 0
        all_edges.extend(edges_1)
        tier_vertices.append(t1[:])
        tier_edges.append(edges_1)
        next_id = v + 1

    # --- Ярусы 2..m ---
    for k in range(2, m + 1):
        prev_tier = tier_order[k - 1]
        n_prev = len(prev_tier)

        adj = defaultdict(set)
        for a, b in all_edges:
            adj[a].add(b)
            adj[b].add(a)

        # Кандидаты-дети для каждого родителя в планарном порядке
        parent_to_children = {}
        for P in prev_tier:
            f = free_edges.get(P, 0)
            parent_to_children[P] = list(range(next_id, next_id + f))
            next_id += f

        # Определяем граничные операции между соседними родителями
        merge_pairs = []
        edge_pairs = []
        for i in range(n_prev):
            P1 = prev_tier[i]
            P2 = prev_tier[(i + 1) % n_prev]
            ch1 = parent_to_children[P1]
            ch2 = parent_to_children[P2]
            if not ch1 or not ch2:
                continue
            c1_right = ch1[-1]
            c2_left = ch2[0]
            d = _bfs_distance(P1, P2, adj)
            if d is None:
                continue
            if 2 + d == g:
                merge_pairs.append((c1_right, c2_left))
            elif 3 + d == g:
                edge_pairs.append((c1_right, c2_left))

        # Применяем слияния через систему непересекающихся множеств
        uf = {}

        def find(x):
            while x in uf:
                x = uf[x]
            return x

        for a, b in merge_pairs:
            ra, rb = find(a), find(b)
            if ra != rb:
                uf[rb] = ra     # b сливается в a, сохраняется меньший id (a)

        # Собираем новый ярус в циркулярном порядке и родительские рёбра
        new_tier = []
        seen = set()
        added_in_tier = []
        new_edges_this_tier = []

        for P in prev_tier:
            for c in parent_to_children[P]:
                fc = find(c)
                if fc not in seen:
                    new_tier.append(fc)
                    seen.add(fc)
                    added_in_tier.append(fc)
                new_edges_this_tier.append((P, fc))

        # Добавляем граничные (обхватные) рёбра
        for a, b in edge_pairs:
            new_edges_this_tier.append((find(a), find(b)))

        all_edges.extend(new_edges_this_tier)

        # Свободные рёбра у новых вершин
        boundary_vs = set()
        for a, b in merge_pairs:
            boundary_vs.add(find(a))
        for a, b in edge_pairs:
            boundary_vs.add(find(a))
            boundary_vs.add(find(b))
        for nv in added_in_tier:
            free_edges[nv] = (v - 2) if nv in boundary_vs else (v - 1)

        tier_order.append(new_tier)
        tier_vertices.append(added_in_tier)
        tier_edges.append(new_edges_this_tier)

    return tier_vertices, tier_edges


def print_graph(m, v, g):
    tv, te = build_planar_graph(m, v, g)
    print(f"Планарный граф l({v}, {g}), число ярусов m = {m}")
    for k in range(m + 1):
        print(f"Ярус {k}")
        print(f"  список вершин: {tv[k]}")
        print(f"  список рёбер:  {te[k]}")


if __name__ == "__main__":
    # Параметры по умолчанию — пример из условия задачи.
    try:
        raw = input("Введите m v g или Enter для примера (3 4 5): ").strip()
    except EOFError:
        raw = ""
    if raw:
        m, v, g = map(int, raw.split())
    else:
        m, v, g = 3, 4, 5
    print_graph(m, v, g)