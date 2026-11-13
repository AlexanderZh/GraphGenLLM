from collections import deque
import json
import networkx as nx
import matplotlib.pyplot as plt


def calculate_min_distance(a, b, next_edges, edges):
    """
    Вычисляет минимальное расстояние между вершинами a и b с помощью BFS.

    Аргументы:
        a, b: вершины, для которых нужно найти расстояние
        next_edges: список рёбер текущего яруса
        edges: список списков рёбер из предыдущих ярусов

    Возвращает:
        Минимальное расстояние или float('inf'), если вершины недостижимы друг из друга
    """
    if a == b:
        return 0

    visited = set()
    queue = deque([(a, 0)])

    while queue:
        node, dist = queue.popleft()

        if node == b:
            return dist

        if node in visited:
            continue

        visited.add(node)

        # Проверяем рёбра текущего яруса (next_edges)
        for edge_a, edge_b in next_edges:
            if edge_a == node and edge_b not in visited:
                queue.append((edge_b, dist + 1))
            elif edge_b == node and edge_a not in visited:
                queue.append((edge_a, dist + 1))

        # Проверяем рёбра из предыдущих ярусов
        for tier_edges in edges:
            for edge_a, edge_b in tier_edges:
                if edge_a == node and edge_b not in visited:
                    queue.append((edge_b, dist + 1))
                elif edge_b == node and edge_a not in visited:
                    queue.append((edge_a, dist + 1))

    return float('inf')

def construct_planar_graph(m, v, g):
    """
    Строит m ярусов плоского графа l(v, g).

    Аргументы:
        m: количество ярусов для конструирования
        v: степень вершины
        g: обхват графа

    Возвращает:
        (vertices, edges) - vertices: список списков вершин по ярусам,
                           edges: список списков рёбер по ярусам
    """
    vertices = []
    edges = []
    p = {}  # словарь, хранящий количество свободных рёбер для каждой вершины

    # Инициализация 0-го яруса
    next_vertices = [0]
    next_edges = []
    h = 0  # накопленное количество вершин из предыдущих ярусов
    p[0] = v

    tier_count = 0

    # M1: Основной цикл конструирования - добавляем ярусы
    while tier_count < m:
        # M1: Добавляем текущий ярус к результату
        vertices.append(next_vertices[:])
        edges.append(next_edges[:])
        tier_count += 1

        if tier_count >= m:
            break

        # Строим вершины и рёбра следующего яруса
        current_vertices = vertices[-1]
        c = len(current_vertices) - 1  # Индекс последней вершины в текущем ярусе
        h += len(current_vertices)  # Обновляем накопленное количество вершин

        next_vertices = []
        next_edges = []

        j = 0
        # M3: Обрабатываем каждую вершину из предыдущего яруса
        while j <= c:
            b = current_vertices[j]

            if j == 0:
                # M4-M5: Специальный случай для первой вершины
                # Создаём p[b] новых вершин и соединяем их с b
                for i in range(1, p[b] + 1):
                    x = h + len(next_vertices)  # Индекс = h + количество уже добавленных вершин
                    next_vertices.append(x)
                    next_edges.append((b, x))
                    p[x] = v - 1  # Новые вершины имеют v-1 свободных рёбер

                j += 1

                if tier_count == 1:
                    break  # Переходим к M1 для 1-го яруса
                # Иначе продолжаем с M3 для следующей вершины
            else:
                # M7-M11: Последующие вершины
                i = 1

                while i <= p[b]:
                    if i == 1:
                        # M9: Обрабатываем первое ребро этой вершины
                        x_prev = next_vertices[-1]  # Последняя добавленная вершина
                        r = calculate_min_distance(b, x_prev, next_edges, edges)

                        if r == g - 1:
                            # Расстояние = g-1: соединяем напрямую с предыдущей вершиной
                            next_edges.append((b, x_prev))
                            p[x_prev] = v - 2
                        elif r == g - 2:
                            # Расстояние = g-2: вставляем промежуточную вершину
                            x = h + len(next_vertices)
                            next_vertices.append(x)
                            next_edges.append((x, x_prev))
                            next_edges.append((b, x))
                            p[x] = v - 2
                            p[x_prev] = v - 2
                        else:
                            # Обычный случай: создаём новую вершину и соединяем
                            x = h + len(next_vertices)
                            next_vertices.append(x)
                            next_edges.append((b, x))
                            p[x] = v - 1
                    elif i == p[b] and j == c:
                        # M11: Последнее ребро последней вершины (замыкающее ребро)
                        f = next_vertices[0]  # Первая вершина, созданная в этом ярусе
                        r = calculate_min_distance(b, f, next_edges, edges)

                        if r == g - 1:
                            # Расстояние = g-1: соединяем напрямую
                            next_edges.append((b, f))
                            p[f] = v - 2
                        elif r == g - 2:
                            # Расстояние = g-2: вставляем промежуточную вершину
                            x = h + len(next_vertices)
                            next_vertices.append(x)
                            next_edges.append((x, f))
                            next_edges.append((b, x))
                            p[x] = v - 2
                            p[f] = v - 2
                        else:
                            # Обычный случай: создаём новую вершину и соединяем
                            x = h + len(next_vertices)
                            next_vertices.append(x)
                            next_edges.append((b, x))
                            p[x] = v - 1

                        i = p[b] + 1  # Выходим из внутреннего цикла
                    else:
                        # M8: Обычные средние рёбра
                        x = h + len(next_vertices)
                        next_vertices.append(x)
                        next_edges.append((b, x))
                        p[x] = v - 1

                    i += 1

                j += 1

    return vertices, edges

# этот метод был добавлен вручную из первого примера
def print_graph(m, v, g):
    tv, te = construct_planar_graph(m, v, g)
    print(f"Планарный граф l({v}, {g}), число ярусов m = {m}")
    for k in range(m):
        print(f"Ярус {k}")
        print(f"  список вершин: {tv[k]}")
        print(f"  список рёбер:  {te[k]}")

# этот метод был добавлен вручную из первого примера
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