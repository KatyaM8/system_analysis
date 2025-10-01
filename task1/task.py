# -*- coding: utf-8 -*-

#TO DO:
#


def main(E: str, e: str): 
    #разбиваю строку на список рёбер
	edges = E.strip().split('\n')

	#множество для уникальных вершин
	nodes_set = set()
	for edge in edges:
		parts = edge.split(',')
		nodes_set.add(parts[0])
		nodes_set.add(parts[1])

	#сортирую множество (отсортированный список)
	nodes_list = sorted(list(nodes_set))
	n = len(nodes_list)
	
	#матрица n на n, заполненная нулями
	matrix0 = [[0] *  n for _ in range(n)]
	matrix1 = [[0] *  n for _ in range(n)] #r1 - отношение управления
	matrix2 = [[0] *  n for _ in range(n)] #r2 - отношение подчинения
	matrix3 = [[0] *  n for _ in range(n)] #r3 - отношение соседства
	matrix4 = [[0] *  n for _ in range(n)] #r4 - опосредованное подчинение
	matrix5 = [[0] *  n for _ in range(n)] #r5 - опосредованное управление
	
	#заполнение матрицы
	for edge in edges:
		parts = edge.split(',')
		u = parts[0]
		v = parts[1]

		i = nodes_list.index(u)
		j = nodes_list.index(v)

		matrix0[i][j] = 1
		matrix0[j][i] = 1
		
		
		matrix1[i][j] = 1
		
		matrix2[j][i] = 1
		
    #matrix3:
	# Находим для каждой вершины её непосредственного начальника
	boss_of = {}
	for edge in edges:
		parts = edge.split(',')
		u = parts[0]
		v = parts[1]
		boss_of[v] = u		
	for i in range(n):
		for j in range(n):
			if i != j:
				node_i = nodes_list[i]
				node_j = nodes_list[j]
				if (node_i in boss_of and node_j in boss_of and boss_of[node_i] == boss_of[node_j]):
					matrix3[i][j] = 1
					matrix3[j][i] = 1
	

    # MATRIX4: опосредованное подчинение (транзитивное замыкание matrix2)
    # Подчинение через промежуточные вершины 
	matrix4 = [[0] * n for _ in range(n)]  # начинаем с нулевой матрицы
	for k in range(n):
		for i in range(n):
			for j in range(n):
                # Если i подчиняется k, и k подчиняется j, и это НЕ прямое подчинение
				if matrix2[i][k] and matrix2[k][j] and not matrix2[i][j] and i != j:
					matrix4[i][j] = 1
					

    # MATRIX5: опосредованное управление (ТОЛЬКО через промежуточные вершины)
	matrix5 = [[0] * n for _ in range(n)]  # начинаем с нулевой матрицы
	for k in range(n):
            for i in range(n):
                for j in range(n):
                    # Если i управляет k, и k управляет j, и это НЕ прямое управление
                    if matrix1[i][k] and matrix1[k][j] and not matrix1[i][j] and i != j:
                        matrix5[i][j] = 1
	return (matrix0, matrix1, matrix2, matrix3, matrix4, matrix5)
			




