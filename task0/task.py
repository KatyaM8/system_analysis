# -*- coding: utf-8 -*-

#TO DO: 
#Вам дан файл в формате csv (например, такой csv), в котором записан граф в виде списка ребер.
#Необходимо написать программу (вызов из функции main() 
#в файле task0\task.py (cpp), которая получает на вход строку 
#(из csv) и возвращает таблицу (список списков), содержащую матрицу смежности для графа заданного в csv.

def main(csv_string):
	#разбиваю строку на список рёбер
	edges = csv_string.strip().split('\n')

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
	matrix = [[0] *  n for _ in range(n)]
	
	#заполнение матрицы
	for edge in edges:
		parts = edge.split(',')
		u = parts[0]
		v = parts[1]

		i = nodes_list.index(u)
		j = nodes_list.index(v)

		matrix[i][j] = 1
		matrix[j][i] = 1 

	return matrix