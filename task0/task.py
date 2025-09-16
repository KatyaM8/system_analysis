# -*- coding: utf-8 -*-

#TO DO: 
#��� ��� ���� � ������� csv (��������, ����� csv), � ������� ������� ���� � ���� ������ �����.
#���������� �������� ��������� (����� �� ������� main() 
#� ����� task0\task.py (cpp), ������� �������� �� ���� ������ 
#(�� csv) � ���������� ������� (������ �������), ���������� ������� ��������� ��� ����� ��������� � csv.

def main(csv_string):
	#�������� ������ �� ������ ����
	edges = csv_string.strip().split('\n')

	#��������� ��� ���������� ������
	nodes_set = set()
	for edge in edges:
		parts = edge.split(',')
		nodes_set.add(parts[0])
		nodes_set.add(parts[1])

	#�������� ��������� (��������������� ������)
	nodes_list = sorted(list(nodes_set))
	n = len(nodes_list)
	
	#������� n �� n, ����������� ������
	matrix = [[0] *  n for _ in range(n)]
	
	#���������� �������
	for edge in edges:
		parts = edge.split(',')
		u = parts[0]
		v = parts[1]

		i = nodes_list.index(u)
		j = nodes_list.index(v)

		matrix[i][j] = 1
		matrix[j][i] = 1 

	return matrix