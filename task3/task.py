# -*- coding: utf-8 -*-


import json
from typing import List, Dict, Tuple, Union


RankingItem = Union[int, List[int]]


def _parse_ranking(json_str: str) -> List[RankingItem]:
    """
    Парсинг JSON-строки с кластерной ранжировкой

    Пример:
        "[1,[2,3],4,[5,6,7],8,9,10]" -> [1, [2,3], 4, [5,6,7], 8, 9, 10]
    """
    data = json.loads(json_str)
    if not isinstance(data, list):
        raise ValueError("Ранжировка должна быть списком.")
    return data


def _collect_objects(r1: List[RankingItem], r2: List[RankingItem]) -> List[int]:
    """
    Собираем множество всех объектов из двух ранжировок и сортируем их
    """
    objs = set()
    for ranking in (r1, r2):
        for item in ranking:
            if isinstance(item, list):
                objs.update(item)
            else:
                objs.add(item)
    return sorted(objs)


def _build_positions(ranking: List[RankingItem]) -> Dict[int, int]:
    """
    Строим словарь: объект -> номер кластера (позиция слева направо, 0,1,2,...).

    Объекты в одном списке-кластере получают одинаковую позицию
    """
    pos: Dict[int, int] = {}
    for idx, item in enumerate(ranking):
        if isinstance(item, list):
            for x in item:
                pos[x] = idx
        else:
            pos[item] = idx
    return pos


def _build_relation_matrix(objects: List[int], positions: Dict[int, int]) -> List[List[int]]:
    """
    Строим матрицу отношений Y размером n×n, где

        y_ij = 1, если x_i стоит правее или в том же кластере, что и x_j
        (т.е. объект i не хуже объекта j в данной ранжировке),
        иначе y_ij = 0.

    Порядок объектов в матрице соответствует списку objects
    """
    n = len(objects)
    Y = [[0] * n for _ in range(n)]
    for i, oi in enumerate(objects):
        for j, oj in enumerate(objects):
            if positions[oi] >= positions[oj]:
                Y[i][j] = 1
            else:
                Y[i][j] = 0
    return Y


def _transpose(mat: List[List[int]]) -> List[List[int]]:
    return [list(row) for row in zip(*mat)]


