
# -*- coding: utf-8 -*-

from typing import List, Tuple


def main(E: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]], 
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:
    # Разбиваем строку на список рёбер
    edges = E.strip().split('\n')
    
    # Множество для уникальных вершин
    nodes_set = set()
    for edge in edges:
        parts = edge.split(',')
        nodes_set.add(parts[0])
        nodes_set.add(parts[1])
    
    # Сортировка вершин
    nodes_list = sorted(list(nodes_set))
    n = len(nodes_list)
    
    # Матрица смежности исходного ориентированного графа
    adj_matrix = [[0] * n for _ in range(n)]
    
    # Заполнение матрицы смежности
    for edge in edges:
        parts = edge.split(',')
        u = parts[0]
        v = parts[1]
        i = nodes_list.index(u)
        j = nodes_list.index(v)
        adj_matrix[i][j] = 1
    
    # r1 - отношение непосредственного управления 
    r1 = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            r1[i][j] = bool(adj_matrix[i][j])
    
    # r2 - отношение непосредственного подчинения 
    r2 = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            r2[i][j] = bool(adj_matrix[j][i])
    
    # r3 - отношение опосредованного управления 
    r3 = [[False] * n for _ in range(n)]
    # Используем алгоритм Флойда-Уоршелла
    # Сначала копируем r1
    for i in range(n):
        for j in range(n):
            r3[i][j] = r1[i][j]
    
    # поиск транзитивного замыкания
    for k in range(n):
        for i in range(n):
            for j in range(n):
                r3[i][j] = r3[i][j] or (r3[i][k] and r3[k][j])

    for i in range(n):
        for j in range(n):
            if r1[i][j]:
                r3[i][j] = False
    
    # r4 - отношение опосредованного подчинения 
    r4 = [[False] * n for _ in range(n)]
    # копирую r2
    for i in range(n):
        for j in range(n):
            r4[i][j] = r2[i][j]
    
    # поиск транзитивного замыкание
    for k in range(n):
        for i in range(n):
            for j in range(n):
                r4[i][j] = r4[i][j] or (r4[i][k] and r4[k][j])
    
    # Убираю прямые подчинения (они уже в r2)
    for i in range(n):
        for j in range(n):
            if r2[i][j]:
                r4[i][j] = False
    
    # r5 - отношение соподчинения 
    r5 = [[False] * n for _ in range(n)]
    
    # Нахожу для каждой вершины её родителя
    parent = {}
    for edge in edges:
        u, v = edge.split(',')
        parent[v] = u
    
    # Две вершины соподчинены, если у них одинаковый непосредственный начальник
    for i in range(n):
        for j in range(n):
            if i != j:
                node_i = nodes_list[i]
                node_j = nodes_list[j]
                if (node_i in parent and node_j in parent and 
                    parent[node_i] == parent[node_j]):
                    r5[i][j] = True
    
    return (r1, r2, r3, r4, r5)