def _mat_and(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    n = len(A)
    m = len(A[0])
    return [[A[i][j] & B[i][j] for j in range(m)] for i in range(n)]


def _mat_or(A: List[List[int]], B: List[List[int]]) -> List[List[int]]:
    n = len(A)
    m = len(A[0])
    return [[A[i][j] | B[i][j] for j in range(m)] for i in range(n)]


def _find_contradiction_core(
    objects: List[int],
    YA: List[List[int]],
    YB: List[List[int]],
) -> Tuple[List[Tuple[int, int]], List[List[int]]]:
    """
    Этап 1: поиск ядра противоречий S(A,B).

    1) YAB   = YA ◦ YB   (поэлементная конъюнкция)
    2) YAB'  = YA^T ◦ YB^T
    3) M     = YAB ∨ YAB' (поэлементное логическое сложение)
    4) Пара (i,j) входит в ядро, если
           M[i,j] == 0 и M[j,i] == 0.

    Возвращает:
        - список пар (объект_i, объект_j) в ядре;
        - матрицу YAB (она пригодится на этапе 2).
    """
    YAT = _transpose(YA)
    YBT = _transpose(YB)

    YAB = _mat_and(YA, YB)
    YAB_T = _mat_and(YAT, YBT)

    M = _mat_or(YAB, YAB_T)

    n = len(objects)
    core_pairs: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            if M[i][j] == 0 and M[j][i] == 0:
                core_pairs.append((objects[i], objects[j]))



    #отсортировываю ядро, чтобы результат был детерминированным
    core_pairs.sort()
    return core_pairs, YAB


def _build_clusters(
    objects: List[int],
    YAB: List[List[int]],
    core_pairs: List[Tuple[int, int]],
) -> List[List[int]]:
    """
    Этап 2 (часть 1): поиск кластеров (компонент связности)

    1) C = YAB — матрица согласованности (общих "не хуже")
    2) E[i,j] = 1, если C[i,j] == 1 и C[j,i] == 1
       (эквивалентность по отношению C)
    3) добавляем рёбра между объектами из ядра противоречий
    4) кластеры = компоненты связности графа по этим рёбрам
    """
    n = len(objects)
    index = {obj: i for i, obj in enumerate(objects)}

    C = YAB

    # Матрица эквивалентности E по C
    E = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if C[i][j] and C[j][i]:
                E[i][j] = 1


    # Строю неориентированный граф: E + связи из ядра противоречий
    adj = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j and E[i][j]:
                adj[i][j] = adj[j][i] = 1

    for a, b in core_pairs:
        ia, ib = index[a], index[b]
        adj[ia][ib] = adj[ib][ia] = 1

    # Поиск компонент связности (DFS)
    visited = [False] * n
    components: List[List[int]] = []

    for i in range(n):
        if not visited[i]:
            stack = [i]
            visited[i] = True
            comp = [i]
            while stack:
                v = stack.pop()
                for u in range(n):
                    if adj[v][u] and not visited[u]:
                        visited[u] = True
                        stack.append(u)
                        comp.append(u)
            comp.sort()
            components.append(comp)

    # Перевожу индексы в номера объектов
    clusters: List[List[int]] = []
    for comp in components:
        cluster = [objects[i] for i in comp]
        cluster.sort()
        clusters.append(cluster)

    return clusters


def _order_clusters(
    clusters: List[List[int]],
    posA: Dict[int, int],
    posB: Dict[int, int],
) -> List[List[int]]:
    """
    Этап 2 (часть 2): упорядочиваем кластеры

    Для каждого кластера считаем "среднюю позицию" по двум ранжировкам:

        score(C_k) = среднее значение (posA[x] + posB[x]) / 2 по x ∈ C_k

    Затем сортируем кластеры по score (от "хуже" к "лучше")
    Это даёт согласованную кластерную ранжировку.
    """
    def score(cluster: List[int]) -> float:
        s = 0.0
        for x in cluster:
            s += (posA[x] + posB[x]) / 2.0
        return s / len(cluster)

    # сортирую по средней позиции и по минимуму объекта для устойчивости
    clusters_sorted = sorted(
        clusters,
        key=lambda c: (score(c), min(c))
    )
    return clusters_sorted


def _format_ranking_for_json(clusters: List[List[int]]) -> List[RankingItem]:
    """
    Преобразую кластеры.
    (одиночные объекты — просто числа, кластеры >1 — списки).
    """
    result: List[RankingItem] = []
    for cl in clusters:
        if len(cl) == 1:
            result.append(cl[0])
        else:
            result.append(cl)
    return result


def main(json_a: str, json_b: str) -> str:
    """
    Главная функция

    Принимает:
        json_a, json_b — две JSON-строки с кластерными ранжировками,
        например:
            "[1,[2,3],4,[5,6,7],8,9,10]"
            "[[1,2],[3,4,5],6,7,9,[8,10]]"

    Возвращает:
        JSON-строку с результатом этапа 2:
        согласованную кластерную ранжировку, например:
        "[[1,3],[2,4],6,[5,7],8,9,10]"
    """
    # --- Парсим вход ---
    ranking_a = _parse_ranking(json_a)
    ranking_b = _parse_ranking(json_b)

    # --- Носитель (множество объектов) ---
    objects = _collect_objects(ranking_a, ranking_b)

    # --- Позиции в каждой ранжировке ---
    posA = _build_positions(ranking_a)
    posB = _build_positions(ranking_b)

    # --- Матрицы отношений YA и YB ---
    YA = _build_relation_matrix(objects, posA)
    YB = _build_relation_matrix(objects, posB)

    # --- Этап 1: ядро противоречий + матрица согласованности YAB ---
    core_pairs, YAB = _find_contradiction_core(objects, YA, YB)

    # --- Этап 2: кластеры (компоненты связности) ---
    clusters = _build_clusters(objects, YAB, core_pairs)

    # --- Этап 2: упорядочивание кластеров ---
    ordered_clusters = _order_clusters(clusters, posA, posB)

    # --- Формируем итоговую кластерную ранжировку для JSON ---
    final_ranking = _format_ranking_for_json(ordered_clusters)

    # Возвращаем только результат этапа 2
    return json.dumps(final_ranking, ensure_ascii=False)




